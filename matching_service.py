"""
Matching service for ranking applicants against job descriptions
Uses SentenceTransformer embeddings and hybrid scoring (70% cosine + 30% BM25)
"""
import chromadb
from chromadb.utils import embedding_functions
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from rank_bm25 import BM25Okapi
import numpy as np
import os
from typing import List, Tuple, Dict

class MatchingService:
    def __init__(self, chroma_path='chroma_storage'):
        """Initialize matching service"""
        self.chroma_path = chroma_path
        self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        self.client = chromadb.PersistentClient(path=chroma_path)
        
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
        try:
            self.resumes_collection = self.client.get_collection(
                name="resumes",
                embedding_function=self.embedding_function
            )
        except:
            self.resumes_collection = self.client.create_collection(
                name="resumes",
                embedding_function=self.embedding_function
            )
        
        try:
            self.jobs_collection = self.client.get_collection(
                name="jobs",
                embedding_function=self.embedding_function
            )
        except:
            self.jobs_collection = self.client.create_collection(
                name="jobs",
                embedding_function=self.embedding_function
            )
    
    def add_resume_to_db(self, user_id: int, resume_text: str):
        """Add resume to ChromaDB"""
        try:
            self.resumes_collection.upsert(
                documents=[resume_text],
                ids=[f"user_{user_id}"],
                metadatas=[{"user_id": user_id}]
            )
            return True
        except Exception as e:
            print(f"Error adding resume to ChromaDB: {e}")
            return False
    
    def add_job_to_db(self, job_id: int, job_description: str, job_role: str):
        """Add job to ChromaDB"""
        try:
            full_text = f"{job_role} {job_description}"
            self.jobs_collection.upsert(
                documents=[full_text],
                ids=[f"job_{job_id}"],
                metadatas=[{"job_id": job_id, "role": job_role}]
            )
            return True
        except Exception as e:
            print(f"Error adding job to ChromaDB: {e}")
            return False
    
    def rank_applicants_for_job(self, job_description: str, job_role: str, 
                                applications: List) -> List[Tuple[int, float]]:
        """
        Rank applicants using hybrid scoring (70% cosine + 30% BM25)
        """
        if not applications:
            return []
        
        job_query = f"{job_role} {job_description}"
        resume_texts = [app.resume_text for app in applications]
        app_ids = [app.id for app in applications]
        
        cosine_scores = self._get_cosine_similarity_scores(job_query, resume_texts)
        bm25_scores = self._get_bm25_scores(job_query, resume_texts)
        
        cosine_scores_norm = self._normalize_scores(cosine_scores)
        bm25_scores_norm = self._normalize_scores(bm25_scores)
        
        final_scores = [
            (0.7 * cos + 0.3 * bm25) * 100
            for cos, bm25 in zip(cosine_scores_norm, bm25_scores_norm)
        ]
        
        rankings = list(zip(app_ids, final_scores))
        rankings.sort(key=lambda x: x[1], reverse=True)
        
        return rankings
    
    def _get_cosine_similarity_scores(self, query: str, documents: List[str]) -> List[float]:
        """Get cosine similarity scores"""
        try:
            query_embedding = self.model.encode([query])
            doc_embeddings = self.model.encode(documents)
            similarities = cosine_similarity(query_embedding, doc_embeddings)[0]
            return similarities.tolist()
        except Exception as e:
            print(f"Error getting cosine similarity scores: {e}")
            return [0.5] * len(documents)
    
    def _get_bm25_scores(self, query: str, documents: List[str]) -> List[float]:
        """Get BM25 scores"""
        try:
            tokenized_corpus = [doc.lower().split() for doc in documents]
            tokenized_query = query.lower().split()
            bm25 = BM25Okapi(tokenized_corpus)
            scores = bm25.get_scores(tokenized_query)
            return scores.tolist()
        except Exception as e:
            print(f"Error getting BM25 scores: {e}")
            return [0] * len(documents)
    
    def _normalize_scores(self, scores: List[float]) -> List[float]:
        """Normalize scores to 0-1"""
        if not scores or max(scores) == min(scores):
            return [0.5] * len(scores)
        
        min_score = min(scores)
        max_score = max(scores)
        normalized = [(s - min_score) / (max_score - min_score) for s in scores]
        return normalized
    
    def get_top_jobs_for_resume(self, resume_text: str, all_jobs: List, 
                                top_n: int = 3) -> List[Tuple[int, float]]:
        """Get top job matches for resume"""
        if not all_jobs:
            return []
        
        job_texts = [f"{job.role} {job.description}" for job in all_jobs]
        job_ids = [job.id for job in all_jobs]
        
        cosine_scores = self._get_cosine_similarity_scores(resume_text, job_texts)
        bm25_scores = self._get_bm25_scores(resume_text, job_texts)
        
        cosine_scores_norm = self._normalize_scores(cosine_scores)
        bm25_scores_norm = self._normalize_scores(bm25_scores)
        
        final_scores = [
            (0.7 * cos + 0.3 * bm25) * 100
            for cos, bm25 in zip(cosine_scores_norm, bm25_scores_norm)
        ]
        
        rankings = list(zip(job_ids, final_scores))
        rankings.sort(key=lambda x: x[1], reverse=True)
        
        return rankings[:top_n]


_matching_service = None

def get_matching_service(chroma_path='chroma_storage') -> MatchingService:
    """Get or create singleton"""
    global _matching_service
    if _matching_service is None:
        _matching_service = MatchingService(chroma_path)
    return _matching_service