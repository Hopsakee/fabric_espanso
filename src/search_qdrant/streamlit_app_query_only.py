import streamlit as st
import pyperclip
from src.fabrics_processor.database import initialize_qdrant_database
from src.search_qdrant.database_query import query_qdrant_database
from src.fabrics_processor.logger import setup_logger
import logging
import atexit
from src.fabrics_processor.config import config

# Configure logging
logger = setup_logger()

def init_session_state():
    """Initialize session state variables."""
    if 'client' not in st.session_state:
        client = initialize_qdrant_database(api_key=st.secrets["api_key"])
        st.session_state.client = client
        # Register cleanup function
        atexit.register(lambda: client.close() if hasattr(client, '_transport') else None)
    if 'selected_prompts' not in st.session_state:
        st.session_state.selected_prompts = []
    if 'comparing' not in st.session_state:
        st.session_state.comparing = False
    if 'comparison_selected' not in st.session_state:
        st.session_state.comparison_selected = None

def show_comparison_view(prompts):
    """Show a full-width comparison view of the selected prompts."""
    st.write("## Compare Selected Prompts")
    
    # Add the back button at the top
    if st.button("Back to search"):
        st.session_state.comparing = False
        st.rerun()
    
    # Create columns for each prompt
    cols = st.columns(len(prompts))
    
    # Track which prompt is selected for copying
    selected_idx = None
    
    for idx, (col, prompt) in enumerate(zip(cols, prompts)):
        with col:
            st.markdown(f"### {prompt.metadata['filename']}")
            
            # Use this prompt button
            if st.button(f"Use this prompt", key=f"compare_use_{idx}"):
                selected_idx = idx
            
            # Display content as markdown
            st.markdown("### Content")
            st.markdown(prompt.metadata["content"])
    
    # Handle selection
    if selected_idx is not None:
        pyperclip.copy(prompts[selected_idx].metadata['content'])
        st.success(f"Copied {prompts[selected_idx].metadata['filename']} to clipboard!")
        # Clear comparison view
        st.session_state.comparing = False
        st.rerun()

def search_interface():
    """Show the search interface."""
    if st.session_state.comparing:
        show_comparison_view(st.session_state.selected_prompts)
        return
        
    query = st.text_area("What are you trying to accomplish? I will then search for good prompts to give you a good start.")
    
    if query:
        try:
            results = query_qdrant_database(
                query=query,
                client=st.session_state.client,
                num_results=5,
                collection_name=config.embedding.collection_name
            )
            
            if results:
                st.write("Which prompts would you like to investigate? Max 3.")
                
                # Create checkboxes for selection
                selected = []
                for r in results:
                    if st.checkbox(f"{r.metadata['filename']}", key=f"select_{r.id}"):
                        selected.append(r)
                
                st.session_state.selected_prompts = selected
                
                if selected:
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Use: copy to clipboard"):
                            if len(selected) == 1:
                                pyperclip.copy(selected[0].metadata['content'])
                                st.success("Copied to clipboard!")
                    
                    with col2:
                        if len(selected) > 1 and st.button("Compare"):
                            st.session_state.comparing = True
                            st.rerun()
                            
        except Exception as e:
            logger.error(f"Error in search_interface: {e}", exc_info=True)
            st.error(f"Error searching database: {e}")

def main():
    """Main function to run the Streamlit app."""
    st.set_page_config(
        page_title="Find fabric prompts",
        page_icon="🔍",
        layout="wide"
    )
    
    st.title("Find fabric prompts")
    
    try:
        init_session_state()
        search_interface()
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
