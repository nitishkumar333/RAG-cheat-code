import google.generativeai as genai
from PIL import Image

genai.configure(api_key="api_key")

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
Analyze this image thoroughly and provide ALL information contained in it:

TEXT EXTRACTION: Extract ALL text exactly as it appears, including:
   - Headings, titles, and subtitles
   - Body text and paragraphs
   - Labels and captions
   - Preserve formatting, line breaks, and structure

TABLES: If tables are present:
   - Describe the table structure (rows × columns)
   - Preserve headers and data relationships
   - Fill the cells where needed, don't left cells empty. Each row and coloumn should be complete even if data is repeating.
   - Format as structured markdown

DIAGRAMS & CHARTS: If present:
   - Extract all labels, values, and legends
   - Describe relationships and flow
   - Complete Information they convey

Exclude any watermarks or stamps.
Do not summarize or skip any content.
"""

# --- Model Interaction ---
# Initialize the Gemini 1.5 Pro model
# 'gemini-1.5-pro-latest' is excellent for multimodal tasks (text and images)
model = genai.GenerativeModel('gemini-2.5-pro')

# The model takes a list containing the prompt and the image object(s)
response = model.generate_content([prompt, img])


# --- Output ---
# Print the extracted text from the model's response
print(response.text)