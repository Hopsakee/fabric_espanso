from src.fabric_to_espanso.database import initialize_qdrant_database
from fastembed import TextEmbedding
from qdrant_client import QdrantClient
import argparse

def query_qdrant_database(query: str, client: QdrantClient, num_results: int = 5, collection_name: str = "markdown_files"):
      return client.query(collection_name=collection_name, query_text=query, limit=num_results)

def main():
      client = initialize_qdrant_database() 

      parser = argparse.ArgumentParser(description="Query Qdrant database")
      parser.add_argument("query", type=str, help="The search query text")
      parser.add_argument("--num_results", "-n", type=int, default=5, help="The number of results to return (default: 5)")
      parser.add_argument("--collection_name", "-c", type=str, default="markdown_files", help="The name of the collection to query (default: markdown_files)")

      args = parser.parse_args()

      results = query_qdrant_database(query=args.query,
                                      client=client,
                                      num_results=args.num_results,
                                      collection_name=args.collection_name
      )

      filenames = [r.metadata['filename'] for r in results]

      print(filenames)

if __name__ == "__main__":
      main()