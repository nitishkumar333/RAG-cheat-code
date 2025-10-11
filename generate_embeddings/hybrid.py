from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader, UnstructuredMarkdownLoader
from dotenv import load_dotenv
from langchain.schema import Document
from .models_sql import Document, KnowledgeBase, create_document_with_embeddings, search_documents
from transformers import AutoModelForMaskedLM, AutoTokenizer
from sentence_transformers import SentenceTransformer
from pgvector.sqlalchemy import SparseVector
from typing import List, Tuple
from transformers import AutoTokenizer
from .database import get_db
import os, torch

_dense_tokenizer = None
_dense_model = None
_sparse_tokenizer = None
_sparse_model = None
load_dotenv()

def get_dense_model():
    """Lazy load dense embedding model."""
    global _dense_tokenizer, _dense_model
    if _dense_tokenizer is None:
        _dense_tokenizer = AutoTokenizer.from_pretrained('nomic-ai/nomic-embed-text-v1')
        _dense_model = SentenceTransformer(
            'nomic-ai/nomic-embed-text-v1',
            trust_remote_code=True
        )
    return _dense_tokenizer, _dense_model

def get_sparse_model():
    """Lazy load sparse embedding model."""
    global _sparse_tokenizer, _sparse_model
    if _sparse_tokenizer is None:
        _sparse_tokenizer = AutoTokenizer.from_pretrained(
            'naver/splade-cocondenser-ensembledistil'
        )
        _sparse_model = AutoModelForMaskedLM.from_pretrained(
            'naver/splade-cocondenser-ensembledistil'
        )
        _sparse_model.eval()
    return _sparse_tokenizer, _sparse_model

class HybridEmbeddings:
    def __init__(self, knowledge_base_id=None):
        self.knowledge_base_id = knowledge_base_id
        self.dense_tokenizer, self.dense_model = get_dense_model()
        self.sparse_tokenizer, self.sparse_model = get_sparse_model()
    
    def generate_dense_embedding(self, text):
        embedding = self.dense_model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    def generate_sparse_embedding(self, text):
        with torch.no_grad():
            tokens = self.sparse_tokenizer(
                text, 
                return_tensors='pt', 
                padding=True, 
                truncation=True,
            )
            output = self.sparse_model(**tokens)
            
            # Get the log sum exp of the token predictions
            vec = torch.max(
                torch.log(1 + torch.relu(output.logits)) * tokens.attention_mask.unsqueeze(-1),
                dim=1
            )[0].squeeze()
            # Convert to sparse representation (only non-zero values)
            cols = vec.nonzero().squeeze().cpu().tolist()
            # extract the non-zero values
            weights = vec[cols].cpu().tolist()
            sparse_dict = dict(zip(cols, weights))
            return sparse_dict

    def create_embeddings(self, file=None, file_name=None, file_id=None):
        full_path = os.path.join(os.getcwd(), file_name)

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

        if not file_name or not file_id:
            print("File name or ID is missing.")
            return

        if file_name.endswith('.pdf'):
            try:
                loader = PyPDFLoader(full_path)
            except Exception as e:
                print(e)
        elif file_name.endswith('.txt'):
            loader = TextLoader(file_path=full_path)
        elif file_name.endswith('.md'):
            loader = UnstructuredMarkdownLoader(file_path=full_path)
        else:
            print(f"Unsupported file type for: {file_name}")
            return
        
        documents = loader.load()
        
        # Add metadata
        for doc in documents:
            doc.metadata['unique_pdf_id'] = file_id
            doc.metadata['file_name'] = file_name
        
        splits = text_splitter.split_documents(documents)
        
        print(f"Processing {len(splits)} chunks from {file_name}...")
        
        db = get_db()
        # Process each split and store in database
        for idx, split in enumerate(splits):
            # Create document record
            kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == self.knowledge_base_id).first()
            if not kb:
                raise Exception(status_code=404, detail=f"Knowledge base not found with id {self.knowledge_base_id}")

            dense_vector = self.generate_dense_embedding(split.page_content)
            sparse_vector_dict = self.generate_sparse_embedding(split.page_content)
            sparse_vector = SparseVector(sparse_vector_dict, 30522)

            doc = create_document_with_embeddings(
                db=db,
                knowledge_base_id=self.knowledge_base_id,
                content=split.page_content,
                metadata={
                    **split.metadata,
                    'chunk_index': idx,
                    'total_chunks': len(splits)
                },
                dense_vector=dense_vector,
                sparse_vector=sparse_vector
            )
            
            if (idx + 1) % 10 == 0:
                print(f"  Processed {idx + 1}/{len(splits)} chunks")
        
        print(f"Successfully processed {file_name}")

    def retrieve_from_rag(
        self,
        query: str,
        top_k: int = 4,
        alpha: float = 0.6,
    ) -> List[Tuple['Document', float]]:
        """
        Perform hybrid retrieval combining dense and sparse embeddings.
        
        Args:
            query: Query text string
            top_k: Number of top documents to return (default: 3)
            alpha: Weight for dense vs sparse scores (0-1). 
                alpha=1 means only dense, alpha=0 means only sparse
        """        
        # Generate embeddings from query text
        print(f"Generating embeddings for query: {query[:50]}...")
        dense_embedding = self.generate_dense_embedding(query)
        sparse_embedding = self.generate_sparse_embedding(query)
        
        sparse_vector_str = '{' + ','.join(
            f'{k}:{v}' for k, v in sparse_embedding.items()
        ) + '}/30522'

        docs = search_documents(
            db=get_db(),
            knowledge_base_id=self.knowledge_base_id,
            dense_vector=dense_embedding,
            sparse_vector=sparse_vector_str,
            alpha=alpha,
            top_k=top_k
        )
        return docs

    def delete_pdf(self, unique_pdf_id):
        db = get_db()
        docs = db.query(Document).filter(
        Document.metadata['unique_pdf_id'].astext == unique_pdf_id
        ).all()
        if not docs:
            raise Exception(
                status_code=404, 
                detail=f"No documents found with unique_pdf_id: {unique_pdf_id}"
            )
        count = len(docs)
        for doc in docs:
            db.delete(doc)
        db.commit()
        print(f"Deleted {count} documents for PDF: {unique_pdf_id}")

if '__main__' == __name__:
    t = HybridEmbeddings(knowledge_base_id=1)
    x = t.retrieve_from_rag("Nitish kumars projects")
    print(x)