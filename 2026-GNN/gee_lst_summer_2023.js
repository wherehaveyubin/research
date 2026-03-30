// Load California tract shapefile
var tracts = ee.FeatureCollection(
  'projects/skilled-text-*/assets/tl_2023_06_tract'
);

// Load California state boundary
var california = ee.FeatureCollection('TIGER/2018/States')
  .filter(ee.Filter.eq('NAME', 'California'));

// Display California tracts
Map.addLayer(tracts, {color: 'red'}, 'California Tracts');
Map.centerObject(california, 6);

// Load MODIS LST
var lst = ee.ImageCollection('MODIS/061/MOD11A2')
  .filterDate('2023-06-01', '2023-09-01')
  .select('LST_Day_1km')
  .map(function(img) {
    return img.multiply(0.02).subtract(273.15)
      .rename('LST')
      .copyProperties(img, ['system:time_start']);
  });

// Mean summer LST
var summerMeanLST = lst.mean();

// Display mean LST for California
Map.addLayer(
  summerMeanLST.clip(california),
  {min: 20, max: 45},
  'California Mean Summer LST'
);

// Export raster image to Google Drive
Export.image.toDrive({
  image: summerMeanLST.clip(california),
  description: 'CA_LST_2023_summer_raster',
  folder: 'GEE_LST',
  fileNamePrefix: 'CA_LST_2023_summer',
  region: california.geometry().bounds(),
  scale: 1000,
  maxPixels: 1e13
});
