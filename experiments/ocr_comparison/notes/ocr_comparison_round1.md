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

I wanted to test a traditional OCR and a modern LLM-based OCR method. My hypothesis was that the LLM OCR would outperform the traditional OCR, but perhaps would be slower than a traditional OCR.

The other challenge for traditional OCR is struggling with handwritten notes. My choice of OCR methods to compare will be based on established OCR benchmarks (due to time limitation, I couldn't write my own, as it is not the major focus of my project). 

I chose to test the following OCR methods because scored high on the following established OCR benchmarks: 
 - https://github.com/getomni-ai/benchmark
 - https://aimultiple.com/ocr-accuracy
 - https://www.dataunboxed.io/blog/ocr-vs-vlm-ocr-naive-benchmarking-accuracy-for-scanned-documents


My choice was to compare Tesseract (traditional OCR) vs. Gemini 3 Flash (modern LLM-based OCR).

### Tesseract

Install tesseract using one of the methods described in https://tesseract-ocr.github.io/tessdoc/Installation.html 

#### Command

In the terminal, run: 

```sh
cd experiments/ocr_comparison/input_pages
tesseract './2026-x-x slide x.png' slidex 
```

where "2026-x-x slide x.png" is the specific slide image, and slidex is the output txt file name.

### Gemini 3 Flash 
LLM-based OCR prompted to transcribe handwritten slide content into structured markdown with LaTeX for mathematical notation.

#### Prompt used
Initially:

```
Transcribe the handwritten lecture slide exactly into clean text.
Preserve:
- mathematical notation
- bullet points
- structure

Do not summarize. Only transcribe the content accurately.

If something is unclear, mark it as [unclear].
```

#### Later on:

Changed due to the ocr output not matching the lecture structure, such as having multiple bullet points within the same line, opposite to what would be written in the slides.

```
I will provide you many PDF lectures prompt by prompt, and I want you to 
Transcribe the handwritten lecture slide into clean structured markdown.

Requirements:
- Preserve mathematical notation using LaTeX ($...$)
- Keep logical structure (titles, bullet points, sections)
- Do not summarize or interpret
- If something is unclear, mark it as [unclear]
```

#### Later on again
I needed a marker phrase to use as a boundary to split pages cleanly for RAG chunking. So this was appended to the prompt:

```
(Also please don't forget to add the "COMP 4107 W2026 Page x" at the bottom of every page as it is in these documents, and not only do that in the very last page of your markdown)
```

For the most part, the LLM was able to insert this marker with a consistent format. (Manual changes/additions/deletions were needed in a few cases)

#### Command

To run the transcription on the PDF slides:
1. Login to Carleton ... to fetch the slides into `data/raw_slides` dir.
2. Install dependencies:

```sh
pip install -r src/requirements.txt
```
3. Set the `GOOGLE_API_KEY` environment variable using your Gemini API key. Obtain your key from https://aistudio.google.com/

4. Run the script:

```sh
python src/transcribe.py
```

This will iterate over the pdf files in the `data/raw_slides` folder and transcribe each PDF into a markdown `.md` file.

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