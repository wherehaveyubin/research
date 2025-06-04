import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches
import community as community_louvain


def make_od_edges(df, gdf):
    # Group by OD pairs and count number of trips
    # OD 쌍별로 그룹화하고 trip 수를 세기
    od_counts = df.groupby(['PULocationID', 'DOLocationID']).size().reset_index(name='trip_count')

    # Remove self-loops and out-of-bound LocationIDs
    # 자기자신 OD 제거 + 유효한 ID만 필터링
    od_counts = od_counts[
        (od_counts['PULocationID'] != od_counts['DOLocationID']) &
        (od_counts['PULocationID'] <= 263) &
        (od_counts['DOLocationID'] <= 263)
    ]

    # Convert IDs to string for merging
    od_counts['origin'] = od_counts['PULocationID'].astype(str)
    od_counts['destination'] = od_counts['DOLocationID'].astype(str)
    gdf['LocationID'] = gdf['LocationID'].astype(str)

    # Merge origin zone centroid
    # 출발지 좌표 병합
    od_counts = od_counts.merge(
        gdf[['LocationID', 'x', 'y']],
        left_on='origin',
        right_on='LocationID',
        how='left'
    ).rename(columns={'x': 'x_orig', 'y': 'y_orig'})

    # Merge destination zone centroid
    # 도착지 좌표 병합
    od_counts = od_counts.merge(
        gdf[['LocationID', 'x', 'y']],
        left_on='destination',
        right_on='LocationID',
        how='left'
    ).rename(columns={'x': 'x_dest', 'y': 'y_dest'})

    # Remove redundant LocationID columns
    # 병합으로 생긴 중복 LocationID 컬럼 제거
    od_counts.drop(columns=['LocationID_x', 'LocationID_y'], inplace=True)

    return od_counts

"""
def plot_od_graph(od_edges, gdf, ax, title):
    gdf.plot(ax=ax, color='lightgrey', edgecolor='white')

    for _, row in od_edges.iterrows():
        ax.plot([row['x_orig'], row['x_dest']],
                [row['y_orig'], row['y_dest']],
                color='red',
                linewidth=row['trip_count'] / 100,
                alpha=0.6)

    ax.set_title(title)
    ax.axis('off')
"""

def plot_od_graph(od_edges, gdf, ax, title, scale='log'):
    gdf.plot(ax=ax, color='lightgrey', edgecolor='white')

    for _, row in od_edges.iterrows():
        if scale == 'log':
            lw = np.log1p(row['trip_count']) / 2
        elif scale == 'linear':
            lw = row['trip_count'] / 100
        else:
            lw = 1
        ax.plot([row['x_orig'], row['x_dest']],
                [row['y_orig'], row['y_dest']],
                color='red',
                linewidth=lw,
                alpha=0.6)

    ax.set_title(title)
    ax.axis('off')

# Build degree centrality graph 
def build_centrality_graph(df):
    # Aggregate OD pairs
    od_counts = df.groupby(['PULocationID', 'DOLocationID']).size().reset_index(name='trip_count')
    od_counts = od_counts[
        (od_counts['PULocationID'] != od_counts['DOLocationID']) &
        (od_counts['PULocationID'] <= 263) &
        (od_counts['DOLocationID'] <= 263)
    ]

    # Build graph
    G = nx.DiGraph()
    for _, row in od_counts.iterrows():
        G.add_edge(int(row['PULocationID']), int(row['DOLocationID']), weight=row['trip_count'])

    # Compute centralities
    out_deg = nx.out_degree_centrality(G)
    in_deg = nx.in_degree_centrality(G)
    total_deg = nx.degree_centrality(G.to_undirected())

    # Convert to DataFrame
    df_centrality = pd.DataFrame({
        'LocationID': list(out_deg.keys()),
        'out_degree_centrality': list(out_deg.values()),
        'in_degree_centrality': list(in_deg.values()),
        'total_degree_centrality': list(total_deg.values())
    })

    return G, df_centrality

def plot_degree_cent_maps(gdf_heat, gdf_nonheat, column, title, filename, vmin=None, vmax=None, cmap='OrRd'):
    """
    Comparative choropleth map visualization (Heatwave vs Non-heatwave)
    폭염일과 비폭염일의 비교 지도 시각화 함수

    Parameters:
    - gdf_heat: GeoDataFrame for heatwave period / 폭염 시기의 GeoDataFrame
    - gdf_nonheat: GeoDataFrame for non-heatwave period / 비폭염 시기의 GeoDataFrame
    - column: name of the column to visualize / 시각화할 컬럼명
    - title: map title to be shown / 지도에 표시할 제목
    - filename: file name to save the figure / 저장할 파일명
    - vmin, vmax: colorbar range (recommended to use same range for both maps) / 컬러바 최소값, 최대값 (동일한 범위 권장)
    - cmap: colormap name / 컬러맵 이름
    """

    # Create subplots (1 row, 2 columns)
    # 서브플롯 생성 (1행 2열)
    fig, axs = plt.subplots(1, 2, figsize=(18, 9))

    # Plot heatwave data
    # 폭염 시기 데이터 시각화
    gdf_heat.plot(
        column=column,
        ax=axs[0],
        cmap=cmap,
        legend=True,
        edgecolor='grey',
        linewidth=0.5,
        vmin=vmin, vmax=vmax,
        missing_kwds={"color": "lightgrey"}  # missing data color / 결측값 색상
    )
    axs[0].set_title(f"Heatwave Days - {title}")  # Set title / 제목 설정
    axs[0].axis('off')  # Hide axis / 축 숨기기

    # Plot non-heatwave data
    # 비폭염 시기 데이터 시각화
    gdf_nonheat.plot(
        column=column,
        ax=axs[1],
        cmap=cmap,
        legend=True,
        edgecolor='grey',
        linewidth=0.5,
        vmin=vmin, vmax=vmax,
        missing_kwds={"color": "lightgrey"}
    )
    axs[1].set_title(f"Non-Heatwave Days - {title}")
    axs[1].axis('off')

    # Adjust layout and save
    # 레이아웃 정렬 및 저장
    plt.tight_layout()
    plt.savefig(filename, dpi=300)
    plt.show()

# Community detection
def detect_communities(G, seed=42):
    # Convert to undirected graph for community detection
    # 커뮤니티 탐지를 위해 방향 그래프를 무방향으로 변환
    G_undirected = G.to_undirected()

    # Run Louvain algorithm
    # Louvain 알고리즘 실행
    partition = community_louvain.best_partition(G_undirected, resolution=1.0, random_state=seed)

    # Convert to DataFrame
    # 결과를 DataFrame으로 변환
    df_comm = pd.DataFrame.from_dict(partition, orient='index', columns=['community'])
    df_comm.index.name = 'LocationID'
    df_comm.reset_index(inplace=True)

    return df_comm

def plot_community_maps(gdf_heat_comm, gdf_nonheat_comm, output_path="community_comparison.png"):
    """
    Plot side-by-side maps of community assignments for heatwave and non-heatwave periods.
    폭염일과 비폭염일에 대한 커뮤니티 분포를 나란히 시각화합니다.
    """

    # Set up the plot canvas
    # 플롯 캔버스 설정
    fig, axs = plt.subplots(1, 2, figsize=(18, 9))

    # Use tab20 colormap
    # tab20 색상 맵 사용
    cmap = plt.get_cmap('tab20')

    # Extract unique community IDs (excluding NaNs)
    # 고유 커뮤니티 ID 추출 (NaN 제외)
    unique_communities = sorted(gdf_heat_comm['community'].dropna().unique().astype(int))

    # Assign colors to each community
    # 커뮤니티별 색상 할당
    colors = [cmap(i % 20) for i in unique_communities]

    # Replace NaN with -1 for unified coloring
    # NaN은 -1로 대체하여 일관된 색상 처리
    gdf_heat_comm['plot_comm'] = gdf_heat_comm['community'].fillna(-1)
    gdf_nonheat_comm['plot_comm'] = gdf_nonheat_comm['community'].fillna(-1)

    # Map community IDs to colors
    # 커뮤니티 ID → 색상 매핑
    comm_color_dict = {comm: colors[i] for i, comm in enumerate(unique_communities)}
    comm_color_dict[-1] = '#d3d3d3'  # Unclassified: gray

    # Create legend patches
    # 범례 패치 생성
    legend_patches = [
        mpatches.Patch(color=comm_color_dict[comm], label=f'{comm}')
        for comm in unique_communities
    ]
    legend_patches.append(mpatches.Patch(color='#d3d3d3', label='Unclassified'))

    # Plot heatwave communities
    # 폭염일 커뮤니티 시각화
    gdf_heat_comm.plot(
        column='plot_comm',
        ax=axs[0],
        cmap=mcolors.ListedColormap([comm_color_dict[c] for c in sorted(comm_color_dict)]),
        edgecolor='black',
        linewidth=0.3,
        legend=False,
        categorical=True
    )
    axs[0].set_title("Communities during Heatwave Days")
    axs[0].axis('off')

    # Plot non-heatwave communities
    # 비폭염일 커뮤니티 시각화
    gdf_nonheat_comm.plot(
        column='plot_comm',
        ax=axs[1],
        cmap=mcolors.ListedColormap([comm_color_dict[c] for c in sorted(comm_color_dict)]),
        edgecolor='black',
        linewidth=0.3,
        legend=False,
        categorical=True
    )
    axs[1].set_title("Communities during Non-Heatwave Days")
    axs[1].axis('off')

    # Add legend to the first subplot
    # 첫 번째 subplot에 범례 추가
    axs[0].legend(handles=legend_patches, title='Community', loc='upper left', fontsize=9, title_fontsize=10)

    # Final layout and save
    # 전체 레이아웃 정리 및 저장
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.show()