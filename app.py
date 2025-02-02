import streamlit as st
from pdf_processor import process_pdf
from ppt_generator import create_ppt
import io
import tempfile
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page config
st.set_page_config(page_title="Research Paper Transformer", page_icon="🧬")

# Initialize session state for debugging
if 'debug_info' not in st.session_state:
    st.session_state.debug_info = []

def log_debug(message):
    """Add debug message to session state and log it"""
    logger.info(message)
    st.session_state.debug_info.append(message)

def process_uploaded_file(uploaded_file):
    """Process the uploaded PDF file with detailed logging"""
    try:
        log_debug("Starting file processing")
        
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            log_debug(f"Created temporary directory: {temp_dir}")
            
            # Save uploaded file
            temp_pdf_path = os.path.join(temp_dir, "input.pdf")
            with open(temp_pdf_path, "wb") as f:
                f.write(uploaded_file.getvalue())
            log_debug(f"Saved uploaded file to: {temp_pdf_path}")
            
            # Process PDF
            log_debug("Starting PDF processing")
            sections, summaries = process_pdf(temp_pdf_path)
            
            if not sections or not summaries:
                log_debug("No content extracted from PDF")
                return None
            
            log_debug(f"Successfully extracted {len(sections)} sections")
            
            # Create presentation
            temp_ppt_path = os.path.join(temp_dir, "output.pptx")
            log_debug(f"Creating presentation at: {temp_ppt_path}")
            
            ppt_path = create_ppt(summaries, temp_ppt_path)
            
            if not ppt_path or not os.path.exists(ppt_path):
                log_debug("Failed to create presentation file")
                return None
            
            log_debug("Reading presentation file")
            with open(ppt_path, 'rb') as ppt_file:
                presentation_data = ppt_file.read()
                log_debug(f"Successfully read presentation ({len(presentation_data)} bytes)")
                return presentation_data
                
    except Exception as e:
        log_debug(f"Error in process_uploaded_file: {str(e)}")
        raise e

# Main app
st.title("🧬 Research Paper Transformer")

# Debug information expander
with st.expander("Debug Information"):
    if st.button("Clear Debug Log"):
        st.session_state.debug_info = []
    
    for msg in st.session_state.debug_info:
        st.text(msg)

# File uploader
uploaded_file = st.file_uploader("Upload Research Paper (PDF)", type=['pdf'])

if uploaded_file:
    log_debug(f"File uploaded: {uploaded_file.name}")
    
    if st.button("Transform to Presentation"):
        try:
            with st.spinner("Processing..."):
                presentation_data = process_uploaded_file(uploaded_file)
                
                if presentation_data:
                    st.success("Transformation complete!")
                    
                    # Create download button
                    st.download_button(
                        label="Download Presentation",
                        data=presentation_data,
                        file_name="presentation.pptx",
                        mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
                    )
                    log_debug("Download button created")
                else:
                    st.error("Failed to create presentation")
                    
        except Exception as e:
            st.error(f"Error: {str(e)}")
            log_debug(f"Error during transformation: {str(e)}")
