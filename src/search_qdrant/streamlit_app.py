import streamlit as st
import pyperclip
from src.fabric_to_espanso.database import initialize_qdrant_database
from src.fabric_to_espanso.database_updater import update_qdrant_database
from src.fabric_to_espanso.file_change_detector import detect_file_changes
from src.fabric_to_espanso.yaml_file_generator import generate_yaml_file
from src.search_qdrant.database_query import query_qdrant_database
import logging
import atexit
from src.fabric_to_espanso.config import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_session_state():
    """Initialize session state variables."""
    if 'client' not in st.session_state:
        client = initialize_qdrant_database()
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
            
            # Create two columns for trigger and button
            trigger_col, button_col = st.columns([0.7, 0.3])
            
            with trigger_col:
                # Add trigger field
                current_trigger = prompt.metadata.get('trigger', '')
                new_trigger = st.text_input("Trigger", 
                                          value=current_trigger,
                                          key=f"trigger_{idx}")
                
                # Update trigger if changed
                if new_trigger != current_trigger:
                    try:
                        st.session_state.client.set_payload(
                            collection_name="markdown_files",
                            payload={"trigger": new_trigger},
                            points=[prompt.id]
                        )
                        st.success(f"Updated trigger to: {new_trigger}")
                    except Exception as e:
                        st.error(f"Failed to update trigger: {str(e)}")
            
            with button_col:
                # Align button with text input using empty space
                st.write("")  # This creates some vertical space
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
        
    st.subheader("Search for prompts")
    
    query = st.text_area("What are you trying to accomplish? I will then search for good prompts to give you a good start.")
    
    if query:
        try:
            results = query_qdrant_database(
                query=query,
                client=st.session_state.client,
                num_results=5,
                collection_name="markdown_files"
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

def update_database():
    """Update the database and YAML files."""
    try:
        with st.spinner("Processing markdown files..."):
            # Get current collection info
            collection_info = st.session_state.client.get_collection("markdown_files")
            initial_points = collection_info.points_count
            
            # Detect file changes
            new_files, modified_files, deleted_files = detect_file_changes(
                client=st.session_state.client,
                markdown_folder=config.markdown_folder
            )
            
            # Update the database
            update_qdrant_database(
                client=st.session_state.client,
                new_files=new_files,
                modified_files=modified_files,
                deleted_files=deleted_files
            )
            
            # Generate YAML file
            generate_yaml_file(
                client=st.session_state.client,
                yaml_output_folder=config.yaml_output_folder
            )
            
            # Get updated collection info
            collection_info = st.session_state.client.get_collection("markdown_files")
            final_points = collection_info.points_count
            
            # Show summary
            st.success(f"""
            Database update completed successfully!
            
            Changes detected:
            - {len(new_files)} new files
            - {len(modified_files)} modified files
            - {len(deleted_files)} deleted files
            
            Database entries:
            - Initial: {initial_points}
            - Final: {final_points}
            """)
            
    except Exception as e:
        logger.error(f"Error updating database: {e}", exc_info=True)
        st.error(f"Error updating database: {e}")

def display_trigger_table():
    """Display the trigger table in the sidebar."""
    with st.sidebar:
        # Add some space to push the table to the bottom
        st.markdown("<br>" * 10, unsafe_allow_html=True)
        
        # Create the table
        st.markdown("""
        | trigger | description |
        |---------|-------------|
        | ;;c | code |
        | ;;s | summarize and extract |
        | ;;t | think |
        """)

def main():
    st.set_page_config(layout="wide")
    init_session_state()
    
    # Sidebar
    with st.sidebar:
        st.title("Prompt Manager")
        page = st.radio("Select Option:", ["Search for prompts", "Update database and YAML files"])
        
        if st.button("Quit"):
            if hasattr(st.session_state.client, '_transport'):
                st.session_state.client.close()
            st.success("Database connection closed.")
            st.stop()
    
    # Main content
    if page == "Search for prompts":
        search_interface()
    else:
        st.subheader("Update Database")
        if st.button("Start Update"):
            update_database()
    
    # Add the trigger table at the end
    display_trigger_table()

if __name__ == "__main__":
    main()
