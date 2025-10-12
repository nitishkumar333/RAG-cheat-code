import google.generativeai as genai
from PIL import Image
from dotenv import load_dotenv
import os
load_dotenv()

genai.configure(api_key=os.environ['GEMINI_API_KEY'])

# --- Image and Prompt Definition ---
# Path to your image
image_path = "TM_Midea_R291.jpg"

# Open the image file
try:
    img = Image.open(image_path)
except FileNotFoundError:
    print(f"Error: The file '{image_path}' was not found. Please check the path.")
    exit()

# The text prompt remains the same
prompt = """
## Guidelines

1. **Tables**
   Analyze the tables and reconstruct it with more clear headings, relationships and context. Remove any grouped headers and make it flattened with single-level headers. Also, prefill any empty cell. You can add or remove any column in the table to make the data more clear.

2. **Textual Content**
   Transcribe **ALL** text verbatim. This includes titles, headings, paragraphs, lists, captions, and any other text. Faithfully preserve all original formatting such as **bolding**, *italics*, *underlining*, and specific line breaks.

3. **Visual Elements (Diagrams, Charts, Graphs)**
   Where a visual element appears in the original, replace it with a comprehensive and descriptive paragraph. This description must detail all labels, values, connections, flows, and the core information the visual is conveying.

## Crucial Constraints

**NO Analytical Headings:** Do not use sections or headings like "Text Extraction," "Table Analysis," or "Diagram Description." The entire response must be a single, flowing document.
**Completeness:** Be exhaustive. Do not summarize, omit, or paraphrase any content.
**Exclusions:** Ignore any watermarks, logos, page artifacts, page number or stamps that are not part of the original document's content.

When you output the recreated document, present it as a single continuous Markdown document that follows these rules exactly.
"""

model = genai.GenerativeModel('gemini-2.5-pro')

response = model.generate_content([prompt, img])

print(response.text)