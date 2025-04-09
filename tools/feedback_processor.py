"""
Client feedback processing tool for the Marketing Ad Agent.
This module handles processing and analyzing client feedback on ads.
"""
import json
from typing import Dict, Any, List, Optional, Union

from config.settings import DEFAULT_MODEL, ANALYTICAL_TEMPERATURE

class ClientFeedbackProcessor:
    """
    Processes and analyzes client feedback on generated marketing ads.
    """
    
    def __init__(self, client):
        """
        Initialize the feedback processor.
        
        Args:
            client: The OpenAI client
        """
        self.client = client
    
    def process(self, 
               ad_record: Dict[str, Any], 
               campaign_brief: Dict[str, Any],
               feedback: str,
               score: Optional[int] = None) -> Dict[str, Any]:
        """
        Process client feedback on a generated ad.
        
        Args:
            ad_record: The ad record
            campaign_brief: The campaign brief
            feedback: Client feedback text
            score: Numerical feedback score (optional, 1-10)
            
        Returns:
            Dictionary containing processed feedback with insights
        """
        # Extract relevant information for processing
        ad_type = ad_record["ad_type"]
        ad_variations = ad_record["variations"]
        ad_variation_text = "\n".join([f"Variation {i+1}: {v}" for i, v in enumerate(ad_variations)])
        
        score_text = ""
        if score is not None:
            score_text = f"Score: {score}/10"
        
        prompt = f"""
        As an expert marketing analyst, analyze the following client feedback on a marketing ad:
        
        CAMPAIGN INFORMATION:
        Product/Service: {campaign_brief['product_name']}
        Description: {campaign_brief['description']}
        Target Audience: {campaign_brief['target_audience']}
        Campaign Goals: {campaign_brief['campaign_goals']}
        
        AD CONTENT:
        Ad Type: {ad_type}
        Ad Variations:
        {ad_variation_text}
        
        CLIENT FEEDBACK:
        {feedback}
        {score_text}
        
        Analyze this feedback and provide:
        
        1. Key Issues: Identify the main issues or concerns raised in the feedback (if any)
        
        2. Positive Aspects: Identify what was well-received (if anything)
        
        3. Specific Elements to Change: List specific elements of the ad that should be modified based on the feedback
        
        4. Elements to Keep: List specific elements of the ad that should be preserved
        
        5. Suggested Improvements: Provide 3-5 specific, actionable suggestions for improving the ad based on the feedback
        
        6. Sentiment Analysis: Categorize the overall sentiment of the feedback (Positive, Neutral, Negative, Mixed)
        
        Format your analysis in a structured way that could be easily parsed.
        """
        
        response = self.client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert marketing analyst who specializes in interpreting client feedback to improve marketing content."},
                {"role": "user", "content": prompt}
            ],
            temperature=ANALYTICAL_TEMPERATURE,
            max_tokens=1200
        )
        
        analysis_text = response.choices[0].message.content
        
        # Parse the analysis into structured data
        structured_analysis = self._parse_analysis(analysis_text)
        
        # Generate improvement recommendations
        improvement_recommendations = self._generate_improvement_recommendations(
            structured_analysis, ad_record, campaign_brief
        )
        
        # Prepare the processed feedback
        processed_feedback = {
            "analysis": structured_analysis,
            "improvement_recommendations": improvement_recommendations,
            "original_feedback": feedback,
            "score": score
        }
        
        return processed_feedback
    
    def _parse_analysis(self, analysis_text: str) -> Dict[str, Any]:
        """
        Parse the analysis text into structured data.
        
        Args:
            analysis_text: The analysis text
            
        Returns:
            Structured analysis data
        """
        # Use another LLM call to parse the text into a clean JSON structure
        parse_prompt = f"""
        Parse the following feedback analysis into a clean, structured JSON format:
        
        {analysis_text}
        
        The JSON should have these main sections:
        - key_issues (array of strings)
        - positive_aspects (array of strings)
        - elements_to_change (array of strings)
        - elements_to_keep (array of strings)
        - suggested_improvements (array of strings)
        - sentiment (string)
        
        Format as valid JSON only with no other text.
        """
        
        response = self.client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": "You are a precision parser that converts text analysis into clean JSON format."},
                {"role": "user", "content": parse_prompt}
            ],
            temperature=0.1,
            max_tokens=800
        )
        
        parsed_text = response.choices[0].message.content
        
        # Clean up the response to ensure it's valid JSON
        try:
            # Remove any markdown code block markers if present
            if "```json" in parsed_text:
                parsed_text = parsed_text.split("```json")[1].split("```")[0].strip()
            elif "```" in parsed_text:
                parsed_text = parsed_text.split("```")[1].split("```")[0].strip()
            
            parsed_analysis = json.loads(parsed_text)
        except json.JSONDecodeError:
            # If parsing fails, return a basic structure
            parsed_analysis = {
                "key_issues": ["Could not parse key issues from feedback"],
                "positive_aspects": ["Could not parse positive aspects from feedback"],
                "elements_to_change": ["Review ad for potential improvements based on feedback"],
                "elements_to_keep": ["Preserve core messaging while making requested changes"],
                "suggested_improvements": ["Consider overall tone and clarity of messaging"],
                "sentiment": "Neutral",
                "parsing_error": True,
                "raw_analysis": analysis_text
            }
        
        return parsed_analysis
    
    def _generate_improvement_recommendations(self, 
                                           analysis: Dict[str, Any],
                                           ad_record: Dict[str, Any],
                                           campaign_brief: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Generate specific improvement recommendations based on the feedback analysis.
        
        Args:
            analysis: Structured feedback analysis
            ad_record: The ad record
            campaign_brief: The campaign brief
            
        Returns:
            List of specific improvement recommendations
        """
        # Extract relevant information
        ad_type = ad_record["ad_type"]
        key_issues = analysis.get("key_issues", [])
        elements_to_change = analysis.get("elements_to_change", [])
        
        # Format the issues and elements to change
        issues_text = "\n".join([f"- {issue}" for issue in key_issues])
        changes_text = "\n".join([f"- {change}" for change in elements_to_change])
        
        prompt = f"""
        As an expert marketing copywriter, provide specific recommendations to improve a {ad_type} based on the following analysis:
        
        Product/Service: {campaign_brief['product_name']}
        Target Audience: {campaign_brief['target_audience']}
        
        Key issues identified:
        {issues_text}
        
        Elements to change:
        {changes_text}
        
        For each issue or element to change, provide:
        1. A specific, actionable recommendation for improvement
        2. A brief example or template of how this might look in practice
        
        Provide 5 specific recommendations in total, prioritizing the most important issues.
        Format each recommendation as a separate object with 'recommendation' and 'example' fields.
        """
        
        response = self.client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert marketing copywriter who specializes in providing specific, actionable recommendations to improve ad content."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            max_tokens=1200
        )
        
        recommendations_text = response.choices[0].message.content
        
        # Parse the recommendations into structured format
        parse_prompt = f"""
        Parse the following recommendations into a JSON array where each object has 'recommendation' and 'example' fields:
        
        {recommendations_text}
        
        Format as valid JSON array only with no other text.
        """
        
        parse_response = self.client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": "You are a precision parser that converts text into clean JSON format."},
                {"role": "user", "content": parse_prompt}
            ],
            temperature=0.1,
            max_tokens=800
        )
        
        parsed_text = parse_response.choices[0].message.content
        
        # Clean up the response to ensure it's valid JSON
        try:
            # Remove any markdown code block markers if present
            if "```json" in parsed_text:
                parsed_text = parsed_text.split("```json")[1].split("```")[0].strip()
            elif "```" in parsed_text:
                parsed_text = parsed_text.split("```")[1].split("```")[0].strip()
            
            recommendations = json.loads(parsed_text)
        except json.JSONDecodeError:
            # If parsing fails, return a basic structure
            recommendations = [
                {
                    "recommendation": "Review and adjust the overall tone to better match the target audience preferences",
                    "example": "Example of tone adjustment"
                },
                {
                    "recommendation": "Strengthen the call-to-action to be more specific and compelling",
                    "example": "Instead of 'Learn More', use 'Discover How [Product] Can [Specific Benefit] Today'"
                },
                {
                    "recommendation": "Focus messaging more directly on the primary benefit for the customer",
                    "example": "Emphasize the main value proposition in the headline"
                },
                {
                    "recommendation": "Use more concrete, specific language rather than general claims",
                    "example": "Instead of 'Improves efficiency', use 'Reduces processing time by 35%'"
                },
                {
                    "recommendation": "Adjust the messaging to better address customer pain points",
                    "example": "Directly mention how the product solves a specific problem"
                }
            ]
        
        return recommendations