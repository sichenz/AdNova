"""
Task planning for the Marketing Ad Agent.
This module handles breaking down complex tasks into manageable steps.
"""
import time
from typing import Dict, Any, List, Optional

from config.settings import DEFAULT_MODEL, ANALYTICAL_TEMPERATURE

class TaskPlanner:
    """
    Plans and manages tasks for the Marketing Ad Agent.
    Breaks down complex tasks into manageable steps.
    """
    
    def __init__(self, client):
        """
        Initialize the task planner.
        
        Args:
            client: The OpenAI client
        """
        self.client = client
    
    def create_plan(self, task: str, **kwargs) -> Dict[str, Any]:
            """
            Create a task plan for a specific task.
            
            Args:
                task: The task to plan for
                **kwargs: Additional data needed for planning
                
            Returns:
                A dictionary containing the task plan
            """
            # Select the appropriate planning method based on the task
            if task == "generate_marketing_ad":
                return self._plan_ad_generation(kwargs.get("campaign_brief"), kwargs.get("ad_type"))
            elif task == "analyze_target_audience":
                return self._plan_audience_analysis(kwargs.get("target_audience"))
            elif task == "process_feedback":
                return self._plan_feedback_processing(kwargs.get("feedback"), kwargs.get("ad_record"))
            elif task == "generate_visual_content":
                return self._plan_visual_generation(kwargs.get("campaign_brief"), kwargs.get("content_type"))
            else:
                # Generic task planning
                return self._generic_task_planning(task, kwargs)
    
    def _plan_ad_generation(self, campaign_brief: Dict[str, Any], ad_type: str) -> Dict[str, Any]:
        """
        Create a plan for generating marketing ad content.
        
        Args:
            campaign_brief: The campaign brief
            ad_type: Type of ad to generate
            
        Returns:
            A dictionary containing the ad generation plan
        """
        prompt = f"""
        You are an expert marketing strategist. Create a detailed plan for generating a {ad_type} for the following product/service:
        
        Product/Service: {campaign_brief['product_name']}
        Description: {campaign_brief['description']}
        Target Audience: {campaign_brief['target_audience']}
        Campaign Goals: {campaign_brief['campaign_goals']}
        Tone: {campaign_brief.get('tone', 'professional')}
        Key Selling Points: {', '.join(campaign_brief.get('key_selling_points', []))}
        
        Create a step-by-step plan with 5-7 steps that outlines the approach to creating an effective {ad_type}.
        For each step, provide:
        1. The action to take
        2. A brief explanation of why this step is important
        
        Also provide:
        - 3-5 key messaging points to emphasize
        - 2-3 potential hooks or attention-grabbers
        - 1-2 effective call-to-action options
        """
        
        response = self.client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert marketing strategist who creates detailed, actionable plans for ad creation."},
                {"role": "user", "content": prompt}
            ],
            temperature=ANALYTICAL_TEMPERATURE,
            max_tokens=1000
        )
        
        plan_text = response.choices[0].message.content
        
        # Extract high-level summary
        summary_prompt = f"""
        Summarize the following marketing ad generation plan in 2-3 sentences:
        
        {plan_text}
        """
        
        summary_response = self.client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": "You are a concise summarizer."},
                {"role": "user", "content": summary_prompt}
            ],
            temperature=0.3,
            max_tokens=150
        )
        
        plan_summary = summary_response.choices[0].message.content
        
        return {
            "task": "generate_marketing_ad",
            "ad_type": ad_type,
            "detailed_plan": plan_text,
            "plan_summary": plan_summary,
            "created_at": time.time()
        }
    
    def _plan_visual_generation(self, campaign_brief: Dict[str, Any], content_type: str) -> Dict[str, Any]:
        """
        Create a plan for generating visual content (images or videos).
        
        Args:
            campaign_brief: The campaign brief
            content_type: Type of visual content to generate ("image", "video", or "both")
            
        Returns:
            A dictionary containing the visual generation plan
        """
        prompt = f"""
        You are an expert marketing strategist specializing in visual content. Create a detailed plan for generating {content_type} content for the following product/service:
        
        Product/Service: {campaign_brief['product_name']}
        Description: {campaign_brief['description']}
        Target Audience: {campaign_brief['target_audience']}
        Campaign Goals: {campaign_brief['campaign_goals']}
        Tone: {campaign_brief.get('tone', 'professional')}
        Key Selling Points: {', '.join(campaign_brief.get('key_selling_points', []))}
        
        Create a step-by-step plan with 5-7 steps that outlines the approach to creating effective marketing {content_type}s.
        For each step, provide:
        1. The action to take
        2. A brief explanation of why this step is important
        
        Also provide:
        - 3-5 key visual elements to include
        - 2-3 suggested visual styles or themes that would resonate with the target audience
        - Specific considerations for {content_type} content (such as composition for images or motion elements for videos)
        """
        
        response = self.client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": f"You are an expert visual marketing strategist who creates detailed, actionable plans for {content_type} content creation."},
                {"role": "user", "content": prompt}
            ],
            temperature=ANALYTICAL_TEMPERATURE,
            max_tokens=1000
        )
        
        plan_text = response.choices[0].message.content
        
        # Extract high-level summary
        summary_prompt = f"""
        Summarize the following marketing {content_type} generation plan in 2-3 sentences:
        
        {plan_text}
        """
        
        summary_response = self.client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": "You are a concise summarizer."},
                {"role": "user", "content": summary_prompt}
            ],
            temperature=0.3,
            max_tokens=150
        )
        
        plan_summary = summary_response.choices[0].message.content
        
        return {
            "task": f"generate_{content_type}_content",
            "content_type": content_type,
            "detailed_plan": plan_text,
            "plan_summary": plan_summary,
            "created_at": time.time()
        }
    
    def _plan_audience_analysis(self, target_audience: str) -> Dict[str, Any]:
        """
        Create a plan for analyzing a target audience.
        
        Args:
            target_audience: Description of the target audience
            
        Returns:
            A dictionary containing the audience analysis plan
        """
        prompt = f"""
        You are an expert market researcher. Create a detailed plan for analyzing the following target audience:
        
        Target Audience: {target_audience}
        
        Create a step-by-step plan with 4-6 steps that outlines how to analyze this audience to inform marketing decisions.
        For each step, provide:
        1. The analysis action to take
        2. A brief explanation of what insights this will provide
        
        Also identify:
        - 3-4 key demographic factors to consider
        - 2-3 potential psychographic characteristics to explore
        - 2-3 likely pain points or desires of this audience
        """
        
        response = self.client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert market researcher who creates detailed, actionable plans for audience analysis."},
                {"role": "user", "content": prompt}
            ],
            temperature=ANALYTICAL_TEMPERATURE,
            max_tokens=800
        )
        
        plan_text = response.choices[0].message.content
        
        # Extract high-level summary
        summary_prompt = f"""
        Summarize the following audience analysis plan in 2-3 sentences:
        
        {plan_text}
        """
        
        summary_response = self.client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": "You are a concise summarizer."},
                {"role": "user", "content": summary_prompt}
            ],
            temperature=0.3,
            max_tokens=150
        )
        
        plan_summary = summary_response.choices[0].message.content
        
        return {
            "task": "analyze_target_audience",
            "detailed_plan": plan_text,
            "plan_summary": plan_summary,
            "created_at": time.time()
        }
    
    def _plan_feedback_processing(self, feedback: str, ad_record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a plan for processing client feedback on an ad.
        
        Args:
            feedback: The client feedback
            ad_record: The ad record that received feedback
            
        Returns:
            A dictionary containing the feedback processing plan
        """
        prompt = f"""
        You are an expert in interpreting and implementing client feedback for marketing campaigns.
        Create a detailed plan for processing and implementing the following feedback on a marketing ad:
        
        Ad Type: {ad_record['ad_type']}
        Client Feedback: {feedback}
        
        Create a step-by-step plan with 3-5 steps that outlines how to interpret this feedback and improve the ad.
        For each step, provide:
        1. The action to take
        2. A brief explanation of how this addresses the feedback
        
        Also identify:
        - 2-3 key issues or concerns raised in the feedback
        - 2-3 specific elements of the ad to modify
        - 1-2 ways to preserve the original intent while incorporating changes
        """
        
        response = self.client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert in interpreting and implementing client feedback for marketing campaigns."},
                {"role": "user", "content": prompt}
            ],
            temperature=ANALYTICAL_TEMPERATURE,
            max_tokens=800
        )
        
        plan_text = response.choices[0].message.content
        
        # Extract high-level summary
        summary_prompt = f"""
        Summarize the following feedback processing plan in 2-3 sentences:
        
        {plan_text}
        """
        
        summary_response = self.client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": "You are a concise summarizer."},
                {"role": "user", "content": summary_prompt}
            ],
            temperature=0.3,
            max_tokens=150
        )
        
        plan_summary = summary_response.choices[0].message.content
        
        return {
            "task": "process_feedback",
            "detailed_plan": plan_text,
            "plan_summary": plan_summary,
            "created_at": time.time()
        }
    
    def _generic_task_planning(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a generic plan for any task.
        
        Args:
            task: The task to plan for
            context: Additional context for the task
            
        Returns:
            A dictionary containing the task plan
        """
        # Construct context string from the provided dictionary
        context_str = "\n".join([f"{k}: {v}" for k, v in context.items()])
        
        prompt = f"""
        You are an expert marketing professional. Create a detailed plan for the following task:
        
        Task: {task}
        
        Context:
        {context_str}
        
        Create a step-by-step plan with 3-7 steps that outlines how to accomplish this task effectively.
        For each step, provide:
        1. The action to take
        2. A brief explanation of why this step is important
        
        Also provide:
        - 2-3 key considerations for this task
        - 1-2 potential challenges and how to address them
        """
        
        response = self.client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert marketing professional who creates detailed, actionable plans."},
                {"role": "user", "content": prompt}
            ],
            temperature=ANALYTICAL_TEMPERATURE,
            max_tokens=800
        )
        
        plan_text = response.choices[0].message.content
        
        # Extract high-level summary
        summary_prompt = f"""
        Summarize the following task plan in 2-3 sentences:
        
        {plan_text}
        """
        
        summary_response = self.client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": "You are a concise summarizer."},
                {"role": "user", "content": summary_prompt}
            ],
            temperature=0.3,
            max_tokens=150
        )
        
        plan_summary = summary_response.choices[0].message.content
        
        return {
            "task": task,
            "detailed_plan": plan_text,
            "plan_summary": plan_summary,
            "created_at": time.time()
        }