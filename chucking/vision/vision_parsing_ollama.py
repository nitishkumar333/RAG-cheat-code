import requests
import base64
import os

def process_image_with_qwen(image_path: str, ollama_url: str = "http://localhost:11434/api/generate"):
    """
    Analyzes a local image using the Qwen-VL model via Ollama to extract all information.

    This function reads an image file, encodes it into base64, and sends it with a
    detailed prompt to the Ollama API. The goal is to get a comprehensive
    description of the image's content, including exact text, parsed tables, and
    descriptions of any diagrams.

    Args:
        image_path (str): The local file path to the image you want to analyze.
        ollama_url (str): The URL of the Ollama API endpoint. Defaults to the standard localhost address.

    Returns:
        str: The detailed analysis from the model. Returns an error message if any step fails.
    """
    # --- 1. Validate the image path ---
    # Check if the file exists at the provided path before proceeding.
    if not os.path.exists(image_path):
        return f"Error: Image path not found at '{image_path}'"

    try:
        # --- 2. Read and encode the image in base64 ---
        # The API requires the image to be sent as a base64 encoded string.
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode('utf-8')

        # --- 3. Construct a detailed prompt ---
        # This prompt guides the model to perform a comprehensive analysis.
        prompt = (
            "You are an expert data extractor. Analyze this image meticulously. "
            "Your task is to extract every piece of information without leaving anything out.\n"
            "1. **Extract All Text:** Transcribe all text verbatim. Preserve the original formatting and line breaks as accurately as possible.\n"
            "2. **Parse Tables:** If you find any tables, extract all their data. Represent the table in a clear, structured format like Markdown. Ensure all headers, rows, and cells are captured correctly.\n"
            "3. **Describe Diagrams and Charts:** If there are diagrams, flowcharts, or graphs, describe them in detail. Explain their components, the relationships between them, and the information they are designed to convey.\n"
            "Provide a complete and exhaustive output of the image content."
        )

        # --- 4. Prepare the payload for the Ollama API ---
        payload = {
            "model": "qwen2.5vl:7b",
            "prompt": prompt,
            "images": [encoded_image],
            "stream": False  # Get the full response at once
        }

        # --- 5. Send the request to the Ollama API ---
        # Using a timeout is good practice for network requests.
        print("Sending request to Ollama... This may take a moment.")
        response = requests.post(ollama_url, json=payload, timeout=300)
        response.raise_for_status()  # This will raise an HTTPError for bad responses (4xx or 5xx)

        # --- 6. Parse and return the response ---
        response_data = response.json()
        return response_data.get('response', 'Error: Could not find "response" key in the API output.')

    except requests.exceptions.RequestException as e:
        return (f"Error: An issue occurred with the API request. Please ensure Ollama is running.\nDetails: {e}")
    except FileNotFoundError:
        return f"Error: The file at {image_path} was not found."
    except Exception as e:
        return f"An unexpected error occurred: {e}"

if __name__ == '__main__':
    # --- Instructions for Use ---
    # 1. Ensure Ollama is running on your machine.
    # 2. Pull the required model by running this command in your terminal:
    #    ollama pull qwen2.5vl:7b
    # 3. Place an image you want to analyze (e.g., 'my_diagram.png') in a known directory.
    # 4. Update the 'image_to_process' variable below with the correct path to your image file.

    image_to_process = "./TM_Midea_R291.jpg" 

    print(f"Attempting to process image: {image_to_process}")

    # A simple check to see if the user has updated the placeholder path.
    if "path/to/your/image.png" in image_to_process or not os.path.exists(image_to_process):
        print("!!!PLEASE UPDATE the 'image_to_process' variable inside!!!")
    else:
        # Call the function to get the analysis from the model
        analysis_result = process_image_with_qwen(image_to_process)

        # Print the final result
        print("\n--- Model Analysis Result ---")
        print(analysis_result)
        print("-" * 50)
