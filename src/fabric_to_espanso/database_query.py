from src.fabric_to_espanso.database import initialize_qdrant_database
from fastembed import TextEmbedding

client = initialize_qdrant_database()

def query_qdrant_database(query: str):
    