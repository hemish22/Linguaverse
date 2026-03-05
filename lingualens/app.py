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


# ─── Custom CSS for Premium Look ─────────────────────────────────────

st.markdown("""
<style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* ── Color Palette ─────────────────────────────────
       Primary:    Deep Blue   #1E3A8A
       Secondary:  Teal        #14B8A6
       Accent:     Soft Orange #F59E0B
       Background: Light Gray  #F8FAFC
       Text:       Dark Gray   #1F2937
    ───────────────────────────────────────────────── */

    /* Global font & background */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #1F2937;
    }
    .stApp {
        background-color: #F8FAFC;
    }

    /* Main header styling */
    .main-header {
        background: linear-gradient(135deg, #1E3A8A 0%, #14B8A6 100%);
        padding: 2rem 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 8px 32px rgba(30, 58, 138, 0.3);
    }
    .main-header h1 {
        color: white;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .main-header p {
        color: rgba(255, 255, 255, 0.9);
        font-size: 1.1rem;
        margin-top: 0.5rem;
        font-weight: 300;
    }

    /* Result cards */
    .result-card {
        background: linear-gradient(145deg, #F8FAFC 0%, #ffffff 100%);
        border: 1px solid rgba(20, 184, 166, 0.2);
        border-left: 4px solid #14B8A6;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .result-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(20, 184, 166, 0.15);
    }
    .result-card h3 {
        color: #1E3A8A;
        font-weight: 600;
        margin-bottom: 0.75rem;
        font-size: 1.1rem;
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1E3A8A 100%);
    }
    [data-testid="stSidebar"] .stMarkdown h2 {
        color: #14B8A6;
    }
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] .stMarkdown li {
        color: #cbd5e1;
    }
    [data-testid="stSidebar"] .stSelectbox label {
        color: #cbd5e1;
    }

    /* Uploaded image container — constrained size */
    .image-container {
        border: 2px dashed rgba(20, 184, 166, 0.4);
        border-radius: 12px;
        padding: 0.75rem;
        text-align: center;
        background: rgba(20, 184, 166, 0.03);
        max-width: 400px;
        margin: 0 auto;
    }
    .image-container img {
        max-height: 300px;
        width: auto;
        object-fit: contain;
    }

    /* Reduce default Streamlit image size */
    [data-testid="stImage"] {
        max-width: 400px;
        margin: 0 auto;
    }
    [data-testid="stImage"] img {
        max-height: 300px;
        object-fit: contain;
    }

    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #1E3A8A 0%, #14B8A6 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.5rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 15px rgba(30, 58, 138, 0.4);
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
        font-size: 0.85rem;
        margin-top: 3rem;
        padding: 1rem;
        border-top: 1px solid #e2e8f0;
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
