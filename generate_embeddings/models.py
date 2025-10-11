from datetime import datetime
from typing import Dict, Any, List
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, ForeignKey, Index
)
from sqlalchemy.orm import relationship, declarative_base, Session
from sqlalchemy.dialects.postgresql import JSONB
from pgvector.sqlalchemy import Vector, SparseVector
from pydantic import BaseModel

Base = declarative_base()

class KnowledgeBase(Base):
    __tablename__ = "knowledge_bases"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    documents = relationship("Document", back_populates="knowledge_base", cascade="all, delete-orphan")


class Document(Base):
    __tablename__ = "home_document"
    
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    metadata = Column(JSONB, default=dict)
    knowledge_base_id = Column(Integer, ForeignKey("knowledge_bases.id", ondelete="CASCADE"), nullable=True)
    
    knowledge_base = relationship("KnowledgeBase", back_populates="documents")
    dense_embedding = relationship("DenseEmbedding", back_populates="document", uselist=False, cascade="all, delete-orphan")
    sparse_embedding = relationship("SparseEmbedding", back_populates="document", uselist=False, cascade="all, delete-orphan")


class DenseEmbedding(Base):
    __tablename__ = "dense_embeddings"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("home_document.id", ondelete="CASCADE"), unique=True, nullable=False)
    embedding = Column(Vector(768), nullable=False)
    model_name = Column(String(255), default="nomic-ai/nomic-embed-text-v1")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    document = relationship("Document", back_populates="dense_embedding")
    
    __table_args__ = (
        Index(
            'dense_embedding_hnsw_idx',
            'embedding',
            postgresql_using='hnsw',
            postgresql_with={'m': 16, 'ef_construction': 64},
            postgresql_ops={'embedding': 'vector_cosine_ops'}
        ),
    )


class SparseEmbedding(Base):
    __tablename__ = "sparse_embeddings"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("home_document.id", ondelete="CASCADE"), unique=True, nullable=False)
    embedding = Column(SparseVector(30522), nullable=False)
    model_name = Column(String(255), default="naver/splade-cocondenser-ensembledistil")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    document = relationship("Document", back_populates="sparse_embedding")
    
    __table_args__ = (
        Index('sparse_embedding_idx', 'embedding'),
    )

def create_document_with_embeddings(
    db: Session,
    knowledge_base_id: int,
    content: str,
    metadata: Dict[str, Any],
    dense_vector: List[float],
    sparse_vector: Dict[int, float]
):
    # Create document
    doc_record = Document(
        knowledge_base_id=knowledge_base_id,
        content=content,
        metadata=metadata
    )
    db.add(doc_record)
    db.flush()  # Get the ID without committing
    
    # Create dense embedding
    dense_emb = DenseEmbedding(
        document_id=doc_record.id,
        embedding=dense_vector
    )
    db.add(dense_emb)
    
    # Create sparse embedding
    sparse_emb = SparseEmbedding(
        document_id=doc_record.id,
        embedding=sparse_vector
    )
    db.add(sparse_emb)
    
    db.commit()
    db.refresh(doc_record)
    return doc_record

class SearchResult(BaseModel):
    document_id: int
    combined_score: float
    content: str
    metadata: Dict[str, Any]

# Search function (equivalent to your Django query)
def search_documents(
    db: Session,
    knowledge_base_id: int,
    dense_vector: List[float],
    sparse_vector: str,  # Format: "{1:0.5,10:0.3,...}"
    alpha: float = 0.5,
    top_k: int = 5
) -> List[SearchResult]:
    query_sql = """
        WITH dense_scores AS (
            SELECT 
                de.document_id,
                1 - (de.embedding <=> :dense_vector::vector) AS dense_score
            FROM dense_embeddings de
            JOIN home_document d ON de.document_id = d.id
            WHERE d.knowledge_base_id = :kb_id_dense
        ),
        sparse_scores AS (
            SELECT 
                se.document_id,
                se.embedding <#> :sparse_vector::sparsevec AS sparse_score
            FROM sparse_embeddings se
            JOIN home_document d ON se.document_id = d.id
            WHERE d.knowledge_base_id = :kb_id_sparse
        ),
        combined_scores AS (
            SELECT 
                COALESCE(ds.document_id, ss.document_id) AS document_id,
                (COALESCE(ds.dense_score, 0) * :alpha1 + 
                COALESCE(ss.sparse_score, 0) * (1 - :alpha2)) AS combined_score
            FROM dense_scores ds
            FULL OUTER JOIN sparse_scores ss ON ds.document_id = ss.document_id
        )
        SELECT document_id, combined_score
        FROM combined_scores
        ORDER BY combined_score DESC
        LIMIT :limit
    """
    
    result = db.execute(
        query_sql,
        {
            "dense_vector": str(dense_vector),
            "kb_id_dense": knowledge_base_id,
            "sparse_vector": sparse_vector,
            "kb_id_sparse": knowledge_base_id,
            "alpha1": alpha,
            "alpha2": alpha,
            "limit": top_k
        }
    )
    
    rows = result.fetchall()
    document_ids = [row[0] for row in rows]
    scores = {row[0]: row[1] for row in rows}
    
    # Fetch documents
    documents = db.query(Document).filter(Document.id.in_(document_ids)).all()
    
    # Create response with scores
    results = [
        SearchResult(
            document_id=doc.id,
            combined_score=scores[doc.id],
            content=doc.content,
            metadata=doc.metadata
        )
        for doc in documents
    ]
    
    # Sort by score
    results.sort(key=lambda x: x.combined_score, reverse=True)
    return results