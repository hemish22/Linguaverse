### Phase 22: LLM Prompt Formatting & Readability Overhaul
**Status**: ✅ Complete

### Phase 21: Numbered List Strict Parsing
**Status**: ✅ Complete

### Phase 20: Typography Optimization & Regex Tuning
**Status**: ✅ Complete

### Phase 19: Strict Fallback Newline Parsing
**Status**: ✅ Complete

### Phase 18: Layout Streamlining & Language Localization
**Status**: ✅ Complete

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
---

### Phase 18: Layout Streamlining & Language Localization
**Status**: ⬜ Not Started
**Objective**: Clean up repetitive text (code blocks vs markdown), enforce newline rendering for LLM points, strip original language if translated language is selected, and shrink the audio player UI.
**Depends on**: Phase 17

**Tasks**:
- [ ] TBD (run /plan 18 to create)

**Verification**:
- TBD
---

### Phase 19: Strict Fallback Newline Parsing
**Status**: ⬜ Not Started
**Objective**: Force bullet points to render on new lines by injecting double newlines () via regex during the parsing step, overriding unpredictable LLM whitespace formatting.
**Depends on**: Phase 18

**Tasks**:
- [ ] TBD (run /plan 19 to create)

**Verification**:
- TBD
---

### Phase 19: Strict Fallback Newline Parsing
**Status**: ⬜ Not Started
**Objective**: Force bullet points to render on new lines by injecting double newlines via regex.
**Depends on**: Phase 18

**Tasks**:
- [ ] TBD (run /plan 19 to create)

**Verification**:
- TBD
---

### Phase 20: Typography Optimization & Regex Tuning
**Status**: ⬜ Not Started
**Objective**: Increase the font size of the output for better readability, and fix the aggressive bullet regex that is splitting sentences in half.
**Depends on**: Phase 19

**Tasks**:
- [ ] TBD (run /plan 20 to create)

**Verification**:
- TBD
---

### Phase 21: Numbered List Strict Parsing
**Status**: ⬜ Not Started
**Objective**: Force the LLM's inline generated numbered lists to render on separate lines using a targeted regex that avoids mid-sentence character breaks.
**Depends on**: Phase 20

**Tasks**:
- [ ] TBD (run /plan 21 to create)

**Verification**:
- TBD
---

### Phase 22: LLM Prompt Formatting & Readability Overhaul
**Status**: ⬜ Not Started
**Objective**: Redesign the LLM prompt to output highly structured, scannable text with icons, dedicated sections (Summary, Key Points, Steps, Notes), and shorter sentences to drastically improve readability.
**Depends on**: Phase 21

**Tasks**:
- [ ] TBD (run /plan 22 to create)

**Verification**:
- TBD
