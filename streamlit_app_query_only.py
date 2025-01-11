import streamlit as st
import pyperclip
from src.fabrics_processor.database import initialize_qdrant_database
from src.search_qdrant.database_query import query_qdrant_database
from src.fabrics_processor.logger import setup_logger
import logging
import atexit
from src.fabrics_processor.config import config
import time

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
    if 'status_key' not in st.session_state:
        st.session_state.status_key = 0

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
            
            # Display content as markdown
            st.markdown("### Content")
            st.code(prompt.metadata["content"], language="markdown", wrap_lines=True)
            
            # Add copy button for each prompt
            if st.button(f"Use this prompt", key=f"compare_use_{idx}"):
                st.code(prompt.metadata["content"], language="markdown", wrap_lines=True)
                selected_idx = idx
    
    # Handle selection
    if selected_idx is not None:
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
                        if len(selected) == 1:
                            st.code(selected[0].metadata["content"], language="markdown", wrap_lines=True)
                    
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
        
        # Add credits at the bottom left
        st.markdown("""
        <style>
        .credits {
            position: fixed;
            left: 1rem;
            bottom: 1rem;
            font-size: 0.8rem;
            color: #666;
            max-width: 600px;
        }
        </style>
        <div class="credits">
        This tool searches the great list of prompts available at <a href="https://github.com/danielmiessler/fabric">https://github.com/danielmiessler/fabric</a>. 
        A great commandline utilty build by Daniel Miessler to make the use of LLM more frictionless.<br>
        All credits to him and his fellow fabric builders.
        </div>
        """, unsafe_allow_html=True)
        
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
