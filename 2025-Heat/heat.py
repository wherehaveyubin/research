# https://docs.deweydata.io/docs/api-access

pip install deweydatapy@git+https://github.com/Dewey-Data/deweydatapy

import deweydatapy as ddp

# Import the library and save permissions
# API Key
apikey = ""

# Product path
# Weekly Patterns - Foot Traffic - Full Historical Data (data endpoint)
pp_ = ""

# Review the meta information of the data product
meta = ddp.get_meta(apikey, pp_, print_meta = True) # returns a dataframe with meta information

# Collect the list of files to download and store in a dataframe
files_df = ddp.get_file_list(apikey, pp_, 
                             start_date = '2024-07-01',
                             end_date = '2024-07-31',
                             print_info = True);

# Download files from the dataframe
ddp.download_files(files_df, "D:/heat", skip_exists = True)
