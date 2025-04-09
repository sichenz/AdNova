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
    
    def regenerate_ad(self, ad_id, feedback_id=None, changes=None):
        """
        Regenerate an ad based on feedback or requested changes.
        
        Args:
            ad_id (str): ID of the original ad
            feedback_id (str, optional): ID of the feedback to incorporate
            changes (dict, optional): Specific changes to make
            
        Returns:
            dict: New ad record
        """
        # Get the original ad record
        ad_file = os.path.join("data/generated_ads", f"{ad_id}.json")
        with open(ad_file, "r") as f:
            original_ad = json.load(f)
        
        # Get the campaign brief
        brief_file = os.path.join("data/campaign_briefs", f"{original_ad['brief_id']}.json")
        with open(brief_file, "r") as f:
            campaign_brief = json.load(f)
        
        # Get feedback if provided
        feedback_data = None
        if feedback_id:
            feedback_file = os.path.join("data/feedback", f"{feedback_id}.json")
            with open(feedback_file, "r") as f:
                feedback_data = json.load(f)
        
        # Generate improved ad
        improved_ad = self.ad_generator.regenerate(
            original_ad=original_ad,
            campaign_brief=campaign_brief,
            feedback=feedback_data,
            changes=changes
        )
        
        # Create the new ad record
        new_ad_id = str(uuid.uuid4())
        new_ad_record = {
            "ad_id": new_ad_id,
            "brief_id": campaign_brief["brief_id"],
            "created_at": datetime.now().isoformat(),
            "ad_type": original_ad["ad_type"],
            "variations": improved_ad,
            "original_ad_id": ad_id,
            "feedback_id": feedback_id,
            "changes_requested": changes,
            "brand_voice_used": original_ad["brand_voice_used"]
        }
        
        # Save the new ad
        new_ad_file = os.path.join("data/generated_ads", f"{new_ad_id}.json")
        with open(new_ad_file, "w") as f:
            json.dump(new_ad_record, f, indent=2)
        
        # Add to memory
        self.memory.add_generated_ad(new_ad_record)
        
        if self.debug_mode:
            print(f"Ad regenerated. ID: {new_ad_id}")
        
        return new_ad_record
    
    def get_ad_recommendations(self, campaign_brief):
        """
        Get recommendations for ad types and approaches based on the campaign brief.
        
        Args:
            campaign_brief (dict): The campaign brief
            
        Returns:
            dict: Recommendations for the campaign
        """
        # Use audience insights to make recommendations
        audience_insights = campaign_brief.get("audience_insights", {})
        
        recommendations_prompt = f"""
        As a marketing expert, provide recommendations for ad types and approaches based on the following campaign brief:
        
        Product/Service: {campaign_brief['product_name']}
        Description: {campaign_brief['description']}
        Target Audience: {campaign_brief['target_audience']}
        Campaign Goals: {campaign_brief['campaign_goals']}
        Tone: {campaign_brief['tone']}
        Key Selling Points: {', '.join(campaign_brief['key_selling_points'])}
        Platform: {campaign_brief.get('platform', 'Not specified')}
        
        Audience Insights: {json.dumps(audience_insights, indent=2)}
        
        Provide the following recommendations:
        1. Best ad types for this campaign
        2. Recommended platforms
        3. Key messaging points
        4. Visual elements or imagery suggestions
        5. Call-to-action recommendations
        6. Best practices for this specific audience
        """
        
        response = self.client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[{"role": "system", "content": "You are a marketing strategy expert specializing in ad campaign optimization."},
                     {"role": "user", "content": recommendations_prompt}],
            temperature=DEFAULT_TEMPERATURE,
            max_tokens=MAX_TOKENS
        )
        
        recommendations = response.choices[0].message.content
        
        # Create recommendations record
        rec_id = str(uuid.uuid4())
        rec_record = {
            "recommendation_id": rec_id,
            "brief_id": campaign_brief["brief_id"],
            "created_at": datetime.now().isoformat(),
            "recommendations": recommendations
        }
        
        # Add to memory
        self.memory.add_recommendation(rec_record)
        
        return rec_record
    
    def export_campaign_assets(self, brief_id, format="json"):
        """
        Export all assets related to a campaign.
        
        Args:
            brief_id (str): ID of the campaign brief
            format (str): Export format (json, md, txt)
            
        Returns:
            str: Path to the exported file
        """
        # Get the campaign brief
        brief_file = os.path.join("data/campaign_briefs", f"{brief_id}.json")
        with open(brief_file, "r") as f:
            campaign_brief = json.load(f)
        
        # Get all ads for this brief
        ads = []
        for filename in os.listdir("data/generated_ads"):
            if filename.endswith(".json"):
                with open(os.path.join("data/generated_ads", filename), "r") as f:
                    ad = json.load(f)
                    if ad["brief_id"] == brief_id:
                        ads.append(ad)
        
        # Get all feedback for these ads
        feedback = []
        for filename in os.listdir("data/feedback"):
            if filename.endswith(".json"):
                with open(os.path.join("data/feedback", filename), "r") as f:
                    fb = json.load(f)
                    if fb["brief_id"] == brief_id:
                        feedback.append(fb)
        
        # Create export
        export = {
            "campaign_brief": campaign_brief,
            "ads": ads,
            "feedback": feedback,
            "exported_at": datetime.now().isoformat()
        }
        
        # Create exports directory if it doesn't exist
        os.makedirs("data/exports", exist_ok=True)
        
        # Save export
        export_path = os.path.join("data/exports", f"{brief_id}_export.{format}")
        
        if format == "json":
            with open(export_path, "w") as f:
                json.dump(export, f, indent=2)
        elif format == "md":
            with open(export_path, "w") as f:
                f.write(f"# Campaign Export: {campaign_brief['product_name']}\n\n")
                f.write(f"## Campaign Brief\n\n")
                f.write(f"**Product:** {campaign_brief['product_name']}\n")
                f.write(f"**Description:** {campaign_brief['description']}\n")
                f.write(f"**Target Audience:** {campaign_brief['target_audience']}\n")
                f.write(f"**Campaign Goals:** {campaign_brief['campaign_goals']}\n\n")
                
                f.write(f"## Generated Ads\n\n")
                for ad in ads:
                    f.write(f"### {ad['ad_type']} (ID: {ad['ad_id']})\n\n")
                    for i, variation in enumerate(ad['variations']):
                        f.write(f"**Variation {i+1}:**\n\n{variation}\n\n")
                
                f.write(f"## Feedback\n\n")
                for fb in feedback:
                    f.write(f"**Feedback on ad {fb['ad_id']}:**\n\n")
                    f.write(f"{fb['feedback']}\n\n")
                    if fb.get('score'):
                        f.write(f"Score: {fb['score']}/10\n\n")
        else:
            # Default to text format
            with open(export_path, "w") as f:
                f.write(f"Campaign Export: {campaign_brief['product_name']}\n\n")
                f.write(f"Campaign Brief:\n")
                f.write(f"Product: {campaign_brief['product_name']}\n")
                f.write(f"Description: {campaign_brief['description']}\n")
                f.write(f"Target Audience: {campaign_brief['target_audience']}\n")
                f.write(f"Campaign Goals: {campaign_brief['campaign_goals']}\n\n")
                
                f.write(f"Generated Ads:\n\n")
                for ad in ads:
                    f.write(f"{ad['ad_type']} (ID: {ad['ad_id']}):\n\n")
                    for i, variation in enumerate(ad['variations']):
                        f.write(f"Variation {i+1}:\n\n{variation}\n\n")
                
                f.write(f"Feedback:\n\n")
                for fb in feedback:
                    f.write(f"Feedback on ad {fb['ad_id']}:\n\n")
                    f.write(f"{fb['feedback']}\n\n")
                    if fb.get('score'):
                        f.write(f"Score: {fb['score']}/10\n\n")
        
        return export_path