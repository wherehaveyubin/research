// =====================================
// 1. Load uploaded tract and place shapefiles
// =====================================
var tracts = ee.FeatureCollection(
  'projects/skilled-text-*/assets/tl_2023_06_tract'
);

var places = ee.FeatureCollection(
  'projects/skilled-text-148213/assets/tl_2023_06_place'
);

// Filter California only (STATEFP = 06)
var places_ca = places.filter(ee.Filter.eq('STATEFP', '06'));

// =====================================
// 2. Select target cities
// =====================================
var sfCity = places_ca.filter(ee.Filter.eq('NAME', 'San Francisco'));
var laCity = places_ca.filter(ee.Filter.eq('NAME', 'Los Angeles'));
var sdCity = places_ca.filter(ee.Filter.eq('NAME', 'San Diego'));

// Select tracts intersecting each city
var sfTracts = tracts.filterBounds(sfCity);
var laTracts = tracts.filterBounds(laCity);
var sdTracts = tracts.filterBounds(sdCity);

// Display
Map.addLayer(sfCity, {color: 'blue'}, 'San Francisco');
Map.addLayer(laCity, {color: 'green'}, 'Los Angeles');
Map.addLayer(sdCity, {color: 'purple'}, 'San Diego');

Map.addLayer(sfTracts, {color: 'red'}, 'SF Tracts');
Map.addLayer(laTracts, {color: 'orange'}, 'LA Tracts');
Map.addLayer(sdTracts, {color: 'yellow'}, 'SD Tracts');

Map.centerObject(laCity, 8);

// =====================================
// 3. Cloud mask + LST conversion
// =====================================
function maskAndConvertLST(image) {
  var qaPixel = image.select('QA_PIXEL');
  var qaRadSat = image.select('QA_RADSAT');

  var cloudShadowBitMask = 1 << 4;
  var cloudBitMask = 1 << 3;
  var snowBitMask = 1 << 5;

  var mask = qaPixel.bitwiseAnd(cloudShadowBitMask).eq(0)
    .and(qaPixel.bitwiseAnd(cloudBitMask).eq(0))
    .and(qaPixel.bitwiseAnd(snowBitMask).eq(0))
    .and(qaRadSat.eq(0));

  var lstC = image.select('ST_B10')
    .multiply(0.00341802)
    .add(149.0)
    .subtract(273.15)
    .rename('LST');

  return lstC.updateMask(mask)
    .copyProperties(image, ['system:time_start']);
}

// =====================================
// 4. Load Landsat 8 and 9
// =====================================
var targetCities = sfCity.merge(laCity).merge(sdCity);

var l8 = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
  .filterDate('2023-06-01', '2023-09-01')
  .filterBounds(targetCities)
  .map(maskAndConvertLST);

var l9 = ee.ImageCollection('LANDSAT/LC09/C02/T1_L2')
  .filterDate('2023-06-01', '2023-09-01')
  .filterBounds(targetCities)
  .map(maskAndConvertLST);

var lst = l8.merge(l9);

// Mean summer LST
var summerMeanLST = lst.mean();

// =====================================
// 5. Function for city-level export
// =====================================
function exportCity(cityFc, tractFc, cityName) {

  // Clip raster to city
  var cityLST = summerMeanLST.clip(cityFc);

  // Export raster
  Export.image.toDrive({
    image: cityLST,
    description: cityName + '_LST_raster',
    folder: 'GEE_LST',
    fileNamePrefix: cityName + '_LST_2023_summer',
    region: cityFc.geometry().bounds(),
    scale: 30,
    maxPixels: 1e13
  });

  // Zonal statistics
  var tractLST = cityLST.reduceRegions({
    collection: tractFc,
    reducer: ee.Reducer.mean(),
    scale: 60,
    tileScale: 8
  });

  // Clean output (remove geometry)
  var cleaned = tractLST.map(function(f) {
    return ee.Feature(null, {
      City: cityName,
      GEOID: f.get('GEOID'),
      NAME: f.get('NAME'),
      COUNTYFP: f.get('COUNTYFP'),
      LST_mean: f.get('mean')
    });
  });

  print(cityName + ' sample:', cleaned.limit(5));

  // Export CSV
  Export.table.toDrive({
    collection: cleaned,
    description: cityName + '_tract_LST_mean',
    folder: 'GEE_LST',
    fileNamePrefix: cityName + '_tract_LST_mean',
    fileFormat: 'CSV'
  });
}

// =====================================
// 6. Run export for each city
// =====================================
exportCity(sfCity, sfTracts, 'SanFrancisco');
exportCity(laCity, laTracts, 'LosAngeles');
exportCity(sdCity, sdTracts, 'SanDiego');
