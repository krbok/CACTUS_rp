import streamlit as st
from pdf_processor import process_pdf
import tempfile
import os

# Page Configuration
st.set_page_config(
    page_title="Research Paper Transformer",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    /* Main App Theme */
    .stApp {
        background: linear-gradient(180deg, #0a0a0f 0%, #1a1a2f 100%);
        color: #e0e0ff;
    }
    
    /* Neon Accent Effects */
    @keyframes neon-pulse {
        0% { box-shadow: 0 0 5px #00ff9d, 0 0 10px #00ff9d, 0 0 15px #00ff9d; }
        50% { box-shadow: 0 0 10px #00ff9d, 0 0 20px #00ff9d, 0 0 30px #00ff9d; }
        100% { box-shadow: 0 0 5px #00ff9d, 0 0 10px #00ff9d, 0 0 15px #00ff9d; }
    }
    
    /* Cyberpunk Title */
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
    
    /* Tech Container */
    .tech-container {
        background: rgba(20, 20, 35, 0.7);
        border: 1px solid #00ff9d40;
        border-radius: 15px;
        padding: 2rem;
        margin: 1rem 0;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    
    .tech-container:hover {
        border-color: #00ff9d;
        box-shadow: 0 0 15px #00ff9d40;
    }
    
    /* Upload Zone */
    .upload-zone {
        border: 2px dashed #00ff9d;
        background: rgba(0, 255, 157, 0.05);
        border-radius: 15px;
        padding: 2.5rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .upload-zone:hover {
        animation: neon-pulse 2s infinite;
    }
    
    /* Button Styling */
    .stButton > button {
        background: linear-gradient(90deg, #00ff9d 0%, #00ccff 100%);
        color: #0a0a0f;
        font-weight: 600;
        padding: 0.75rem 2rem;
        border-radius: 10px;
        border: none;
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 0 20px #00ff9d80;
    }
    
    /* Progress Bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, #00ff9d, #00ccff);
    }
    
    /* Success Message */
    .success-msg {
        background: rgba(0, 255, 157, 0.1);
        border: 1px solid #00ff9d;
        color: #00ff9d;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    /* Error Message */
    .error-msg {
        background: rgba(255, 0, 87, 0.1);
        border: 1px solid #ff0057;
        color: #ff0057;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    /* Selectbox Styling */
    .stSelectbox > div > div {
        background: rgba(20, 20, 35, 0.9);
        border: 1px solid #00ff9d40;
        color: #e0e0ff;
    }
    
    /* File Uploader */
    .stUploader {
        padding: 2rem;
        border-radius: 10px;
        background: rgba(20, 20, 35, 0.5);
    }
    
    /* Footer */
    .cyber-footer {
        text-align: center;
        padding: 2rem;
        color: #00ff9d;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        background: linear-gradient(90deg, transparent, #00ff9d20, transparent);
    }
    
    /* Spinner */
    .stSpinner > div {
        border-top-color: #00ff9d !important;
    }
    </style>
""", unsafe_allow_html=True)


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

# Format Selection
st.markdown("### SELECT OUTPUT FORMAT")
option = st.selectbox(
    "",
    ["NEURAL PPT™", "QUANTUM PODCAST™"],
    format_func=lambda x: f"⚡ {x}"
)

# Generate Section
if uploaded_file:
    if st.button("INITIATE TRANSFORMATION", use_container_width=True):
        try:
            # Create a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(uploaded_file.getbuffer())
                temp_path = tmp_file.name
            
            with st.spinner("INITIALIZING NEURAL NETWORKS..."):
                # Processing with progress tracking
                progress = st.progress(0)
                
                # Process PDF
                st.markdown("🔮 QUANTUM TEXT EXTRACTION IN PROGRESS...")
                sections, summaries = process_pdf(temp_path)
                progress.progress(50)
                
                if not sections or not summaries:
                    st.markdown(
                        "<div class='error-msg'>⚠️ EXTRACTION FAILED: NEURAL NETWORK DISRUPTION</div>",
                        unsafe_allow_html=True
                    )
                else:
                    # Format Generation
                    st.markdown("⚡ INITIATING QUANTUM TRANSFORMATION...")
                    output_file = None
                    
                    # Generate output based on selected format
                    if "PPT" in option:
                        from ppt_generator import create_ppt
                        output_file = create_ppt(summaries)
                    elif "PODCAST" in option:
                        from podcast_generator import generate_podcast
                        output_file = generate_podcast(summaries)
                    elif "ABSTRACT" in option:
                        from graphical_abstract import generate_graphical_abstract
                        output_file = generate_graphical_abstract(summaries)
                    elif "VIDEO" in option:
                        from video_generator import generate_video
                        output_file = generate_video(summaries)
                    
                    progress.progress(100)
                    
                    # Handle output
                    if output_file and os.path.exists(output_file):
                        st.balloons()
                        st.markdown(
                            "<div class='success-msg'>✨ TRANSFORMATION COMPLETE: DOWNLOAD READY</div>",
                            unsafe_allow_html=True
                        )
                        
                        with open(output_file, "rb") as f:
                            st.download_button(
                                "DOWNLOAD SYNTHESIS",
                                f,
                                file_name=os.path.basename(output_file),
                                use_container_width=True
                            )
                    else:
                        st.markdown(
                            "<div class='error-msg'>⚠️ SYNTHESIS FAILED: QUANTUM INSTABILITY DETECTED</div>",
                            unsafe_allow_html=True
                        )
        
        except Exception as e:
            st.markdown(
                f"<div class='error-msg'>⚠️ SYSTEM FAILURE: {str(e)}</div>",
                unsafe_allow_html=True
            )
        
        finally:
            # Cleanup
            if 'temp_path' in locals() and os.path.exists(temp_path):
                os.remove(temp_path)

st.markdown("</div>", unsafe_allow_html=True)

# Cyber Footer
st.markdown("""
    <div class='cyber-footer'>
        POWERED BY QUANTUM AI • EST. 2025
    </div>
""", unsafe_allow_html=True)
