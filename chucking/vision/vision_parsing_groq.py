from groq import Groq
import base64

# Function to encode the image
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

# Path to your image
image_path = "TM_Midea_R291.jpg"

# Getting the base64 string
base64_image = encode_image(image_path)

client = Groq(api_key="api_key")

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": """
Analyze this image thoroughly and provide ALL information contained in it:

1. TEXT EXTRACTION: Extract ALL text exactly as it appears, including:
   - Headings, titles, and subtitles
   - Body text and paragraphs
   - Labels and captions
   - Preserve formatting, line breaks, and structure

2. TABLES: If tables are present:
   - Describe the table structure (rows × columns)
   - Extract ALL cell contents exactly
   - Preserve headers and data relationships
   - Format as structured data

3. DIAGRAMS & CHARTS: If present:
   - Describe the type (flowchart, bar chart, pie chart, etc.)
   - Extract all labels, values, and legends
   - Describe relationships and flow
   - Note any arrows, connections, or hierarchies

Exclude any watermarks or stamps
Be exhaustive and precise. Do not summarize or skip any content.
                """},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}",
                    },
                },
            ],
        }
    ],
    model="openai/gpt-oss-120b",
)

print(chat_completion.choices[0].message.content)