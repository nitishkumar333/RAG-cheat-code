from pdf2image import convert_from_path
import os, time, tempfile, shutil
from fastapi.responses import JSONResponse
from vision.gemini_parsing import GeminiImageAnalyzer
from chunking.contextualize_chunks import ContextualRetrieval
from fastapi import FastAPI, UploadFile, File, HTTPException

app = FastAPI(title="PDF Processing API")

@app.post("/process-pdf")
async def process_pdf(file: UploadFile = File(...)):

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        pdf_path = os.path.join(tmp_dir, file.filename)
        with open(pdf_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        output_dir = os.path.join(tmp_dir, "pdf_images")
        os.makedirs(output_dir, exist_ok=True)
        try:
            # Convert PDF to images
            pages = convert_from_path(pdf_path)
            results = []
            for i, page in enumerate(pages, start=1):
                image_path = os.path.join(output_dir, f"page_{i}.png")
                page.save(image_path, "png")
                analyzer = GeminiImageAnalyzer(os.environ['GEMINI_API_KEY'])
                result = analyzer.analyze_table(image_path)
                results.append(result)

                if os.path.exists(image_path):
                    os.remove(image_path)

                time.sleep(15)
                print(f"[INFO] Processed and removed page {i} image")

            # Combine text and contextualize
            full_doc = " ".join(results)
            chunker = ContextualRetrieval(full_document=full_doc, api_key=os.environ['GEMINI_API_KEY'])
            chunks = chunker.process_document()
            return JSONResponse(content={"status": "success", "chunks": chunks})

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def health():
    return JSONResponse("Working")