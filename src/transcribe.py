import os
import base64
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

# Prepare LLM model
os.environ["GOOGLE_API_KEY"] = ""

if not os.environ["GOOGLE_API_KEY"]:
    print("Error: you need to set GOOGLE_API_KEY environment variable.")
    exit()
model = ChatGoogleGenerativeAI(model="gemini-3-flash-preview")


def transcribe_pdf_file(pdf_file_path):
    """
    Uses Gemini LLM to transcribe a given pdf_file.
    """

    # Prepare the input file
    with open(pdf_file_path, 'rb') as f:
        pdf_file = f.read() # binary data
    pdf_file = base64.b64encode(pdf_file).decode('utf-8')

    # Prepare prompts (system prompt, chat conversation, etc.) 
    messages = [
        (
            "system",
            """
            I will provide you many lectures as PDF files, and I want you to Transcribe the handwritten lecture slide into clean structured markdown.

            Requirements:
            - Preserve mathematical notation using LaTeX ($...$)
            - Keep logical structure (titles, bullet points, sections)
            - Do not summarize or interpret
            - If something is unclear, mark it as [unclear]
            - Also please don't forget to add the "COMP 4107 W2026 Page x" or "*month day* , 2026 | Matthew S. Holden, School of Computer Science, Carleton University | x*", depending on what it is at the bottom of every page as it is in these documents
            """,
        ),
        HumanMessage(
            content=[
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:application/pdf;base64,{pdf_file}" 
                    }
                }
            ],
        )
    ]

    # Invoke the model
    ai_response = model.invoke(messages)

    # Examine the response
    # print(ai_response.text)

    # Write Markdown file
    output_path = os.path.splitext(pdf_file_path)[0]
    output_path = f"{output_path}.md"
    with open(output_path, 'w') as f:
        f.write(ai_response.text)


def transcribe_folder(dir_path):
    for filename in os.listdir(dir_path):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(dir_path, filename)
            transcribe_pdf_file(pdf_path)

if __name__ == "__main__":
    transcribe_folder('data/raw_slides')