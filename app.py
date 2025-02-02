import streamlit as st
from pdf_processor import process_pdf
import tempfile
import os
import base64
from pathlib import Path

# Page Configuration
st.set_page_config(
    page_title="Research Paper Transformer",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS (keeping your existing styles)
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(180deg, #0a0a0f 0%, #1a1a2f 100%);
        color: #e0e0ff;
    }
    
    .cyber-title {
        font-family: 'BlinkMacSystemFont', sans-serif;
        font-size: 3.5rem;
        font-weight: 800;
        text-align: center;
        color: #00ff9d;
        text-shadow: 0 0 10px #00ff9d80;
        letter-spacing: 2px;
        margin: 2rem 0;
        padding: 1rem;
        background: linear-gradient(90deg, #0a0a0f 0%, #1a1a2f 50%, #0a0a0f 100%);
        border-radius: 10px;
        border: 1px solid #00ff9d40;
    }
    
    .tech-container {
        background: rgba(20, 20, 35, 0.7);
        border: 1px solid #00ff9d40;
        border-radius: 15px;
        padding: 2rem;
        margin: 1rem 0;
    }
    
    .upload-zone {
        border: 2px dashed #00ff9d;
        background: rgba(0, 255, 157, 0.05);
        border-radius: 15px;
        padding: 2.5rem;
        text-align: center;
    }
    
    .success-msg {
        background: rgba(0, 255, 157, 0.1);
        border: 1px solid #00ff9d;
        color: #00ff9d;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .error-msg {
        background: rgba(255, 0, 87, 0.1);
        border: 1px solid #ff0057;
        color: #ff0057;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'temp_files' not in st.session_state:
    st.session_state.temp_files = []

def cleanup_temp_files():
    """Clean up temporary files at the end of the session"""
    for temp_file in st.session_state.temp_files:
        try:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        except Exception as e:
            st.error(f"Error cleaning up temporary file: {e}")
    st.session_state.temp_files = []

# App Title
st.markdown("<h1 class='cyber-title'>🧬 RESEARCH TRANSFORMER</h1>", unsafe_allow_html=True)

# Main Container
st.markdown("<div class='tech-container'>", unsafe_allow_html=True)

# Upload Section
st.markdown("<div class='upload-zone'>", unsafe_allow_html=True)
uploaded_file = st.file_uploader(
    "INITIALIZE PAPER UPLOAD",
    type=["pdf"],
    help="Upload your research paper (PDF format)"
)
st.markdown("</div>", unsafe_allow_html=True)

if uploaded_file:
    try:
        # Create a temporary directory that will be cleaned up automatically
        with tempfile.TemporaryDirectory() as temp_dir:
            # Save uploaded file to temporary directory
            temp_path = Path(temp_dir) / "input.pdf"
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            st.session_state.temp_files.append(str(temp_path))

            if st.button("INITIATE TRANSFORMATION", use_container_width=True):
                with st.spinner("PROCESSING DOCUMENT..."):
                    try:
                        # Process PDF
                        progress = st.progress(0)
                        st.markdown("🔮 EXTRACTING CONTENT...")
                        
                        sections, summaries = process_pdf(str(temp_path))
                        progress.progress(50)

                        if not sections or not summaries:
                            st.markdown(
                                "<div class='error-msg'>⚠️ EXTRACTION FAILED: No content could be extracted</div>",
                                unsafe_allow_html=True
                            )
                        else:
                            # Generate PPT
                            st.markdown("⚡ GENERATING PRESENTATION...")
                            from ppt_generator import create_ppt
                            
                            output_path = Path(temp_dir) / "output.pptx"
                            output_file = create_ppt(summaries, str(output_path))
                            
                            progress.progress(100)

                            if output_file and Path(output_file).exists():
                                st.balloons()
                                st.markdown(
                                    "<div class='success-msg'>✨ TRANSFORMATION COMPLETE!</div>",
                                    unsafe_allow_html=True
                                )
                                
                                # Read the file and create download button
                                with open(output_file, "rb") as f:
                                    bytes_data = f.read()
                                    b64 = base64.b64encode(bytes_data).decode()
                                    
                                    href = f'<a href="data:application/vnd.openxmlformats-officedocument.presentationml.presentation;base64,{b64}" download="presentation.pptx" class="download-button">DOWNLOAD PRESENTATION</a>'
                                    st.markdown(href, unsafe_allow_html=True)
                            else:
                                st.markdown(
                                    "<div class='error-msg'>⚠️ GENERATION FAILED: Could not create presentation</div>",
                                    unsafe_allow_html=True
                                )

                    except Exception as e:
                        st.markdown(
                            f"<div class='error-msg'>⚠️ PROCESSING ERROR: {str(e)}</div>",
                            unsafe_allow_html=True
                        )

    except Exception as e:
        st.markdown(
            f"<div class='error-msg'>⚠️ FILE HANDLING ERROR: {str(e)}</div>",
            unsafe_allow_html=True
        )

st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("""
    <div style='text-align: center; padding: 2rem; color: #00ff9d; font-size: 0.9rem;'>
        POWERED BY QUANTUM AI • EST. 2025
    </div>
""", unsafe_allow_html=True)

# Cleanup temp files when the session ends
cleanup_temp_files()
