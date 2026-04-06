// ============================================================
// 0. Load tract shapefile and select target counties
// ============================================================
var tracts = ee.FeatureCollection(
  'projects/skilled-text-*/assets/tl_2023_06_tract'
);

// Select counties:
// Los Angeles County = 06037  -> COUNTYFP = 037
// San Diego County   = 06073  -> COUNTYFP = 073
// San Francisco      = 06075  -> COUNTYFP = 075
var selectedTracts = tracts.filter(
  ee.Filter.inList('COUNTYFP', ['037', '073', '075'])
);

Map.centerObject(selectedTracts, 8);
Map.addLayer(selectedTracts, {color: 'red'}, 'Selected Tracts');

// ============================================================
// 1. Cloud masking function for Landsat 8 Collection 2 Level 2
// ============================================================
function maskL8sr(image) {
  var qaPixel = image.select('QA_PIXEL');

  // Bit flags
  var fill = qaPixel.bitwiseAnd(1 << 0).neq(0);
  var dilatedCloud = qaPixel.bitwiseAnd(1 << 1).neq(0);
  var cirrus = qaPixel.bitwiseAnd(1 << 2).neq(0);
  var cloud = qaPixel.bitwiseAnd(1 << 3).neq(0);
  var cloudShadow = qaPixel.bitwiseAnd(1 << 4).neq(0);

  var mask = fill.or(dilatedCloud)
                 .or(cirrus)
                 .or(cloud)
                 .or(cloudShadow)
                 .not();

  return image.updateMask(mask);
}

// ============================================================
// 2. Scaling + variable calculation
// ============================================================
function addVariables(image) {
  // Scale optical reflectance bands
  var optical = image.select([
      'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7'
    ])
    .multiply(0.0000275)
    .add(-0.2);

  // Scale surface temperature band (Kelvin -> Celsius)
  var lst = image.select('ST_B10')
    .multiply(0.00341802)
    .add(149.0)
    .subtract(273.15)
    .rename('LST');

  // Rename scaled optical bands for convenience
  var blue  = optical.select('SR_B2');
  var green = optical.select('SR_B3');
  var red   = optical.select('SR_B4');
  var nir   = optical.select('SR_B5');
  var swir1 = optical.select('SR_B6');
  var swir2 = optical.select('SR_B7');

  // Indices
  var ndvi = nir.subtract(red).divide(nir.add(red)).rename('NDVI');

  var ndbi = swir1.subtract(nir).divide(swir1.add(nir)).rename('NDBI');

  var ndwi = green.subtract(nir).divide(green.add(nir)).rename('NDWI');

  var ndmi = nir.subtract(swir1).divide(nir.add(swir1)).rename('NDMI');

  var savi = nir.subtract(red)
    .multiply(1.5)
    .divide(nir.add(red).add(0.5))
    .rename('SAVI');

  // Broadband albedo (Liang 2001 style coefficients)
  var albedo = blue.multiply(0.356)
    .add(red.multiply(0.130))
    .add(nir.multiply(0.373))
    .add(swir1.multiply(0.085))
    .add(swir2.multiply(0.072))
    .subtract(0.0018)
    .rename('Albedo');

  return image.addBands(optical, null, true)
              .addBands(lst)
              .addBands(ndvi)
              .addBands(ndbi)
              .addBands(ndwi)
              .addBands(ndmi)
              .addBands(savi)
              .addBands(albedo);
}

// ============================================================
// 3. Load summer Landsat 8 images
//    Change date if needed
// ============================================================
var landsat = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
  .filterBounds(selectedTracts)
  .filterDate('2023-06-01', '2023-08-31')
  .filter(ee.Filter.lt('CLOUD_COVER', 30))
  .map(maskL8sr)
  .map(addVariables);

print('Landsat collection:', landsat);

// ============================================================
// 4. Create summer mean composite
// ============================================================
var lstMean = landsat.select('LST').mean().rename('LST_mean');
var lstStd  = landsat.select('LST').reduce(ee.Reducer.stdDev()).rename('LST_std');

var ndviMean   = landsat.select('NDVI').mean().rename('NDVI_mean');
var ndbiMean   = landsat.select('NDBI').mean().rename('NDBI_mean');
var ndwiMean   = landsat.select('NDWI').mean().rename('NDWI_mean');
var ndmiMean   = landsat.select('NDMI').mean().rename('NDMI_mean');
var saviMean   = landsat.select('SAVI').mean().rename('SAVI_mean');
var albedoMean = landsat.select('Albedo').mean().rename('Albedo_mean');

// Final multiband image
var finalImage = ee.Image.cat([
  lstMean,
  lstStd,
  ndviMean,
  ndbiMean,
  ndwiMean,
  ndmiMean,
  saviMean,
  albedoMean
]);

print('Final image:', finalImage);

// ============================================================
// 5. Visualization
// ============================================================
Map.addLayer(lstMean, {
  min: 20,
  max: 50,
  palette: ['blue', 'cyan', 'green', 'yellow', 'orange', 'red']
}, 'LST_mean');

Map.addLayer(ndviMean, {
  min: -0.2,
  max: 0.8,
  palette: ['brown', 'yellow', 'green']
}, 'NDVI_mean');

Map.addLayer(ndbiMean, {
  min: -0.5,
  max: 0.5,
  palette: ['blue', 'white', 'red']
}, 'NDBI_mean');

// ============================================================
// 6. Zonal statistics by tract
// ============================================================
var stats = finalImage.reduceRegions({
  collection: selectedTracts,
  reducer: ee.Reducer.mean(),
  scale: 30,
  crs: 'EPSG:32611' // optional; can remove if not needed
});

print('Tract-level stats:', stats.limit(10));

// ============================================================
// 7. Keep only useful columns if desired
//    (Modify property names depending on your tract attribute table)
// ============================================================
var output = stats.map(function(f) {
  return f.select([
    'STATEFP',
    'COUNTYFP',
    'TRACTCE',
    'GEOID',
    'NAME',
    'LST_mean',
    'LST_std',
    'NDVI_mean',
    'NDBI_mean',
    'NDWI_mean',
    'NDMI_mean',
    'SAVI_mean',
    'Albedo_mean'
  ]);
});

print('Output preview:', output.limit(10));

// ============================================================
// 8. Export to Google Drive as CSV
// ============================================================
Export.table.toDrive({
  collection: output,
  description: 'CA_tract_LST_NDVI_NDBI_NDWI_NDMI_SAVI_Albedo_2023summer',
  fileFormat: 'CSV'
});
