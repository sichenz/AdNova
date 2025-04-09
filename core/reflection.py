"""
Self-reflection and improvement mechanism for the Marketing Ad Agent.
This module allows the agent to learn from feedback and improve over time.
"""
import os
import json
import time
from typing import Dict, Any, List, Optional
from datetime import datetime

from config.settings import DEFAULT_MODEL, ANALYTICAL_TEMPERATURE

class FeedbackProcessor:
    """
    Process feedback and enable the agent to learn and improve over time.
    """
    
    def __init__(self, client):
        """
        Initialize the feedback processor.
        
        Args:
            client: The OpenAI client
        """
        self.client = client
        self.insights_dir = "data/insights"
        os.makedirs(self.insights_dir, exist_ok=True)
    
    def reflect_on_feedback(self, 
                          ad_record: Dict[str, Any], 
                          campaign_brief: Dict[str, Any],
                          feedback_record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Reflect on feedback to derive insights and improvements.
        
        Args:
            ad_record: The ad that received feedback
            campaign_brief: The campaign brief
            feedback_record: The feedback record
            
        Returns:
            Dictionary containing insights derived from reflection
        """
        feedback_text = feedback_record["feedback"]
        score = feedback_record.get("score")
        
        # Extract relevant info from the ad record
        ad_type = ad_record["ad_type"]
        ad_variations = ad_record["variations"]
        ad_variation_text = "\n".join([f"Variation {i+1}: {v}" for i, v in enumerate(ad_variations)])
        
        # Create the reflection prompt
        prompt = f"""
        As a marketing expert, analyze the following client feedback on a marketing ad and extract insights for improvement:
        
        Product/Service: {campaign_brief['product_name']}
        Description: {campaign_brief['description']}
        Target Audience: {campaign_brief['target_audience']}
        Campaign Goals: {campaign_brief['campaign_goals']}
        
        Ad Type: {ad_type}
        Ad Variations:
        {ad_variation_text}
        
        Client Feedback: {feedback_text}
        {f"Score: {score}/10" if score else ""}
        
        Provide the following reflections:
        
        1. Key Insights: What are 3-5 key insights from this feedback that can improve future ads?
        
        2. Strengths: What aspects of the ad were effective according to the feedback?
        
        3. Areas for Improvement: What specific aspects need improvement?
        
        4. Action Items: What are 3-4 specific actions to take in future ads for this client?
        
        5. Pattern Recognition: Does this feedback reveal any patterns or preferences about this client that should be remembered for future work?
        """
        
        response = self.client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert marketing strategist who specializes in analyzing client feedback to extract actionable insights."},
                {"role": "user", "content": prompt}
            ],
            temperature=ANALYTICAL_TEMPERATURE,
            max_tokens=1200
        )
        
        reflection_text = response.choices[0].message.content
        
        # Create a reflection record
        reflection_id = f"{feedback_record['feedback_id']}_reflection"
        reflection_record = {
            "reflection_id": reflection_id,
            "feedback_id": feedback_record["feedback_id"],
            "ad_id": ad_record["ad_id"],
            "brief_id": campaign_brief["brief_id"],
            "reflection": reflection_text,
            "created_at": datetime.now().isoformat()
        }
        
        # Parse the reflection to extract structured insights
        insights_prompt = f"""
        Parse the following marketing ad feedback reflection into a structured JSON format:
        
        {reflection_text}
        
        Format the response as valid JSON with the following structure:
        {{
            "key_insights": ["insight 1", "insight 2", ...],
            "strengths": ["strength 1", "strength 2", ...],
            "areas_for_improvement": ["area 1", "area 2", ...],
            "action_items": ["action 1", "action 2", ...],
            "pattern_recognition": ["pattern 1", "pattern 2", ...]
        }}
        
        Format as valid JSON only with no other text.
        """
        
        insights_response = self.client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": "You are a precision parser that converts text analysis into clean JSON format."},
                {"role": "user", "content": insights_prompt}
            ],
            temperature=0.1,
            max_tokens=800
        )
        
        insights_text = insights_response.choices[0].message.content
        
        # Clean up the response to ensure it's valid JSON
        try:
            # Remove any markdown code block markers if present
            if "```json" in insights_text:
                insights_text = insights_text.split("```json")[1].split("```")[0].strip()
            elif "```" in insights_text:
                insights_text = insights_text.split("```")[1].split("```")[0].strip()
            
            structured_insights = json.loads(insights_text)
            reflection_record["structured_insights"] = structured_insights
        except json.JSONDecodeError:
            # If parsing fails, store the raw text
            reflection_record["structured_insights"] = None
            reflection_record["parsing_error"] = True
        
        # Save the reflection
        with open(os.path.join(self.insights_dir, f"{reflection_id}.json"), "w") as f:
            json.dump(reflection_record, f, indent=2)
        
        # Check if we need to update the agent's strategy for this client/campaign
        self._update_client_strategy(campaign_brief["brief_id"], structured_insights)
        
        return reflection_record
    
    def _update_client_strategy(self, brief_id: str, insights: Dict[str, List[str]]) -> None:
        """
        Update the agent's strategy for a specific client based on accumulated insights.
        
        Args:
            brief_id: The campaign brief ID
            insights: Structured insights from reflection
        """
        # Path to the client strategy file
        strategy_file = os.path.join(self.insights_dir, f"{brief_id}_strategy.json")
        
        # Load existing strategy if it exists
        if os.path.exists(strategy_file):
            with open(strategy_file, "r") as f:
                client_strategy = json.load(f)
        else:
            # Create a new strategy
            client_strategy = {
                "brief_id": brief_id,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "key_insights": [],
                "strengths_to_maintain": [],
                "areas_to_improve": [],
                "client_preferences": [],
                "effective_approaches": []
            }
        
        # Update with new insights
        if insights:
            # Update timestamps
            client_strategy["updated_at"] = datetime.now().isoformat()
            client_strategy["update_count"] = client_strategy.get("update_count", 0) + 1
            
            # Append new insights
            if "key_insights" in insights:
                client_strategy["key_insights"].extend(insights["key_insights"])
            
            if "strengths" in insights:
                client_strategy["strengths_to_maintain"].extend(insights["strengths"])
            
            if "areas_for_improvement" in insights:
                client_strategy["areas_to_improve"].extend(insights["areas_for_improvement"])
            
            if "pattern_recognition" in insights:
                client_strategy["client_preferences"].extend(insights["pattern_recognition"])
            
            if "action_items" in insights:
                client_strategy["effective_approaches"].extend(insights["action_items"])
            
            # Remove duplicates while preserving order
            for key in client_strategy:
                if isinstance(client_strategy[key], list):
                    # Create a set for O(1) lookups while preserving order with a list
                    seen = set()
                    deduped = []
                    for item in client_strategy[key]:
                        if item not in seen:
                            seen.add(item)
                            deduped.append(item)
                    client_strategy[key] = deduped
        
        # Save the updated strategy
        with open(strategy_file, "w") as f:
            json.dump(client_strategy, f, indent=2)
    
    def get_client_strategy(self, brief_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the current strategy for a client.
        
        Args:
            brief_id: The campaign brief ID
            
        Returns:
            The client strategy or None if not found
        """
        strategy_file = os.path.join(self.insights_dir, f"{brief_id}_strategy.json")
        
        if os.path.exists(strategy_file):
            with open(strategy_file, "r") as f:
                return json.load(f)
        
        return None
    
    def generate_improvement_suggestions(self, ad_record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate suggestions to improve an ad based on past learnings.
        
        Args:
            ad_record: The ad record to improve
            
        Returns:
            Dictionary containing improvement suggestions
        """
        brief_id = ad_record["brief_id"]
        strategy = self.get_client_strategy(brief_id)
        
        if not strategy:
            # No previous strategy, generate generic suggestions
            return self._generate_generic_suggestions(ad_record)
        
        # Get the ad variations
        ad_variations = ad_record["variations"]
        ad_variation_text = "\n".join([f"Variation {i+1}: {v}" for i, v in enumerate(ad_variations)])
        
        # Format the client preferences and insights
        key_insights = "\n".join([f"- {insight}" for insight in strategy.get("key_insights", [])])
        strengths = "\n".join([f"- {strength}" for strength in strategy.get("strengths_to_maintain", [])])
        areas_to_improve = "\n".join([f"- {area}" for area in strategy.get("areas_to_improve", [])])
        client_preferences = "\n".join([f"- {pref}" for pref in strategy.get("client_preferences", [])])
        
        prompt = f"""
        As a marketing expert, provide specific suggestions to improve the following ad based on what we've learned about this client's preferences:
        
        Ad Type: {ad_record['ad_type']}
        
        Ad Variations:
        {ad_variation_text}
        
        What we've learned about this client:
        
        Key Insights:
        {key_insights}
        
        Strengths to Maintain:
        {strengths}
        
        Areas to Improve:
        {areas_to_improve}
        
        Client Preferences:
        {client_preferences}
        
        Provide 5-7 specific, actionable suggestions to improve this ad based on these learnings. For each suggestion:
        1. Describe the change to make
        2. Explain how it addresses a known client preference or feedback pattern
        3. Provide a specific example of the change applied to the ad content
        """
        
        response = self.client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert marketing strategist who specializes in providing actionable suggestions to improve marketing content based on client preferences."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=1200
        )
        
        suggestions_text = response.choices[0].message.content
        
        # Create suggestion record
        suggestion_id = f"{ad_record['ad_id']}_suggestions"
        suggestion_record = {
            "suggestion_id": suggestion_id,
            "ad_id": ad_record["ad_id"],
            "brief_id": brief_id,
            "suggestions": suggestions_text,
            "based_on_strategy": True,
            "created_at": datetime.now().isoformat()
        }
        
        # Save the suggestions
        with open(os.path.join(self.insights_dir, f"{suggestion_id}.json"), "w") as f:
            json.dump(suggestion_record, f, indent=2)
        
        return suggestion_record
    
    def _generate_generic_suggestions(self, ad_record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate generic suggestions to improve an ad when no client strategy exists.
        
        Args:
            ad_record: The ad record to improve
            
        Returns:
            Dictionary containing generic improvement suggestions
        """
        # Get the ad variations
        ad_variations = ad_record["variations"]
        ad_variation_text = "\n".join([f"Variation {i+1}: {v}" for i, v in enumerate(ad_variations)])
        
        prompt = f"""
        As a marketing expert, provide specific suggestions to improve the following ad:
        
        Ad Type: {ad_record['ad_type']}
        
        Ad Variations:
        {ad_variation_text}
        
        Provide 5-7 specific, actionable suggestions to improve this ad based on best practices in marketing. For each suggestion:
        1. Describe the change to make
        2. Explain how it improves the effectiveness of the ad
        3. Provide a specific example of the change applied to the ad content
        """
        
        response = self.client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert marketing strategist who specializes in providing actionable suggestions to improve marketing content."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=1200
        )
        
        suggestions_text = response.choices[0].message.content
        
        # Create suggestion record
        suggestion_id = f"{ad_record['ad_id']}_suggestions"
        suggestion_record = {
            "suggestion_id": suggestion_id,
            "ad_id": ad_record["ad_id"],
            "brief_id": ad_record["brief_id"],
            "suggestions": suggestions_text,
            "based_on_strategy": False,
            "created_at": datetime.now().isoformat()
        }
        
        # Save the suggestions
        with open(os.path.join(self.insights_dir, f"{suggestion_id}.json"), "w") as f:
            json.dump(suggestion_record, f, indent=2)
        
        return suggestion_record