# OCR Comparison Round 2

## Data
Slides from COMP 4107 lecture (January 5, 2026), focusing on text-heavy and diagram-based slides.

## Observations

### Tesseract
- Struggles with layout and structured elements (e.g., Venn diagram content)
- Misses or truncates important text
- Introduces noise and formatting inconsistencies

Example:
"Attificial neural networks are machine learning models..."
:contentReference[oaicite:0]{index=0}

### Gemini
- Accurately captures full text content
- Successfully reconstructs structured information (e.g., Venn diagram relationships)
- Produces clean, readable markdown

Example:
- AI contains ML, which contains NN/DL
- DS overlaps with AI/ML

## Conclusion
Across both mathematical and text-heavy slides, Gemini consistently produces higher-quality, structured, and usable outputs compared to Tesseract.

Gemini is selected as the OCR method for downstream processing.