"""
Memory management for the Marketing Ad Agent.
This module handles storing, retrieving, and managing the agent's memory.
"""
import os
import json
import time
from datetime import datetime
import numpy as np
import faiss
import tiktoken
from typing import List, Dict, Any, Optional, Tuple

from config.settings import MEMORY_INDEX_PATH, MAX_MEMORY_ITEMS, DEFAULT_MODEL

class AgentMemory:
    """
    Manages the agent's memory using a vector store for semantic retrieval.
    """
    
    def __init__(self):
        """Initialize the memory system."""
        # Memory storage
        self.campaign_briefs = {}
        self.generated_ads = {}
        self.feedback = {}
        self.recommendations = {}
        
        # Vector index for semantic search
        self.index = None
        self.text_to_id = {}
        self.id_to_metadata = {}
        
        # Initialize the vector index
        self._initialize_vector_index()
        
        # Load any existing memory data
        self._load_existing_data()
    
    def _initialize_vector_index(self):
        """Initialize the FAISS vector index."""
        # Using 1536 dimensions for OpenAI embeddings
        dimension = 1536
        self.index = faiss.IndexFlatL2(dimension)
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(MEMORY_INDEX_PATH), exist_ok=True)
        
        # Load existing index if it exists
        if os.path.exists(f"{MEMORY_INDEX_PATH}.index"):
            self.index = faiss.read_index(f"{MEMORY_INDEX_PATH}.index")
            
            # Load mappings
            if os.path.exists(f"{MEMORY_INDEX_PATH}_text_to_id.json"):
                with open(f"{MEMORY_INDEX_PATH}_text_to_id.json", "r") as f:
                    self.text_to_id = json.load(f)
            
            if os.path.exists(f"{MEMORY_INDEX_PATH}_id_to_metadata.json"):
                with open(f"{MEMORY_INDEX_PATH}_id_to_metadata.json", "r") as f:
                    self.id_to_metadata = json.load(f)
    
    def _save_vector_index(self):
        """Save the current state of the vector index."""
        # Save index
        faiss.write_index(self.index, f"{MEMORY_INDEX_PATH}.index")
        
        # Save mappings
        with open(f"{MEMORY_INDEX_PATH}_text_to_id.json", "w") as f:
            json.dump(self.text_to_id, f)
        
        with open(f"{MEMORY_INDEX_PATH}_id_to_metadata.json", "w") as f:
            json.dump(self.id_to_metadata, f)
    
    def _load_existing_data(self):
        """Load existing data from disk."""
        # Load campaign briefs
        if os.path.exists("data/campaign_briefs"):
            for filename in os.listdir("data/campaign_briefs"):
                if filename.endswith(".json"):
                    with open(os.path.join("data/campaign_briefs", filename), "r") as f:
                        brief = json.load(f)
                        self.campaign_briefs[brief["brief_id"]] = brief
        
        # Load generated ads
        if os.path.exists("data/generated_ads"):
            for filename in os.listdir("data/generated_ads"):
                if filename.endswith(".json"):
                    with open(os.path.join("data/generated_ads", filename), "r") as f:
                        ad = json.load(f)
                        self.generated_ads[ad["ad_id"]] = ad
        
        # Load feedback
        if os.path.exists("data/feedback"):
            for filename in os.listdir("data/feedback"):
                if filename.endswith(".json"):
                    with open(os.path.join("data/feedback", filename), "r") as f:
                        feedback = json.load(f)
                        self.feedback[feedback["feedback_id"]] = feedback
    
    def _get_embedding(self, text: str) -> np.ndarray:
        """
        Get embedding for a text using OpenAI's embedding API.
        
        Args:
            text: The text to embed
            
        Returns:
            numpy.ndarray: The embedding vector
        """
        import openai
        from utils.api_utils import get_openai_client
        
        client = get_openai_client()
        
        # Truncate text if needed
        if len(text) > 8000:
            text = text[:8000]
        
        # Get embedding
        response = client.embeddings.create(
            input=text,
            model="text-embedding-ada-002"
        )
        
        embedding = response.data[0].embedding
        return np.array(embedding, dtype=np.float32).reshape(1, -1)
    
    def add_to_vector_store(self, text: str, metadata: Dict[str, Any], item_id: str) -> None:
        """
        Add an item to the vector store for semantic search.
        
        Args:
            text: The text to embed and store
            metadata: Associated metadata
            item_id: Unique identifier for this item
        """
        # Get embedding
        embedding = self._get_embedding(text)
        
        # Add to index
        self.index.add(embedding)
        
        # Store mappings
        self.text_to_id[text[:100]] = item_id  # Use beginning of text as key
        self.id_to_metadata[item_id] = metadata
        
        # Save index
        self._save_vector_index()
    
    def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Search the vector store for semantically similar items.
        
        Args:
            query: The search query
            k: Number of results to return
            
        Returns:
            List of metadata for the most similar items
        """
        # Get embedding for the query
        query_embedding = self._get_embedding(query)
        
        # Search the index
        distances, indices = self.index.search(query_embedding, k)
        
        # Get metadata for the results
        results = []
        for i, idx in enumerate(indices[0]):
            if idx != -1:  # Valid index
                # Find the corresponding text
                text_key = list(self.text_to_id.keys())[idx]
                item_id = self.text_to_id[text_key]
                
                # Get metadata
                metadata = self.id_to_metadata.get(item_id, {})
                
                # Add distance score
                metadata["similarity_score"] = float(distances[0][i])
                
                results.append(metadata)
        
        return results
    
    def add_campaign_brief(self, brief: Dict[str, Any]) -> None:
        """
        Add a campaign brief to memory.
        
        Args:
            brief: The campaign brief dictionary
        """
        brief_id = brief["brief_id"]
        self.campaign_briefs[brief_id] = brief
        
        # Prepare text for vector storage
        text = f"""
        Campaign Brief: {brief['product_name']}
        Description: {brief['description']}
        Target Audience: {brief['target_audience']}
        Campaign Goals: {brief['campaign_goals']}
        Tone: {brief.get('tone', 'Not specified')}
        Key Selling Points: {', '.join(brief.get('key_selling_points', []))}
        """
        
        # Add to vector store
        self.add_to_vector_store(
            text=text,
            metadata={
                "type": "campaign_brief",
                "brief_id": brief_id,
                "product_name": brief["product_name"],
                "created_at": brief["created_at"]
            },
            item_id=f"brief_{brief_id}"
        )
    
    def add_generated_ad(self, ad: Dict[str, Any]) -> None:
        """
        Add a generated ad to memory.
        
        Args:
            ad: The generated ad dictionary
        """
        ad_id = ad["ad_id"]
        self.generated_ads[ad_id] = ad
        
        # Prepare text for vector storage
        text = f"""
        Ad Type: {ad['ad_type']}
        Variations:
        {' '.join(ad['variations'])}
        """
        
        # Add to vector store
        self.add_to_vector_store(
            text=text,
            metadata={
                "type": "generated_ad",
                "ad_id": ad_id,
                "brief_id": ad["brief_id"],
                "ad_type": ad["ad_type"],
                "created_at": ad["created_at"]
            },
            item_id=f"ad_{ad_id}"
        )
    
    def add_feedback(self, feedback: Dict[str, Any]) -> None:
        """
        Add client feedback to memory.
        
        Args:
            feedback: The feedback dictionary
        """
        feedback_id = feedback["feedback_id"]
        self.feedback[feedback_id] = feedback
        
        # Prepare text for vector storage
        text = f"""
        Feedback: {feedback['feedback']}
        Score: {feedback.get('score', 'Not provided')}
        Processed Feedback: {feedback.get('processed_feedback', {})}
        """
        
        # Add to vector store
        self.add_to_vector_store(
            text=text,
            metadata={
                "type": "feedback",
                "feedback_id": feedback_id,
                "ad_id": feedback["ad_id"],
                "brief_id": feedback["brief_id"],
                "created_at": feedback["created_at"]
            },
            item_id=f"feedback_{feedback_id}"
        )
    
    def add_recommendation(self, recommendation: Dict[str, Any]) -> None:
        """
        Add a recommendation to memory.
        
        Args:
            recommendation: The recommendation dictionary
        """
        rec_id = recommendation["recommendation_id"]
        self.recommendations[rec_id] = recommendation
        
        # Prepare text for vector storage
        text = f"""
        Recommendations: {recommendation['recommendations']}
        """
        
        # Add to vector store
        self.add_to_vector_store(
            text=text,
            metadata={
                "type": "recommendation",
                "recommendation_id": rec_id,
                "brief_id": recommendation["brief_id"],
                "created_at": recommendation["created_at"]
            },
            item_id=f"rec_{rec_id}"
        )
    
    def get_campaign_brief(self, brief_id: str) -> Optional[Dict[str, Any]]:
        """Get a campaign brief by ID."""
        return self.campaign_briefs.get(brief_id)
    
    def get_generated_ad(self, ad_id: str) -> Optional[Dict[str, Any]]:
        """Get a generated ad by ID."""
        return self.generated_ads.get(ad_id)
    
    def get_feedback(self, feedback_id: str) -> Optional[Dict[str, Any]]:
        """Get feedback by ID."""
        return self.feedback.get(feedback_id)
    
    def get_recommendation(self, rec_id: str) -> Optional[Dict[str, Any]]:
        """Get a recommendation by ID."""
        return self.recommendations.get(rec_id)
    
    def get_ads_for_brief(self, brief_id: str) -> List[Dict[str, Any]]:
        """Get all ads generated for a specific campaign brief."""
        return [ad for ad in self.generated_ads.values() if ad["brief_id"] == brief_id]
    
    def get_feedback_for_ad(self, ad_id: str) -> List[Dict[str, Any]]:
        """Get all feedback for a specific ad."""
        return [fb for fb in self.feedback.values() if fb["ad_id"] == ad_id]
    
    def get_similar_campaigns(self, description: str, k: int = 3) -> List[Dict[str, Any]]:
        """Find similar campaign briefs based on description."""
        results = self.search(description, k)
        # Filter to only include campaign briefs
        return [r for r in results if r.get("type") == "campaign_brief"]