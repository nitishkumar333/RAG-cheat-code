import base64, os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

class OpenRouterImageAnalyzer:
    def __init__(self, api_key: str, model_name: str = 'qwen/qwen2.5-vl-32b-instruct:free'):
        self.api_key = api_key
        self.model_name = model_name
        self.model = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key,
        )

    def analyze_table(self, image_path: str):
        """
        Analyze the image at the given path with the provided prompt.
        """
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

        if not os.path.exists(image_path):
            return f"Error: Image path not found at '{image_path}'"

        def encode_image(image_path):
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')

        base64_image = encode_image(image_path)
        chat_completion = self.model.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpg;base64,{base64_image}",
                            },
                        },
                    ],
                }
            ],
            model=self.model_name,
        )
        return chat_completion.choices[0].message.content

if __name__ == "__main__":
   image_path = "TM_Midea_R291.jpg"

   analyzer = OpenRouterImageAnalyzer(api_key=os.environ['OPENROUTER_API_KEY'])

   try:
      result = analyzer.analyze_table(image_path)
      print(result)
   except Exception as e:
      print(f"Error: {e}")