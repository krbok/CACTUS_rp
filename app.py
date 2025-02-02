import streamlit as st
import os
import tempfile
import logging
import gc
import atexit
import shutil
from pathlib import Path
from pdf_processor import process_pdf
from ppt_generator import create_ppt

# Configure environment variables
os.environ['TRANSFORMERS_CACHE'] = '/tmp/transformers_cache'
os.environ['NLTK_DATA'] = '/tmp/nltk_data'

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Cleanup function for temporary files
def cleanup_temp_files():
    """Clean up temporary directories on app shutdown"""
    try:
        for path in ['/tmp/transformers_cache', '/tmp/nltk_data']:
            if os.path.exists(path):
                shutil.rmtree(path, ignore_errors=True)
                logger.info(f"Cleaned up {path}")
    except Exception as e:
        logger.error(f"Cleanup error: {e}")

# Register cleanup function
atexit.register(cleanup_temp_files)

@st.cache_resource
def initialize_models():
    """Initialize required NLP models and downloads"""
    try:
        # Initialize NLTK
        import nltk
        nltk.download('punkt', quiet=True, download_dir='/tmp/nltk_data')
        logger.info("NLTK initialized successfully")

        # Initialize spaCy
        import spacy
        if not spacy.util.is_package('en_core_web_sm'):
            spacy.cli.download('en_core_web_sm')
        nlp = spacy.load('en_core_web_sm')
        logger.info("spaCy initialized successfully")

        # Initialize transformers (without downloading model yet)
        from transformers import AutoTokenizer
        logger.info("Transformers initialized successfully")

        return True
    except Exception as e:
        logger.error(f"Model initialization failed: {e}")
        return False

class AppState:
    """Manage application state and session variables"""
    def __init__(self):
        if 'debug_info' not in st.session_state:
            st.session_state.debug_info = []
        if 'processing_complete' not in st.session_state:
            st.session_state.processing_complete = False
        if 'temp_dir' not in st.session_state:
            st.session_state.temp_dir = None

    def log_debug(self, message: str):
        """Add debug message to session state and log it"""
        logger.info(message)
        st.session_state.debug_info.append(f"{message}")

    def clear_debug(self):
        """Clear debug information"""
        st.session_state.debug_info = []

def process_uploaded_file(uploaded_file, app_state: AppState):
    """Process the uploaded PDF file with enhanced error handling"""
    try:
        app_state.log_debug("Starting file processing")
        
        # Create temporary directory
        temp_dir = tempfile.mkdtemp()
        st.session_state.temp_dir = temp_dir
        app_state.log_debug(f"Created temporary directory: {temp_dir}")
        
        try:
            # Save uploaded file
            temp_pdf_path = os.path.join(temp_dir, "input.pdf")
            with open(temp_pdf_path, "wb") as f:
                f.write(uploaded_file.getvalue())
            app_state.log_debug(f"Saved uploaded file ({uploaded_file.size} bytes)")
            
            # Verify file
            if not os.path.exists(temp_pdf_path):
                raise FileNotFoundError("Failed to save PDF")
            
            # Process PDF
            app_state.log_debug("Processing PDF...")
            sections, summaries = process_pdf(temp_pdf_path)
            
            if not sections or not summaries:
                raise ValueError("No content extracted from PDF")
            
            app_state.log_debug(f"Extracted {len(sections)} sections")
            
            # Create presentation
            temp_ppt_path = os.path.join(temp_dir, "output.pptx")
            app_state.log_debug("Creating presentation...")
            
            ppt_path = create_ppt(summaries, temp_ppt_path)
            if not ppt_path or not os.path.exists(ppt_path):
                raise FileNotFoundError("Failed to create presentation")
            
            # Read presentation
            with open(ppt_path, 'rb') as ppt_file:
                presentation_data = ppt_file.read()
            
            app_state.log_debug(f"Created presentation ({len(presentation_data)} bytes)")
            gc.collect()  # Force garbage collection
            
            return presentation_data
            
        finally:
            # Cleanup
            if st.session_state.temp_dir:
                shutil.rmtree(st.session_state.temp_dir, ignore_errors=True)
                st.session_state.temp_dir = None
                app_state.log_debug("Cleaned up temporary files")
    
    except Exception as e:
        app_state.log_debug(f"Error: {str(e)}")
        raise

def main():
    """Main application entry point"""
    # Page configuration
    st.set_page_config(
        page_title="Research Paper Transformer",
        page_icon="🧬",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Initialize app state
    app_state = AppState()

    # Initialize models
    if not initialize_models():
        st.error("Failed to initialize required models. Please try refreshing the page.")
        st.stop()

    # Sidebar
    with st.sidebar:
        st.title("🧬 Controls")
        st.info("System Status: Active")
        
        if st.button("Clear Debug Log"):
            app_state.clear_debug()
    
    # Main content
    st.title("Research Paper Transformer")
    st.write("Transform your research papers into presentations automatically.")

    # File upload
    uploaded_file = st.file_uploader(
        "Upload Research Paper (PDF)",
        type=['pdf'],
        help="Maximum file size: 200MB"
    )

    # Process file
    if uploaded_file:
        app_state.log_debug(f"File uploaded: {uploaded_file.name}")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            if st.button("🔄 Transform to Presentation", type="primary", use_container_width=True):
                try:
                    with st.spinner("Processing your paper..."):
                        presentation_data = process_uploaded_file(uploaded_file, app_state)
                        
                    if presentation_data:
                        st.success("✨ Transformation complete!")
                        st.download_button(
                            label="📥 Download Presentation",
                            data=presentation_data,
                            file_name=f"{uploaded_file.name.rsplit('.', 1)[0]}.pptx",
                            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                            use_container_width=True
                        )
                        st.session_state.processing_complete = True
                    else:
                        st.error("Failed to create presentation")
                        
                except Exception as e:
                    st.error(f"Error during transformation: {str(e)}")
                    app_state.log_debug(f"Processing error: {str(e)}")
                finally:
                    gc.collect()

    # Debug information
    with st.expander("🔍 Debug Information", expanded=False):
        st.text("Recent activity:")
        for msg in st.session_state.debug_info:
            st.text(msg)

    # Footer
    st.markdown("---")
    st.markdown("Made with ❤️ by Your Team")

if __name__ == "__main__":
    main()
