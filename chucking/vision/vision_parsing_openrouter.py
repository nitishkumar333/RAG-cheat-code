import base64, os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ['OPENROUTER_API_KEY'],
)

# Path to your local image
image_path = "TM_Midea_R291.jpg"

# Read and encode the image to base64
with open(image_path, "rb") as f:
    image_bytes = f.read()
    base64_image = base64.b64encode(image_bytes).decode("utf-8")

# Create the data URL for the image
image_data_url = f"data:image/jpg;base64,{base64_image}"

# Send it to the model
completion = client.chat.completions.create(
    model="qwen/qwen2.5-vl-32b-instruct:free",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": """
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

When you output the recreated document, present it as a single continuous Markdown document that follows these rules exactly."""},
                {"type": "image_url", "image_url": {"url": image_data_url}},
            ],
        }
    ],
)

print(completion.choices[0].message.content)
