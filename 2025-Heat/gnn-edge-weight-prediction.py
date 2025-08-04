import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import GCNConv
import random
import numpy as np

def set_seed(seed=42):
    torch.manual_seed(seed)
    np.random.seed(seed)
    random.seed(seed)
    
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True  
        torch.backends.cudnn.benchmark = False     

set_seed(42) 

# -------------------------------
# 1. Node Features (5 nodes, 2 features each)
# -------------------------------
node_features = torch.tensor([
    [100, 50],   # Node 0
    [200, 60],   # Node 1
    [150, 45],   # Node 2
    [180, 70],   # Node 3
    [120, 55]    # Node 4
], dtype=torch.float)

# -------------------------------
# 2. Graph Connectivity (Edge Information)
# -------------------------------
edge_index = torch.tensor([
    [0, 0, 1, 3],  # from
    [1, 2, 3, 4]   # to
], dtype=torch.long)

# GCNConv requires undirected edges → Add reverse edges to make it bidirectional
edge_index = torch.cat([edge_index, edge_index[[1, 0]]], dim=1)
