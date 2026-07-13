from pathlib import Path

import networkx as nx
import pandas as pd


# ---------------------------------------------------
# Project paths
# ---------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw_invalid"
ERROR_DIR = BASE_DIR / "data" / "errors"

NODES_PATH = RAW_DIR / "nodes.csv"
EDGES_PATH = RAW_DIR / "edges.csv"
REPORT_PATH = ERROR_DIR / "validation_report_invalid.txt"

# Create the output directory if it does not exist
ERROR_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------
# Load raw datasets
# ---------------------------------------------------

nodes = pd.read_csv(NODES_PATH)
edges = pd.read_csv(EDGES_PATH)


# ---------------------------------------------------
# Validation containers
# ---------------------------------------------------

errors = []
warnings = []


# ---------------------------------------------------
# Basic statistics
# ---------------------------------------------------

total_nodes = len(nodes)
total_edges = len(edges)


# ---------------------------------------------------
# 1. Missing values validation
# ---------------------------------------------------

missing_nodes = nodes.isnull().sum()
missing_edges = edges.isnull().sum()

for column, count in missing_nodes.items():
    if count > 0:
        errors.append(
            f"nodes.csv: column '{column}' contains {count} missing values"
        )

for column, count in missing_edges.items():
    if count > 0:
        errors.append(
            f"edges.csv: column '{column}' contains {count} missing values"
        )


# ---------------------------------------------------
# 2. Duplicate node IDs
# ---------------------------------------------------

duplicate_nodes = nodes[nodes["id"].duplicated()]

if not duplicate_nodes.empty:
    errors.append(
        f"nodes.csv: found {len(duplicate_nodes)} duplicated node IDs"
    )


# ---------------------------------------------------
# 3. Duplicate edges
# ---------------------------------------------------

duplicate_edges = edges[
    edges.duplicated(subset=["source", "target"])
]

if not duplicate_edges.empty:
    warnings.append(
        f"edges.csv: found {len(duplicate_edges)} duplicated edges"
    )


# ---------------------------------------------------
# 4. Referential integrity validation
# ---------------------------------------------------

node_ids = set(nodes["id"])

invalid_sources = edges[
    ~edges["source"].isin(node_ids)
]

invalid_targets = edges[
    ~edges["target"].isin(node_ids)
]

if not invalid_sources.empty:
    errors.append(
        f"edges.csv: {len(invalid_sources)} edges contain invalid source nodes"
    )

if not invalid_targets.empty:
    errors.append(
        f"edges.csv: {len(invalid_targets)} edges contain invalid target nodes"
    )


# ---------------------------------------------------
# 5. Isolated nodes validation
# ---------------------------------------------------

connected_nodes = set(edges["source"]).union(set(edges["target"]))

isolated_nodes = nodes[
    ~nodes["id"].isin(connected_nodes)
]

if not isolated_nodes.empty:
    warnings.append(
        f"Found {len(isolated_nodes)} isolated nodes without any connections"
    )


# ---------------------------------------------------
# 6. Node type validation
# ---------------------------------------------------

allowed_node_types = {
    "source",
    "transformer",
    "junction",
    "station",
    "client",
}

invalid_node_types = nodes[
    ~nodes["type"].isin(allowed_node_types)
]

if not invalid_node_types.empty:
    errors.append(
        f"nodes.csv: found {len(invalid_node_types)} invalid node types"
    )


# ---------------------------------------------------
# 7. Status validation
# ---------------------------------------------------

allowed_statuses = {
    "active",
    "inactive",
}

invalid_node_statuses = nodes[
    ~nodes["status"].isin(allowed_statuses)
]

invalid_edge_statuses = edges[
    ~edges["status"].isin(allowed_statuses)
]

if not invalid_node_statuses.empty:
    errors.append(
        f"nodes.csv: found {len(invalid_node_statuses)} invalid node statuses"
    )

if not invalid_edge_statuses.empty:
    errors.append(
        f"edges.csv: found {len(invalid_edge_statuses)} invalid edge statuses"
    )


# ---------------------------------------------------
# 8. Edge length validation
# ---------------------------------------------------

if "length" in edges.columns:
    invalid_lengths = edges[
        edges["length"] <= 0
    ]

    if not invalid_lengths.empty:
        errors.append(
            f"edges.csv: found {len(invalid_lengths)} edges with length <= 0"
        )


# ---------------------------------------------------
# 9. Graph connectivity analysis
# ---------------------------------------------------

valid_edges = edges[
    edges["source"].isin(node_ids)
    & edges["target"].isin(node_ids)
]

graph = nx.Graph()

graph.add_nodes_from(nodes["id"])

graph.add_edges_from(
    valid_edges[["source", "target"]]
    .itertuples(index=False, name=None)
)

connected_components = list(nx.connected_components(graph))
components_count = len(connected_components)

if components_count > 1:
    warnings.append(
        "Graph is not fully connected. "
        f"Number of connected components: {components_count}"
    )


# ---------------------------------------------------
# Save validation report
# ---------------------------------------------------

with open(REPORT_PATH, "w", encoding="utf-8") as file:
    file.write("=== ETL DATA VALIDATION REPORT ===\n\n")

    file.write("1. BASIC STATISTICS\n")
    file.write(f"- Total nodes: {total_nodes}\n")
    file.write(f"- Total edges: {total_edges}\n")
    file.write(f"- Connected components: {components_count}\n\n")

    file.write("2. VALIDATION RESULTS\n")
    file.write(f"- Critical errors: {len(errors)}\n")
    file.write(f"- Warnings: {len(warnings)}\n\n")

    file.write("3. CRITICAL ERRORS\n")

    if errors:
        for error in errors:
            file.write(f"- {error}\n")
    else:
        file.write("- No critical errors found\n")

    file.write("\n4. WARNINGS\n")

    if warnings:
        for warning in warnings:
            file.write(f"- {warning}\n")
    else:
        file.write("- No warnings found\n")

    file.write("\n5. FINAL STATUS\n")

    if errors:
        file.write("VALIDATION FAILED\n")
    else:
        file.write("VALIDATION SUCCESS\n")


print(f"Validation report saved to {REPORT_PATH}")