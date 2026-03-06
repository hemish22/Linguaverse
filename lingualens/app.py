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
from llm_module import simplify_and_translate, answer_question, generate_suggested_questions
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

    /* Global font */
    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif !important;
        line-height: 1.6 !important;
    }

    /* Main header styling - Liquid Glass */
    .main-header {
        background: linear-gradient(135deg, rgba(37, 99, 235, 0.85) 0%, rgba(20, 184, 166, 0.85) 100%) !important;
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

    /* Result cards - Solid light gray to contrast dark background */
    .result-card {
        background: #E5E7EB !important;
        color: #0B0F19 !important; /* Dark text on light card */
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-left: 4px solid #2563EB;
        border-radius: 16px;
        padding: 1.75rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.3);
        transition: all 300ms cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        z-index: 10;
    }
    .result-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 32px rgba(37, 99, 235, 0.2);
        background: #f3f4f6 !important;
    }
    .result-card h3 {
        color: #2563EB !important;
        font-weight: 700;
        margin-bottom: 1rem;
        font-size: 1.25rem;
        letter-spacing: -0.3px;
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

    /* Button styling - Amber Highlight */
    .stButton > button {
        background: linear-gradient(135deg, #F59E0B 0%, #d97706 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px;
        padding: 0.75rem 1.75rem;
        font-weight: 600;
        font-size: 1.05rem;
        letter-spacing: 0.3px;
        transition: all 250ms cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer !important;
        box-shadow: 0 4px 12px rgba(245, 158, 11, 0.2);
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
        box-shadow: 0 8px 20px rgba(245, 158, 11, 0.4);
    }
    .stButton > button:hover::after {
        opacity: 1;
    }
    .stButton > button:active {
        transform: translateY(0);
        box-shadow: 0 2px 8px rgba(245, 158, 11, 0.2);
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

    /* Q&A Section Header */
    .qa-header {
        background: linear-gradient(135deg, rgba(20, 184, 166, 0.12) 0%, rgba(37, 99, 235, 0.08) 100%);
        border: 1px solid rgba(20, 184, 166, 0.3);
        border-left: 4px solid #14B8A6;
        border-radius: 16px;
        padding: 1.75rem;
        margin-bottom: 1.5rem;
    }
    .qa-header h3 {
        color: #14B8A6 !important;
        font-weight: 700;
        margin-bottom: 0.5rem;
        font-size: 1.25rem;
    }
    .qa-header p {
        color: #64748b;
        margin: 0;
        font-size: 0.95rem;
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


# ─── Session State Initialization ─────────────────────────────────────

if "ocr_text" not in st.session_state:
    st.session_state.ocr_text = ""
if "ocr_confidence" not in st.session_state:
    st.session_state.ocr_confidence = 0.0
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "suggested_questions" not in st.session_state:
    st.session_state.suggested_questions = []
if "analysis_language" not in st.session_state:
    st.session_state.analysis_language = "English"


# ─── Header ──────────────────────────────────────────────────────────

st.markdown("""
<div class="main-header">
    <h1>🔍 LinguaLens</h1>
    <p>Upload a document → Get explanations in your language → Ask questions by text or voice</p>
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
    
    # Target Audience
    difficulty = st.selectbox(
        "🧠 Explain For",
        options=["Child (12 years old)", "Student", "Professional"],
        index=1,
        help="Adjust the simplicity and reading level of the explanation",
    )

    st.markdown("---")
    
    # Input Language Selection (to fix EasyOCR incompatibility)
    source_language = st.selectbox(
        "📸 Image Text Language",
        options=["English & Hindi", "English & Tamil"],
        index=0,
        help="Select which language is present in the image. EasyOCR cannot load Hindi and Tamil simultaneously.",
    )

    st.markdown("---")
    st.markdown("## 📖 How it works")
    st.markdown("""
    1. **Upload** an image with text
    2. **OCR** extracts the text automatically
    3. **AI** simplifies and explains it
    4. **Translation** in your chosen language
    5. **Listen** to the explanation (optional)
    6. **Ask questions** about the document 💬
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

tab_upload, tab_camera, tab_text = st.tabs(["📁 Upload Image", "📷 Capture from Camera", "✍️ Write Text Directly"])

input_image = None
direct_text_input = ""

with tab_upload:
    uploaded_file = st.file_uploader(
        "Choose an image...", 
        type=["jpg", "jpeg", "png", "webp"],
        label_visibility="collapsed"
    )
    st.markdown("<p style='color:#64748b; font-size: 0.95rem; text-align: center;'>Supported: forms, medicine labels, instructions, research papers</p>", unsafe_allow_html=True)
    
    if uploaded_file is not None:
        input_image = Image.open(uploaded_file)
        st.markdown('<div class="image-container">', unsafe_allow_html=True)
        st.image(input_image, caption="Uploaded Image", width=400)
        st.markdown('</div>', unsafe_allow_html=True)

with tab_camera:
    st.markdown('<div class="result-card" style="text-align: center;">', unsafe_allow_html=True)
    st.markdown("<h3 style='margin-bottom: 0;'>📷 Camera Capture</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748b; font-size: 0.95rem; margin-bottom: 1.5rem;'>Enable your camera to take a photo directly.</p>", unsafe_allow_html=True)
    
    enable_camera = st.toggle("Enable Camera", value=False)
    
    if enable_camera:
        camera_photo = st.camera_input(
            "Take a photo of text you want explained",
            help="Point your camera at a document, label, or sign",
            label_visibility="collapsed"
        )
        if camera_photo is not None:
            input_image = Image.open(camera_photo)
    else:
        st.info("💡 Tip: Click 'Enable Camera' when you're ready to capture.")
        
    st.markdown('</div>', unsafe_allow_html=True)

with tab_text:
    st.markdown('<div class="result-card">', unsafe_allow_html=True)
    st.markdown("<h3 style='margin-bottom: 0;'>✍️ Write or Paste Text</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748b; font-size: 0.95rem; margin-bottom: 1.5rem;'>Paste standard text here to bypass OCR extraction.</p>", unsafe_allow_html=True)
    
    text_input_area = st.text_area(
        "Enter text to explain:", 
        height=200, 
        label_visibility="collapsed",
        placeholder="Type or paste the complex text you want LinguaLens to simplify..."
    )
    
    if text_input_area.strip():
        direct_text_input = text_input_area.strip()
        
    st.markdown('</div>', unsafe_allow_html=True)


# ─── Processing ──────────────────────────────────────────────────────

if input_image is not None or direct_text_input:
    button_label = "🔍 Analyze Text" if direct_text_input else "🔍 Analyze Image"
    if st.button(button_label, use_container_width=True, type="primary"):
        # Clear previous Q&A history for new analysis
        st.session_state.chat_history = []

        # Step 1: Text Retrieval (OCR or Direct)
        with st.status("🔄 Processing your input...", expanded=True) as status:
            if direct_text_input:
                st.write("📝 Using directly inputted text...")
                extracted_text = direct_text_input
                ocr_confidence = 1.0
            else:
                st.write("📸 Extracting text from image...")
                extracted_text, ocr_confidence = extract_text(input_image, source_language)

            if not extracted_text.strip():
                status.update(
                    label="⚠️ No text detected or provided",
                    state="error",
                    expanded=True,
                )
                st.error(
                    "Could not detect any text. "
                    "Please provide valid text or a clearer image."
                )
                st.session_state.analysis_result = None
            else:
                st.write(f"✅ Found {len(extracted_text.split())} words")

                # Step 2: LLM Processing
                st.write("🧠 AI is simplifying and translating...")
                result = simplify_and_translate(extracted_text, target_language, difficulty)

                st.write("💡 Generating suggested questions...")
                suggested = generate_suggested_questions(extracted_text, target_language)

                # Save everything to session state for persistent display
                st.session_state.ocr_text = extracted_text
                st.session_state.ocr_confidence = ocr_confidence
                st.session_state.analysis_result = result
                st.session_state.suggested_questions = suggested
                st.session_state.analysis_language = target_language

                status.update(
                    label="✅ Analysis complete!",
                    state="complete",
                    expanded=False,
                )


# ─── Display Results (from session state) ────────────────────────────

if st.session_state.get("analysis_result"):
    result = st.session_state.analysis_result
    ocr_confidence = st.session_state.get("ocr_confidence", 0.0)
    extracted_text = st.session_state.get("ocr_text", "")

    st.markdown(f"""
    <div style="display: flex; gap: 2rem; margin-bottom: 1rem; padding: 1rem; background: rgba(226, 232, 240, 0.4); border-radius: 8px; border: 1px solid #e2e8f0;">
        <div><span style="color: #64748b; font-size: 0.9rem;">OCR Confidence</span><br><strong>{ocr_confidence*100:.0f}%</strong></div>
        <div><span style="color: #64748b; font-size: 0.9rem;">Detected Language</span><br><strong>{result.get('detected_language', 'Unknown')}</strong></div>
    </div>
    """, unsafe_allow_html=True)

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
        # Toggleable Tabs for Explanation and Key Points
        exp_tab, key_tab = st.tabs(["💡 AI Simplified Explanation", "🎯 Key Points"])

        with exp_tab:
            st.markdown(result["explanation"])
            st.code(result["explanation"], language=None)

        with key_tab:
            if result["key_points"]:
                st.markdown(result["key_points"])
                st.code(result["key_points"], language=None)
            else:
                st.info("No key points generated.")

    with col_right:
        # Translation
        st.markdown(f"""
        <div class="result-card">
            <h3>🌐 Translation ({target_language})</h3>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(result["translation"])
        st.code(result["translation"], language=None)

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

    # ─── Document Q&A Section ────────────────────────────────────────

    st.markdown("---")
    st.markdown("""
    <div class="qa-header">
        <h3>💬 Ask Questions About This Document</h3>
        <p>Ask in any language — type or speak your question</p>
    </div>
    """, unsafe_allow_html=True)

    # Suggested questions
    if st.session_state.get("suggested_questions"):
        st.markdown("**💡 Suggested questions:**")
        sq_cols = st.columns(min(3, len(st.session_state.suggested_questions)))
        for i, sq in enumerate(st.session_state.suggested_questions):
            with sq_cols[i % 3]:
                if st.button(sq, key=f"sq_{i}", use_container_width=True):
                    with st.spinner("🤔 Thinking..."):
                        sq_answer = answer_question(
                            st.session_state.ocr_text,
                            target_language,
                            question_text=sq,
                        )
                    st.session_state.chat_history.append({"role": "user", "content": sq})
                    st.session_state.chat_history.append({"role": "assistant", "content": sq_answer})
                    st.rerun()

    # Text question input (form allows Enter to submit + auto-clear)
    with st.form("qa_form", clear_on_submit=True):
        user_question = st.text_input(
            "Type your question in any language...",
            placeholder="e.g., What documents are required? / इस फॉर्म में क्या भरना है? / இதில் என்ன நிரப்ப வேண்டும்?",
            label_visibility="collapsed",
        )
        ask_submitted = st.form_submit_button("💬 Ask Question", use_container_width=True)

    if ask_submitted and user_question.strip():
        with st.spinner("🤔 Thinking..."):
            text_answer = answer_question(
                st.session_state.ocr_text,
                target_language,
                question_text=user_question,
            )
        st.session_state.chat_history.append({"role": "user", "content": user_question})
        st.session_state.chat_history.append({"role": "assistant", "content": text_answer})
        st.rerun()

    # Voice question input
    st.markdown(
        '<p style="text-align: center; color: #64748b; margin: 0.5rem 0;">— OR —</p>',
        unsafe_allow_html=True,
    )

    voice_col1, voice_col2 = st.columns([3, 1])
    with voice_col1:
        voice_audio = st.audio_input(
            "🎤 Record your question in any language",
            key="voice_q_input",
        )
    with voice_col2:
        st.markdown("<br>", unsafe_allow_html=True)
        send_voice = st.button("📤 Send", key="send_voice_btn", use_container_width=True)

    if send_voice and voice_audio is not None:
        with st.spinner("🎧 Listening and thinking..."):
            audio_data = voice_audio.read()
            voice_answer = answer_question(
                st.session_state.ocr_text,
                target_language,
                audio_bytes=audio_data,
            )
        st.session_state.chat_history.append({"role": "user", "content": "🎤 Voice question"})
        st.session_state.chat_history.append({"role": "assistant", "content": voice_answer})
        st.rerun()

    # Display conversation history
    if st.session_state.get("chat_history"):
        st.markdown("### 📜 Conversation History")
        for idx, msg in enumerate(st.session_state.chat_history):
            with st.chat_message("user" if msg["role"] == "user" else "assistant"):
                st.markdown(msg["content"])
                if msg["role"] == "assistant":
                    try:
                        ans_audio = text_to_speech(msg["content"], target_language)
                        st.audio(ans_audio, format="audio/mp3")
                    except Exception:
                        pass


# ─── Empty State ──────────────────────────────────────────────────────

elif not (input_image is not None or direct_text_input):
    st.markdown("""
    <div style="text-align: center; padding: 4rem 2rem; color: #9CA3AF;">
        <p style="font-size: 4rem; margin-bottom: 1rem;">📸 / ✍️</p>
        <h3 style="color: #2563EB; font-weight: 500;">Provide an image or text to get started</h3>
        <p style="color: #9CA3AF;">Upload an image, take a photo, or directly paste text you want explained</p>
    </div>
    """, unsafe_allow_html=True)


# ─── Footer ──────────────────────────────────────────────────────────

st.markdown("""
<div class="footer">
    Built By Hemish Jain and Anukool Kashyap
</div>
""", unsafe_allow_html=True)
