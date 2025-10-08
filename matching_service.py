"""
Matching service for ranking applicants against job descriptions
Uses SentenceTransformer embeddings and hybrid scoring.

SCORING FORMULA (CONSISTENT ACROSS ALL MATCHING):
Final Score = (Cosine Similarity × 70) + (BM25 Score × 30)

Where:
- Cosine Similarity: Semantic understanding using sentence embeddings (0-1 range)
- BM25 Score: Keyword matching using BM25 algorithm (normalized to 0-1 range)
- Final Score: 0-100 point scale

This formula is used identically for:
1. Candidate shortlisting (rank_applicants_for_job)
2. User job matching (get_top_jobs_for_resume)
3. Matchmaking explanations
"""
import warnings
import chromadb
from chromadb.utils import embedding_functions
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from rank_bm25 import BM25Okapi
import numpy as np
import os
from typing import List, Tuple, Dict

# Suppress ChromaDB warnings
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', message='.*PersistentClient.*')

class MatchingService:
    def __init__(self, chroma_path='chroma_storage'):
        """Initialize matching service"""
        self.chroma_path = chroma_path
        self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        
        try:
            # For ChromaDB 0.3.25, use the correct API
            import chromadb.config
            self.client = chromadb.Client(chromadb.config.Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory=chroma_path
            ))
        except Exception as e:
            print(f"Error initializing ChromaDB with version 0.3.25 API: {e}")
            try:
                # Fallback for newer versions
                if hasattr(chromadb, 'PersistentClient'):
                    self.client = chromadb.PersistentClient(path=chroma_path)
                else:
                    # Use basic client as last resort
                    self.client = chromadb.Client()
            except Exception as e2:
                print(f"Error with fallback ChromaDB initialization: {e2}")
                # Use in-memory client as final fallback
                self.client = chromadb.Client()
        
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
            # Avoid printing verbose telemetry errors (Posthog signature mismatches)
            # which surface from chromadb's telemetry. Provide a concise warning
            # and attempt a retry with telemetry disabled.
            err_str = str(e)
            if 'Posthog.capture' in err_str or 'posthog' in err_str.lower():
                print("Warning: ChromaDB telemetry error while adding resume (suppressed details)")
            else:
                print(f"Error adding resume to ChromaDB (first attempt): {err_str}")
            try:
                import os
                os.environ.setdefault('CHROMA_DISABLE_TELEMETRY', '1')
                # Recreate client and collections with telemetry disabled and retry
                try:
                    # Use the correct API for ChromaDB 0.3.25
                    self.client = chromadb.Client(chromadb.config.Settings(
                        chroma_db_impl="duckdb+parquet",
                        persist_directory=self.chroma_path
                    ))
                    self.resumes_collection = self.client.get_collection(
                        name="resumes",
                        embedding_function=self.embedding_function
                    )
                except Exception:
                    # If get_collection fails try create_collection
                    self.resumes_collection = self.client.create_collection(
                        name="resumes",
                        embedding_function=self.embedding_function
                    )

                self.resumes_collection.upsert(
                    documents=[resume_text],
                    ids=[f"user_{user_id}"],
                    metadatas=[{"user_id": user_id}]
                )
                return True
            except Exception as e2:
                err2 = str(e2)
                if 'Posthog.capture' in err2 or 'posthog' in err2.lower():
                    print("Warning: ChromaDB telemetry error on retry (suppressed details)")
                else:
                    print(f"Error adding resume to ChromaDB (retry): {err2}")
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
        Rank applicants using the EXACT hybrid scoring formula.
        Formula: Final Score = (Cosine Similarity × 70) + (BM25 Score × 30)
        This ensures consistency with the shortlisting algorithm.
        """
        if not applications:
            return []
        
        job_query = f"{job_role} {job_description}"
        resume_texts = [app.resume_text for app in applications]
        app_ids = [app.id for app in applications]
        
        # Get cosine similarity scores (already 0-1 range)
        cosine_scores = self._get_cosine_similarity_scores(job_query, resume_texts)
        
        # Get BM25 scores and normalize them to 0-1 range
        bm25_scores = self._get_bm25_scores(job_query, resume_texts)
        bm25_scores_normalized = self._normalize_scores(bm25_scores)
        
        # Apply the EXACT same formula as shortlisting:
        # Final Score = (Cosine Similarity × 70) + (BM25 Score × 30)
        final_scores = [
            (cos * 70) + (bm25_norm * 30)
            for cos, bm25_norm in zip(cosine_scores, bm25_scores_normalized)
        ]
        
        rankings = list(zip(app_ids, final_scores))
        rankings.sort(key=lambda x: x[1], reverse=True)
        
        return rankings
    
    def _preprocess_for_matching(self, text: str) -> str:
        """
        Preprocess text for optimal matching performance.
        Applies NLP preprocessing if available, falls back to basic cleaning.
        """
        if not text:
            return ""
        
        try:
            from app.utils.text_preprocessing import preprocess_resume_text
            return preprocess_resume_text(text, for_matching=True)
        except ImportError:
            # Fallback to basic preprocessing if module not available
            return text.lower().strip()
        except Exception as e:
            print(f"Warning: Error in text preprocessing: {e}")
            return text.lower().strip()
    
    def _get_cosine_similarity_scores(self, query: str, documents: List[str]) -> List[float]:
        """Get cosine similarity scores with preprocessing"""
        try:
            # Preprocess query and documents for better matching
            processed_query = self._preprocess_for_matching(query)
            processed_docs = [self._preprocess_for_matching(doc) for doc in documents]
            
            query_embedding = self.model.encode([processed_query])
            doc_embeddings = self.model.encode(processed_docs)
            similarities = cosine_similarity(query_embedding, doc_embeddings)[0]
            return similarities.tolist()
        except Exception as e:
            print(f"Error getting cosine similarity scores: {e}")
            return [0.5] * len(documents)
    
    def _get_bm25_scores(self, query: str, documents: List[str]) -> List[float]:
        """Get BM25 scores with preprocessing"""
        try:
            # Preprocess query and documents for better tokenization
            processed_query = self._preprocess_for_matching(query)
            processed_docs = [self._preprocess_for_matching(doc) for doc in documents]
            
            # Tokenize preprocessed text
            tokenized_corpus = [doc.split() for doc in processed_docs]
            tokenized_query = processed_query.split()
            
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
        """
        Get top job matches for resume using the EXACT same formula as candidate shortlisting.
        Formula: Final Score = (Cosine Similarity × 70) + (BM25 Score × 30)
        """
        if not all_jobs:
            return []
        
        job_texts = [f"{job.role} {job.description}" for job in all_jobs]
        job_ids = [job.id for job in all_jobs]
        
        # Get cosine similarity scores (already 0-1 range)
        cosine_scores = self._get_cosine_similarity_scores(resume_text, job_texts)
        
        # Get BM25 scores and normalize them to 0-1 range (same as shortlisting)
        bm25_scores = self._get_bm25_scores(resume_text, job_texts)
        bm25_scores_normalized = self._normalize_scores(bm25_scores)
        
        # Apply the EXACT same formula as shortlisting:
        # Final Score = (Cosine Similarity × 70) + (BM25 Score × 30)
        final_scores = [
            (cos * 70) + (bm25_norm * 30)
            for cos, bm25_norm in zip(cosine_scores, bm25_scores_normalized)
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