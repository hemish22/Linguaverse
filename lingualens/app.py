"""
app.py — LinguaLens Streamlit Application

Main entry point for the LinguaLens UI. Provides:
- Image upload and webcam capture
- Language selection (English, Hindi, Tamil)
- OCR text extraction display
- LLM-powered simplification and explanation
- Text-to-speech audio playback
"""

import streamlit as st
from PIL import Image
import numpy as np

# Import project modules
from ocr_module import extract_text
from llm_module import simplify_and_translate
from utils import text_to_speech, LANGUAGE_MAP


# ─── Page Configuration ──────────────────────────────────────────────

st.set_page_config(
    page_title="LinguaLens — AI Text Explainer",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)


import time # Added for cache busting

# ─── Custom CSS for Premium Look ─────────────────────────────────────

# Generate a timestamp to act as a cache buster for the CSS
CACHE_BUSTER = int(time.time())

st.markdown("""
<style>
    /* Import Google Font - DM Sans for Premium Look with cache busting */
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap&v=""" + str(CACHE_BUSTER) + """');

    /* ── Color Palette ─────────────────────────────────
       Primary:    Deep Blue   #1E3A8A
       Secondary:  Teal        #14B8A6
       Accent:     Soft Orange #F59E0B
       Background: Light Gray  #F8FAFC
       Text:       Dark Gray   #1F2937
    ───────────────────────────────────────────────── */

    /* Global font & background */
    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif !important;
        color: #1F2937 !important;
        line-height: 1.6 !important;
    }
    .stApp {
        background-color: #F8FAFC !important;
    }

    /* Main header styling - Liquid Glass */
    .main-header {
        background: linear-gradient(135deg, rgba(30, 58, 138, 0.85) 0%, rgba(20, 184, 166, 0.85) 100%) !important;
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        padding: 2.5rem 2rem;
        border-radius: 20px;
        margin-bottom: 2.5rem;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 10px 40px rgba(30, 58, 138, 0.15), inset 0 1px 0 rgba(255, 255, 255, 0.3);
        position: relative;
        overflow: hidden;
    }
    .main-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 60%);
        opacity: 0.5;
        pointer-events: none;
    }
    .main-header h1 {
        color: white;
        font-size: 3rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -1px;
        text-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    .main-header p {
        color: rgba(255, 255, 255, 0.95);
        font-size: 1.15rem;
        margin-top: 0.75rem;
        font-weight: 400;
        letter-spacing: 0.2px;
    }

    /* Result cards - Glassmorphism */
    .result-card {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.5);
        border-left: 4px solid #14B8A6;
        border-radius: 16px;
        padding: 1.75rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.03);
        transition: all 300ms cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        z-index: 10;
    }
    .result-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 32px rgba(20, 184, 166, 0.12);
        background: rgba(255, 255, 255, 0.9);
    }
    .result-card h3 {
        color: #1E3A8A;
        font-weight: 700;
        margin-bottom: 1rem;
        font-size: 1.25rem;
        letter-spacing: -0.3px;
    }

    /* Sidebar styling - Modern Dark */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1E3A8A 100%);
        border-right: 1px solid rgba(255,255,255,0.05);
    }
    [data-testid="stSidebar"] .stMarkdown h2 {
        color: #14B8A6;
        font-weight: 600;
        letter-spacing: -0.5px;
    }
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] .stMarkdown li {
        color: #cbd5e1;
        font-weight: 400;
    }
    [data-testid="stSidebar"] .stSelectbox label {
        color: #cbd5e1;
        font-weight: 500;
    }

    /* Uploaded image container — constrained size with fluid styling */
    .image-container {
        border: 2px dashed rgba(20, 184, 166, 0.4);
        border-radius: 16px;
        padding: 1rem;
        text-align: center;
        background: rgba(20, 184, 166, 0.02);
        max-width: 400px;
        margin: 0 auto;
        transition: all 300ms ease;
    }
    .image-container:hover {
        border-color: rgba(20, 184, 166, 0.8);
        background: rgba(20, 184, 166, 0.05);
    }
    .image-container img {
        max-height: 300px;
        width: auto;
        object-fit: contain;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }

    /* Reduce default Streamlit image size */
    [data-testid="stImage"] {
        max-width: 400px;
        margin: 0 auto;
    }
    [data-testid="stImage"] img {
        max-height: 300px;
        object-fit: contain;
        border-radius: 8px;
    }

    /* Button styling - Fluid Interactive */
    .stButton > button {
        background: linear-gradient(135deg, #1E3A8A 0%, #14B8A6 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px;
        padding: 0.75rem 1.75rem;
        font-weight: 600;
        font-size: 1.05rem;
        letter-spacing: 0.3px;
        transition: all 250ms cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer !important;
        box-shadow: 0 4px 12px rgba(30, 58, 138, 0.2);
        position: relative;
        overflow: hidden;
    }
    .stButton > button::after {
        content: '';
        position: absolute;
        top: 0; left: 0; width: 100%; height: 100%;
        background: linear-gradient(rgba(255,255,255,0.2), transparent);
        opacity: 0;
        transition: opacity 250ms ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(30, 58, 138, 0.35);
    }
    .stButton > button:hover::after {
        opacity: 1;
    }
    .stButton > button:active {
        transform: translateY(0);
        box-shadow: 0 2px 8px rgba(30, 58, 138, 0.2);
    }

    /* Interactive Elements Cursor */
    [data-testid="stFileUploader"] section, 
    .stSelectbox div[role="button"] {
        cursor: pointer !important;
    }

    /* Accent highlight for important elements */
    .accent-highlight {
        color: #F59E0B;
        font-weight: 600;
    }

    /* Footer */
    .footer {
        text-align: center;
        color: #64748b;
        font-size: 0.9rem;
        font-weight: 400;
        margin-top: 4rem;
        padding: 1.5rem;
        border-top: 1px solid rgba(30, 58, 138, 0.1);
    }
</style>
""", unsafe_allow_html=True)


# ─── Header ──────────────────────────────────────────────────────────

st.markdown("""
<div class="main-header">
    <h1>🔍 LinguaLens</h1>
    <p>Upload an image with text → Get simple explanations in your language</p>
</div>
""", unsafe_allow_html=True)


# ─── Sidebar ─────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## ⚙️ Settings")
    st.markdown("---")

    # Language selection
    target_language = st.selectbox(
        "🌐 Output Language",
        options=["English", "Hindi", "Tamil"],
        index=1,  # Default to Hindi
        help="Select the language for the translated explanation",
    )

    st.markdown("---")
    st.markdown("## 📖 How it works")
    st.markdown("""
    1. **Upload** an image with text
    2. **OCR** extracts the text automatically
    3. **AI** simplifies and explains it
    4. **Translation** in your chosen language
    5. **Listen** to the explanation (optional)
    """)

    st.markdown("---")
    st.markdown("## 🎯 Works great with")
    st.markdown("""
    - 💊 Medicine labels
    - 📄 Government documents
    - 🚏 Signboards
    - 📋 Instructions & manuals
    - 📑 Research papers
    """)


# ─── Main Content: Image Input ───────────────────────────────────────

tab_upload, tab_camera = st.tabs(["📁 Upload Image", "📷 Capture from Webcam"])

input_image = None

with tab_upload:
    uploaded_file = st.file_uploader(
        "Choose an image file",
        type=["png", "jpg", "jpeg", "bmp", "tiff", "webp"],
        help="Upload an image containing text you want explained",
    )
    if uploaded_file is not None:
        input_image = Image.open(uploaded_file)
        st.markdown('<div class="image-container">', unsafe_allow_html=True)
        st.image(input_image, caption="Uploaded Image", width=400)
        st.markdown('</div>', unsafe_allow_html=True)

with tab_camera:
    camera_photo = st.camera_input(
        "Take a photo of text you want explained",
        help="Point your camera at a document, label, or sign",
    )
    if camera_photo is not None:
        input_image = Image.open(camera_photo)


# ─── Processing ──────────────────────────────────────────────────────

if input_image is not None:
    if st.button("🔍 Analyze Image", use_container_width=True, type="primary"):

        # Step 1: OCR Extraction
        with st.status("🔄 Processing your image...", expanded=True) as status:
            st.write("📸 Extracting text from image...")
            extracted_text = extract_text(input_image)

            if not extracted_text.strip():
                status.update(
                    label="⚠️ No text detected",
                    state="error",
                    expanded=True,
                )
                st.error(
                    "Could not detect any text in the image. "
                    "Please try with a clearer image or different angle."
                )
            else:
                st.write(f"✅ Found {len(extracted_text.split())} words")

                # Step 2: LLM Processing
                st.write("🧠 AI is simplifying and translating...")
                result = simplify_and_translate(extracted_text, target_language)
                
                status.update(
                    label="✅ Analysis complete!",
                    state="complete",
                    expanded=False,
                )

                # ─── Display Results ──────────────────────────────

                st.markdown("---")

                # Extracted Text
                st.markdown("""
                <div class="result-card">
                    <h3>📝 Extracted Text</h3>
                </div>
                """, unsafe_allow_html=True)
                st.code(extracted_text, language=None)

                # Two-column layout for explanation and translation
                col_left, col_right = st.columns(2)

                with col_left:
                    # Simple Explanation
                    st.markdown("""
                    <div class="result-card">
                        <h3>💡 Simple Explanation</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    st.markdown(result["explanation"])

                    # Key Points
                    if result["key_points"]:
                        st.markdown("""
                        <div class="result-card">
                            <h3>🎯 Key Points</h3>
                        </div>
                        """, unsafe_allow_html=True)
                        st.markdown(result["key_points"])

                with col_right:
                    # Translation
                    st.markdown(f"""
                    <div class="result-card">
                        <h3>🌐 Translation ({target_language})</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    st.markdown(result["translation"])

                    # Text-to-Speech
                    st.markdown("""
                    <div class="result-card">
                        <h3>🔊 Listen</h3>
                    </div>
                    """, unsafe_allow_html=True)

                    tts_text = result["translation"] if result["translation"] else result["explanation"]
                    
                    try:
                        audio_bytes = text_to_speech(tts_text, target_language)
                        st.audio(audio_bytes, format="audio/mp3")
                    except Exception as e:
                        st.warning(f"Text-to-speech unavailable: {str(e)}")


# ─── Empty State ──────────────────────────────────────────────────────

else:
    st.markdown("""
    <div style="text-align: center; padding: 4rem 2rem; color: #9ca3af;">
        <p style="font-size: 4rem; margin-bottom: 1rem;">📸</p>
        <h3 style="color: #1E3A8A; font-weight: 500;">Upload an image to get started</h3>
        <p style="color: #64748b;">Take a photo or upload an image containing text you want explained</p>
    </div>
    """, unsafe_allow_html=True)


# ─── Footer ──────────────────────────────────────────────────────────

st.markdown("""
<div class="footer">
    Built with ❤️ using Streamlit, EasyOCR, and Google Gemini | LinguaLens v1.0
</div>
""", unsafe_allow_html=True)
