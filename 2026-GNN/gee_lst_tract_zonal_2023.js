// Load tract shapefile
var tracts = ee.FeatureCollection(
  'projects/skilled-text-*/assets/tl_2023_06_tract'
);

// Load city boundary (places)
var places = ee.FeatureCollection(
  'projects/skilled-text-148213/assets/tl_2023_06_place'
);

// Select cities
var cities = places.filter(
  ee.Filter.inList('NAME', [
    'Los Angeles',
    'San Diego',
    'San Francisco'
  ])
);

// Create 1km buffer
var cities_buffer = cities.map(function(f) {
  return f.buffer(1000);
});

// Display
Map.addLayer(cities, {color: 'blue'}, 'Cities');
Map.addLayer(cities_buffer, {color: 'green'}, 'Cities Buffer');
Map.centerObject(cities_buffer.bounds(), 8);

// Select tracts using buffer (centroid-based)
var cityTracts = tracts.map(function(f) {
  var centroid = f.geometry().centroid(100);
  var inside = cities_buffer.filterBounds(centroid).size().gt(0);
  return f.set('inside_buffer', inside);
}).filter(ee.Filter.eq('inside_buffer', true));

Map.addLayer(cityTracts, {color: 'red'}, 'Buffered City Tracts');

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

// Display LST (buffered)
Map.addLayer(
  summerMeanLST.clip(cities_buffer),
  {min: 20, max: 45},
  'Buffered Mean LST'
);

// Zonal statistics (mean per tract)
var tractLST = summerMeanLST.reduceRegions({
  collection: cityTracts,
  reducer: ee.Reducer.mean(),
  scale: 1000
});

// Rename field
tractLST = tractLST.map(function(f) {
  return f.set('LST_mean', f.get('mean')).select(
    f.propertyNames().remove('mean').add('LST_mean')
  );
});

print('Buffered tract LST:', tractLST.limit(10));

// Export shapefile
Export.table.toDrive({
  collection: tractLST,
  description: 'LST_tract_city_buffer_1km',
  folder: 'GEE_LST',
  fileNamePrefix: 'LST_tract_city_buffer_1km',
  fileFormat: 'SHP'
});

// Export raster
Export.image.toDrive({
  image: summerMeanLST.clip(cities_buffer),
  description: 'LST_city_buffer_1km_raster',
  folder: 'GEE_LST',
  fileNamePrefix: 'LST_city_buffer_1km',
  region: cities_buffer.geometry().bounds(),
  scale: 1000,
  maxPixels: 1e13
});
