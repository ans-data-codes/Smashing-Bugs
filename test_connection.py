import os

from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

uri = os.getenv("NEO4J_URI")
user = os.getenv("NEO4J_USERNAME")
password = os.getenv("NEO4J_PASSWORD")

if not uri or not user or not password:
    raise ValueError(
        "Missing Neo4j connection settings. Update your .env file with "
        "NEO4J_URI, NEO4J_USERNAME, and NEO4J_PASSWORD."
    )

if uri in ("neo4j://address:7687", "bolt://address:7687"):
    raise ValueError(
        "The .env file still contains placeholder Neo4j values. Replace them "
        "with your actual Aura or local database connection details."
    )

try:
    driver = GraphDatabase.driver(uri, auth=(user, password))
    with driver.session() as session:
        result = session.run("MATCH (b:Bug) RETURN b.id AS id LIMIT 5")
        for record in result:
            print(record["id"])
except Exception as exc:
    print(f"Neo4j connection failed: {exc}")
    raise
finally:
    if "driver" in locals():
        driver.close()