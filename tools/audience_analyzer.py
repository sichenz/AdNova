"""
Audience analysis tool for the Marketing Ad Agent.
This module analyzes target audience descriptions to extract insights.
"""
import json
from typing import Dict, Any, List

from config.settings import DEFAULT_MODEL, ANALYTICAL_TEMPERATURE

class AudienceAnalyzer:
    """
    Analyzes target audience descriptions to extract demographic, psychographic,
    and behavioral insights for marketing campaign optimization.
    """
    
    def __init__(self, client):
        """
        Initialize the audience analyzer.
        
        Args:
            client: The OpenAI client
        """
        self.client = client
    
    def analyze(self, target_audience_description: str) -> Dict[str, Any]:
        """
        Analyze a target audience description to extract marketing insights.
        
        Args:
            target_audience_description: Description of the target audience
            
        Returns:
            Dictionary containing audience insights
        """
        prompt = f"""
        As a market research expert, analyze the following target audience description and extract detailed insights:
        
        Target Audience: {target_audience_description}
        
        Provide a comprehensive analysis structured as follows:
        
        1. Demographics:
           - Age range (specific ranges, not just 'young' or 'old')
           - Gender distribution (if applicable)
           - Income level
           - Education level
           - Occupation/Professional background
           - Geographic location/Urban vs. rural
           - Family status
        
        2. Psychographics:
           - Values and beliefs
           - Interests and hobbies
           - Lifestyle characteristics
           - Personality traits
           - Aspirations and goals
        
        3. Behavioral Insights:
           - Purchasing behavior
           - Brand preferences/loyalty
           - Media consumption habits
           - Online behavior
           - Decision-making factors
        
        4. Pain Points & Needs:
           - Key challenges or problems
           - Unmet needs
           - Motivations for purchase
           - Objections or hesitations
        
        5. Communication Preferences:
           - Tone that resonates best
           - Message framing that works
           - Content types likely to engage
           - Platforms/channels to reach them
        
        6. Audience Segments:
           - Identify 2-3 distinct sub-segments within this audience
           - For each sub-segment, note key distinguishing characteristics
        
        Format each section with clear bullet points. If any information is not explicitly stated or cannot be reasonably inferred, indicate this with "Not specified" rather than making unfounded assumptions.
        """
        
        response = self.client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert market research analyst who extracts detailed, actionable audience insights from descriptions."},
                {"role": "user", "content": prompt}
            ],
            temperature=ANALYTICAL_TEMPERATURE,
            max_tokens=1500
        )
        
        analysis_text = response.choices[0].message.content
        
        # Convert the analysis text to structured data
        structured_insights = self._convert_analysis_to_structured_data(analysis_text)
        
        # Generate marketing recommendations based on the analysis
        recommendations = self._generate_recommendations(structured_insights)
        
        # Combine the insights and recommendations
        audience_insights = {
            "analysis": structured_insights,
            "recommendations": recommendations,
            "original_description": target_audience_description
        }
        
        return audience_insights
    
    def _convert_analysis_to_structured_data(self, analysis_text: str) -> Dict[str, Any]:
        """
        Convert the analysis text to structured data.
        
        Args:
            analysis_text: The raw analysis text
            
        Returns:
            Dictionary containing structured insights
        """
        # Parse the analysis using another LLM call
        parse_prompt = f"""
        Convert the following audience analysis into a clean, structured JSON format:
        
        {analysis_text}
        
        The JSON structure should be:
        {{
            "demographics": {{
                "age_range": "",
                "gender_distribution": "",
                "income_level": "",
                "education_level": "",
                "occupation": "",
                "location": "",
                "family_status": ""
            }},
            "psychographics": {{
                "values_and_beliefs": [],
                "interests_and_hobbies": [],
                "lifestyle": [],
                "personality_traits": [],
                "aspirations_and_goals": []
            }},
            "behavioral_insights": {{
                "purchasing_behavior": [],
                "brand_preferences": [],
                "media_consumption": [],
                "online_behavior": [],
                "decision_factors": []
            }},
            "pain_points_and_needs": {{
                "challenges": [],
                "unmet_needs": [],
                "motivations": [],
                "objections": []
            }},
            "communication_preferences": {{
                "tone": [],
                "message_framing": [],
                "content_types": [],
                "platforms": []
            }},
            "audience_segments": [
                {{
                    "name": "",
                    "characteristics": []
                }}
            ]
        }}
        
        For array fields, extract individual points as separate list items.
        Use "Not specified" for any fields without clear information.
        Format as valid JSON only with no other text.
        """
        
        parsing_response = self.client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": "You are a precision parser that converts analytical text into clean JSON format."},
                {"role": "user", "content": parse_prompt}
            ],
            temperature=0.1,
            max_tokens=1500
        )
        
        parsed_text = parsing_response.choices[0].message.content
        
        # Clean up the response to ensure it's valid JSON
        try:
            # Remove any markdown code block markers if present
            if "```json" in parsed_text:
                parsed_text = parsed_text.split("```json")[1].split("```")[0].strip()
            elif "```" in parsed_text:
                parsed_text = parsed_text.split("```")[1].split("```")[0].strip()
            
            structured_data = json.loads(parsed_text)
        except json.JSONDecodeError:
            # If parsing fails, return a basic structure
            structured_data = {
                "demographics": {},
                "psychographics": {},
                "behavioral_insights": {},
                "pain_points_and_needs": {},
                "communication_preferences": {},
                "audience_segments": [],
                "parsing_error": True,
                "raw_analysis": analysis_text
            }
        
        return structured_data
    
    def _generate_recommendations(self, insights: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Generate marketing recommendations based on audience insights.
        
        Args:
            insights: Structured audience insights
            
        Returns:
            Dictionary containing marketing recommendations
        """
        # Convert insights back to text for the prompt
        insights_text = json.dumps(insights, indent=2)
        
        recommendations_prompt = f"""
        Based on the following structured audience insights, provide specific marketing recommendations:
        
        {insights_text}
        
        Generate concise, actionable recommendations in the following categories:
        
        1. Messaging Strategy: How to frame messages to resonate with this audience
        2. Channel Strategy: Best platforms and media to reach this audience
        3. Content Strategy: Types of content likely to engage this audience
        4. Targeting Approach: How to segment and target this audience effectively
        5. Creative Direction: Visual and tonal elements that will appeal to this audience
        
        For each category, provide 3-5 specific, practical recommendations as bullet points.
        Format your response as a structured JSON with these categories as keys, each containing an array of recommendation strings.
        """
        
        response = self.client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert marketing strategist who provides specific, actionable recommendations based on audience insights."},
                {"role": "user", "content": recommendations_prompt}
            ],
            temperature=ANALYTICAL_TEMPERATURE,
            max_tokens=1200
        )
        
        recommendations_text = response.choices[0].message.content
        
        # Parse the recommendations
        try:
            # Remove any markdown code block markers if present
            if "```json" in recommendations_text:
                recommendations_text = recommendations_text.split("```json")[1].split("```")[0].strip()
            elif "```" in recommendations_text:
                recommendations_text = recommendations_text.split("```")[1].split("```")[0].strip()
            
            recommendations = json.loads(recommendations_text)
        except json.JSONDecodeError:
            # If parsing fails, return a basic structure
            recommendations = {
                "messaging_strategy": [
                    "Customize messaging to address the specific needs and pain points identified in the audience analysis.",
                    "Use language and terminology that reflects the audience's level of understanding and familiarity with your product/service.",
                    "Focus on the primary benefits that align with the audience's motivations."
                ],
                "channel_strategy": [
                    "Prioritize channels based on the audience's media consumption habits.",
                    "Consider a multi-channel approach to reach different segments of your audience.",
                    "Allocate budget according to where your audience spends most of their time."
                ],
                "content_strategy": [
                    "Create content that addresses the specific challenges identified in the analysis.",
                    "Use formats that match the audience's preferred way of consuming information.",
                    "Balance educational and promotional content based on the audience's buying stage."
                ],
                "targeting_approach": [
                    "Develop separate messaging for the identified sub-segments.",
                    "Use the demographic and psychographic data for precise ad targeting.",
                    "Test different approaches with smaller audience segments before scaling."
                ],
                "creative_direction": [
                    "Align visual elements with the audience's aesthetic preferences and values.",
                    "Use a tone that matches the audience's communication style.",
                    "Incorporate elements that reflect the audience's aspirations and goals."
                ],
                "parsing_error": True
            }
        
        return recommendations