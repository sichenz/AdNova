"""
Ad generation tool for the Marketing Ad Agent.
This module handles the generation of various types of marketing ad content.
"""
import json
import time
from typing import Dict, Any, List, Optional, Union

from config.settings import DEFAULT_MODEL, CREATIVE_TEMPERATURE, MAX_TOKENS, DEFAULT_AD_FORMATS, MAX_AD_VARIATIONS

class AdGenerator:
    """
    Generates various types of marketing ad content based on campaign briefs.
    """
    
    def __init__(self, client):
        """
        Initialize the ad generator.
        
        Args:
            client: The OpenAI client
        """
        self.client = client
        self.ad_formats = {
            "social_media_post": self._generate_social_media_post,
            "headline": self._generate_headline,
            "email_subject": self._generate_email_subject,
            "banner_copy": self._generate_banner_copy,
            "product_description": self._generate_product_description,
            "landing_page": self._generate_landing_page,
            "video_script": self._generate_video_script,
            "radio_ad": self._generate_radio_ad,
            "press_release": self._generate_press_release,
            "blog_post": self._generate_blog_post
        }
    
    def generate(self, 
                brief: Dict[str, Any], 
                ad_type: str = "social_media_post", 
                variations: int = 3,
                brand_voice: Dict[str, Any] = None) -> List[str]:
        """
        Generate marketing ad content based on the campaign brief.
        
        Args:
            brief: The campaign brief
            ad_type: Type of ad to generate
            variations: Number of variations to generate
            brand_voice: Brand voice characteristics
            
        Returns:
            List of generated ad variations
        """
        # Validate the ad type
        if ad_type not in self.ad_formats:
            raise ValueError(f"Unsupported ad type: {ad_type}. Supported types: {', '.join(self.ad_formats.keys())}")
        
        # Limit the number of variations
        variations = min(variations, MAX_AD_VARIATIONS)
        
        # Generate the ad content using the appropriate method
        ad_content = self.ad_formats[ad_type](brief, variations, brand_voice)
        
        return ad_content
    
    def regenerate(self, 
                 original_ad: Dict[str, Any], 
                 campaign_brief: Dict[str, Any], 
                 feedback: Optional[Dict[str, Any]] = None,
                 changes: Optional[Dict[str, Any]] = None) -> List[str]:
        """
        Regenerate or improve an existing ad based on feedback or requested changes.
        
        Args:
            original_ad: The original ad record
            campaign_brief: The campaign brief
            feedback: Feedback data (optional)
            changes: Specific changes to make (optional)
            
        Returns:
            List of improved ad variations
        """
        ad_type = original_ad["ad_type"]
        original_variations = original_ad["variations"]
        brand_voice = original_ad.get("brand_voice_used", {})
        
        # Construct the regeneration prompt
        feedback_text = ""
        if feedback:
            feedback_text = f"""
            Client Feedback:
            {feedback.get('feedback', '')}
            {f"Score: {feedback.get('score', 'Not provided')}/10" if feedback.get('score') else ""}
            
            Processed Feedback Insights:
            {json.dumps(feedback.get('processed_feedback', {}), indent=2)}
            """
        
        changes_text = ""
        if changes:
            changes_text = "Requested Changes:\n"
            for key, value in changes.items():
                changes_text += f"- {key}: {value}\n"
        
        original_text = "\n".join([f"Variation {i+1}: {v}" for i, v in enumerate(original_variations)])
        
        prompt = f"""
        You are an expert marketing copywriter. Your task is to improve the following {ad_type} based on the client feedback and/or requested changes.
        
        ORIGINAL CONTENT:
        {original_text}
        
        CAMPAIGN INFORMATION:
        Product/Service: {campaign_brief['product_name']}
        Description: {campaign_brief['description']}
        Target Audience: {campaign_brief['target_audience']}
        Campaign Goals: {campaign_brief['campaign_goals']}
        Tone: {campaign_brief.get('tone', 'professional')}
        Key Selling Points: {', '.join(campaign_brief.get('key_selling_points', []))}
        
        {feedback_text}
        {changes_text}
        
        Create {len(original_variations)} improved variations of the {ad_type} that address the feedback and requested changes while maintaining the core message and brand voice.
        
        For each variation:
        1. Keep what worked well in the original
        2. Address the issues raised in the feedback or implement the requested changes
        3. Ensure the tone and messaging align with the campaign goals and target audience
        
        Present each variation clearly numbered.
        """
        
        response = self.client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert marketing copywriter specializing in creating compelling ad content."},
                {"role": "user", "content": prompt}
            ],
            temperature=CREATIVE_TEMPERATURE,
            max_tokens=MAX_TOKENS
        )
        
        content = response.choices[0].message.content
        
        # Parse the variations
        improved_variations = self._parse_variations(content, len(original_variations))
        
        return improved_variations
    
    def _generate_social_media_post(self, 
                                  brief: Dict[str, Any], 
                                  variations: int = 3,
                                  brand_voice: Dict[str, Any] = None) -> List[str]:
        """
        Generate social media post content.
        
        Args:
            brief: The campaign brief
            variations: Number of variations to generate
            brand_voice: Brand voice characteristics
            
        Returns:
            List of social media post variations
        """
        # Prepare brand voice text
        brand_voice_text = ""
        if brand_voice:
            brand_voice_text = f"""
            Brand Voice:
            Tone: {brand_voice.get('tone', brief.get('tone', 'professional'))}
            Personality: {brand_voice.get('personality', 'Not specified')}
            Language Style: {brand_voice.get('language_style', 'Not specified')}
            """
        
        # Build the platform-specific instructions
        platform = brief.get('platform', '').lower()
        platform_instructions = ""
        
        if 'instagram' in platform:
            platform_instructions = """
            Platform: Instagram
            - Create engaging, visually descriptive content
            - Include 5-7 relevant hashtags
            - Keep the post concise but impactful
            - Consider how the post would complement a visual
            """
        elif 'facebook' in platform:
            platform_instructions = """
            Platform: Facebook
            - Create conversational and engaging content
            - Can be slightly longer than Instagram posts
            - Include a clear call-to-action
            - Consider how to encourage comments and shares
            """
        elif 'twitter' in platform or 'x' in platform:
            platform_instructions = """
            Platform: Twitter/X
            - Keep posts under 280 characters
            - Make it punchy and direct
            - Include 1-2 relevant hashtags
            - Consider adding a question or call-to-action to encourage engagement
            """
        elif 'linkedin' in platform:
            platform_instructions = """
            Platform: LinkedIn
            - Maintain a professional tone
            - Focus on industry relevance and business value
            - Can be longer and more detailed than other platforms
            - Include professional insights or statistics when relevant
            """
        else:
            platform_instructions = """
            Platform: General social media
            - Create versatile content that works across platforms
            - Include a compelling hook and clear call-to-action
            - Keep the messaging concise and impactful
            - Consider how to make the content shareable
            """
        
        prompt = f"""
        Create {variations} compelling social media post variations for the following product/service:
        
        Product/Service: {brief['product_name']}
        Description: {brief['description']}
        Target Audience: {brief['target_audience']}
        Campaign Goals: {brief['campaign_goals']}
        Key Selling Points: {', '.join(brief.get('key_selling_points', []))}
        
        {brand_voice_text}
        
        {platform_instructions}
        
        Each post should:
        1. Grab attention with a compelling hook
        2. Highlight a key benefit or feature
        3. Include a clear call-to-action
        4. Match the specified tone and brand voice
        5. Resonate with the target audience
        
        Present each variation clearly numbered.
        """
        
        response = self.client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert social media copywriter who specializes in creating engaging, platform-optimized content."},
                {"role": "user", "content": prompt}
            ],
            temperature=CREATIVE_TEMPERATURE,
            max_tokens=MAX_TOKENS
        )
        
        content = response.choices[0].message.content
        
        # Parse the variations
        post_variations = self._parse_variations(content, variations)
        
        return post_variations
    
    def _generate_headline(self, 
                         brief: Dict[str, Any], 
                         variations: int = 3,
                         brand_voice: Dict[str, Any] = None) -> List[str]:
        """
        Generate headline content.
        
        Args:
            brief: The campaign brief
            variations: Number of variations to generate
            brand_voice: Brand voice characteristics
            
        Returns:
            List of headline variations
        """
        # Prepare brand voice text
        brand_voice_text = ""
        if brand_voice:
            brand_voice_text = f"""
            Brand Voice:
            Tone: {brand_voice.get('tone', brief.get('tone', 'professional'))}
            Personality: {brand_voice.get('personality', 'Not specified')}
            Language Style: {brand_voice.get('language_style', 'Not specified')}
            """
        
        headline_type = "general"
        if "awareness" in brief.get('campaign_goals', '').lower():
            headline_type = "awareness"
        elif "conversion" in brief.get('campaign_goals', '').lower():
            headline_type = "conversion"
        elif "promotional" in brief.get('campaign_goals', '').lower():
            headline_type = "promotional"
        
        headline_instructions = ""
        if headline_type == "awareness":
            headline_instructions = """
            Headline Type: Awareness/Brand Building
            - Focus on conveying the brand's value proposition
            - Create intrigue or emotional connection
            - Emphasize what makes the brand unique
            """
        elif headline_type == "conversion":
            headline_instructions = """
            Headline Type: Conversion/Direct Response
            - Create a sense of urgency or necessity
            - Clearly state the value proposition
            - Use action-oriented language
            """
        elif headline_type == "promotional":
            headline_instructions = """
            Headline Type: Promotional/Sales
            - Highlight offers, discounts, or limited-time opportunities
            - Use numbers when relevant (e.g., "50% Off")
            - Create a sense of urgency or exclusivity
            """
        
        prompt = f"""
        Create {variations} compelling headline variations for the following product/service:
        
        Product/Service: {brief['product_name']}
        Description: {brief['description']}
        Target Audience: {brief['target_audience']}
        Campaign Goals: {brief['campaign_goals']}
        Key Selling Points: {', '.join(brief.get('key_selling_points', []))}
        
        {brand_voice_text}
        
        {headline_instructions}
        
        Each headline should:
        1. Be concise and impactful (ideally under 10 words)
        2. Capture the primary benefit or unique selling proposition
        3. Use powerful, evocative language
        4. Match the specified tone and brand voice
        5. Resonate with the target audience
        
        Present each variation clearly numbered.
        """
        
        response = self.client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert copywriter who specializes in creating compelling, attention-grabbing headlines."},
                {"role": "user", "content": prompt}
            ],
            temperature=CREATIVE_TEMPERATURE,
            max_tokens=MAX_TOKENS
        )
        
        content = response.choices[0].message.content
        
        # Parse the variations
        headline_variations = self._parse_variations(content, variations)
        
        return headline_variations
    
    def _generate_email_subject(self, 
                              brief: Dict[str, Any], 
                              variations: int = 3,
                              brand_voice: Dict[str, Any] = None) -> List[str]:
        """
        Generate email subject line content.
        
        Args:
            brief: The campaign brief
            variations: Number of variations to generate
            brand_voice: Brand voice characteristics
            
        Returns:
            List of email subject line variations
        """
        # Prepare brand voice text
        brand_voice_text = ""
        if brand_voice:
            brand_voice_text = f"""
            Brand Voice:
            Tone: {brand_voice.get('tone', brief.get('tone', 'professional'))}
            Personality: {brand_voice.get('personality', 'Not specified')}
            Language Style: {brand_voice.get('language_style', 'Not specified')}
            """
        
        email_type = "general"
        if "newsletter" in brief.get('campaign_goals', '').lower():
            email_type = "newsletter"
        elif "promotional" in brief.get('campaign_goals', '').lower():
            email_type = "promotional"
        elif "announcement" in brief.get('campaign_goals', '').lower():
            email_type = "announcement"
        
        email_instructions = ""
        if email_type == "newsletter":
            email_instructions = """
            Email Type: Newsletter
            - Focus on providing value and information
            - Create interest without seeming too promotional
            - Emphasize relevance to the recipient
            """
        elif email_type == "promotional":
            email_instructions = """
            Email Type: Promotional
            - Highlight offers, discounts, or limited-time opportunities
            - Create a sense of urgency or exclusivity
            - Make the value proposition immediately clear
            """
        elif email_type == "announcement":
            email_instructions = """
            Email Type: Announcement
            - Create excitement or anticipation
            - Clearly indicate that something new or important is happening
            - Use language that suggests insider information or exclusive news
            """
        
        prompt = f"""
        Create {variations} compelling email subject line variations for the following product/service:
        
        Product/Service: {brief['product_name']}
        Description: {brief['description']}
        Target Audience: {brief['target_audience']}
        Campaign Goals: {brief['campaign_goals']}
        Key Selling Points: {', '.join(brief.get('key_selling_points', []))}
        
        {brand_voice_text}
        
        {email_instructions}
        
        Each subject line should:
        1. Be concise (under 50 characters is ideal)
        2. Create immediate interest or curiosity
        3. Avoid spam trigger words
        4. Match the specified tone and brand voice
        5. Provide a compelling reason to open the email
        
        Present each variation clearly numbered.
        """
        
        response = self.client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert email marketer who specializes in creating high-performing subject lines with strong open rates."},
                {"role": "user", "content": prompt}
            ],
            temperature=CREATIVE_TEMPERATURE,
            max_tokens=MAX_TOKENS
        )
        
        content = response.choices[0].message.content
        
        # Parse the variations
        subject_variations = self._parse_variations(content, variations)
        
        return subject_variations
    
    def _generate_banner_copy(self, 
                            brief: Dict[str, Any], 
                            variations: int = 3,
                            brand_voice: Dict[str, Any] = None) -> List[str]:
        """
        Generate banner ad copy.
        
        Args:
            brief: The campaign brief
            variations: Number of variations to generate
            brand_voice: Brand voice characteristics
            
        Returns:
            List of banner copy variations
        """
        # Prepare brand voice text
        brand_voice_text = ""
        if brand_voice:
            brand_voice_text = f"""
            Brand Voice:
            Tone: {brand_voice.get('tone', brief.get('tone', 'professional'))}
            Personality: {brand_voice.get('personality', 'Not specified')}
            Language Style: {brand_voice.get('language_style', 'Not specified')}
            """
        
        banner_type = "general"
        if "display" in brief.get('platform', '').lower():
            banner_type = "display"
        elif "retargeting" in brief.get('campaign_goals', '').lower():
            banner_type = "retargeting"
        
        banner_instructions = ""
        if banner_type == "display":
            banner_instructions = """
            Banner Type: Display Ad
            - Create immediate visual impact with words
            - Focus on a single clear message
            - Use concise, powerful language
            """
        elif banner_type == "retargeting":
            banner_instructions = """
            Banner Type: Retargeting Ad
            - Create a sense of familiarity
            - Address potential hesitations
            - Include a clear incentive to return/convert
            """
        else:
            banner_instructions = """
            Banner Type: General
            - Create immediate impact with minimal words
            - Focus on a single clear message
            - Include a compelling call-to-action
            """
        
        prompt = f"""
        Create {variations} compelling banner ad copy variations for the following product/service:
        
        Product/Service: {brief['product_name']}
        Description: {brief['description']}
        Target Audience: {brief['target_audience']}
        Campaign Goals: {brief['campaign_goals']}
        Key Selling Points: {', '.join(brief.get('key_selling_points', []))}
        
        {brand_voice_text}
        
        {banner_instructions}
        
        For each variation, provide:
        1. Headline (5-7 words maximum)
        2. Subheading/supporting text (optional, 5-10 words)
        3. Call-to-action button text (2-4 words)
        
        Each banner variation should:
        - Create immediate visual impact through words
        - Focus on a single key benefit or message
        - Use powerful, evocative language
        - Include a compelling call-to-action
        
        Present each variation clearly numbered.
        """
        
        response = self.client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert digital advertising copywriter who specializes in creating high-converting banner ad copy."},
                {"role": "user", "content": prompt}
            ],
            temperature=CREATIVE_TEMPERATURE,
            max_tokens=MAX_TOKENS
        )
        
        content = response.choices[0].message.content
        
        # Parse the variations
        banner_variations = self._parse_variations(content, variations)
        
        return banner_variations
    
    def _generate_product_description(self, 
                                    brief: Dict[str, Any], 
                                    variations: int = 3,
                                    brand_voice: Dict[str, Any] = None) -> List[str]:
        """
        Generate product description content.
        
        Args:
            brief: The campaign brief
            variations: Number of variations to generate
            brand_voice: Brand voice characteristics
            
        Returns:
            List of product description variations
        """
        # Implementation follows similar pattern to methods above
        # Prepare brand voice text
        brand_voice_text = ""
        if brand_voice:
            brand_voice_text = f"""
            Brand Voice:
            Tone: {brand_voice.get('tone', brief.get('tone', 'professional'))}
            Personality: {brand_voice.get('personality', 'Not specified')}
            Language Style: {brand_voice.get('language_style', 'Not specified')}
            """
        
        prompt = f"""
        Create {variations} compelling product description variations for the following product/service:
        
        Product/Service: {brief['product_name']}
        Description: {brief['description']}
        Target Audience: {brief['target_audience']}
        Campaign Goals: {brief['campaign_goals']}
        Key Selling Points: {', '.join(brief.get('key_selling_points', []))}
        
        {brand_voice_text}
        
        Each product description should:
        1. Open with an engaging hook
        2. Highlight the key benefits and features
        3. Address the target audience's needs and pain points
        4. Include sensory and descriptive language
        5. End with a subtle call-to-action
        6. Be approximately 150-200 words
        
        Present each variation clearly numbered.
        """
        
        response = self.client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert product copywriter who specializes in creating compelling, benefit-focused product descriptions."},
                {"role": "user", "content": prompt}
            ],
            temperature=CREATIVE_TEMPERATURE,
            max_tokens=MAX_TOKENS
        )
        
        content = response.choices[0].message.content
        
        # Parse the variations
        desc_variations = self._parse_variations(content, variations)
        
        return desc_variations
    
    # The following methods would be implemented similarly to the above
    def _generate_landing_page(self, brief, variations, brand_voice):
        # Simplified implementation - would be more detailed in production
        return self._generate_generic_content("landing page", brief, variations, brand_voice)
    
    def _generate_video_script(self, brief, variations, brand_voice):
        return self._generate_generic_content("video script", brief, variations, brand_voice)
    
    def _generate_radio_ad(self, brief, variations, brand_voice):
        return self._generate_generic_content("radio ad", brief, variations, brand_voice)
    
    def _generate_press_release(self, brief, variations, brand_voice):
        return self._generate_generic_content("press release", brief, variations, brand_voice)
    
    def _generate_blog_post(self, brief, variations, brand_voice):
        return self._generate_generic_content("blog post", brief, variations, brand_voice)
    
    def _generate_generic_content(self, content_type, brief, variations, brand_voice):
        """Generic content generation method for types not fully implemented"""
        # Prepare brand voice text
        brand_voice_text = ""
        if brand_voice:
            brand_voice_text = f"""
            Brand Voice:
            Tone: {brand_voice.get('tone', brief.get('tone', 'professional'))}
            Personality: {brand_voice.get('personality', 'Not specified')}
            Language Style: {brand_voice.get('language_style', 'Not specified')}
            """
        
        prompt = f"""
        Create {variations} compelling {content_type} variations for the following product/service:
        
        Product/Service: {brief['product_name']}
        Description: {brief['description']}
        Target Audience: {brief['target_audience']}
        Campaign Goals: {brief['campaign_goals']}
        Key Selling Points: {', '.join(brief.get('key_selling_points', []))}
        
        {brand_voice_text}
        
        Each {content_type} should:
        1. Engage the target audience effectively
        2. Highlight the key benefits and features
        3. Address the target audience's needs and pain points
        4. Match the specified tone and brand voice
        5. Include a clear call-to-action
        
        Present each variation clearly numbered.
        """
        
        response = self.client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": f"You are an expert copywriter who specializes in creating compelling {content_type} content."},
                {"role": "user", "content": prompt}
            ],
            temperature=CREATIVE_TEMPERATURE,
            max_tokens=MAX_TOKENS
        )
        
        content = response.choices[0].message.content
        
        # Parse the variations
        content_variations = self._parse_variations(content, variations)
        
        return content_variations
    
    def _parse_variations(self, content: str, expected_count: int) -> List[str]:
        """
        Parse the variations from the LLM response.
        
        Args:
            content: The content from the LLM
            expected_count: Expected number of variations
            
        Returns:
            List of parsed variations
        """
        variations = []
        
        # Split by variation numbers and clean up
        lines = content.split("\n")
        current_variation = ""
        current_number = 1
        
        for line in lines:
            # Check if this line starts a new variation
            starts_new = False
            
            # Check different numbering formats
            if line.strip().startswith(f"{current_number}.") or \
               line.strip().startswith(f"Variation {current_number}:") or \
               line.strip().startswith(f"Variation {current_number}.") or \
               line.strip() == f"Variation {current_number}" or \
               line.strip() == f"{current_number}":
                starts_new = True
            
            if starts_new:
                # Save the previous variation if it exists
                if current_variation and current_number > 1:
                    variations.append(current_variation.strip())
                
                # Start a new variation
                current_variation = line.split(":", 1)[1].strip() if ":" in line else ""
                current_number += 1
            else:
                # Continue with the current variation
                if current_variation or line.strip():  # Only append if we have content or the line isn't empty
                    current_variation += "\n" + line if current_variation else line
        
        # Add the last variation
        if current_variation:
            variations.append(current_variation.strip())
        
        # If parsing didn't work well, try a more aggressive approach
        if len(variations) < expected_count:
            variations = []
            
            # Force split by variation numbers
            for i in range(1, expected_count + 1):
                marker_options = [
                    f"{i}.", 
                    f"Variation {i}:", 
                    f"Variation {i}.", 
                    f"Variation {i}"
                ]
                
                # Find where this variation starts
                start_idx = -1
                for marker in marker_options:
                    for idx, line in enumerate(lines):
                        if line.strip().startswith(marker):
                            start_idx = idx
                            break
                    if start_idx != -1:
                        break
                
                if start_idx == -1:
                    continue
                
                # Find where the next variation starts
                end_idx = len(lines)
                if i < expected_count:
                    for j in range(start_idx + 1, len(lines)):
                        for next_marker in [f"{i+1}.", f"Variation {i+1}:", f"Variation {i+1}.", f"Variation {i+1}"]:
                            if lines[j].strip().startswith(next_marker):
                                end_idx = j
                                break
                        if end_idx != len(lines):
                            break
                
                # Extract the variation content
                var_content = "\n".join(lines[start_idx:end_idx])
                
                # Clean up the content
                for marker in marker_options:
                    if var_content.strip().startswith(marker):
                        var_content = var_content.replace(marker, "", 1).strip()
                        break
                
                variations.append(var_content.strip())
        
        # If we still don't have enough variations, just split the content evenly
        if len(variations) < expected_count:
            content_parts = content.split("\n\n")
            variations = content_parts[:expected_count]
        
        # Ensure we have the expected number of variations
        while len(variations) < expected_count:
            variations.append("Content generation failed. Please try again.")
        
        return variations[:expected_count]