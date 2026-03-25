import geopandas as gpd
import pandas as pd
import os
import matplotlib.pyplot as plt

# load data
tract["GEOID"] = tract["GEOID"].astype(str).str[1:]
mhlth = pd.read_csv("2023CA_MHLTH.csv")

tract["GEOID_2"] = tract["GEOID_2"].astype(str)
mhlth["LocationID"] = mhlth["LocationID"].astype(str)

# join on GEOID and LocationID
merged = tract.merge(mhlth, left_on="GEOID", right_on="LocationID", how="left")
merged = merged[merged["LocationID"].notna()]
merged.to_file("tract_MHLTH.shp") # 3450 rows

# map
counties = merged["CountyName"].dropna().unique()

for county in counties:
    subset = merged[merged["CountyName"] == county]

    fig, ax = plt.subplots(1, 1, figsize=(8, 6))

    # plot with legend outside
    subset.plot(
        column="Data_Value",
        cmap="OrRd",
        scheme="quantiles",
        k=5,
        legend=True,
        edgecolor="black",
        linewidth=0.1,
        ax=ax
    )

    ax.set_title(f"{county} County\n% of Frequent Mental Distress")
    ax.axis("off")

    # move legend outside
    leg = ax.get_legend()
    if leg:
        leg.set_bbox_to_anchor((1.02, 0.5))  # move right
        leg._loc = 6  # vertical center
        leg.set_frame_on(True)

    plt.tight_layout()
    plt.show()
