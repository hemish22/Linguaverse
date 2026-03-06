# LinguaLens Roadmap

### Phase 17: Redesigning Explanations & Key Points UI
**Status**: ✅ Complete
**Objective**: Redesign the UI to prioritize actionable key points, reduce font size, separate translations, and execute TTS efficiently.
**Depends on**: Phase 16

**Tasks**:
- [x] Modify LLM prompts to output single-liner Key Points and Translations
- [x] Update Streamlit tabs in UI to show Key Points first
- [x] Inject `.small-text` CSS typography
- [x] Split Text-to-Speech logic (Fast Key points, background Detailed Explanation)

**Verification**:
- [x] App runs without error
- [x] All 4 UI changes visible and reactive
