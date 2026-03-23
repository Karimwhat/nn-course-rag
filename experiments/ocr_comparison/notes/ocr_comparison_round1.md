# OCR Comparison Round 1

## Goal
Compare Tesseract and Gemini OCR on handwritten COMP 4107 lecture slides to determine which produces more usable text for downstream RAG tasks.

## Data
Test pages stored in:
- `experiments/ocr_comparison/input_pages/`

Outputs stored in:
- `experiments/ocr_comparison/tesseract_output/`
- `experiments/ocr_comparison/gemini_output/`

## Methods

### Tesseract
Traditional OCR run locally on slide images.

### Gemini
LLM-based OCR prompted to transcribe handwritten slide content into structured markdown with LaTeX for mathematical notation.

## Observations

### Tesseract
- Struggles significantly with handwriting
- Frequently corrupts mathematical notation
- Produces noisy text that is difficult to use directly for retrieval

### Gemini
- Produces much cleaner transcription
- Preserves most mathematical content in LaTeX form
- Maintains logical meaning even when exact visual spacing differs from the original slide

## Formatting Note
Gemini does not always preserve the exact spatial layout or line spacing of the original handwritten slide. However, the resulting transcription remains semantically correct and logically structured, which is more important for downstream embedding and retrieval tasks.

## Preliminary Conclusion
Gemini OCR appears substantially more suitable than Tesseract for converting handwritten neural network lecture slides into text for later chunking, embedding, and retrieval.