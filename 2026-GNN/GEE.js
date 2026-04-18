// ============================================================
// Environmental variables for LA, SD, SF census tracts
// 
// Outputs CSV with:
//   - GEOID (for tract matching)
//   - STATEFP, COUNTYFP, NAME (identification)
//   - 18 environmental variables
//   - NO geometry (.geo) column
//   - NO TRACTCE column
// ============================================================


// ============================================================
// 0. Load tract shapefile and select target counties
// ============================================================
var tracts = ee.FeatureCollection(
  'projects/skilled-text-*/assets/tracts'
);

// LA County = 06037, San Diego = 06073, San Francisco = 06075
var selectedTracts = tracts.filter(
  ee.Filter.inList('COUNTYFP', ['037', '073', '075'])
);

Map.centerObject(selectedTracts, 8);
Map.addLayer(selectedTracts, {color: 'red'}, 'Selected Tracts');


// ============================================================
// 1. Constants
// ============================================================
var TREND_START = 2013;
var TREND_END   = 2023;
var SUMMER_START_MONTH = 6;
var SUMMER_END_MONTH   = 8;


// ============================================================
// 2. Landsat 8 cloud masking
// ============================================================
function maskL8sr(image) {
  var qaPixel = image.select('QA_PIXEL');
  var fill         = qaPixel.bitwiseAnd(1 << 0).neq(0);
  var dilatedCloud = qaPixel.bitwiseAnd(1 << 1).neq(0);
  var cirrus       = qaPixel.bitwiseAnd(1 << 2).neq(0);
  var cloud        = qaPixel.bitwiseAnd(1 << 3).neq(0);
  var cloudShadow  = qaPixel.bitwiseAnd(1 << 4).neq(0);
  var mask = fill.or(dilatedCloud).or(cirrus).or(cloud).or(cloudShadow).not();
  return image.updateMask(mask);
}


// ============================================================
// 3. Landsat variable calculation
// ============================================================
function addVariables(image) {
  var optical = image.select([
      'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7'
    ])
    .multiply(0.0000275)
    .add(-0.2);

  var lst = image.select('ST_B10')
    .multiply(0.00341802)
    .add(149.0)
    .subtract(273.15)
    .rename('LST');

  var blue  = optical.select('SR_B2');
  var green = optical.select('SR_B3');
  var red   = optical.select('SR_B4');
  var nir   = optical.select('SR_B5');
  var swir1 = optical.select('SR_B6');
  var swir2 = optical.select('SR_B7');

  var ndvi = nir.subtract(red).divide(nir.add(red)).rename('NDVI');
  var ndbi = swir1.subtract(nir).divide(swir1.add(nir)).rename('NDBI');
  var ndwi = green.subtract(nir).divide(green.add(nir)).rename('NDWI');
  var ndmi = nir.subtract(swir1).divide(nir.add(swir1)).rename('NDMI');

  var savi = nir.subtract(red).multiply(1.5)
    .divide(nir.add(red).add(0.5))
    .rename('SAVI');

  var albedo = blue.multiply(0.356)
    .add(red.multiply(0.130))
    .add(nir.multiply(0.373))
    .add(swir1.multiply(0.085))
    .add(swir2.multiply(0.072))
    .subtract(0.0018)
    .rename('Albedo');

  return image.addBands(optical, null, true)
              .addBands(lst).addBands(ndvi).addBands(ndbi)
              .addBands(ndwi).addBands(ndmi).addBands(savi)
              .addBands(albedo);
}


// ============================================================
// 4A. SUMMER 2023 — Landsat daytime LST + vegetation/albedo (8 vars)
// ============================================================
var landsat2023 = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
  .filterBounds(selectedTracts)
  .filterDate('2023-06-01', '2023-08-31')
  .filter(ee.Filter.lt('CLOUD_COVER', 30))
  .map(maskL8sr)
  .map(addVariables);

var lstDayMean = landsat2023.select('LST').mean().rename('LST_day_mean');
var lstDayStd  = landsat2023.select('LST').reduce(ee.Reducer.stdDev()).rename('LST_day_std');
var ndviMean   = landsat2023.select('NDVI').mean().rename('NDVI_mean');
var ndbiMean   = landsat2023.select('NDBI').mean().rename('NDBI_mean');
var ndwiMean   = landsat2023.select('NDWI').mean().rename('NDWI_mean');
var ndmiMean   = landsat2023.select('NDMI').mean().rename('NDMI_mean');
var saviMean   = landsat2023.select('SAVI').mean().rename('SAVI_mean');
var albedoMean = landsat2023.select('Albedo').mean().rename('Albedo_mean');


// ============================================================
// 4B. TREND — Daytime LST Sen's slope (2013-2023)
// ============================================================
var years = ee.List.sequence(TREND_START, TREND_END);

var yearlyDayLST = ee.ImageCollection.fromImages(
  years.map(function(y) {
    y = ee.Number(y);
    var start = ee.Date.fromYMD(y, SUMMER_START_MONTH, 1);
    var end   = ee.Date.fromYMD(y, SUMMER_END_MONTH, 31);

    var summerLST = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
      .filterBounds(selectedTracts)
      .filterDate(start, end)
      .filter(ee.Filter.lt('CLOUD_COVER', 30))
      .map(maskL8sr)
      .map(function(img) {
        return img.select('ST_B10')
          .multiply(0.00341802).add(149.0).subtract(273.15)
          .rename('LST');
      })
      .mean();

    return summerLST
      .addBands(ee.Image.constant(y).float().rename('year'))
      .set('year', y);
  })
);

var lstDayTrend = yearlyDayLST
  .select(['year', 'LST'])
  .reduce(ee.Reducer.sensSlope())
  .select('slope')
  .rename('LST_day_trend');


// ============================================================
// 5A. SUMMER 2023 — MODIS nighttime LST (2 vars)
// ============================================================
var modis2023 = ee.ImageCollection('MODIS/061/MOD11A2')
  .filterDate('2023-06-01', '2023-08-31')
  .select('LST_Night_1km')
  .map(function(img) {
    return img.multiply(0.02).subtract(273.15)
      .rename('LST_night')
      .copyProperties(img, ['system:time_start']);
  });

var lstNightMean = modis2023.mean().rename('LST_night_mean');
var lstNightStd  = modis2023.reduce(ee.Reducer.stdDev()).rename('LST_night_std');


// ============================================================
// 5B. TREND — Nighttime LST Sen's slope (2013-2023)
// ============================================================
var yearlyNightLST = ee.ImageCollection.fromImages(
  years.map(function(y) {
    y = ee.Number(y);
    var start = ee.Date.fromYMD(y, SUMMER_START_MONTH, 1);
    var end   = ee.Date.fromYMD(y, SUMMER_END_MONTH, 31);

    var summerNight = ee.ImageCollection('MODIS/061/MOD11A2')
      .filterDate(start, end)
      .select('LST_Night_1km')
      .map(function(img) {
        return img.multiply(0.02).subtract(273.15).rename('LST');
      })
      .mean();

    return summerNight
      .addBands(ee.Image.constant(y).float().rename('year'))
      .set('year', y);
  })
);

var lstNightTrend = yearlyNightLST
  .select(['year', 'LST'])
  .reduce(ee.Reducer.sensSlope())
  .select('slope')
  .rename('LST_night_trend');


// ============================================================
// 6. ANNUAL 2023 — VIIRS Nighttime Lights
// ============================================================
var viirs = ee.ImageCollection('NOAA/VIIRS/DNB/MONTHLY_V1/VCMSLCFG')
  .filterDate('2023-01-01', '2023-12-31')
  .select('avg_rad');
var ntlMean = viirs.mean().rename('NTL_mean');


// ============================================================
// 7. STATIC — SRTM Elevation and Slope
// ============================================================
var srtm = ee.Image('USGS/SRTMGL1_003');
var elevation = srtm.select('elevation').rename('Elevation');
var slopeImg  = ee.Terrain.slope(srtm).rename('Slope');


// ============================================================
// 8. ANNUAL 2023 — Sentinel-5P NO2 and Aerosol Index
// ============================================================
var no2 = ee.ImageCollection('COPERNICUS/S5P/OFFL/L3_NO2')
  .filterDate('2023-01-01', '2023-12-31')
  .select('tropospheric_NO2_column_number_density');
var no2Mean = no2.mean().multiply(1e6).rename('NO2_mean');

var aerosol = ee.ImageCollection('COPERNICUS/S5P/OFFL/L3_AER_AI')
  .filterDate('2023-01-01', '2023-12-31')
  .select('absorbing_aerosol_index');
var aerosolMean = aerosol.mean().rename('Aerosol_index');


// ============================================================
// 9. Combine all 18 variables
// ============================================================
var finalImage = ee.Image.cat([
  lstDayMean, lstDayStd,
  ndviMean, ndbiMean, ndwiMean, ndmiMean, saviMean, albedoMean,
  lstDayTrend,
  lstNightMean, lstNightStd,
  lstNightTrend,
  ntlMean,
  elevation, slopeImg,
  no2Mean, aerosolMean
]);

print('Final image (18 bands):', finalImage);


// ============================================================
// 10. Zonal statistics by tract (GEOID-keyed)
// ============================================================
var stats = finalImage.reduceRegions({
  collection: selectedTracts,
  reducer: ee.Reducer.mean(),
  scale: 30
});

print('Tract-level stats preview:', stats.limit(5));


// ============================================================
// 11. Export to Google Drive (folder: GEE)
//     `selectors` specifies exact CSV columns — this automatically
//     excludes the .geo geometry column.
//     TRACTCE is not included in selectors, so it will be omitted.
// ============================================================
Export.table.toDrive({
  collection: stats,
  description: 'ENV_VARS_LA_SD_SF_2023_with_trend',
  folder: 'GEE',
  fileFormat: 'CSV',
  selectors: [
    // Identifiers
    'GEOID', 'STATEFP', 'COUNTYFP', 'NAME',
    // Daytime LST (Landsat)
    'LST_day_mean', 'LST_day_std', 'LST_day_trend',
    // Nighttime LST (MODIS)
    'LST_night_mean', 'LST_night_std', 'LST_night_trend',
    // Vegetation and albedo (Landsat)
    'NDVI_mean', 'NDBI_mean', 'NDWI_mean', 'NDMI_mean',
    'SAVI_mean', 'Albedo_mean',
    // NTL
    'NTL_mean',
    // Terrain
    'Elevation', 'Slope',
    // Air quality
    'NO2_mean', 'Aerosol_index'
  ]
});
