from pdf2image import convert_from_path
import os, time, tempfile, shutil
from fastapi.responses import JSONResponse
from vision.gemini_parsing import GeminiImageAnalyzer
from chunking.contextualize_chunks import ContextualRetrieval
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="PDF Processing API")
origins = [
    "http://localhost:5173",  # Vite default
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],       # allow all methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],       # allow all headers
)

@app.post("/pdf-chunks")
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
            pages = convert_from_path(pdf_path, poppler_path="C:\\Users\\aenit\\Downloads\\Release-25.07.0-0\\poppler-25.07.0\\Library\\bin")
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
            return JSONResponse(content={"status": "success", "chunks": [
                {"page_content": c.page_content, "metadata": c.metadata}
                for c in chunks
            ]})

        except Exception as e:
            print(e)
            raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def health():
    return JSONResponse("Working")