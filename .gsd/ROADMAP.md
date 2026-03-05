# ROADMAP.md

> **Current Phase**: All complete
> **Milestone**: v1.0 — Working Prototype ✅

## Must-Haves (from SPEC)

- [x] OCR text extraction from images
- [x] LLM-powered simplification and explanation
- [x] Multilingual translation (English, Hindi, Tamil)
- [x] Streamlit UI with upload + webcam
- [x] Clean modular project structure

## Phases

### Phase 1: Project Scaffolding & OCR Module
**Status**: ✅ Complete
**Objective**: Set up project structure, dependencies, and build the OCR extraction module
**Deliverables**:
- `requirements.txt` with all dependencies
- `ocr_module.py` with `extract_text()` function using EasyOCR
- `utils.py` with shared utilities (image processing, config loading)
- Basic project structure in place

### Phase 2: LLM Processing Module
**Status**: ✅ Complete
**Objective**: Build the LLM interaction module for text simplification, explanation, and translation
**Deliverables**:
- `llm_module.py` with functions for simplification and translation
- Prompt templates for explanation generation
- Gemini API integration with error handling
- `.env` configuration for API keys

### Phase 3: Streamlit UI & Integration
**Status**: ✅ Complete
**Objective**: Build the complete Streamlit frontend and wire all modules together
**Deliverables**:
- `app.py` — full Streamlit application
- Image upload and webcam capture
- Language selection dropdown
- Display panels for extracted text, explanation, and translation
- Optional TTS playback with gTTS

### Phase 4: Polish & Documentation
**Status**: ✅ Complete
**Objective**: Final testing, error handling improvements, README, and run instructions
**Deliverables**:
- README.md with setup and run instructions
- Error handling for edge cases (no text found, API failures)
- Code comments and docstrings
- Final verification of end-to-end flow

### Phase 5: UI Polish — Color Scheme & Image Preview
**Status**: ✅ Complete
**Objective**: Apply branded color scheme and reduce image preview size
**Depends on**: Phase 3
**Deliverables**:
- New color palette: Deep Blue #1E3A8A, Teal #14B8A6, Soft Orange #F59E0B, Light Gray #F8FAFC, Dark Gray #1F2937
- Reduced image preview (max 400px width, 300px height)
- Updated sidebar, header, buttons, and result cards to match palette

### Phase 6: UI/UX Pro Max Refinement
**Status**: ✅ Complete
**Objective**: Improve the look of the website using the ui-ux-pro-max skill guidelines
**Depends on**: Phase 5

**Tasks**:
- [x] Run ui-ux-pro-max search to generate a premium design system
- [x] Implement recommended styles, typography, and UX best practices in Streamlit CSS
- [x] Add animations and hover effects per guidelines
- [x] Verify accessibility requirements

**Verification**:
- Verify design matches premium Pro Max standards

### Phase 8: Native Theming & Deployment
**Status**: ✅ Complete
**Objective**: Fix Streamlit dark mode fallback and deploy code to GitHub.
**Depends on**: Phase 7

**Tasks**:
- [ ] Create `.streamlit/config.toml` to enforce light theme
- [ ] Simplify `app.py` CSS to rely on native theming for the sidebar and widgets
- [ ] Initialize Git remote to `https://github.com/hemish22/Linguaverse.git`
- [ ] Push codebase to `main` branch

**Verification**:
- UI correctly renders the uploader and sidebar in the intended light palette.
- Code successfully pushed to GitHub.

### Phase 9: Lazy Camera Activation
**Status**: ✅ Complete
**Objective**: Prevent `st.camera_input` from automatically asking for camera permissions on page load.
**Depends on**: Phase 8

**Tasks**:
- [x] Wrap `st.camera_input` in an `st.toggle` within the Webcam tab.
- [x] Commit and push fix to GitHub

**Verification**:
- The browser no longer requests camera access until the user explicitly toggles it on.
