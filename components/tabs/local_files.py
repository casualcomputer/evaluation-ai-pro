import os
import shutil

import streamlit as st

import utils.helpers as func
import utils.ollama as ollama
import utils.llama_index as llama_index
import utils.logs as logs
import utils.rag_pipeline as rag
from utils.llama_index import load_documents #added
import shutil

supported_files = (
    "csv",
    "docx",
    "epub",
    "ipynb",
    "json",
    "md",
    "pdf",
    "ppt",
    "pptx",
    "txt",
)

import os
import utils.logs as logs
from io import BytesIO

# # The function commented out is the original function
# def local_files():
#     # Force users to confirm Settings before uploading files
#     if st.session_state["selected_model"] is not None:
#         uploaded_files = st.file_uploader(
#             "Select Files",
#             accept_multiple_files=True,
#             type=supported_files,
#         )
#     else:
#         st.warning("Please configure Ollama settings before proceeding!", icon="⚠️")
#         file_upload_container = st.container(border=True)
#         with file_upload_container:
#             uploaded_files = st.file_uploader(
#                 "Select Files",
#                 accept_multiple_files=True,
#                 type=supported_files,
#                 disabled=True,
#             )

#     if len(uploaded_files) > 0:
#         st.session_state["file_list"] = uploaded_files

#         with st.spinner("Processing..."):
#             # Initiate the RAG pipeline, providing documents to be saved on disk if necessary
#             error = rag.rag_pipeline(uploaded_files)

#             # Display errors (if any) or proceed
#             if error is not None:
#                 st.exception(error)
#             else:
#                 st.write("Your files are ready. Let's chat! 😎") # TODO: This should be a button.


def get_local_files_as_uploaded_files(directory: str):
    local_files = []
    for filename in os.listdir(directory):
        if os.path.isfile(os.path.join(directory, filename)):
            with open(os.path.join(directory, filename), "rb") as f:
                file_data = BytesIO(f.read())
                file_data.name = filename
                local_files.append(file_data)
    return local_files

def local_files():
    cleaned_data_dir = "cleaned-evaluation-reports"
    temp_data_dir = "data"

    # Ensure the directories exist
    if not os.path.exists(cleaned_data_dir):
        os.makedirs(cleaned_data_dir)
    if not os.path.exists(temp_data_dir):
        os.makedirs(temp_data_dir)

    # Force users to confirm Settings before uploading files
    if st.session_state.get("selected_model") is not None:
        uploaded_files = st.file_uploader(
            "Select Files",
            accept_multiple_files=True,
            type=supported_files,
        )
    else:
        st.warning("Please configure Ollama settings before proceeding!", icon="⚠️")
        file_upload_container = st.container(border=True)
        with file_upload_container:
            uploaded_files = st.file_uploader(
                "Select Files",
                accept_multiple_files=True,
                type=supported_files,
                disabled=True,
            )

    if not uploaded_files:
        uploaded_files = get_local_files_as_uploaded_files(cleaned_data_dir)

    if uploaded_files and len(uploaded_files) > 0:
        st.session_state["file_list"] = uploaded_files

        with st.spinner("Processing..."):
            # Save uploaded files to the 'cleaned-evaluation-reports' directory
            for uploaded_file in uploaded_files:
                with open(os.path.join(cleaned_data_dir, uploaded_file.name), "wb") as f:
                    f.write(uploaded_file.getbuffer())

            # Copy files to the temporary 'data' directory
            for file_name in os.listdir(cleaned_data_dir):
                full_file_name = os.path.join(cleaned_data_dir, file_name)
                if os.path.isfile(full_file_name):
                    shutil.copy(full_file_name, temp_data_dir)

            # Initiate the RAG pipeline, providing documents to be saved on disk if necessary
            error = rag.rag_pipeline(uploaded_files)

            # Display errors (if any) or proceed
            if error is not None:
                st.exception(error)
            else:
                st.write("Your files are ready. Let's chat! 😎")  # TODO: This should be a button.

    # Check for local files if no files are uploaded
    else:
        try:
            local_files = [f for f in os.listdir(cleaned_data_dir) if os.path.isfile(os.path.join(cleaned_data_dir, f))]
            print("local_files:", local_files)
            if local_files:
                # Copy files to the temporary 'data' directory
                for file_name in local_files:
                    full_file_name = os.path.join(cleaned_data_dir, file_name)
                    if os.path.isfile(full_file_name):
                        shutil.copy(full_file_name, temp_data_dir)

                with st.spinner("Processing preloaded local files..."):
                    documents = llama_index.load_documents(temp_data_dir)
                    st.session_state["documents"] = documents
                    st.caption("✔️ Local files loaded and processed")

                if st.session_state.get("documents"):
                    with st.spinner("Creating query engine for preloaded files..."):
                        query_engine = llama_index.create_query_engine(st.session_state["documents"])
                        st.session_state["query_engine"] = query_engine
                        st.caption("✔️ Query engine created from existing preloaded documents")

        except Exception as err:
            logs.log.error(f"Document Load Error: {str(err)}")
            st.exception(err)
            st.stop()