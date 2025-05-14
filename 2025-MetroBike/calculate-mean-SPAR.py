# Calculate mean SPAR
spar_values = []  

# Import kiosk buffer
kiosk_buffer = gpd.read_file(f'b9.shp')
kiosk_buffer['ID'] = [name.split(' :')[0] for name in kiosk_buffer['Name']]
kiosk_buffer['ID'] = kiosk_buffer['ID'].astype(str)

# Import kiosk point
kiosk_point = gpd.read_file('kiosk_point.shp')
kiosk_point.rename(columns={'Number of': 'Capacity', 'Kiosk ID': 'ID'}, inplace=True)
kiosk_point['ID'] = kiosk_point['ID'].astype(str)

# Join kiosk to kiosk buffer
kiosk_buffer = gpd.GeoDataFrame(kiosk_buffer[['ID', 'geometry']]).merge(
    kiosk_point[['ID', 'Kiosk Name', 'Capacity']], on='ID', how='inner')
kiosk_buffer = gpd.GeoDataFrame(kiosk_buffer, geometry='geometry')

# Import census point
census_point = gpd.read_file('census_point.shp')
census_point.rename(columns={'NAME': 'name'}, inplace=True)
census_point = census_point[['name', 'POPDEN', 'geometry']]
census_point = census_point.to_crs(kiosk_buffer.crs)

# Spatial join
result = gpd.sjoin(kiosk_buffer, census_point, how="inner", predicate="intersects")
sum_pop_rate = result.groupby('ID')['POPDEN'].sum().reset_index()
sum_pop_rate.rename(columns={'POPDEN': 'pop_sum'}, inplace=True)
kiosk_buffer['pop_sum'] = kiosk_buffer['ID'].map(sum_pop_rate.set_index('ID')['pop_sum']).fillna(0)

# Join kiosk buffer to kiosk
kiosk_point = gpd.GeoDataFrame(kiosk_buffer[['ID', 'pop_sum']]).merge(
    kiosk_point[['ID', 'Capacity', 'geometry']], on='ID', how='inner')
kiosk_point = gpd.GeoDataFrame(kiosk_point, geometry='geometry')

# Import pop buffer
pop_buffer = gpd.read_file(f'c9.shp')
pop_buffer['name'] = [name.split(' :')[0] for name in pop_buffer['Name']]

# Join pop to pop buffer
pop_buffer = pop_buffer[['name', 'geometry']].merge(census_point[['name', 'POPDEN']], on='name', how='inner')

# Spatial join
result = gpd.sjoin(pop_buffer, kiosk_point, how="inner", predicate="intersects")
sum_ProToPop = result.groupby('name')['pop_sum'].sum().reset_index()
sum_ProToPop.rename(columns={'pop_sum': 'sfca'}, inplace=True)
pop_buffer['sfca'] = pop_buffer['name'].map(sum_ProToPop.set_index('name')['sfca']).fillna(0)

# Divide by mean
pop_buffer['spar'] = pop_buffer['sfca'] / pop_buffer['sfca'].mean()

# Save the mean SPAR score
spar_values.append(pop_buffer['spar'].mean())
    
print(spar_values)
