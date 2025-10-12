from pdf2image import convert_from_path
import os
from vision.gemini_parsing import GeminiImageAnalyzer

def process_pdf(pdf_path, output_dir="pdf_images"):
    os.makedirs(output_dir, exist_ok=True)
    pages = convert_from_path(pdf_path, poppler_path="C:\\Users\\aenit\\Downloads\\Release-25.07.0-0\\poppler-25.07.0\\Library\\bin")
    results = []

    for i, page in enumerate(pages, start=1):
        image_path = os.path.join(output_dir, f"page_{i}.png")
        page.save(image_path, "png")

        try:
            analyzer = GeminiImageAnalyzer(os.environ['GEMINI_API_KEY'])
            result = analyzer.analyze_table(image_path)
            results.append(result)
        finally:
            if os.path.exists(image_path):
                os.remove(image_path)
                print(f"[CLEANUP] Deleted temporary file: {image_path}")

        print(f"[INFO] Processed page {i}")

    # Optional: Remove the folder if it's empty
    if not os.listdir(output_dir):
        os.rmdir(output_dir)
        print(f"[CLEANUP] Removed empty folder: {output_dir}")

    return results

print(process_pdf("temp.pdf"))