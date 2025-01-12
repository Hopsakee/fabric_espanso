import gradio as gr
import pyperclip
from src.fabrics_processor.database import initialize_qdrant_database
from src.search_qdrant.database_query import query_qdrant_database
from src.fabrics_processor.logger import setup_logger
import logging
import atexit
from src.fabrics_processor.config import config
import time
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logger = setup_logger()

# Initialize the database client
client = None
def init_client():
    global client
    if client is None:
        client = initialize_qdrant_database(api_key=os.environ.get("QDRANT_API_KEY"))
        # Register cleanup function
        atexit.register(lambda: client.close() if hasattr(client, '_transport') else None)
    return client

def search_prompts(query):
    """Search for prompts based on the query."""
    try:
        client = init_client()
        results = query_qdrant_database(
            query=query,
            client=client,
            num_results=5,
            collection_name=config.embedding.collection_name
        )
        
        if not results:
            return gr.Radio(choices=[]), None
        
        # Format results for radio buttons - just filenames
        filenames = [r.metadata['filename'] for r in results]
        # Store the full results for later use
        global current_results
        current_results = results
        return gr.Radio(choices=filenames), None
    
    except Exception as e:
        logger.error(f"Error during search: {str(e)}")
        return gr.Radio(choices=[]), None

def show_selected_prompt(selected_filename):
    """Display the content of the selected prompt."""
    if not selected_filename or not current_results:
        return ""
    
    # Find the selected result
    selected_prompt = next(
        (r for r in current_results if r.metadata['filename'] == selected_filename),
        None
    )
    
    if selected_prompt:
        return selected_prompt.metadata['content']
    return ""

def create_ui():
    # Store current results globally
    global current_results
    current_results = []
    
    with gr.Blocks() as demo:
        gr.Markdown("# Prompt Search and Comparison")
        
        with gr.Column():
            query_input = gr.Textbox(
                label="What are you trying to accomplish? I will then search for good prompts to give you a good start.",
                lines=3,
                autofocus=True,  # This will focus the textbox when the page loads
                interactive=True  # This enables keyboard events
            )
            search_button = gr.Button("Search")
        
            # Radio buttons for selecting prompts
            results_radio = gr.Radio(
                choices=[],
                label="Select a prompt",
                interactive=True
            )
            
            # Display area for selected prompt using Markdown
            selected_prompt_display = gr.Markdown(label="Selected Prompt", show_copy_button=True)
        
        # Set up event handlers
        query_input.submit(
            fn=search_prompts,
            inputs=[query_input],
            outputs=[results_radio, selected_prompt_display]
        )
        search_button.click(
            fn=search_prompts,
            inputs=[query_input],
            outputs=[results_radio, selected_prompt_display]
        )
        
        results_radio.change(
            fn=show_selected_prompt,
            inputs=[results_radio],
            outputs=[selected_prompt_display]
        )
    
    return demo

if __name__ == "__main__":
    demo = create_ui()
    demo.launch(pwa=True)
