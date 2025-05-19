# https://docs.deweydata.io/docs/api-access
# Download Github Desktop first

pip install deweydatapy@git+https://github.com/Dewey-Data/deweydatapy

import deweydatapy as ddp

workspace = "D:/*"

## Download data
# API Key
apikey = "*"

# Product path (Weekly Patterns - Foot Traffic - Full Historical Data (data endpoint))
pp_ = "*"

# Review the metadata of the data product
meta = ddp.get_meta(apikey, pp_, print_meta = True) # returns a dataframe with meta information

# Collect the list of files to download and store in a dataframe
files_df = ddp.get_file_list(apikey, pp_, 
                             start_date = '2024-05-27',
                             end_date = '2024-10-05',
                             print_info = True)

# Download files from the dataframe
ddp.download_files(files_df, workspace+"dewey", skip_exists = True)

## Import downloaded data
# Import list of files ending with csv.gz
files = glob.glob(workspace+"dewey/" + "*csv.gz")

df = DataFrame()

for f in files:
    df = pd.read_csv(f,compression='gzip', encoding='utf-8', dtype={'POI_CBG': str} )
    break

# Select Phoenix, Arizona data 
df_az = df[
    (df['region'].str.upper() == 'AZ') & 
    (df['city'].str.lower() == 'phoenix')
]
df_az.head()

df_az_selected = df_az[
    df_az["visitor_home_cbgs"].notnull() & df_az["poi_cbg"].notnull()
][["visitor_home_cbgs", "poi_cbg", "raw_visit_counts"]]
