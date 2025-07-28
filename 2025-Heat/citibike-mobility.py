import pandas as pd
import geopandas as gpd
import glob
import os
from tqdm import tqdm
import polars as pl

workspace = "D:/heat-mobility/data/"

# ==========================================================
# Import raw data and export
# ==========================================================
# Set the folder path
folder_path = r"D:\heat-mobility\data\citibike"
csv_files = glob.glob(os.path.join(folder_path, "**", "*.csv"), recursive=True)

# Define consistent schema
fixed_schema = {
    "ride_id": pl.Utf8,
    "rideable_type": pl.Utf8,
    "started_at": pl.Datetime,
    "ended_at": pl.Datetime,
    "start_station_name": pl.Utf8,
    "start_station_id": pl.Utf8,
    "end_station_name": pl.Utf8,
    "end_station_id": pl.Utf8,
    "start_lat": pl.Float64,
    "start_lng": pl.Float64,
    "end_lat": pl.Float64,
    "end_lng": pl.Float64,
    "member_casual": pl.Utf8,
}

# Read and concatenate all CSVs with column projection
df_list = []
for file in csv_files:
    try:
        df = pl.read_csv(
            file,
            schema_overrides=fixed_schema,
            try_parse_dates=True,
            ignore_errors=True
        )
        df_list.append(df)
        print(f"Loaded: {os.path.basename(file)}")
    except Exception as e:
        print(f"Error reading {file}: {e}")

# Combine into one DataFrame
citibike = pl.concat(df_list, how="diagonal_relaxed")
print(f"Total rows: {citibike.shape[0]:,}") # 47,462,131 rows

# Ensure datetime column exists
citibike = citibike.with_columns([
    pl.col("started_at").cast(pl.Datetime),
    pl.col("ended_at").cast(pl.Datetime)
])

# Filter by summer months (2022–2024)
citibike = citibike.filter(
    (
        (pl.col("started_at") >= pl.datetime(2022,6,1)) &
        (pl.col("ended_at") <= pl.datetime(2022,8,31,23,59,59))
    ) |
    (
        (pl.col("started_at") >= pl.datetime(2023,6,1)) &
        (pl.col("ended_at") <= pl.datetime(2023,8,31,23,59,59))
    ) |
    (
        (pl.col("started_at") >= pl.datetime(2024,6,1)) &
        (pl.col("ended_at") <= pl.datetime(2024,8,31,23,59,59))
    )
) # 47,459,523 rows

# Add date, hour, weekday columns
citibike = citibike.with_columns([
    pl.col("started_at").dt.date().alias("date"),
    pl.col("started_at").dt.hour().alias("hour"),
    pl.col("started_at").dt.strftime("%A").alias("weekday")
])

# citibike.write_csv(r"D:\heat-mobility\data\citibike.csv")

# ==========================================================
# Import data
# ==========================================================
use_cols = ['ride_id', 'started_at', 'ended_at', 'start_station_id', 'end_station_id', 'date', 'hour', 'weekday']
citibike = pd.read_csv(workspace + "citibike.csv", usecols=use_cols, low_memory=False)
print(citibike.columns)


# heat index
weather = pd.read_csv("D:/heat/data/2022_2024_summer_heat_index.csv") # 8,541 rows
weather['DATE'] = pd.to_datetime(weather['DATE'])
if isinstance(weather, pd.DataFrame):
    weather = pl.from_pandas(weather)

citibike = citibike.with_columns(
    pl.col("started_at").dt.cast_time_unit("ns")
)
weather = weather.with_columns(
    pl.col("DATE").dt.cast_time_unit("ns")
)

# Sort values (required for merge_asof)
citibike = citibike.sort('started_at')
weather = weather.sort('DATE')

# Join using the nearest timestamp
citibike = citibike.join_asof(
    weather.select(["DATE", "heat_index", "is_heat"]),
    left_on="started_at",
    right_on="DATE",
    strategy="nearest"  # "backward" (default), "forward", or "nearest"
)
