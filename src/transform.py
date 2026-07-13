from pathlib import Path

import pandas as pd


# ---------------------------------------------------
# Project paths
# ---------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

NODES_PATH = RAW_DIR / "nodes.csv"
EDGES_PATH = RAW_DIR / "edges.csv"

PROCESSED_NODES_PATH = PROCESSED_DIR / "processed_nodes.csv"
PROCESSED_EDGES_PATH = PROCESSED_DIR / "processed_edges.csv"

# Create processed directory if it does not exist
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------
# Load raw datasets
# ---------------------------------------------------

nodes = pd.read_csv(NODES_PATH)
edges = pd.read_csv(EDGES_PATH)


# ---------------------------------------------------
# 1. Remove duplicated nodes
# ---------------------------------------------------

nodes = nodes.drop_duplicates(subset=["id"])


# ---------------------------------------------------
# 2. Remove edges referencing non-existing nodes
# ---------------------------------------------------

valid_node_ids = set(nodes["id"])

edges = edges[
    edges["source"].isin(valid_node_ids)
    & edges["target"].isin(valid_node_ids)
].copy()


# ---------------------------------------------------
# 3. Standardize column names for Neo4j
# ---------------------------------------------------

nodes = nodes.rename(
    columns={
        "id": "node_id"
    }
)


# ---------------------------------------------------
# 4. Save processed datasets
# ---------------------------------------------------

nodes.to_csv(
    PROCESSED_NODES_PATH,
    index=False
)

edges.to_csv(
    PROCESSED_EDGES_PATH,
    index=False
)


# ---------------------------------------------------
# Final summary
# ---------------------------------------------------

print("Transformation completed successfully.")
print(f"Total processed nodes: {len(nodes)}")
print(f"Total processed edges: {len(edges)}")
print(f"Processed nodes saved to: {PROCESSED_NODES_PATH}")
print(f"Processed edges saved to: {PROCESSED_EDGES_PATH}")