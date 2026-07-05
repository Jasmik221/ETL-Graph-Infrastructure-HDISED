import pandas as pd
from neo4j import GraphDatabase

URI = "bolt://localhost:7687"
USERNAME = "neo4j"
PASSWORD = "MASNOni1906"

NODES_PATH = "data/processed/processed_nodes.csv"
EDGES_PATH = "data/processed/processed_edges.csv"

driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD)
)

nodes = pd.read_csv(NODES_PATH)
edges = pd.read_csv(EDGES_PATH)

with driver.session() as session:
    session.run("MATCH (n) DETACH DELETE n")

    for _, row in nodes.iterrows():
        session.run(
            """
            CREATE (:Node {
                id: $id,
                name: $name,
                type: $type,
                x: $x,
                y: $y,
                status: $status
            })
            """,
            id=int(row["node_id"]),
            name=row["name"],
            type=row["type"],
            x=float(row["x"]),
            y=float(row["y"]),
            status=row["status"]
        )

    for _, row in edges.iterrows():
        session.run(
            """
            MATCH (a:Node {id: $source})
            MATCH (b:Node {id: $target})
            CREATE (a)-[:CONNECTED_TO {
                type: $type,
                length: $length,
                status: $status
            }]->(b)
            """,
            source=int(row["source"]),
            target=int(row["target"]),
            type=row["type"],
            length=float(row["length"]),
            status=row["status"]
        )

driver.close()

print("Data successfully loaded into Neo4j.")