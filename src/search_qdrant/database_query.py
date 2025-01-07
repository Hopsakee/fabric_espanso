import logging
from src.fabrics_processor.database import initialize_qdrant_database
from fastembed import TextEmbedding
from qdrant_client import QdrantClient
from qdrant_client.models import QueryResponse
import argparse

def query_qdrant_database(
      query: str,
      client: QdrantClient,
      num_results: int = 5,
      collection_name: str = "markdown_files") -> list[QueryResponse]:
      """Query the Qdrant database for similar documents.
      
      Args:
            query: The search query text
            client: Initialized QdrantClient instance
            num_results: Maximum number of results to return
            collection_name: Name of the collection to query
      
      Returns:
            List of QueryResponse objects containing matches
            
      Raises:
            QdrantException: If there's an error querying the database
      """
      try:
            results = client.query(collection_name=collection_name, query_text=query, limit=num_results)
            return results
      except Exception as e:
            logging.error(f"Error querying Qdrant database: {e}")
            raise

def main():
      client = initialize_qdrant_database() 

      parser = argparse.ArgumentParser(description="Query Qdrant database")
      parser.add_argument("query", type=str, help="The search query text")
      parser.add_argument("--num_results", "-n", type=int, default=5, help="The number of results to return (default: 5)")
      parser.add_argument("--collection_name", "-c", type=str, default="markdown_files", help="The name of the collection to query (default: markdown_files)")

      args = parser.parse_args()

      try:
          results = query_qdrant_database(query=args.query,
                                        client=client,
                                        num_results=args.num_results,
                                        collection_name=args.collection_name
          )

          filenames = [r.metadata['filename'] for r in results]
          print(filenames)
      finally:
          client.close()

if __name__ == "__main__":
      main()