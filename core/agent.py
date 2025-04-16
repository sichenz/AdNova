"""
Core implementation of the Marketing Ad Agent.
This module contains the main agent class that coordinates all components.
"""
import os
import json
import time
import uuid
from datetime import datetime

from config.settings import DEFAULT_MODEL, DEFAULT_TEMPERATURE, MAX_TOKENS
from core.memory import AgentMemory
from core.planning import TaskPlanner
from core.reflection import FeedbackProcessor
from tools.ad_generator import AdGenerator
from tools.audience_analyzer import AudienceAnalyzer
from tools.brand_voice import BrandVoiceManager
from tools.feedback_processor import ClientFeedbackProcessor
from tools.visual_generator import VisualGenerator
from utils.api_utils import get_openai_client
from utils.text_processing import summarize_text

class MarketingAdAgent:
    """
    The core agent class that coordinates all components of the marketing ad generation system.
    """
    
    def __init__(self, debug_mode=False):
        """
        Initialize the Marketing Ad Agent.
        
        Args:
            debug_mode (bool): Whether to run in debug mode with more verbose output.
        """
        self.debug_mode = debug_mode
        self.client = get_openai_client()
        self.memory = AgentMemory()
        self.planner = TaskPlanner(self.client)
        self.reflection = FeedbackProcessor(self.client)
        
        # Tools
        self.ad_generator = AdGenerator(self.client)
        self.audience_analyzer = AudienceAnalyzer(self.client)
        self.brand_voice_manager = BrandVoiceManager(self.client)
        self.feedback_processor = ClientFeedbackProcessor(self.client)
        self.visual_generator = VisualGenerator(self.client)
        
        # Session info
        self.session_id = str(uuid.uuid4())
        self.session_start_time = datetime.now()
        
        if self.debug_mode:
            print(f"Marketing Ad Agent initialized. Session ID: {self.session_id}")
    
    def create_campaign_brief(self, 
                             product_name, 
                             description, 
                             target_audience, 
                             campaign_goals,
                             tone="professional",
                             key_selling_points=None,
                             campaign_duration=None,
                             budget=None,
                             platform=None,
                             competitors=None,
                             additional_notes=None):
        """
        Create a comprehensive campaign brief from client inputs.
        
        Args:
            product_name (str): Name of the product or service
            description (str): Description of the product or service
            target_audience (str): Description of the target audience
            campaign_goals (str): Goals of the marketing campaign
            tone (str, optional): Desired tone for the ads
            key_selling_points (list, optional): Key selling points of the product
            campaign_duration (str, optional): Duration of the campaign
            budget (str, optional): Budget for the campaign
            platform (str, optional): Platform where ads will be displayed
            competitors (list, optional): Main competitors
            additional_notes (str, optional): Any additional information
            
        Returns:
            dict: The campaign brief
        """
        brief_id = str(uuid.uuid4())
        
        # Create the brief
        brief = {
            "brief_id": brief_id,
            "created_at": datetime.now().isoformat(),
            "product_name": product_name,
            "description": description,
            "target_audience": target_audience,
            "campaign_goals": campaign_goals,
            "tone": tone,
            "key_selling_points": key_selling_points or [],
            "campaign_duration": campaign_duration,
            "budget": budget,
            "platform": platform,
            "competitors": competitors or [],
            "additional_notes": additional_notes,
        }
        
        # Save the brief
        brief_file = os.path.join("data/campaign_briefs", f"{brief_id}.json")
        with open(brief_file, "w") as f:
            json.dump(brief, f, indent=2)
        
        # Analyze audience
        audience_insights = self.audience_analyzer.analyze(target_audience)
        brief["audience_insights"] = audience_insights
        
        # Add to memory
        self.memory.add_campaign_brief(brief)
        
        if self.debug_mode:
            print(f"Campaign brief created. ID: {brief_id}")
        
        return brief
    
    def generate_ad(self, campaign_brief, ad_type="social_media_post", variations=3):
        """
        Generate marketing ad content based on the campaign brief.
        
        Args:
            campaign_brief (dict): The campaign brief
            ad_type (str): Type of ad to generate
            variations (int): Number of variations to generate
            
        Returns:
            dict: Generated ad content with metadata
        """
        # Plan the ad generation task
        task_plan = self.planner.create_plan(
            task="generate_marketing_ad",
            campaign_brief=campaign_brief,
            ad_type=ad_type
        )
        
        if self.debug_mode:
            print(f"Task plan created: {task_plan['plan_summary']}")
        
        # Get brand voice
        brand_voice = self.brand_voice_manager.create_or_get_voice(
            product_name=campaign_brief["product_name"],
            description=campaign_brief["description"],
            tone=campaign_brief["tone"],
            target_audience=campaign_brief["target_audience"]
        )
        
        # Generate ad content
        ad_content = self.ad_generator.generate(
            brief=campaign_brief,
            ad_type=ad_type,
            variations=variations,
            brand_voice=brand_voice
        )
        
        # Create the ad record
        ad_id = str(uuid.uuid4())
        ad_record = {
            "ad_id": ad_id,
            "brief_id": campaign_brief["brief_id"],
            "created_at": datetime.now().isoformat(),
            "ad_type": ad_type,
            "variations": ad_content,
            "brand_voice_used": brand_voice,
            "task_plan": task_plan
        }
        
        # Save the ad
        ad_file = os.path.join("data/generated_ads", f"{ad_id}.json")
        with open(ad_file, "w") as f:
            json.dump(ad_record, f, indent=2)
        
        # Add to memory
        self.memory.add_generated_ad(ad_record)
        
        if self.debug_mode:
            print(f"Ad generated. ID: {ad_id}")
        
        return ad_record
    
    def generate_visual_content(self, 
                              campaign_brief, 
                              content_type="image", 
                              count=1, 
                              visual_theme=None,
                              width=None,
                              height=None,
                              prompt_override=None):
        """
        Generate visual content (images or videos) based on the campaign brief.
        
        Args:
            campaign_brief (dict): The campaign brief
            content_type (str): Type of visual content to generate ("image", "video", or "both")
            count (int): Number of visuals to generate of each type
            visual_theme (str, optional): Visual theme for the content
            width (int, optional): Width of the visual content
            height (int, optional): Height of the visual content
            prompt_override (str, optional): Override the automatic prompt generation
            
        Returns:
            dict: Generated visual content with metadata
        """
        # Plan the visual generation task
        task_plan = self.planner.create_plan(
            task="generate_visual_content",
            campaign_brief=campaign_brief,
            content_type=content_type
        )
        
        if self.debug_mode:
            print(f"Visual generation plan created: {task_plan['plan_summary']}")
        
        # Get custom prompt if not provided
        custom_prompt = prompt_override
        if not custom_prompt:
            prompt_response = self.client.chat.completions.create(
                model=DEFAULT_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert at creating prompts for AI image and video generation based on marketing briefs."},
                    {"role": "user", "content": f"Create a detailed prompt for generating a marketing {content_type} for the following product/service:\n\nProduct: {campaign_brief['product_name']}\nDescription: {campaign_brief['description']}\nTarget Audience: {campaign_brief['target_audience']}\nCampaign Goals: {campaign_brief['campaign_goals']}\nTone: {campaign_brief['tone']}\n\nThe prompt should be detailed and visually descriptive, focusing on what should be seen in the {content_type}. If this is a video prompt, include motion details."}
                ],
                temperature=CREATIVE_TEMPERATURE,
                max_tokens=300
            )
            custom_prompt = prompt_response.choices[0].message.content
        
        # Generate the visual content
        visuals = self.visual_generator.generate_marketing_visuals(
            campaign_brief=campaign_brief,
            content_type=content_type,
            count=count,
            visual_theme=visual_theme
        )
        
        # Create the visual content record
        visual_id = str(uuid.uuid4())
        visual_record = {
            "visual_id": visual_id,
            "brief_id": campaign_brief["brief_id"],
            "created_at": datetime.now().isoformat(),
            "content_type": content_type,
            "count": count,
            "visual_theme": visual_theme,
            "custom_prompt": custom_prompt,
            "visuals": visuals,
            "task_plan": task_plan
        }
        
        # Save the visual record
        visual_file = os.path.join("data/visual_content", f"{visual_id}.json")
        os.makedirs(os.path.dirname(visual_file), exist_ok=True)
        with open(visual_file, "w") as f:
            json.dump(visual_record, f, indent=2)
        
        if self.debug_mode:
            print(f"Visual content generated. ID: {visual_id}")
        
        return visual_record
    
    def generate_integrated_ad_campaign(self,
                                      campaign_brief,
                                      ad_types=None,
                                      include_images=True,
                                      include_videos=False,
                                      images_count=1,
                                      videos_count=1,
                                      ad_variations=2,
                                      visual_theme=None):
        """
        Generate a complete ad campaign with both textual and visual content.
        
        Args:
            campaign_brief (dict): The campaign brief
            ad_types (list): Types of ads to generate
            include_images (bool): Whether to include images
            include_videos (bool): Whether to include videos
            images_count (int): Number of images to generate
            videos_count (int): Number of videos to generate
            ad_variations (int): Number of variations for each ad type
            visual_theme (str, optional): Visual theme for consistency
            
        Returns:
            dict: Complete campaign with textual and visual content
        """
        # Default ad types if not specified
        if not ad_types:
            ad_types = ["social_media_post", "headline"]
        
        campaign_id = str(uuid.uuid4())
        
        # Generate text ads
        text_ads = {}
        for ad_type in ad_types:
            ad_record = self.generate_ad(
                campaign_brief=campaign_brief,
                ad_type=ad_type,
                variations=ad_variations
            )
            text_ads[ad_type] = ad_record
        
        # Generate visual content
        visual_content = {}
        
        # Generate images if requested
        if include_images and images_count > 0:
            image_record = self.generate_visual_content(
                campaign_brief=campaign_brief,
                content_type="image",
                count=images_count,
                visual_theme=visual_theme
            )
            visual_content["images"] = image_record
        
        # Generate videos if requested
        if include_videos and videos_count > 0:
            video_record = self.generate_visual_content(
                campaign_brief=campaign_brief,
                content_type="video",
                count=videos_count,
                visual_theme=visual_theme
            )
            visual_content["videos"] = video_record
        
        # Create the integrated campaign record
        campaign_record = {
            "campaign_id": campaign_id,
            "brief_id": campaign_brief["brief_id"],
            "created_at": datetime.now().isoformat(),
            "text_ads": text_ads,
            "visual_content": visual_content,
            "visual_theme": visual_theme
        }
        
        # Save the campaign record
        campaign_file = os.path.join("data/integrated_campaigns", f"{campaign_id}.json")
        os.makedirs(os.path.dirname(campaign_file), exist_ok=True)
        with open(campaign_file, "w") as f:
            json.dump(campaign_record, f, indent=2)
        
        if self.debug_mode:
            print(f"Integrated ad campaign generated. ID: {campaign_id}")
        
        return campaign_record
    
    def process_feedback(self, ad_id, feedback, score=None):
        """
        Process client feedback on a generated ad.
        
        Args:
            ad_id (str): ID of the ad
            feedback (str): Client feedback
            score (int, optional): Numerical score (1-10)
            
        Returns:
            dict: Processed feedback with improvement suggestions
        """
        # Get the ad record
        ad_file = os.path.join("data/generated_ads", f"{ad_id}.json")
        with open(ad_file, "r") as f:
            ad_record = json.load(f)
        
        # Get the campaign brief
        brief_file = os.path.join("data/campaign_briefs", f"{ad_record['brief_id']}.json")
        with open(brief_file, "r") as f:
            campaign_brief = json.load(f)
        
        # Process the feedback
        processed_feedback = self.feedback_processor.process(
            ad_record=ad_record,
            campaign_brief=campaign_brief,
            feedback=feedback,
            score=score
        )
        
        # Create feedback record
        feedback_id = str(uuid.uuid4())
        feedback_record = {
            "feedback_id": feedback_id,
            "ad_id": ad_id,
            "brief_id": ad_record["brief_id"],
            "created_at": datetime.now().isoformat(),
            "feedback": feedback,
            "score": score,
            "processed_feedback": processed_feedback
        }
        
        # Save the feedback
        feedback_file = os.path.join("data/feedback", f"{feedback_id}.json")
        with open(feedback_file, "w") as f:
            json.dump(feedback_record, f, indent=2)
        
        # Add to memory
        self.memory.add_feedback(feedback_record)
        
        # Trigger reflection
        self.reflection.reflect_on_feedback(
            ad_record=ad_record,
            campaign_brief=campaign_brief,
            feedback_record=feedback_record
        )
        
        if self.debug_mode:
            print(f"Feedback processed. ID: {feedback_id}")
        
        return feedback_record