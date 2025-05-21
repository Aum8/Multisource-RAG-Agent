import streamlit as st
from pathlib import Path
import uuid
from file_handler import FileHandler
from RAG import RAGProcessor
import xxhash

# Configuration
WORKING_DIR = Path("./.docchat_data")
WORKING_DIR.mkdir(exist_ok=True)

# Initialize components
file_handler = FileHandler(WORKING_DIR)
rag_processor = RAGProcessor(WORKING_DIR)

# Session state
if "sources" not in st.session_state:
    st.session_state.sources = {}
if "messages" not in st.session_state:
    st.session_state.messages = []

# App UI
st.title("Multi-source RAG Agent")

# File upload with description
with st.expander("Upload Documents", expanded=True):
    uploaded_files = st.file_uploader(
        "Select files",
        type=["pdf", "csv", "json", "xlsx", "txt", "md"],
        accept_multiple_files=True,
        key="file_uploader"
    )
    
    # Description input for each file
    file_descriptions = {}
    if uploaded_files:
        # print("uploaded_files", st.session_state.sources)
        for file in uploaded_files:
            default_desc = ""
            if str(file.name) in {Path(k).name for k in st.session_state.sources.keys()}:
                existing_path = next(k for k in st.session_state.sources.keys() if Path(k).name == file.name)
                default_desc = st.session_state.sources[existing_path].get("description", "")
            
            file_descriptions[file.name] = st.text_input(
                f"Description for {file.name}",
                value=default_desc,
                key=f"desc_{file.name}"
            )

# Process uploads
if uploaded_files and st.button("Add to Context"):
    current_hashes = {src["hash"] for src in st.session_state.sources.values()}
    
    for uploaded_file in uploaded_files:
        file_hash = xxhash.xxh64(uploaded_file.getvalue()).hexdigest()
        if file_hash not in current_hashes:
            # Save file
            file_id = uuid.uuid4().hex
            file_ext = Path(uploaded_file.name).suffix
            file_path = WORKING_DIR / f"{file_id}{file_ext}"
            
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Debug: Print file path
            st.write(f"Processing file: {file_path}")
            
            # Process content
            content = file_handler.process_file(file_path)
            if not content:
                st.error(f"Failed to process file: {uploaded_file.name}")
                continue
            
            # Debug: Print content
            # st.write(f"Content of {uploaded_file.name}:", content[:500])  # Print first 500 characters
            
            description = file_descriptions.get(uploaded_file.name, "")
            
            # Add to sources
            st.session_state.sources[str(file_path)] = {
                "name": uploaded_file.name,
                "description": description,
                "hash": file_hash,
                "content": content
            }
    
    # Debug: Print updated sources
    # st.write("Updated Sources:", st.session_state.sources)
    
    st.rerun()

# Display uploaded files with remove option
if st.session_state.sources:
    st.write("**Current Context:**")
    for file_path, info in list(st.session_state.sources.items()):
        col1, col2 = st.columns([0.9, 0.1])
        with col1:
            st.markdown(f"**{info['name']}**")
            st.caption(info['description'] or "No description provided")
        with col2:
            if st.button("×", key=f"remove_{file_path}"):
                Path(file_path).unlink(missing_ok=True)
                del st.session_state.sources[file_path]
                st.rerun()

# Chat interface
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask about your documents"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Map file names to file paths
    file_name_to_path = {Path(v["name"]).name: k for k, v in st.session_state.sources.items()}
    
    # Select relevant files
    relevant_files = rag_processor.select_relevant_files(
        prompt,
        st.session_state.sources
    )
    
    st.write("Relevant files:", relevant_files)
    
    # Map relevant file names to paths
    relevant_file_paths = [
        file_name_to_path[file] for file in relevant_files if file in file_name_to_path
    ]
    
    # Check if relevant_file_paths is empty
    if not relevant_file_paths:
        st.error("No relevant files found. Please check your input or upload files.")
    else:
        # Generate response
        with st.spinner("Analyzing documents..."):
            response = rag_processor.query(
                prompt, 
                {k: v for k, v in st.session_state.sources.items() if k in relevant_file_paths}
            )
        
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(response)