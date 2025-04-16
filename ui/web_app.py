"""
Web application for the Marketing Ad Agent.
This module provides a web-based interface for interacting with the agent.
"""
import os
import sys
import json
import time
from datetime import datetime
from typing import Dict, Any, List, Optional, Union

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from config.settings import APP_NAME, APP_VERSION, TONE_OPTIONS, AUDIENCE_SEGMENTS, CAMPAIGN_TYPES, WEB_UI_TITLE

def run_web_app(agent):
    """
    Run the web application.
    
    Args:
        agent: The MarketingAdAgent instance
    """
    # Set page config
    st.set_page_config(
        page_title=WEB_UI_TITLE,
        page_icon="📝",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Store the agent in session state
    if "agent" not in st.session_state:
        st.session_state.agent = agent
    
    # Initialize session state variables
    if "current_tab" not in st.session_state:
        st.session_state.current_tab = "Create Brief"
    
    if "created_brief_id" not in st.session_state:
        st.session_state.created_brief_id = None
    
    if "generated_ad_id" not in st.session_state:
        st.session_state.generated_ad_id = None
    
    # Set up the sidebar navigation
    with st.sidebar:
        st.title(f"{WEB_UI_TITLE}")
        st.caption(f"v{APP_VERSION}")
        
        st.subheader("Navigation")
        tabs = [
            "Create Brief",
            "Generate Ads",
            "Visual Content",
            "View Ads",
            "Feedback & Improvement",
            "Analytics & Insights",
            "Export"
        ]
        
        for tab in tabs:
            if st.button(tab, key=f"btn_{tab}", use_container_width=True):
                st.session_state.current_tab = tab
        
        st.divider()
        st.markdown("### About")
        st.markdown("""
        AdNova uses advanced LLM technology to generate marketing ad content. We have been trained to help you with
        
        - Creating campaign briefs
        - Generating various ad formats
        - Getting audience insights
        - Improving ads with feedback
        """)
    
    # Main content area
    if st.session_state.current_tab == "Create Brief":
        display_create_brief_tab()
    elif st.session_state.current_tab == "Generate Ads":
        display_generate_ads_tab()
    elif st.session_state.current_tab == "Visual Content":
        display_visual_content_tab()
    elif st.session_state.current_tab == "View Ads":
        display_view_ads_tab()
    elif st.session_state.current_tab == "Feedback & Improvement":
        display_feedback_tab()
    elif st.session_state.current_tab == "Analytics & Insights":
        display_analytics_tab()
    elif st.session_state.current_tab == "Export":
        display_export_tab()

def display_create_brief_tab():
    """Display the Create Campaign Brief tab."""
    st.header("Create Campaign Brief")
    st.markdown("Define your marketing campaign details to get started. The brief will be used to generate targeted ad content.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        with st.form("campaign_brief_form"):
            st.subheader("Campaign Details")
            
            product_name = st.text_input("Product/Service Name *", help="Name of the product or service being advertised")
            
            description = st.text_area("Product/Service Description *", 
                                       height=100, 
                                       help="Detailed description of the product or service")
            
            st.subheader("Audience & Goals")
            
            target_audience = st.text_area("Target Audience *", 
                                          height=80, 
                                          help="Describe your target audience (demographics, interests, behaviors)")
            
            campaign_goals = st.text_area("Campaign Goals *", 
                                         height=80, 
                                         help="What you want to achieve with this campaign (awareness, conversions, etc.)")
            
            st.subheader("Additional Information")
            
            col_a, col_b = st.columns(2)
            
            with col_a:
                tone = st.selectbox("Tone", 
                                   options=[""] + TONE_OPTIONS,
                                   format_func=lambda x: x.capitalize() if x else "Select Tone",
                                   help="The tone of voice for your ad content")
                
                campaign_duration = st.text_input("Campaign Duration", 
                                                 help="How long will the campaign run (e.g., '2 weeks')")
            
            with col_b:
                platform = st.text_input("Platform/Media", 
                                        help="Where the ads will be displayed (e.g., 'Facebook, Instagram')")
                
                budget = st.text_input("Budget", 
                                      help="Campaign budget (optional)")
            
            # Key selling points with dynamic addition
            st.subheader("Key Selling Points")
            
            if "selling_points" not in st.session_state:
                st.session_state.selling_points = [""]
            
            for i, point in enumerate(st.session_state.selling_points):
                col_point, col_btn = st.columns([5, 1])
                with col_point:
                    st.session_state.selling_points[i] = st.text_input(
                        f"Point {i+1}", 
                        value=point,
                        key=f"ksp_{i}"
                    )
            
            point_cols = st.columns([5, 1, 5])
            # with point_cols[0]:
            #     if st.button("+ Add Selling Point"):
            #         st.session_state.selling_points.append("")
            #         st.rerun()
            
            # with point_cols[1]:
            #     if len(st.session_state.selling_points) > 1 and st.button("- Remove"):
            #         st.session_state.selling_points.pop()
            #         st.rerun()
            
            # Competitors
            st.subheader("Competitors")
            
            if "competitors" not in st.session_state:
                st.session_state.competitors = [""]
            
            for i, competitor in enumerate(st.session_state.competitors):
                col_comp, col_btn = st.columns([5, 1])
                with col_comp:
                    st.session_state.competitors[i] = st.text_input(
                        f"Competitor {i+1}", 
                        value=competitor,
                        key=f"comp_{i}"
                    )
            
            comp_cols = st.columns([5, 1, 5])
            # with comp_cols[0]:
            #     if st.button("+ Add Competitor"):
            #         st.session_state.competitors.append("")
            #         st.rerun()
            
            # with comp_cols[1]:
            #     if len(st.session_state.competitors) > 1 and st.button("- Remove Competitor"):
            #         st.session_state.competitors.pop()
            #         st.rerun()
            
            additional_notes = st.text_area("Additional Notes", 
                                           height=80, 
                                           help="Any other information about the campaign")
            
            submitted = st.form_submit_button("Create Campaign Brief", use_container_width=True)
            
            if submitted:
                if not product_name or not description or not target_audience or not campaign_goals:
                    st.error("Please fill in all required fields (marked with *).")
                else:
                    with st.spinner("Creating campaign brief and analyzing audience..."):
                        # Filter out empty values
                        key_selling_points = [p for p in st.session_state.selling_points if p]
                        competitors = [c for c in st.session_state.competitors if c]
                        
                        # Create the brief
                        brief = st.session_state.agent.create_campaign_brief(
                            product_name=product_name,
                            description=description,
                            target_audience=target_audience,
                            campaign_goals=campaign_goals,
                            tone=tone if tone else "professional",
                            key_selling_points=key_selling_points,
                            campaign_duration=campaign_duration,
                            budget=budget,
                            platform=platform,
                            competitors=competitors,
                            additional_notes=additional_notes
                        )
                        
                        st.session_state.created_brief_id = brief["brief_id"]
                        st.success(f"Campaign brief created successfully! (ID: {brief['brief_id']})")
                        
                        # Display button to go to ad generation
                        st.button("Generate Ads for this Campaign", on_click=lambda: setattr(st.session_state, 'current_tab', 'Generate Ads'))
    
    with col2:
        st.subheader("What You'll Get")
        st.info("""
        Creating a campaign brief will:
        
        1. Store your campaign details
        2. Analyze your target audience
        3. Provide audience insights
        4. Enable ad generation
        """)
        
        st.subheader("Tips for Better Results")
        st.success("""
        - Be specific about your target audience
        - Clearly define your campaign goals
        - Include distinctive selling points
        - Specify preferred tone and platforms
        """)
        
        # Display audience insights if brief was just created
        if st.session_state.created_brief_id:
            try:
                brief_file = os.path.join("data/campaign_briefs", f"{st.session_state.created_brief_id}.json")
                if os.path.exists(brief_file):
                    with open(brief_file, "r") as f:
                        brief = json.load(f)
                        
                        if 'audience_insights' in brief and 'analysis' in brief['audience_insights']:
                            with st.expander("View Audience Insights", expanded=True):
                                st.subheader("Audience Insights")
                                
                                analysis = brief['audience_insights']['analysis']
                                
                                # Display demographics
                                if 'demographics' in analysis:
                                    st.markdown("##### Demographics")
                                    demo = analysis['demographics']
                                    demo_text = ""
                                    
                                    if 'age_range' in demo and demo['age_range'] and demo['age_range'] != "Not specified":
                                        demo_text += f"**Age:** {demo['age_range']}\n\n"
                                    
                                    if 'gender_distribution' in demo and demo['gender_distribution'] and demo['gender_distribution'] != "Not specified":
                                        demo_text += f"**Gender:** {demo['gender_distribution']}\n\n"
                                    
                                    if 'income_level' in demo and demo['income_level'] and demo['income_level'] != "Not specified":
                                        demo_text += f"**Income:** {demo['income_level']}\n\n"
                                    
                                    if 'education_level' in demo and demo['education_level'] and demo['education_level'] != "Not specified":
                                        demo_text += f"**Education:** {demo['education_level']}\n\n"
                                    
                                    if 'location' in demo and demo['location'] and demo['location'] != "Not specified":
                                        demo_text += f"**Location:** {demo['location']}\n\n"
                                    
                                    st.markdown(demo_text)
                                
                                # Display psychographics
                                if 'psychographics' in analysis and 'values_and_beliefs' in analysis['psychographics']:
                                    st.markdown("##### Psychographics")
                                    
                                    values = analysis['psychographics'].get('values_and_beliefs', [])
                                    if values and values[0] != "Not specified":
                                        st.markdown("**Values & Beliefs:**")
                                        for value in values[:3]:
                                            st.markdown(f"- {value}")
                                    
                                    interests = analysis['psychographics'].get('interests_and_hobbies', [])
                                    if interests and interests[0] != "Not specified":
                                        st.markdown("**Interests:**")
                                        for interest in interests[:3]:
                                            st.markdown(f"- {interest}")
                                
                                # Display pain points
                                if 'pain_points_and_needs' in analysis and 'challenges' in analysis['pain_points_and_needs']:
                                    st.markdown("##### Pain Points & Needs")
                                    
                                    challenges = analysis['pain_points_and_needs'].get('challenges', [])
                                    if challenges and challenges[0] != "Not specified":
                                        for challenge in challenges[:3]:
                                            st.markdown(f"- {challenge}")
                                
                                # Display recommendations
                                if 'recommendations' in brief['audience_insights']:
                                    with st.expander("Marketing Recommendations"):
                                        recommendations = brief['audience_insights']['recommendations']
                                        
                                        if 'messaging_strategy' in recommendations:
                                            st.markdown("**Messaging Strategy:**")
                                            for rec in recommendations['messaging_strategy'][:3]:
                                                st.markdown(f"- {rec}")
                                        
                                        if 'channel_strategy' in recommendations:
                                            st.markdown("**Channel Strategy:**")
                                            for rec in recommendations['channel_strategy'][:3]:
                                                st.markdown(f"- {rec}")
            except Exception as e:
                st.warning(f"Could not load audience insights: {str(e)}")

def display_generate_ads_tab():
    """Display the Generate Ads tab."""
    st.header("Generate Marketing Ads")
    st.markdown("Generate compelling ad content for your marketing campaigns.")
    
    # Check if there are any campaign briefs
    briefs_dir = "data/campaign_briefs"
    if not os.path.exists(briefs_dir) or not os.listdir(briefs_dir):
        st.warning("No campaign briefs found. Please create a campaign brief first.")
        if st.button("Create Campaign Brief"):
            st.session_state.current_tab = "Create Brief"
        return
    
    # Load all campaign briefs
    briefs = []
    for filename in os.listdir(briefs_dir):
        if filename.endswith(".json"):
            with open(os.path.join(briefs_dir, filename), "r") as f:
                brief = json.load(f)
                briefs.append(brief)
    
    # Sort briefs by creation date (newest first)
    briefs.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        with st.form("generate_ads_form"):
            st.subheader("Ad Generation Settings")
            
            # Campaign brief selection
            brief_options = {brief['brief_id']: f"{brief['product_name']} (Created: {brief.get('created_at', 'Unknown')})" for brief in briefs}
            selected_brief_id = st.selectbox(
                "Select Campaign Brief",
                options=list(brief_options.keys()),
                format_func=lambda x: brief_options[x],
                index=0 if st.session_state.created_brief_id not in brief_options else list(brief_options.keys()).index(st.session_state.created_brief_id)
            )
            
            # Get the selected brief
            selected_brief = next((b for b in briefs if b['brief_id'] == selected_brief_id), None)
            
            if selected_brief:
                st.markdown("##### Campaign Summary")
                st.markdown(f"**Product:** {selected_brief['product_name']}")
                st.markdown(f"**Target Audience:** {selected_brief['target_audience'][:100]}...")
                st.markdown(f"**Goals:** {selected_brief['campaign_goals'][:100]}...")
            
            # Ad type selection
            ad_types = [
                "social_media_post", "headline", "email_subject", "banner_copy",
                "product_description", "landing_page", "video_script", "radio_ad",
                "press_release", "blog_post"
            ]
            
            ad_type_names = {
                "social_media_post": "Social Media Post",
                "headline": "Headline/Title",
                "email_subject": "Email Subject Line",
                "banner_copy": "Banner Ad Copy",
                "product_description": "Product Description",
                "landing_page": "Landing Page Content",
                "video_script": "Video Script",
                "radio_ad": "Radio Ad Script",
                "press_release": "Press Release",
                "blog_post": "Blog Post"
            }
            
            selected_ad_type = st.selectbox(
                "Ad Type",
                options=ad_types,
                format_func=lambda x: ad_type_names.get(x, x.replace("_", " ").title())
            )
            
            # Number of variations
            variations = st.slider("Number of Variations", min_value=1, max_value=5, value=3)
            
            # Generation button
            generate_submitted = st.form_submit_button("Generate Ads", use_container_width=True)
            
            if generate_submitted:
                if not selected_brief:
                    st.error("Please select a valid campaign brief.")
                else:
                    with st.spinner(f"Generating {variations} {ad_type_names.get(selected_ad_type, selected_ad_type)} variations..."):
                        try:
                            # Generate the ads
                            ad_record = st.session_state.agent.generate_ad(
                                campaign_brief=selected_brief,
                                ad_type=selected_ad_type,
                                variations=variations
                            )
                            
                            st.session_state.generated_ad_id = ad_record["ad_id"]
                            st.success(f"Ad generation complete! (ID: {ad_record['ad_id']})")
                            
                            # Display the generated ads
                            st.subheader("Generated Ad Variations")
                            for i, variation in enumerate(ad_record['variations'], 1):
                                with st.expander(f"Variation {i}", expanded=(i==1)):
                                    st.markdown(variation)
                                    st.button(f"Copy Variation {i}", key=f"copy_var_{i}", on_click=lambda v=variation: st.write(v))
                            
                            # Display button to view all ads
                            st.button("View All Generated Ads", on_click=lambda: setattr(st.session_state, 'current_tab', 'View Ads'))
                        
                        except Exception as e:
                            st.error(f"Error generating ads: {str(e)}")
    
    with col2:
        st.subheader("Ad Type Information")
        
        # Ad type descriptions
        ad_type_info = {
            "social_media_post": {
                "description": "Short, engaging content optimized for social platforms.",
                "best_for": "Brand awareness, engagement, and community building.",
                "typical_length": "50-280 characters depending on platform.",
                "tips": "Include a hook, clear value proposition, and call-to-action."
            },
            "headline": {
                "description": "Attention-grabbing titles that convey the main message.",
                "best_for": "Ads, landing pages, articles, and email campaigns.",
                "typical_length": "5-10 words, concise and impactful.",
                "tips": "Focus on benefits, create curiosity, or address pain points."
            },
            "email_subject": {
                "description": "Compelling email subject lines to improve open rates.",
                "best_for": "Email marketing campaigns and newsletters.",
                "typical_length": "30-50 characters for optimal display.",
                "tips": "Create urgency, ask questions, or promise value."
            },
            "banner_copy": {
                "description": "Concise text for display ads with clear CTAs.",
                "best_for": "Digital advertising across websites and platforms.",
                "typical_length": "Headline: 5-7 words, CTA: 2-4 words.",
                "tips": "Focus on a single message and compelling visual language."
            },
            "product_description": {
                "description": "Detailed, benefit-focused description of products.",
                "best_for": "E-commerce sites, catalogs, and product pages.",
                "typical_length": "100-300 words depending on complexity.",
                "tips": "Highlight features and benefits, use sensory language."
            }
        }
        
        # Display info for the selected ad type
        if selected_ad_type in ad_type_info:
            info = ad_type_info[selected_ad_type]
            st.info(f"""
            **{ad_type_names.get(selected_ad_type, selected_ad_type.replace("_", " ").title())}**
            
            {info['description']}
            
            **Best for:** {info['best_for']}
            
            **Typical length:** {info['typical_length']}
            
            **Tips:** {info['tips']}
            """)
        
        st.subheader("Tips for Better Results")
        st.success("""
        - Choose the right ad type for your campaign goals
        - More variations give you more options to test
        - Review and provide feedback to improve future generations
        - Consider your target platform's requirements
        """)
        
        # Show recently generated ads
        ads_dir = "data/generated_ads"
        if os.path.exists(ads_dir) and os.listdir(ads_dir):
            with st.expander("Recently Generated Ads"):
                # Get recent ads
                recent_ads = []
                for filename in os.listdir(ads_dir):
                    if filename.endswith(".json"):
                        with open(os.path.join(ads_dir, filename), "r") as f:
                            ad = json.load(f)
                            
                            # Get brief info
                            brief_file = os.path.join("data/campaign_briefs", f"{ad['brief_id']}.json")
                            product_name = "Unknown Product"
                            if os.path.exists(brief_file):
                                with open(brief_file, "r") as bf:
                                    brief = json.load(bf)
                                    product_name = brief['product_name']
                            
                            recent_ads.append({
                                "ad_id": ad["ad_id"],
                                "product_name": product_name,
                                "ad_type": ad_type_names.get(ad["ad_type"], ad["ad_type"].replace("_", " ").title()),
                                "created_at": ad.get("created_at", "Unknown date")
                            })
                
                # Sort by creation date (newest first)
                recent_ads.sort(key=lambda x: x["created_at"], reverse=True)
                
                # Display recent ads
                for ad in recent_ads[:5]:
                    st.markdown(f"**{ad['product_name']}** - {ad['ad_type']} ({ad['created_at'][:10]})")

def display_visual_content_tab():
    """Display the Visual Content tab for generating images and videos."""
    st.header("Generate Visual Content")
    st.markdown("Create compelling images and videos for your marketing campaigns using state-of-the-art AI models.")
    
    # Check if CUDA is available
    import torch
    cuda_available = torch.cuda.is_available()
    
    if not cuda_available:
        st.warning("⚠️ No GPU with CUDA detected. Visual generation will use placeholders only. For full functionality, please run on a system with a compatible GPU.")
    
    # Check if there are any campaign briefs
    briefs_dir = "data/campaign_briefs"
    if not os.path.exists(briefs_dir) or not os.listdir(briefs_dir):
        st.warning("No campaign briefs found. Please create a campaign brief first.")
        if st.button("Create Campaign Brief"):
            st.session_state.current_tab = "Create Brief"
        return
    
    # Load all campaign briefs
    briefs = []
    for filename in os.listdir(briefs_dir):
        if filename.endswith(".json"):
            with open(os.path.join(briefs_dir, filename), "r") as f:
                brief = json.load(f)
                briefs.append(brief)
    
    # Sort briefs by creation date (newest first)
    briefs.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        with st.form("generate_visuals_form"):
            st.subheader("Visual Content Settings")
            
            # Campaign brief selection
            brief_options = {brief['brief_id']: f"{brief['product_name']} (Created: {brief.get('created_at', 'Unknown')[:10]})" for brief in briefs}
            selected_brief_id = st.selectbox(
                "Select Campaign Brief",
                options=list(brief_options.keys()),
                format_func=lambda x: brief_options[x],
                index=0 if not hasattr(st.session_state, 'created_brief_id') or st.session_state.created_brief_id not in brief_options 
                      else list(brief_options.keys()).index(st.session_state.created_brief_id)
            )
            
            # Get the selected brief
            selected_brief = next((b for b in briefs if b['brief_id'] == selected_brief_id), None)
            
            if selected_brief:
                st.markdown("##### Campaign Summary")
                st.markdown(f"**Product:** {selected_brief['product_name']}")
                st.markdown(f"**Target Audience:** {selected_brief['target_audience'][:100]}...")
            
            # Visual content type selection
            content_type = st.radio(
                "Content Type",
                options=["Images Only", "Videos Only", "Both Images and Videos"],
                horizontal=True
            )
            
            # Number of visuals
            col_img, col_vid = st.columns(2)
            
            with col_img:
                if content_type in ["Images Only", "Both Images and Videos"]:
                    images_count = st.slider(
                        "Number of Images", 
                        min_value=1, 
                        max_value=5, 
                        value=1,
                        disabled=content_type == "Videos Only"
                    )
                else:
                    images_count = 0
            
            with col_vid:
                if content_type in ["Videos Only", "Both Images and Videos"]:
                    videos_count = st.slider(
                        "Number of Videos", 
                        min_value=1, 
                        max_value=3, 
                        value=1,
                        disabled=content_type == "Images Only"
                    )
                else:
                    videos_count = 0
            
            # Visual theme selection
            from config.settings import VISUAL_THEMES
            visual_theme = st.selectbox(
                "Visual Theme",
                options=[""] + VISUAL_THEMES,
                format_func=lambda x: "No specific theme" if not x else x
            )
            
            # Custom prompt (optional)
            with st.expander("Advanced Options"):
                custom_prompt = st.text_area(
                    "Custom Prompt (Optional)",
                    help="Leave blank to automatically generate a prompt based on the campaign brief",
                    height=100
                )
                
                # Image size options (if generating images)
                if content_type in ["Images Only", "Both Images and Videos"]:
                    st.markdown("##### Image Size")
                    img_size_options = {
                        "square": "Square (1:1) - 1024x1024",
                        "portrait": "Portrait (3:4) - 768x1024",
                        "landscape": "Landscape (16:9) - 1024x576"
                    }
                    img_size = st.radio(
                        "Image Aspect Ratio",
                        options=list(img_size_options.keys()),
                        format_func=lambda x: img_size_options[x],
                        horizontal=True
                    )
                
                # Video size options (if generating videos)
                if content_type in ["Videos Only", "Both Images and Videos"]:
                    st.markdown("##### Video Size")
                    video_size_options = {
                        "widescreen": "Widescreen (16:9) - 848x480",
                        "square": "Square (1:1) - 512x512",
                        "vertical": "Vertical (9:16) - 480x848"
                    }
                    video_size = st.radio(
                        "Video Aspect Ratio",
                        options=list(video_size_options.keys()),
                        format_func=lambda x: video_size_options[x],
                        horizontal=True
                    )
            
            # Warning about generation time
            if content_type in ["Videos Only", "Both Images and Videos"]:
                st.info("⏱️ Video generation can take several minutes per video depending on available GPU resources.")
            
            # Generation button
            generate_submitted = st.form_submit_button("Generate Visual Content", use_container_width=True)
            
            if generate_submitted:
                if not selected_brief:
                    st.error("Please select a valid campaign brief.")
                elif content_type == "Images Only" and images_count < 1:
                    st.error("Please select at least one image to generate.")
                elif content_type == "Videos Only" and videos_count < 1:
                    st.error("Please select at least one video to generate.")
                else:
                    # Determine content type parameter
                    content_type_param = "image" if content_type == "Images Only" else "video" if content_type == "Videos Only" else "both"
                    
                    # Set image dimensions based on selection
                    if content_type in ["Images Only", "Both Images and Videos"]:
                        if img_size == "square":
                            img_width, img_height = 1024, 1024
                        elif img_size == "portrait":
                            img_width, img_height = 768, 1024
                        elif img_size == "landscape":
                            img_width, img_height = 1024, 576
                    
                    # Set video dimensions based on selection
                    if content_type in ["Videos Only", "Both Images and Videos"]:
                        if video_size == "widescreen":
                            video_width, video_height = 848, 480
                        elif video_size == "square":
                            video_width, video_height = 512, 512
                        elif video_size == "vertical":
                            video_width, video_height = 480, 848
                    
                    with st.spinner("Generating visual content... This may take a few minutes."):
                        try:
                            # Generate the visual content
                            visual_record = st.session_state.agent.generate_visual_content(
                                campaign_brief=selected_brief,
                                content_type=content_type_param,
                                count=max(images_count if content_type != "Videos Only" else 0, 
                                         videos_count if content_type != "Images Only" else 0),
                                visual_theme=visual_theme if visual_theme else None,
                                prompt_override=custom_prompt if custom_prompt else None
                            )
                            
                            st.session_state.generated_visual_id = visual_record["visual_id"]
                            st.success(f"Visual content generation complete! (ID: {visual_record['visual_id']})")
                            
                            # Display the generated visuals
                            st.subheader("Generated Visual Content")
                            
                            # Display images
                            if content_type in ["Images Only", "Both Images and Videos"] and "visuals" in visual_record:
                                image_visuals = [v for v in visual_record["visuals"] if "image_id" in v]
                                if image_visuals:
                                    st.markdown("### Generated Images")
                                    image_cols = st.columns(min(3, len(image_visuals)))
                                    
                                    for i, img_visual in enumerate(image_visuals):
                                        col_idx = i % len(image_cols)
                                        with image_cols[col_idx]:
                                            if os.path.exists(img_visual["output_path"]):
                                                st.image(img_visual["output_path"], caption=f"Image {i+1}")
                                                st.download_button(
                                                    f"Download Image {i+1}", 
                                                    open(img_visual["output_path"], "rb"), 
                                                    file_name=f"marketing_image_{i+1}.png"
                                                )
                                            else:
                                                st.warning(f"Image file not found: {img_visual['output_path']}")
                            
                            # Display videos
                            if content_type in ["Videos Only", "Both Images and Videos"] and "visuals" in visual_record:
                                video_visuals = [v for v in visual_record["visuals"] if "video_id" in v]
                                if video_visuals:
                                    st.markdown("### Generated Videos")
                                    for i, vid_visual in enumerate(video_visuals):
                                        if os.path.exists(vid_visual["output_path"]):
                                            st.video(vid_visual["output_path"])
                                            st.download_button(
                                                f"Download Video {i+1}", 
                                                open(vid_visual["output_path"], "rb"), 
                                                file_name=f"marketing_video_{i+1}.mp4"
                                            )
                                        else:
                                            st.warning(f"Video file not found: {vid_visual['output_path']}")
                        
                        except Exception as e:
                            st.error(f"Error generating visual content: {str(e)}")
    
    with col2:
        st.subheader("Visual Content Information")
        
        # Visual models information
        with st.expander("About the AI Models", expanded=True):
            st.markdown("""
            **Image Generation**: Stable Diffusion 3.5 Large
            - State-of-the-art text-to-image model
            - High quality image generation
            - Strong typography capabilities
            - Excellent prompt adherence
            
            **Video Generation**: Mochi 1
            - Advanced text-to-video model
            - High-fidelity motion
            - Strong prompt adherence
            - 31-84 frames per video
            """)
        
        st.subheader("Tips for Better Results")
        st.success("""
        **For Better Visual Content:**
        
        - Choose visual themes that match your brand identity
        - Select aspect ratios appropriate for your platform
        - Images work well for print, social media posts, and banners
        - Videos are great for social media ads, stories, and web headers
        
        **Prompt Tips:**
        - Be specific about what should be in the scene
        - Describe lighting, style, and mood
        - Mention your product or service prominently
        - For videos, describe motion and temporal progression
        """)
        
        # Show recently generated visuals
        visual_dir = "data/visual_content"
        if os.path.exists(visual_dir) and os.listdir(visual_dir):
            with st.expander("Recently Generated Visuals"):
                # Get recent visual records
                recent_visuals = []
                for filename in os.listdir(visual_dir):
                    if filename.endswith(".json"):
                        with open(os.path.join(visual_dir, filename), "r") as f:
                            visual = json.load(f)
                            
                            # Get brief info
                            brief_file = os.path.join("data/campaign_briefs", f"{visual['brief_id']}.json")
                            product_name = "Unknown Product"
                            if os.path.exists(brief_file):
                                with open(brief_file, "r") as bf:
                                    brief = json.load(bf)
                                    product_name = brief['product_name']
                            
                            recent_visuals.append({
                                "visual_id": visual["visual_id"],
                                "product_name": product_name,
                                "content_type": visual["content_type"],
                                "created_at": visual.get("created_at", "Unknown date")
                            })
                
                # Sort by creation date (newest first)
                recent_visuals.sort(key=lambda x: x["created_at"], reverse=True)
                
                # Display recent visuals
                for visual in recent_visuals[:5]:
                    st.markdown(f"**{visual['product_name']}** - {visual['content_type']} ({visual['created_at'][:10]})")
                    
def display_view_ads_tab():
    """Display the View Ads tab."""
    st.header("View Generated Ads")
    st.markdown("Browse and review previously generated marketing ads.")
    
    # Check if there are any ads
    ads_dir = "data/generated_ads"
    if not os.path.exists(ads_dir) or not os.listdir(ads_dir):
        st.warning("No ads found. Please generate ads first.")
        if st.button("Generate Ads"):
            st.session_state.current_tab = "Generate Ads"
        return
    
    # Load all ads and group by campaign
    ads_by_campaign = {}
    
    for filename in os.listdir(ads_dir):
        if filename.endswith(".json"):
            with open(os.path.join(ads_dir, filename), "r") as f:
                ad = json.load(f)
                
                # Get brief info
                brief_id = ad['brief_id']
                brief_file = os.path.join("data/campaign_briefs", f"{brief_id}.json")
                
                if os.path.exists(brief_file):
                    with open(brief_file, "r") as bf:
                        brief = json.load(bf)
                        
                        if brief_id not in ads_by_campaign:
                            ads_by_campaign[brief_id] = {
                                "brief": brief,
                                "ads": []
                            }
                        
                        ads_by_campaign[brief_id]["ads"].append(ad)
    
    # Create tabs for each campaign
    if not ads_by_campaign:
        st.warning("No ads with valid campaign briefs found.")
        return
    
    campaign_tabs = st.tabs([f"{campaign['brief']['product_name']} ({len(campaign['ads'])})" for campaign in ads_by_campaign.values()])
    
    # Display ads for each campaign
    for i, (brief_id, campaign) in enumerate(ads_by_campaign.items()):
        with campaign_tabs[i]:
            st.subheader(f"Campaign: {campaign['brief']['product_name']}")
            
            # Campaign info
            with st.expander("Campaign Brief"):
                st.markdown(f"**Product:** {campaign['brief']['product_name']}")
                st.markdown(f"**Description:** {campaign['brief']['description']}")
                st.markdown(f"**Target Audience:** {campaign['brief']['target_audience']}")
                st.markdown(f"**Campaign Goals:** {campaign['brief']['campaign_goals']}")
                
                if 'key_selling_points' in campaign['brief'] and campaign['brief']['key_selling_points']:
                    st.markdown("**Key Selling Points:**")
                    for point in campaign['brief']['key_selling_points']:
                        st.markdown(f"- {point}")
            
            # Sort ads by creation date (newest first)
            ads = campaign['ads']
            ads.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            
            # Group ads by type
            ad_types = {}
            for ad in ads:
                ad_type = ad['ad_type'].replace('_', ' ').title()
                if ad_type not in ad_types:
                    ad_types[ad_type] = []
                ad_types[ad_type].append(ad)
            
            # Create columns for ad types
            col1, col2 = st.columns(2)
            
            # Display ad type sections
            col_index = 0
            for ad_type, type_ads in ad_types.items():
                # Alternate between columns
                with col1 if col_index % 2 == 0 else col2:
                    st.markdown(f"##### {ad_type} ({len(type_ads)})")
                    
                    for ad in type_ads:
                        with st.expander(f"{ad_type} (Created: {ad.get('created_at', 'Unknown')[:10]})"):
                            for i, variation in enumerate(ad['variations'], 1):
                                st.markdown(f"**Variation {i}:**")
                                st.markdown(variation)
                                st.markdown("---")
                            
                            # Action buttons
                            col_view, col_feedback, col_regen = st.columns(3)
                            
                            with col_view:
                                # Mark selected ad for reference in other tabs
                                if st.button("Select", key=f"select_{ad['ad_id']}"):
                                    st.session_state.selected_ad_id = ad['ad_id']
                                    st.info("Ad selected for reference in other tabs.")
                            
                            with col_feedback:
                                if st.button("Give Feedback", key=f"feedback_{ad['ad_id']}"):
                                    st.session_state.selected_ad_id = ad['ad_id']
                                    st.session_state.current_tab = "Feedback & Improvement"
                            
                            with col_regen:
                                if st.button("Regenerate", key=f"regen_{ad['ad_id']}"):
                                    st.session_state.selected_ad_id = ad['ad_id']
                                    st.session_state.current_tab = "Feedback & Improvement"
                
                col_index += 1

def display_feedback_tab():
    """Display the Feedback & Improvement tab."""
    st.header("Feedback & Improvement")
    st.markdown("Provide feedback on generated ads and create improved versions.")
    
    tabs = st.tabs(["Give Feedback", "Regenerate Ads", "Improvement History"])
    
    # GIVE FEEDBACK TAB
    with tabs[0]:
        st.subheader("Provide Feedback on Ads")
        
        # Check if there are any ads
        ads_dir = "data/generated_ads"
        if not os.path.exists(ads_dir) or not os.listdir(ads_dir):
            st.warning("No ads found. Please generate ads first.")
            return
        
        # Load all ads
        ads = []
        for filename in os.listdir(ads_dir):
            if filename.endswith(".json"):
                with open(os.path.join(ads_dir, filename), "r") as f:
                    ad = json.load(f)
                    
                    # Get brief info
                    brief_file = os.path.join("data/campaign_briefs", f"{ad['brief_id']}.json")
                    product_name = "Unknown Product"
                    if os.path.exists(brief_file):
                        with open(brief_file, "r") as bf:
                            brief = json.load(bf)
                            product_name = brief['product_name']
                    
                    ads.append({
                        "ad": ad,
                        "product_name": product_name
                    })
        
        # Sort ads by creation date (newest first)
        ads.sort(key=lambda x: x['ad'].get('created_at', ''), reverse=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Ad selection
            ad_options = {ad['ad']['ad_id']: f"{ad['product_name']} - {ad['ad']['ad_type'].replace('_', ' ').title()}" for ad in ads}
            
            selected_ad_id = st.selectbox(
                "Select Ad to Review",
                options=list(ad_options.keys()),
                format_func=lambda x: ad_options[x],
                index=0 if not hasattr(st.session_state, 'selected_ad_id') or st.session_state.selected_ad_id not in ad_options 
                      else list(ad_options.keys()).index(st.session_state.selected_ad_id)
            )
            
            # Get the selected ad
            selected_item = next((item for item in ads if item['ad']['ad_id'] == selected_ad_id), None)
            
            if selected_item:
                selected_ad = selected_item['ad']
                
                # Display the ad
                st.markdown(f"##### {selected_ad['ad_type'].replace('_', ' ').title()} for {selected_item['product_name']}")
                
                for i, variation in enumerate(selected_ad['variations'], 1):
                    with st.expander(f"Variation {i}", expanded=(i==1)):
                        st.markdown(variation)
                
                # Feedback form
                with st.form("feedback_form"):
                    st.subheader("Your Feedback")
                    
                    feedback_text = st.text_area("What do you think about this ad? What works well? What could be improved?", height=150)
                    score = st.slider("Score (1-10)", min_value=1, max_value=10, value=7)
                    
                    submitted = st.form_submit_button("Submit Feedback", use_container_width=True)
                    
                    if submitted:
                        if not feedback_text:
                            st.error("Please provide feedback text.")
                        else:
                            with st.spinner("Processing feedback..."):
                                try:
                                    # Process the feedback
                                    feedback_record = st.session_state.agent.process_feedback(
                                        ad_id=selected_ad_id,
                                        feedback=feedback_text,
                                        score=score
                                    )
                                    
                                    st.success("Feedback submitted successfully!")
                                    
                                    # Display processed feedback
                                    if 'processed_feedback' in feedback_record and 'analysis' in feedback_record['processed_feedback']:
                                        analysis = feedback_record['processed_feedback']['analysis']
                                        
                                        st.subheader("Feedback Analysis")
                                        
                                        col_a, col_b = st.columns(2)
                                        
                                        with col_a:
                                            if 'sentiment' in analysis:
                                                st.markdown(f"**Overall Sentiment:** {analysis['sentiment']}")
                                            
                                            if 'key_issues' in analysis and analysis['key_issues']:
                                                st.markdown("**Key Issues Identified:**")
                                                for issue in analysis['key_issues']:
                                                    st.markdown(f"- {issue}")
                                        
                                        with col_b:
                                            if 'positive_aspects' in analysis and analysis['positive_aspects']:
                                                st.markdown("**Positive Aspects:**")
                                                for aspect in analysis['positive_aspects']:
                                                    st.markdown(f"- {aspect}")
                                        
                                        st.markdown("**Suggested Improvements:**")
                                        if 'suggested_improvements' in analysis and analysis['suggested_improvements']:
                                            for improvement in analysis['suggested_improvements']:
                                                st.markdown(f"- {improvement}")
                                        
                                        # Button to regenerate
                                        if st.button("Regenerate Based on Feedback"):
                                            st.session_state.selected_ad_id = selected_ad_id
                                            st.session_state.selected_feedback_id = feedback_record["feedback_id"]
                                            st.experimental_rerun()
                                
                                except Exception as e:
                                    st.error(f"Error processing feedback: {str(e)}")
        
        with col2:
            st.subheader("Feedback Tips")
            st.info("""
            **Effective Feedback:**
            
            - Be specific about what works and what doesn't
            - Focus on both content and tone
            - Relate feedback to campaign goals
            - Consider the target audience
            - Suggest alternatives when possible
            
            Your feedback helps improve future generations.
            """)
            
            # Show feedback history if available
            feedback_dir = "data/feedback"
            if os.path.exists(feedback_dir) and os.listdir(feedback_dir):
                with st.expander("Recent Feedback History"):
                    # Get recent feedback
                    recent_feedback = []
                    for filename in os.listdir(feedback_dir):
                        if filename.endswith(".json"):
                            with open(os.path.join(feedback_dir, filename), "r") as f:
                                feedback = json.load(f)
                                
                                # Get ad info
                                ad_file = os.path.join("data/generated_ads", f"{feedback['ad_id']}.json")
                                if os.path.exists(ad_file):
                                    with open(ad_file, "r") as af:
                                        ad = json.load(af)
                                        ad_type = ad['ad_type'].replace('_', ' ').title()
                                        
                                        recent_feedback.append({
                                            "feedback_id": feedback["feedback_id"],
                                            "ad_id": feedback["ad_id"],
                                            "ad_type": ad_type,
                                            "score": feedback.get("score", "N/A"),
                                            "created_at": feedback.get("created_at", "Unknown date")
                                        })
                    
                    # Sort by creation date (newest first)
                    recent_feedback.sort(key=lambda x: x["created_at"], reverse=True)
                    
                    # Display recent feedback
                    for fb in recent_feedback[:5]:
                        st.markdown(f"**{fb['ad_type']}** - Score: {fb['score']}/10 ({fb['created_at'][:10]})")
    
    # REGENERATE ADS TAB
    with tabs[1]:
        st.subheader("Regenerate Improved Ads")
        
        # Check if there are any feedback records
        feedback_dir = "data/feedback"
        if not os.path.exists(feedback_dir) or not os.listdir(feedback_dir):
            st.warning("No feedback found. Please provide feedback on ads first.")
            return
        
        # Load feedback records
        feedback_records = []
        for filename in os.listdir(feedback_dir):
            if filename.endswith(".json"):
                with open(os.path.join(feedback_dir, filename), "r") as f:
                    feedback = json.load(f)
                    
                    # Get ad info
                    ad_file = os.path.join("data/generated_ads", f"{feedback['ad_id']}.json")
                    if os.path.exists(ad_file):
                        with open(ad_file, "r") as af:
                            ad = json.load(af)
                            
                            # Get brief info
                            brief_file = os.path.join("data/campaign_briefs", f"{ad['brief_id']}.json")
                            product_name = "Unknown Product"
                            if os.path.exists(brief_file):
                                with open(brief_file, "r") as bf:
                                    brief = json.load(bf)
                                    product_name = brief['product_name']
                            
                            feedback_records.append({
                                "feedback": feedback,
                                "ad": ad,
                                "product_name": product_name
                            })
        
        # Sort feedback by creation date (newest first)
        feedback_records.sort(key=lambda x: x['feedback'].get('created_at', ''), reverse=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Feedback selection
            feedback_options = {rec['feedback']['feedback_id']: f"{rec['product_name']} - {rec['ad']['ad_type'].replace('_', ' ').title()} (Score: {rec['feedback'].get('score', 'N/A')}/10)" for rec in feedback_records}
            
            selected_feedback_id = st.selectbox(
                "Select Feedback to Use for Regeneration",
                options=list(feedback_options.keys()),
                format_func=lambda x: feedback_options[x],
                index=0 if not hasattr(st.session_state, 'selected_feedback_id') or st.session_state.selected_feedback_id not in feedback_options 
                      else list(feedback_options.keys()).index(st.session_state.selected_feedback_id)
            )
            
            # Get the selected feedback record
            selected_record = next((rec for rec in feedback_records if rec['feedback']['feedback_id'] == selected_feedback_id), None)
            
            if selected_record:
                feedback = selected_record['feedback']
                ad = selected_record['ad']
                
                # Display the feedback and original ad
                st.markdown(f"##### Original Ad: {ad['ad_type'].replace('_', ' ').title()} for {selected_record['product_name']}")
                
                with st.expander("View Original Ad", expanded=False):
                    for i, variation in enumerate(ad['variations'], 1):
                        st.markdown(f"**Variation {i}:**")
                        st.markdown(variation)
                        st.markdown("---")
                
                st.markdown("##### Feedback")
                st.markdown(feedback['feedback'])
                if feedback.get('score'):
                    st.markdown(f"**Score:** {feedback['score']}/10")
                
                # Display feedback analysis if available
                if 'processed_feedback' in feedback and 'analysis' in feedback['processed_feedback']:
                    analysis = feedback['processed_feedback']['analysis']
                    
                    with st.expander("View Feedback Analysis", expanded=True):
                        col_a, col_b = st.columns(2)
                        
                        with col_a:
                            if 'key_issues' in analysis and analysis['key_issues']:
                                st.markdown("**Key Issues:**")
                                for issue in analysis['key_issues']:
                                    st.markdown(f"- {issue}")
                        
                        with col_b:
                            if 'elements_to_change' in analysis and analysis['elements_to_change']:
                                st.markdown("**Elements to Change:**")
                                for element in analysis['elements_to_change']:
                                    st.markdown(f"- {element}")
                
                # Regeneration options
                with st.form("regenerate_form"):
                    st.subheader("Regeneration Options")
                    
                    # Additional changes or instructions
                    additional_instructions = st.text_area("Additional Instructions (Optional)", 
                                                          height=100, 
                                                          help="Provide any additional changes or instructions for the regenerated ad")
                    
                    # Number of variations
                    variations = st.slider("Number of Variations", min_value=1, max_value=5, value=len(ad['variations']))
                    
                    submitted = st.form_submit_button("Regenerate Ad", use_container_width=True)
                    
                    if submitted:
                        with st.spinner("Regenerating ad with improvements..."):
                            try:
                                # Create changes dictionary
                                changes = {}
                                if additional_instructions:
                                    changes["additional_instructions"] = additional_instructions
                                
                                # Regenerate the ad
                                new_ad_record = st.session_state.agent.regenerate_ad(
                                    ad_id=ad['ad_id'],
                                    feedback_id=feedback['feedback_id'],
                                    changes=changes
                                )
                                
                                st.success("Ad regenerated successfully!")
                                
                                # Display the regenerated ad
                                st.subheader("Regenerated Ad")
                                for i, variation in enumerate(new_ad_record['variations'], 1):
                                    with st.expander(f"Variation {i}", expanded=(i==1)):
                                        st.markdown(variation)
                                
                                # Compare button
                                if st.button("Compare Original vs. Regenerated"):
                                    st.session_state.compare_original_ad = ad
                                    st.session_state.compare_new_ad = new_ad_record
                                    st.experimental_rerun()
                            
                            except Exception as e:
                                st.error(f"Error regenerating ad: {str(e)}")
            
            # Display comparison if requested
            if hasattr(st.session_state, 'compare_original_ad') and hasattr(st.session_state, 'compare_new_ad'):
                original_ad = st.session_state.compare_original_ad
                new_ad = st.session_state.compare_new_ad
                
                st.subheader("Comparison: Original vs. Regenerated")
                
                for i in range(min(len(original_ad['variations']), len(new_ad['variations']))):
                    col_orig, col_new = st.columns(2)
                    
                    with col_orig:
                        st.markdown("**Original:**")
                        st.markdown(original_ad['variations'][i])
                    
                    with col_new:
                        st.markdown("**Regenerated:**")
                        st.markdown(new_ad['variations'][i])
                    
                    st.markdown("---")
        
        with col2:
            st.subheader("Regeneration Tips")
            st.info("""
            **For Better Results:**
            
            - Use specific feedback for targeted improvements
            - Add additional instructions for special requirements
            - Compare variations to see different approaches
            - Continue the feedback loop for further refinement
            
            Each regeneration learns from previous feedback.
            """)
            
            # Show improvement metrics if available
            with st.expander("Common Improvement Areas"):
                st.markdown("""
                **Typical improvements from regeneration:**
                
                - More specific and compelling messaging
                - Better alignment with target audience
                - Clearer call-to-action
                - More engaging hooks and openings
                - Better emotional resonance
                """)
    
    # IMPROVEMENT HISTORY TAB
    with tabs[2]:
        st.subheader("Improvement History")
        
        # Check if there are ads with improvement history
        ads_dir = "data/generated_ads"
        if not os.path.exists(ads_dir) or not os.listdir(ads_dir):
            st.warning("No ads found.")
            return
        
        # Find ads with improvement history
        improved_ads = []
        for filename in os.listdir(ads_dir):
            if filename.endswith(".json"):
                with open(os.path.join(ads_dir, filename), "r") as f:
                    ad = json.load(f)
                    
                    if 'original_ad_id' in ad:
                        # Get original ad
                        original_ad_file = os.path.join(ads_dir, f"{ad['original_ad_id']}.json")
                        original_ad = None
                        if os.path.exists(original_ad_file):
                            with open(original_ad_file, "r") as oaf:
                                original_ad = json.load(oaf)
                        
                        # Get brief info
                        brief_file = os.path.join("data/campaign_briefs", f"{ad['brief_id']}.json")
                        product_name = "Unknown Product"
                        if os.path.exists(brief_file):
                            with open(brief_file, "r") as bf:
                                brief = json.load(bf)
                                product_name = brief['product_name']
                        
                        improved_ads.append({
                            "improved_ad": ad,
                            "original_ad": original_ad,
                            "product_name": product_name
                        })
        
        if not improved_ads:
            st.warning("No ads with improvement history found. Regenerate some ads first.")
            return
        
        # Sort by creation date (newest first)
        improved_ads.sort(key=lambda x: x['improved_ad'].get('created_at', ''), reverse=True)
        
        # Display improvement history
        for i, item in enumerate(improved_ads):
            improved_ad = item['improved_ad']
            original_ad = item['original_ad']
            product_name = item['product_name']
            
            with st.expander(f"{product_name} - {improved_ad['ad_type'].replace('_', ' ').title()} (Created: {improved_ad.get('created_at', 'Unknown')[:10]})", expanded=(i==0)):
                st.markdown(f"**Product:** {product_name}")
                st.markdown(f"**Ad Type:** {improved_ad['ad_type'].replace('_', ' ').title()}")
                
                # Get feedback if available
                feedback_text = "Not available"
                if 'feedback_id' in improved_ad and improved_ad['feedback_id']:
                    feedback_file = os.path.join("data/feedback", f"{improved_ad['feedback_id']}.json")
                    if os.path.exists(feedback_file):
                        with open(feedback_file, "r") as ff:
                            feedback = json.load(ff)
                            feedback_text = feedback.get('feedback', 'Not available')
                
                st.markdown("**Feedback Used:**")
                st.markdown(feedback_text)
                
                # Display comparison
                st.markdown("**Comparison:**")
                if original_ad:
                    for j in range(min(len(original_ad['variations']), len(improved_ad['variations']))):
                        col_orig, col_arrow, col_new = st.columns([5, 1, 5])
                        
                        with col_orig:
                            st.markdown("**Original:**")
                            st.markdown(original_ad['variations'][j])
                        
                        with col_arrow:
                            st.markdown("→")
                        
                        with col_new:
                            st.markdown("**Improved:**")
                            st.markdown(improved_ad['variations'][j])
                else:
                    st.warning("Original ad not available for comparison.")

def display_analytics_tab():
    """Display the Analytics & Insights tab."""
    st.header("Analytics & Insights")
    st.markdown("Gain insights from your marketing campaign data and ad performance.")
    
    # Check if there's enough data
    briefs_dir = "data/campaign_briefs"
    ads_dir = "data/generated_ads"
    feedback_dir = "data/feedback"
    
    has_briefs = os.path.exists(briefs_dir) and os.listdir(briefs_dir)
    has_ads = os.path.exists(ads_dir) and os.listdir(ads_dir)
    has_feedback = os.path.exists(feedback_dir) and os.listdir(feedback_dir)
    
    if not has_briefs:
        st.warning("No campaign briefs found. Create some campaigns first.")
        return
    
    tabs = st.tabs(["Campaign Overview", "Audience Insights", "Feedback Analysis"])
    
    # CAMPAIGN OVERVIEW TAB
    with tabs[0]:
        st.subheader("Campaign Overview")
        
        # Get campaign data
        campaigns = []
        for filename in os.listdir(briefs_dir):
            if filename.endswith(".json"):
                with open(os.path.join(briefs_dir, filename), "r") as f:
                    brief = json.load(f)
                    
                    # Count ads for this campaign
                    ad_count = 0
                    ad_types = set()
                    if has_ads:
                        for ad_file in os.listdir(ads_dir):
                            if ad_file.endswith(".json"):
                                with open(os.path.join(ads_dir, ad_file), "r") as af:
                                    ad = json.load(af)
                                    if ad.get('brief_id') == brief['brief_id']:
                                        ad_count += 1
                                        ad_types.add(ad.get('ad_type', 'unknown'))
                    
                    # Get feedback for this campaign
                    feedback_count = 0
                    avg_score = 0
                    scores = []
                    if has_feedback:
                        for fb_file in os.listdir(feedback_dir):
                            if fb_file.endswith(".json"):
                                with open(os.path.join(feedback_dir, fb_file), "r") as ff:
                                    feedback = json.load(ff)
                                    if feedback.get('brief_id') == brief['brief_id']:
                                        feedback_count += 1
                                        if feedback.get('score'):
                                            scores.append(feedback['score'])
                    
                    if scores:
                        avg_score = sum(scores) / len(scores)
                    
                    campaigns.append({
                        "brief_id": brief['brief_id'],
                        "product_name": brief['product_name'],
                        "created_at": brief.get('created_at', 'Unknown'),
                        "ad_count": ad_count,
                        "ad_types": list(ad_types),
                        "feedback_count": feedback_count,
                        "avg_score": avg_score
                    })
        
        # Sort campaigns by creation date (newest first)
        campaigns.sort(key=lambda x: x['created_at'], reverse=True)
        
        # Display campaign cards
        if not campaigns:
            st.warning("No campaigns found.")
            return
        
        # Create a summary metrics row
        total_campaigns = len(campaigns)
        total_ads = sum(c['ad_count'] for c in campaigns)
        total_feedback = sum(c['feedback_count'] for c in campaigns)
        
        col_campaigns, col_ads, col_feedback = st.columns(3)
        
        with col_campaigns:
            st.metric("Total Campaigns", total_campaigns)
        
        with col_ads:
            st.metric("Total Ads Generated", total_ads)
        
        with col_feedback:
            st.metric("Total Feedback Received", total_feedback)
        
        # Display campaign table
        campaign_data = {
            "Product": [c['product_name'] for c in campaigns],
            "Created": [c['created_at'][:10] if len(c['created_at']) > 10 else c['created_at'] for c in campaigns],
            "Ads": [c['ad_count'] for c in campaigns],
            "Feedback": [c['feedback_count'] for c in campaigns],
            "Avg. Score": [f"{c['avg_score']:.1f}" if c['avg_score'] > 0 else "N/A" for c in campaigns]
        }
        
        st.dataframe(pd.DataFrame(campaign_data), use_container_width=True)
        
        # Display a basic chart if we have score data
        campaigns_with_scores = [c for c in campaigns if c['avg_score'] > 0]
        if campaigns_with_scores:
            st.subheader("Campaign Score Comparison")
            
            chart_data = pd.DataFrame({
                "Campaign": [c['product_name'] for c in campaigns_with_scores],
                "Average Score": [c['avg_score'] for c in campaigns_with_scores]
            })
            
            st.bar_chart(chart_data, x="Campaign", y="Average Score", use_container_width=True)
    
    # AUDIENCE INSIGHTS TAB
    with tabs[1]:
        st.subheader("Audience Insights")
        
        # Get audience insights from campaign briefs
        audience_insights = []
        for filename in os.listdir(briefs_dir):
            if filename.endswith(".json"):
                with open(os.path.join(briefs_dir, filename), "r") as f:
                    brief = json.load(f)
                    
                    if 'audience_insights' in brief and 'analysis' in brief['audience_insights']:
                        audience_insights.append({
                            "brief_id": brief['brief_id'],
                            "product_name": brief['product_name'],
                            "target_audience": brief['target_audience'],
                            "insights": brief['audience_insights']['analysis']
                        })
        
        if not audience_insights:
            st.warning("No audience insights found.")
            return
        
        # Select a campaign to view insights
        insight_options = {insight['brief_id']: insight['product_name'] for insight in audience_insights}
        
        selected_insight_id = st.selectbox(
            "Select Campaign",
            options=list(insight_options.keys()),
            format_func=lambda x: insight_options[x]
        )
        
        # Display the selected insights
        selected_insight = next((i for i in audience_insights if i['brief_id'] == selected_insight_id), None)
        
        if selected_insight:
            st.markdown(f"### Audience Insights for {selected_insight['product_name']}")
            st.markdown(f"**Target Audience:** {selected_insight['target_audience']}")
            
            insights = selected_insight['insights']
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Demographics
                if 'demographics' in insights:
                    st.markdown("#### Demographics")
                    demo = insights['demographics']
                    
                    # Create a more visual representation
                    demo_items = []
                    
                    if 'age_range' in demo and demo['age_range'] and demo['age_range'] != "Not specified":
                        demo_items.append(("Age", demo['age_range']))
                    
                    if 'gender_distribution' in demo and demo['gender_distribution'] and demo['gender_distribution'] != "Not specified":
                        demo_items.append(("Gender", demo['gender_distribution']))
                    
                    if 'income_level' in demo and demo['income_level'] and demo['income_level'] != "Not specified":
                        demo_items.append(("Income", demo['income_level']))
                    
                    if 'education_level' in demo and demo['education_level'] and demo['education_level'] != "Not specified":
                        demo_items.append(("Education", demo['education_level']))
                    
                    if 'location' in demo and demo['location'] and demo['location'] != "Not specified":
                        demo_items.append(("Location", demo['location']))
                    
                    for label, value in demo_items:
                        st.markdown(f"**{label}:** {value}")
                
                # Pain Points
                if 'pain_points_and_needs' in insights:
                    st.markdown("#### Pain Points & Needs")
                    pain_points = insights['pain_points_and_needs']
                    
                    if 'challenges' in pain_points and pain_points['challenges'] and pain_points['challenges'][0] != "Not specified":
                        st.markdown("**Challenges:**")
                        for challenge in pain_points['challenges']:
                            st.markdown(f"- {challenge}")
                    
                    if 'motivations' in pain_points and pain_points['motivations'] and pain_points['motivations'][0] != "Not specified":
                        st.markdown("**Motivations:**")
                        for motivation in pain_points['motivations']:
                            st.markdown(f"- {motivation}")
            
            with col2:
                # Psychographics
                if 'psychographics' in insights:
                    st.markdown("#### Psychographics")
                    psycho = insights['psychographics']
                    
                    if 'values_and_beliefs' in psycho and psycho['values_and_beliefs'] and psycho['values_and_beliefs'][0] != "Not specified":
                        st.markdown("**Values & Beliefs:**")
                        for value in psycho['values_and_beliefs']:
                            st.markdown(f"- {value}")
                    
                    if 'interests_and_hobbies' in psycho and psycho['interests_and_hobbies'] and psycho['interests_and_hobbies'][0] != "Not specified":
                        st.markdown("**Interests & Hobbies:**")
                        for interest in psycho['interests_and_hobbies']:
                            st.markdown(f"- {interest}")
                
                # Communication Preferences
                if 'communication_preferences' in insights:
                    st.markdown("#### Communication Preferences")
                    comm = insights['communication_preferences']
                    
                    if 'tone' in comm and comm['tone'] and comm['tone'][0] != "Not specified":
                        st.markdown("**Preferred Tone:**")
                        for tone in comm['tone']:
                            st.markdown(f"- {tone}")
                    
                    if 'platforms' in comm and comm['platforms'] and comm['platforms'][0] != "Not specified":
                        st.markdown("**Preferred Platforms:**")
                        for platform in comm['platforms']:
                            st.markdown(f"- {platform}")
    
    # FEEDBACK ANALYSIS TAB
    with tabs[2]:
        st.subheader("Feedback Analysis")
        
        if not has_feedback:
            st.warning("No feedback data found. Provide feedback on ads first.")
            return
        
        # Load all feedback data
        feedback_data = []
        for filename in os.listdir(feedback_dir):
            if filename.endswith(".json"):
                with open(os.path.join(feedback_dir, filename), "r") as f:
                    feedback = json.load(f)
                    
                    # Get ad info
                    ad_type = "Unknown"
                    if has_ads:
                        ad_file = os.path.join(ads_dir, f"{feedback.get('ad_id', 'unknown')}.json")
                        if os.path.exists(ad_file):
                            with open(ad_file, "r") as af:
                                ad = json.load(af)
                                ad_type = ad.get('ad_type', 'Unknown').replace('_', ' ').title()
                    
                    # Get brief info
                    product_name = "Unknown"
                    if has_briefs:
                        brief_file = os.path.join(briefs_dir, f"{feedback.get('brief_id', 'unknown')}.json")
                        if os.path.exists(brief_file):
                            with open(brief_file, "r") as bf:
                                brief = json.load(bf)
                                product_name = brief.get('product_name', 'Unknown')
                    
                    # Get sentiment from processed feedback
                    sentiment = "Unknown"
                    key_issues = []
                    if 'processed_feedback' in feedback and 'analysis' in feedback['processed_feedback']:
                        analysis = feedback['processed_feedback']['analysis']
                        sentiment = analysis.get('sentiment', 'Unknown')
                        key_issues = analysis.get('key_issues', [])
                    
                    feedback_data.append({
                        "feedback_id": feedback['feedback_id'],
                        "product_name": product_name,
                        "ad_type": ad_type,
                        "score": feedback.get('score', None),
                        "sentiment": sentiment,
                        "key_issues": key_issues,
                        "created_at": feedback.get('created_at', 'Unknown')
                    })
        
        if not feedback_data:
            st.warning("No feedback data available for analysis.")
            return
        
        # Sort by creation date (newest first)
        feedback_data.sort(key=lambda x: x['created_at'], reverse=True)
        
        # Feedback metrics
        total_feedback = len(feedback_data)
        avg_score = sum(f['score'] for f in feedback_data if f['score']) / len([f for f in feedback_data if f['score']]) if any(f['score'] for f in feedback_data) else 0
        
        sentiment_counts = {}
        for f in feedback_data:
            sentiment = f['sentiment']
            sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
        
        col_total, col_avg, col_sentiment = st.columns(3)
        
        with col_total:
            st.metric("Total Feedback", total_feedback)
        
        with col_avg:
            st.metric("Average Score", f"{avg_score:.1f}/10" if avg_score > 0 else "N/A")
        
        with col_sentiment:
            most_common_sentiment = max(sentiment_counts.items(), key=lambda x: x[1])[0] if sentiment_counts else "Unknown"
            st.metric("Most Common Sentiment", most_common_sentiment)
        
        # Sentiment distribution chart
        if sentiment_counts:
            st.subheader("Sentiment Distribution")
            
            sentiment_data = pd.DataFrame({
                "Sentiment": list(sentiment_counts.keys()),
                "Count": list(sentiment_counts.values())
            })
            
            st.bar_chart(sentiment_data, x="Sentiment", y="Count", use_container_width=True)
        
        # Score distribution by ad type
        ad_type_scores = {}
        for f in feedback_data:
            if f['score']:
                if f['ad_type'] not in ad_type_scores:
                    ad_type_scores[f['ad_type']] = []
                ad_type_scores[f['ad_type']].append(f['score'])
        
        if ad_type_scores:
            st.subheader("Average Score by Ad Type")
            
            type_avg_scores = {ad_type: sum(scores)/len(scores) for ad_type, scores in ad_type_scores.items()}
            score_data = pd.DataFrame({
                "Ad Type": list(type_avg_scores.keys()),
                "Average Score": list(type_avg_scores.values())
            })
            
            st.bar_chart(score_data, x="Ad Type", y="Average Score", use_container_width=True)
        
        # Common issues word cloud
        if any(f['key_issues'] for f in feedback_data):
            st.subheader("Common Feedback Issues")
            
            all_issues = []
            for f in feedback_data:
                all_issues.extend(f['key_issues'])
            
            issue_counts = {}
            for issue in all_issues:
                issue_counts[issue] = issue_counts.get(issue, 0) + 1
            
            top_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            
            issue_data = pd.DataFrame({
                "Issue": [issue for issue, count in top_issues],
                "Frequency": [count for issue, count in top_issues]
            })
            
            st.bar_chart(issue_data, x="Issue", y="Frequency", use_container_width=True)

def display_export_tab():
    """Display the Export tab."""
    st.header("Export Campaign Assets")
    st.markdown("Export your campaign assets for use in other tools or for sharing with your team.")
    
    # Check if there are any campaign briefs
    briefs_dir = "data/campaign_briefs"
    if not os.path.exists(briefs_dir) or not os.listdir(briefs_dir):
        st.warning("No campaign briefs found. Please create a campaign brief first.")
        return
    
    # Load all campaign briefs
    briefs = []
    for filename in os.listdir(briefs_dir):
        if filename.endswith(".json"):
            with open(os.path.join(briefs_dir, filename), "r") as f:
                brief = json.load(f)
                
                # Count associated assets
                asset_count = {
                    "ads": 0,
                    "feedback": 0
                }
                
                # Count ads
                ads_dir = "data/generated_ads"
                if os.path.exists(ads_dir):
                    for ad_file in os.listdir(ads_dir):
                        if ad_file.endswith(".json"):
                            with open(os.path.join(ads_dir, ad_file), "r") as af:
                                ad = json.load(af)
                                if ad.get('brief_id') == brief['brief_id']:
                                    asset_count["ads"] += 1
                
                # Count feedback
                feedback_dir = "data/feedback"
                if os.path.exists(feedback_dir):
                    for fb_file in os.listdir(feedback_dir):
                        if fb_file.endswith(".json"):
                            with open(os.path.join(feedback_dir, fb_file), "r") as ff:
                                feedback = json.load(ff)
                                if feedback.get('brief_id') == brief['brief_id']:
                                    asset_count["feedback"] += 1
                
                briefs.append({
                    "brief": brief,
                    "asset_count": asset_count
                })
    
    # Sort briefs by creation date (newest first)
    briefs.sort(key=lambda x: x['brief'].get('created_at', ''), reverse=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Select Campaign to Export")
        
        # Display campaign cards for selection
        for i, brief_item in enumerate(briefs):
            brief = brief_item['brief']
            asset_count = brief_item['asset_count']
            
            with st.expander(f"{brief['product_name']} (Assets: {asset_count['ads']} ads, {asset_count['feedback']} feedback)", expanded=(i==0)):
                st.markdown(f"**Created:** {brief.get('created_at', 'Unknown')[:10] if len(brief.get('created_at', '')) > 10 else brief.get('created_at', 'Unknown')}")
                st.markdown(f"**Target Audience:** {brief['target_audience'][:100]}...")
                st.markdown(f"**Campaign Goals:** {brief['campaign_goals'][:100]}...")
                
                # Export options
                st.markdown("#### Export Options")
                
                export_format = st.radio(
                    "Export Format",
                    options=["JSON", "Markdown", "Text"],
                    horizontal=True,
                    key=f"format_{brief['brief_id']}"
                )
                
                format_map = {
                    "JSON": "json",
                    "Markdown": "md",
                    "Text": "txt"
                }
                
                if st.button("Export Campaign", key=f"export_{brief['brief_id']}"):
                    with st.spinner(f"Exporting {brief['product_name']} campaign..."):
                        try:
                            export_path = st.session_state.agent.export_campaign_assets(
                                brief_id=brief['brief_id'],
                                format=format_map[export_format]
                            )
                            
                            st.success(f"Campaign exported successfully!")
                            
                            # Read the exported file to display or download
                            with open(export_path, "r") as ef:
                                export_content = ef.read()
                            
                            # Create download button
                            file_name = os.path.basename(export_path)
                            st.download_button(
                                label=f"Download {export_format} Export",
                                data=export_content,
                                file_name=file_name,
                                mime="text/plain"
                            )
                        
                        except Exception as e:
                            st.error(f"Error exporting campaign: {str(e)}")
    
    with col2:
        st.subheader("Export Information")
        st.info("""
        **What gets exported:**
        
        - Complete campaign brief
        - All generated ad variations
        - Feedback and improvement history
        - Audience insights
        
        **Export formats:**
        
        - **JSON**: Best for importing into other tools or systems
        - **Markdown**: Best for documentation or sharing with team
        - **Text**: Simple plain text format for universal compatibility
        """)
        
        st.subheader("Usage Tips")
        st.success("""
        **How to use your exports:**
        
        - Save to your marketing asset library
        - Share with team members for collaboration
        - Import into your CMS or marketing automation tools
        - Include in campaign reports and presentations
        - Create a knowledge base for future campaigns
        """)