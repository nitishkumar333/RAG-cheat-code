import datetime
from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain.prompts import ChatPromptTemplate
import google.generativeai as genai

class ContextualRetrieval:
    def __init__(self, full_document: str, api_key: str, model_name: str = 'gemini-2.5-pro'):
        """
        Initialize the ContextualRetrieval system.
        """
        self.model_name = model_name
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=100,
        )
        genai.configure(api_key=api_key)
        self.llm = self.generate_cache_model(full_document)
    
    def process_document(self, document: str) -> List[Document]:
        """
        Process a document by splitting it into chunks and generating context for each chunk.
        """
        chunks = self.text_splitter.create_documents([document])
        contextualized_chunks = self._generate_contextualized_chunks(document, chunks)
        return contextualized_chunks

    def _generate_contextualized_chunks(self, document: str, chunks: List[Document]) -> List[Document]:
        """
        Generate contextualized versions of the given chunks.
        """
        contextualized_chunks = []
        for chunk in chunks:
            context = self._generate_context(document, chunk.page_content)
            contextualized_content = f"{context}\n\n{chunk.page_content}"
            contextualized_chunks.append(Document(page_content=contextualized_content, metadata=chunk.metadata))
        return contextualized_chunks

    def _generate_context(self, chunk: str) -> str:
        """
        Generate context for a specific chunk using the language model.
        """
        prompt = ChatPromptTemplate.from_template("""
        Here is the chunk to situate within the whole document::
        <chunk>
        {chunk}
        </chunk>
        """)
        messages = prompt.format_messages(chunk=chunk)
        response = self.llm.generate_content(messages)
        return response.text

    def generate_cache_model(self, full_document):
        """
        Generate a cache for a document.
        """
        try:
            print(f"Creating cache for model: {self.model_name}...")
            expiration_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=50)
            cache = genai.caching.CachedContent.create(
                model=self.model_name,
                system_instruction=f"""You are an AI assistant specializing in analysis. Your task is to provide brief, relevant context for a chunk of text from the whole document.
                <document>
                {full_document}
                </document>

                Situate the chuck provide by the user within the whole document.

                Provide a concise context (2-3 sentences) for this chunk, considering the following guidelines:
                1. If applicable, mention any relevant time periods or comparison.
                2. If applicable, note how this information relates to overall document.
                3. Include any key figures or percentages that provide important context.
                4. Do not use phrases like "This chunk discusses" or "This section provides". Instead, directly state the context.

                Please give a short succinct context to situate this chunk within the overall document for the purposes of improving search retrieval of the chunk. Answer only with the succinct context and nothing else.

                Context:
                """,
                ttl=expiration_time,
            )
            print(f"Cache created successfully: {cache.name}")
            print(f"This cache will expire at: {cache.expire_time.isoformat()}")
            model = genai.GenerativeModel.from_cached_content(cached_content=cache)
        finally:
            if cache:
                print(f"Deleting cache: {cache.name}")
                cache.delete()
                print("Cache deleted.")
        return model