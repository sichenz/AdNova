"""
Brand voice management tool for the Marketing Ad Agent.
This module handles defining and maintaining consistent brand voice.
"""
import os
import json
from typing import Dict, Any, Optional
from datetime import datetime

from config.settings import DEFAULT_MODEL, ANALYTICAL_TEMPERATURE, TONE_OPTIONS

class BrandVoiceManager:
    """
    Manages the definition and maintenance of consistent brand voice for marketing content.
    """
    
    def __init__(self, client):
        """
        Initialize the brand voice manager.
        
        Args:
            client: The OpenAI client
        """
        self.client = client
        self.voices_dir = "data/brand_voices"
        os.makedirs(self.voices_dir, exist_ok=True)
    
    def create_or_get_voice(self, 
                          product_name: str, 
                          description: str,
                          tone: str = "professional",
                          target_audience: Optional[str] = None,
                          existing_content: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new brand voice or retrieve an existing one.
        
        Args:
            product_name: Name of the product or service
            description: Description of the product or service
            tone: Desired tone for the brand voice
            target_audience: Description of the target audience (optional)
            existing_content: Examples of existing content to match (optional)
            
        Returns:
            Dictionary containing the brand voice definition
        """
        # Check if a brand voice already exists for this product
        voice_file = os.path.join(self.voices_dir, f"{self._sanitize_filename(product_name)}_voice.json")
        
        if os.path.exists(voice_file):
            # Load existing voice
            with open(voice_file, "r") as f:
                brand_voice = json.load(f)
            return brand_voice
        
        # Create a new brand voice
        return self.create_voice(product_name, description, tone, target_audience, existing_content)
    
    def create_voice(self, 
                   product_name: str, 
                   description: str,
                   tone: str = "professional",
                   target_audience: Optional[str] = None,
                   existing_content: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new brand voice definition.
        
        Args:
            product_name: Name of the product or service
            description: Description of the product or service
            tone: Desired tone for the brand voice
            target_audience: Description of the target audience (optional)
            existing_content: Examples of existing content to match (optional)
            
        Returns:
            Dictionary containing the new brand voice definition
        """
        # Validate the tone
        if tone not in TONE_OPTIONS:
            tone = "professional"  # Default to professional if invalid
        
        # Create the prompt
        prompt = f"""
        Create a detailed brand voice guide for the following product/service:
        
        Product/Service: {product_name}
        Description: {description}
        Desired Tone: {tone}
        """
        
        if target_audience:
            prompt += f"\nTarget Audience: {target_audience}"
        
        if existing_content:
            prompt += f"""
            
            Examples of existing content:
            {existing_content}
            
            Analyze these examples to extract the existing voice characteristics.
            """
        
        prompt += """
        
        Create a comprehensive brand voice guide with the following components:
        
        1. Voice Characteristics:
           - Three adjectives that best describe the brand voice
           - Overall personality and character of the brand
           - How the voice should make the audience feel
        
        2. Tone Specification:
           - When to use a more formal vs. casual tone
           - Emotional range (what emotions should be expressed and how strongly)
           - Level of authority/expertise to convey
        
        3. Language Patterns:
           - Sentence length and structure preferences
           - Vocabulary level and complexity
           - Types of words to emphasize (e.g., action verbs, descriptive adjectives)
           - Words or phrases to use frequently
           - Words or phrases to avoid
        
        4. Writing Style Guidelines:
           - Use of literary devices (metaphors, analogies, etc.)
           - Approach to humor or wit
           - How to address the audience (e.g., first person, second person)
           - Punctuation and formatting preferences
        
        5. Examples:
           - Provide three short examples demonstrating this voice in different contexts
        
        Format your response as structured data that could be parsed into JSON.
        """
        
        response = self.client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert brand strategist who specializes in developing distinctive and consistent brand voices."},
                {"role": "user", "content": prompt}
            ],
            temperature=ANALYTICAL_TEMPERATURE,
            max_tokens=1500
        )
        
        voice_guide_text = response.choices[0].message.content
        
        # Parse the voice guide to structured format
        structured_voice = self._parse_voice_guide(voice_guide_text, product_name, tone)
        
        # Save the brand voice
        voice_file = os.path.join(self.voices_dir, f"{self._sanitize_filename(product_name)}_voice.json")
        with open(voice_file, "w") as f:
            json.dump(structured_voice, f, indent=2)
        
        return structured_voice
    
    def update_voice(self, 
                   product_name: str,
                   updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing brand voice.
        
        Args:
            product_name: Name of the product or service
            updates: Dictionary of updates to apply
            
        Returns:
            Updated brand voice definition
        """
        # Get existing voice
        voice_file = os.path.join(self.voices_dir, f"{self._sanitize_filename(product_name)}_voice.json")
        
        if not os.path.exists(voice_file):
            raise ValueError(f"No existing brand voice found for {product_name}")
        
        with open(voice_file, "r") as f:
            brand_voice = json.load(f)
        
        # Apply updates
        for key, value in updates.items():
            if key in brand_voice:
                if isinstance(value, dict) and isinstance(brand_voice[key], dict):
                    # Merge dictionaries
                    brand_voice[key].update(value)
                else:
                    # Replace value
                    brand_voice[key] = value
        
        # Update metadata
        brand_voice["updated_at"] = datetime.now().isoformat()
        brand_voice["version"] = brand_voice.get("version", 1) + 1
        
        # Save updated voice
        with open(voice_file, "w") as f:
            json.dump(brand_voice, f, indent=2)
        
        return brand_voice
    
    def get_voice_for_content(self, 
                            product_name: str, 
                            content_type: str,
                            target_audience: Optional[str] = None) -> Dict[str, str]:
        """
        Get specific voice guidelines for a particular type of content.
        
        Args:
            product_name: Name of the product or service
            content_type: Type of content (e.g., social media, email, landing page)
            target_audience: Specific target audience for this content (optional)
            
        Returns:
            Dictionary containing specific voice guidelines for this content
        """
        # Get the base brand voice
        voice_file = os.path.join(self.voices_dir, f"{self._sanitize_filename(product_name)}_voice.json")
        
        if not os.path.exists(voice_file):
            # No voice exists - create a generic one
            return {
                "tone": "professional",
                "personality": "Trustworthy, knowledgeable, and helpful",
                "language_style": "Clear, concise, and straightforward",
                "content_type_specific": f"Standard {content_type} best practices"
            }
        
        with open(voice_file, "r") as f:
            brand_voice = json.load(f)
        
        # Create a prompt to get content-specific guidelines
        prompt = f"""
        You have the following brand voice guide:
        
        {json.dumps(brand_voice, indent=2)}
        
        Now provide specific guidance for adapting this brand voice to {content_type} content{f' targeting {target_audience}' if target_audience else ''}.
        
        Include:
        1. Tone adaptations specific to this content type
        2. Language style recommendations
        3. Content structure guidance
        4. Any special considerations for this format
        
        Format as concise bullet points that can be directly used by a copywriter.
        """
        
        response = self.client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert in adapting brand voice guidelines to specific content formats."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            max_tokens=800
        )
        
        specific_guidelines = response.choices[0].message.content
        
        # Create the content-specific voice guide
        content_voice = {
            "tone": brand_voice.get("tone", "professional"),
            "personality": brand_voice.get("voice_characteristics", {}).get("personality", "Not specified"),
            "language_style": brand_voice.get("language_patterns", {}).get("style", "Not specified"),
            "content_type_specific": specific_guidelines
        }
        
        return content_voice
    
    def _parse_voice_guide(self, voice_text: str, product_name: str, tone: str) -> Dict[str, Any]:
        """
        Parse the voice guide text into a structured format.
        
        Args:
            voice_text: The voice guide text
            product_name: Product name
            tone: Desired tone
            
        Returns:
            Structured voice guide
        """
        # Use another LLM call to parse the text into structured format
        parse_prompt = f"""
        Parse the following brand voice guide into a structured JSON format:
        
        {voice_text}
        
        Convert it to a clean JSON structure with these main categories:
        - voice_characteristics
        - tone_specification
        - language_patterns
        - writing_style
        - examples
        
        Format as valid JSON only with no other text.
        """
        
        response = self.client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": "You are a precision parser that converts text into clean JSON format."},
                {"role": "user", "content": parse_prompt}
            ],
            temperature=0.1,
            max_tokens=1000
        )
        
        parsed_text = response.choices[0].message.content
        
        # Clean up the response to ensure it's valid JSON
        try:
            # Remove any markdown code block markers if present
            if "```json" in parsed_text:
                parsed_text = parsed_text.split("```json")[1].split("```")[0].strip()
            elif "```" in parsed_text:
                parsed_text = parsed_text.split("```")[1].split("```")[0].strip()
            
            parsed_guide = json.loads(parsed_text)
        except json.JSONDecodeError:
            # If parsing fails, create a basic structure
            parsed_guide = {
                "voice_characteristics": {
                    "adjectives": ["professional", "clear", "trustworthy"],
                    "personality": "Professional and trustworthy",
                    "audience_feel": "Confident and informed"
                },
                "tone_specification": {
                    "formality": "Generally professional with appropriate casual elements",
                    "emotional_range": "Moderate, emphasizing confidence and optimism",
                    "authority": "Knowledgeable but approachable"
                },
                "language_patterns": {
                    "sentence_structure": "Mix of medium and short sentences for readability",
                    "vocabulary": "Industry-appropriate but accessible",
                    "emphasized_words": ["quality", "results", "value"],
                    "words_to_use": ["discover", "enhance", "optimize"],
                    "words_to_avoid": ["cheap", "complicated", "difficult"]
                },
                "writing_style": {
                    "literary_devices": "Occasional metaphors to explain complex ideas",
                    "humor": "Light, professional humor where appropriate",
                    "audience_address": "Direct second-person (you/your)",
                    "punctuation": "Standard punctuation with occasional emphasis"
                },
                "examples": [
                    "Example 1: Standard marketing message",
                    "Example 2: Customer communication",
                    "Example 3: Technical explanation"
                ],
                "parsing_error": True
            }
        
        # Add metadata
        brand_voice = {
            "product_name": product_name,
            "tone": tone,
            "created_at": datetime.now().isoformat(),
            "version": 1,
            **parsed_guide
        }
        
        return brand_voice
    
    def _sanitize_filename(self, name: str) -> str:
        """
        Sanitize the product name for use in a filename.
        
        Args:
            name: Product name
            
        Returns:
            Sanitized filename
        """
        # Remove invalid characters and replace spaces with underscores
        invalid_chars = '<>:"/\\|?*'
        filename = ''.join(c for c in name if c not in invalid_chars)
        filename = filename.replace(' ', '_').lower()
        return filename