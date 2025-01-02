# 1. Data preprocessing
import pandas as pd
import geopandas as gpd
import networkx as nx
from shapely.geometry import LineString, Point

### Prepare the bike data ###
# Import bike trip data
bike = pd.read_csv('Austin_MetroBike_Trips_20240916.csv')
bike.head(5) # Display first 5 rows of the bike data

# Select data for April 2024
bike_2024 = bike[bike['Year'] == 2024] # 141,144 rows
bike_2024['Month'].value_counts() # April 2024 has the most data
bike_apr_2024 = bike_2024[bike_2024['Month'] == 4] # 33,203 rows
bike_apr_2024 = bike_apr_2024[['Trip ID', 'Checkout Date', 'Checkout Time', 'Checkout Kiosk', 'Return Kiosk', 'Trip Duration Minutes']] # Select relevant columns for analysis
bike_apr_2024['Checkout Kiosk'] = bike_apr_2024['Checkout Kiosk'].str.strip() # Remove leading/trailing spaces from 'Checkout Kiosk' column
bike_apr_2024 = bike_apr_2024.replace('11th/Salina ', '11th/Salina')

### Prepare the kiosk data for merging ###
# Import kiosk data
kiosk = pd.read_csv("Austin_MetroBike_Kiosk_Locations.csv") # 102 rows
kiosk['Kiosk ID'] = kiosk['Kiosk ID'].astype('object')

# Check unique kiosk names
unique_bike = pd.DataFrame(sorted(bike_apr_2024['Checkout Kiosk'].unique()), columns=['Unique Checkout Kiosk'])
unique_kiosk = pd.DataFrame(sorted(kiosk['Kiosk Name'].unique()), columns=['Unique Checkout Kiosk'])
unique_names = pd.concat([unique_bike, unique_kiosk], axis=1) # Concatenate the two DataFrames

# Replace ' & ' with '/' in the 'Kiosk Name' column of the kiosk data
kiosk['Kiosk Name'] = kiosk['Kiosk Name'].str.replace(' & ', '/', regex=False)

# Replace 'Kiosk Name' column using the dictionary
replacement_dict = {
    'Capitol Station / Congress/11th' : '11th/Congress @ The Texas Capitol',
    'State Capitol Visitors Garage @ San Jacinto/12th' : '12th/San Jacinto @ State Capitol Visitors Garage',
    '13th/Trinity' : '13th/Trinity @ Waterloo Greenway',
    'Guadalupe/21st' : '21st/Guadalupe',
    '21st/Speedway @PCL' : '21st/Speedway @ PCL',
    '22nd 1/2/Rio Grande' : '22.5/Rio Grande',
    #'' : '23rd/Pearl', # 30.287329976401352, -97.74632802031869 location driven from app
    'Nueces/26th' : '26th/Nueces',
    'Rio Grande/28th' : '28th/Rio Grande',
    'City Hall / Lavaca/2nd' : '2nd/Lavaca @ City Hall',
    'Nueces @ 3rd' : '3rd/Nueces',
    'Nueces/3rd' : '3rd/Nueces',
    'Convention Center / 3rd/Trinity' : '3rd/Trinity @ The Convention Center',
    'Lavaca/6th' : '6th/Lavaca',
    'Trinity/6th Street' : '6th/Trinity',
    'West/6th St.' : '6th/West',
    'Red River/8th Street' : '8th/Red River',
    'San Jacinto/8th Street' : '8th/San Jacinto',
    'Henderson/9th' : '9th/Henderson',
    'Palmer Auditorium' : 'Barton Springs/Bouldin @ Palmer Auditorium',
    'Barton Springs @ Kinney Ave' : 'Barton Springs/Kinney',
    'Congress/Cesar Chavez' : 'Cesar Chavez/Congress',
    #'' : 'Dean Keeton/Park Place', # 30.287836617190724, -97.72845870365327
    'East 11th St./San Marcos' : 'East 11th/San Marcos',
    'East 11th St. at Victory Grill' : 'East 11th/Victory Grill',
    'Capital Metro HQ - East 5th at Broadway' : 'East 5th/Broadway @ Capital Metro HQ',
    'Medina/East 6th' : 'East 6th/Medina',
    'East 6th/Pedernales St.' : 'East 6th/Pedernales',
    'East 6th at Robert Martinez' : 'East 6th/Robert T. Martinez',
    'Pfluger Bridge @ W 2nd Street' : 'Electric Drive/Sandra Muraida Way @ Pfluger Ped Bridge',
    'UT West Mall @ Guadalupe' : 'Guadalupe/West Mall @ University Co-op',
    'Lake Austin Blvd @ Deep Eddy' : 'Lake Austin Blvd/Deep Eddy',
    'Lakeshore @ Austin Hostel' : 'Lakeshore/Austin Hostel',
    'Nash Hernandez @ RBJ South' : 'Nash Hernandez/East @ RBJ South',
    #'' : 'One Texas Center', # 30.25767062481796, -97.74897583987295
    'Rainey St @ Cummings' : 'Rainey/Cummings',
    'ACC - Rio Grande/12th' : 'Rio Grande/12th',
    'Riverside @ S. Lamar' : 'Riverside/South Lamar',
    'Long Center @ South 1st/Riverside' : 'South 1st/Riverside @ Long Center',
    'South Congress/Barton Springs at the Austin American-Statesman' : 'South Congress/Barton Springs @ The Austin American-Statesman',
    'Sterzing at Barton Springs' : 'Sterzing/Barton Springs',
    'MoPac Pedestrian Bridge @ Veterans Drive' : 'Veterans/Atlanta @ MoPac Ped Bridge'
}
kiosk['Kiosk Name'] = kiosk['Kiosk Name'].replace(replacement_dict)

# Select specific columns from the 'kiosk' DataFrame
kiosk = kiosk[['Kiosk ID', 'Kiosk Name', 'Lat', 'Lon', 'Number of Docks']]

# Create a DataFrame with additional kiosk information to add
add_kiosk = pd.DataFrame({
    'Kiosk Name': ['23rd/Pearl', 'Dean Keeton/Park Place', 'One Texas Center'],
    'Lat': [30.287329976401352, 30.287836617190724, 30.25767062481796],
    'Lon': [-97.74632802031869, -97.72845870365327, -97.74897583987295]
})

# Concatenate the new kiosks (add_kiosk) to the existing kiosk DataFrame
kiosk = pd.concat([kiosk, add_kiosk], ignore_index=True) # 105 rows

# 'Number of Docks' retrieved from the Bikeshare app and assign 'Kiosk ID'
kiosk.loc[kiosk['Kiosk Name'] == '3rd/Nueces', ['Number of Docks', 'Kiosk ID']] = [8, 2]
kiosk.loc[kiosk['Kiosk Name'] == '6th/Lavaca', ['Number of Docks', 'Kiosk ID']] = [6, 3]
kiosk.loc[kiosk['Kiosk Name'] == 'Dean Keeton/Park Place', ['Number of Docks', 'Kiosk ID']] = [13, 4]
kiosk.loc[kiosk['Kiosk Name'] == 'East 7th/Pleasant Valley', ['Number of Docks', 'Kiosk ID']] = [8, 5]
kiosk.loc[kiosk['Kiosk Name'] == 'One Texas Center', ['Number of Docks', 'Kiosk ID']] = [13, 6]

# Remove rows without dock information in the Bikeshare app
kiosks_to_remove = [
    '23rd/Pearl',
    '5th/San Marcos',
    '6th/Navasota St.',
    '8th/Guadalupe',
    'ACC - West/12th Street',
    'Bullock Museum @ Congress/MLK',
    'OFFICE/Main/Shop/Repair',
    'Pease Park',
    'Rainey @ River St',
    'Red River/LBJ Library',
    'Republic Square',
    'Rio Grande/12th',
    'State Capitol @ 14th/Colorado',
    'State Parking Garage @ Brazos/18th',
    'Toomey Rd @ South Lamar',
    'Waller/6th St.',
    'Zilker Park West'
]

# Remove rows where 'Kiosk Name' matches any in the list
kiosk = kiosk[~kiosk['Kiosk Name'].isin(kiosks_to_remove)] # 88 rows

# Drop duplicates based on the 'Kiosk Name' column to keep unique kiosks only
kiosk = kiosk.drop_duplicates(subset='Kiosk Name') # 86 rows
kiosk.to_csv('kiosk.csv', index = False)




###############################
# kiosk df to point
kiosk['geometry'] = kiosk.apply(lambda row: Point(row['Lon'], row['Lat']), axis=1)
kiosk_geo = gpd.GeoDataFrame(kiosk, geometry='geometry')
kiosk_geo = kiosk_geo.drop(columns=['index_right'])
kiosk_geo.set_crs("EPSG:4326", inplace=True)

study_area = gpd.read_file('Study_area.shp') # 177 rows
study_area = study_area.to_crs(kiosk_geo.crs)
kiosk_geo = gpd.sjoin(kiosk_geo, study_area[['GEOID', 'geometry']], how='left', predicate='intersects')
kiosk_geo = kiosk_geo.drop(columns=['GEOID_left', 'index_right'])
kiosk_geo = kiosk_geo.rename(columns={'GEOID_right': 'GEOID'})

###########################################

# Filter the DataFrame to exclude rows where 'Checkout Kiosk' or 'Return Kiosk' contains any of the values in the kiosks_to_remove list
bike_apr_2024 = bike_apr_2024[~bike_apr_2024['Checkout Kiosk'].isin(kiosks_to_remove) & ~bike_apr_2024['Return Kiosk'].isin(kiosks_to_remove)] # 30,809 rows
bike_apr_2024.to_csv('bike_apr_2024.csv', index = False)

### Merge bike and kiosk data ###
merged_co = pd.merge(bike_apr_2024, kiosk_geo, left_on = 'Checkout Kiosk', right_on = 'Kiosk Name')
merged_co = merged_co[['Checkout Date', 'Checkout Time', 'Number of Docks', 'GEOID']]

# Rename columns
merged_co = merged_co.rename(columns={
    'Number of Docks': 'CO_Docks',
    'GEOID': 'CO_GEOID'
})

merged_rt = pd.merge(bike_apr_2024, kiosk, left_on = 'Return Kiosk', right_on = 'Kiosk Name')
merged_rt = merged_rt[['Number of Docks', 'GEOID']]
merged_rt = merged_rt.rename(columns={
    'Number of Docks': 'RT_Docks',
    'GEOID': 'RT_GEOID'
})

merged_df = pd.concat([merged_co, merged_rt], axis=1)
merged_df.to_csv('merged_df.csv', index = False)
