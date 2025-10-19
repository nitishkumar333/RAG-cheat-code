import time
from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
import google.generativeai as genai

class ContextualRetrieval:
    def __init__(self, full_document: str, api_key: str, model_name: str = 'gemini-2.5-flash'):
        """
        Initialize the ContextualRetrieval system.
        """
        self.model_name = model_name
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=100,
        )
        self.full_document = full_document
        genai.configure(api_key=api_key)
        self.llm = genai.GenerativeModel(self.model_name)
    
    def process_document(self) -> List[Document]:
        """
        Process a document by splitting it into chunks and generating context for each chunk.
        """
        chunks = self.text_splitter.create_documents([self.full_document])
        contextualized_chunks = self._generate_contextualized_chunks(chunks)
        return contextualized_chunks

    def _generate_contextualized_chunks(self, chunks: List[Document]) -> List[Document]:
        """
        Generate contextualized versions of the given chunks.
        """
        contextualized_chunks = []
        for chunk in chunks:
            context = self._generate_context(chunk.page_content)
            contextualized_content = f"{context}\n\n{chunk.page_content}"
            contextualized_chunks.append(Document(page_content=contextualized_content, metadata=chunk.metadata))
        return contextualized_chunks

    def _generate_context(self, chunk: str) -> str:
        """
        Generate context for a specific chunk using the language model.
        """
        prompt = f"""
        You are an AI assistant specializing in analysis. Your task is to provide brief, relevant context for a chunk of text from the whole document.
        <document>
        {self.full_document}
        </document>

        Here is the chunk to situate within the whole document::
        <chunk>
        {chunk}
        </chunk>

        Provide a concise context (3-4 sentences) for this chunk, considering the following guidelines:
        1. If applicable, mention any relevant time periods or comparison.
        2. If applicable, note how this information relates to overall document.
        3. Include any key figures or percentages that provide important context.
        4. Do not use phrases like "This chunk discusses" or "This section provides". Instead, directly state the context.

        Please give a short succinct context to situate this chunk within the overall document for the purposes of improving search retrieval of the chunk. Answer only with the succinct context and nothing else.

        Context:
        """
        response = self.llm.generate_content(prompt)
        return response.text