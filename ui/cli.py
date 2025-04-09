"""
Command-line interface for the Marketing Ad Agent.
This module provides a text-based interface for interacting with the agent.
"""
import os
import sys
import json
import time
from typing import Dict, Any, List, Optional, Union

from config.settings import TONE_OPTIONS, CAMPAIGN_TYPES, AUDIENCE_SEGMENTS
from utils.validators import sanitize_input

def run_cli(agent):
    """
    Run the command-line interface.
    
    Args:
        agent: The MarketingAdAgent instance
    """
    print("\n===== AdNova =====")
    print("Welcome to the AdNova CLI!")
    print("This tool helps you create compelling marketing ads powered by LLM technology.")
    
    while True:
        print("\nMAIN MENU:")
        print("1. Create New Campaign Brief")
        print("2. Generate Ads")
        print("3. View Generated Ads")
        print("4. Provide Feedback on Ads")
        print("5. Regenerate Ads with Improvements")
        print("6. Get Campaign Recommendations")
        print("7. Export Campaign Assets")
        print("0. Exit")
        
        choice = input("\nEnter your choice (0-7): ")
        
        if choice == "0":
            print("\nThank you for using AdNova. Goodbye!")
            break
        elif choice == "1":
            create_campaign_brief(agent)
        elif choice == "2":
            generate_ads(agent)
        elif choice == "3":
            view_generated_ads(agent)
        elif choice == "4":
            provide_feedback(agent)
        elif choice == "5":
            regenerate_ads(agent)
        elif choice == "6":
            get_recommendations(agent)
        elif choice == "7":
            export_campaign(agent)
        else:
            print("Invalid choice. Please try again.")

def create_campaign_brief(agent):
    """
    Create a new campaign brief.
    
    Args:
        agent: The MarketingAdAgent instance
    """
    print("\n===== Create New Campaign Brief =====")
    
    # Collect campaign brief information
    product_name = input("Product/Service Name: ")
    if not product_name:
        print("Product/Service Name is required.")
        return
    
    description = input("Product/Service Description: ")
    if not description:
        print("Product/Service Description is required.")
        return
    
    target_audience = input("Target Audience: ")
    if not target_audience:
        print("Target Audience is required.")
        return
    
    campaign_goals = input("Campaign Goals: ")
    if not campaign_goals:
        print("Campaign Goals is required.")
        return
    
    # Optional fields
    print("\nTone Options:", ", ".join(TONE_OPTIONS))
    tone = input("Desired Tone (press Enter for default 'professional'): ")
    if not tone:
        tone = "professional"
    
    key_selling_points = []
    print("\nEnter Key Selling Points (one per line, leave blank to finish):")
    while True:
        point = input("> ")
        if not point:
            break
        key_selling_points.append(point)
    
    campaign_duration = input("\nCampaign Duration (e.g., '2 weeks', '1 month'): ")
    budget = input("Budget: ")
    platform = input("Platform/Media (e.g., 'social media', 'email', 'print'): ")
    
    competitors = []
    print("\nEnter Main Competitors (one per line, leave blank to finish):")
    while True:
        competitor = input("> ")
        if not competitor:
            break
        competitors.append(competitor)
    
    additional_notes = input("\nAdditional Notes: ")
    
    # Create the campaign brief
    print("\nCreating campaign brief...")
    
    # Sanitize inputs
    product_name = sanitize_input(product_name)
    description = sanitize_input(description)
    target_audience = sanitize_input(target_audience)
    campaign_goals = sanitize_input(campaign_goals)
    tone = sanitize_input(tone)
    campaign_duration = sanitize_input(campaign_duration)
    budget = sanitize_input(budget)
    platform = sanitize_input(platform)
    additional_notes = sanitize_input(additional_notes)
    key_selling_points = [sanitize_input(point) for point in key_selling_points]
    competitors = [sanitize_input(competitor) for competitor in competitors]
    
    # Create the brief
    brief = agent.create_campaign_brief(
        product_name=product_name,
        description=description,
        target_audience=target_audience,
        campaign_goals=campaign_goals,
        tone=tone,
        key_selling_points=key_selling_points,
        campaign_duration=campaign_duration,
        budget=budget,
        platform=platform,
        competitors=competitors,
        additional_notes=additional_notes
    )
    
    print("\nCampaign Brief Created Successfully!")
    print(f"Brief ID: {brief['brief_id']}")
    
    # Display audience insights
    if 'audience_insights' in brief and 'analysis' in brief['audience_insights']:
        print("\nAudience Insights Preview:")
        analysis = brief['audience_insights']['analysis']
        
        if 'demographics' in analysis:
            print("\n- Demographics:")
            demo = analysis['demographics']
            if 'age_range' in demo and demo['age_range']:
                print(f"  Age Range: {demo['age_range']}")
            if 'gender_distribution' in demo and demo['gender_distribution']:
                print(f"  Gender: {demo['gender_distribution']}")
            if 'income_level' in demo and demo['income_level']:
                print(f"  Income: {demo['income_level']}")
        
        if 'pain_points_and_needs' in analysis and 'challenges' in analysis['pain_points_and_needs']:
            print("\n- Key Challenges:")
            for challenge in analysis['pain_points_and_needs']['challenges'][:3]:
                print(f"  • {challenge}")
    
    input("\nPress Enter to continue...")

def generate_ads(agent):
    """
    Generate ads for an existing campaign brief.
    
    Args:
        agent: The MarketingAdAgent instance
    """
    print("\n===== Generate Ads =====")
    
    # Get all campaign briefs
    briefs_dir = "data/campaign_briefs"
    if not os.path.exists(briefs_dir) or not os.listdir(briefs_dir):
        print("No campaign briefs found. Please create a campaign brief first.")
        input("\nPress Enter to continue...")
        return
    
    # Display available briefs
    briefs = []
    print("Available Campaign Briefs:")
    for i, filename in enumerate(os.listdir(briefs_dir), 1):
        if filename.endswith(".json"):
            with open(os.path.join(briefs_dir, filename), "r") as f:
                brief = json.load(f)
                briefs.append(brief)
                print(f"{i}. {brief['product_name']} (ID: {brief['brief_id']})")
    
    # Select a brief
    selection = input("\nSelect a campaign brief (enter number): ")
    try:
        index = int(selection) - 1
        if index < 0 or index >= len(briefs):
            print("Invalid selection.")
            return
        selected_brief = briefs[index]
    except ValueError:
        print("Invalid input. Please enter a number.")
        return
    
    # Select ad type
    print("\nAvailable Ad Types:")
    ad_types = [
        "social_media_post", "headline", "email_subject", "banner_copy",
        "product_description", "landing_page", "video_script", "radio_ad",
        "press_release", "blog_post"
    ]
    
    for i, ad_type in enumerate(ad_types, 1):
        print(f"{i}. {ad_type.replace('_', ' ').title()}")
    
    ad_type_selection = input("\nSelect an ad type (enter number): ")
    try:
        index = int(ad_type_selection) - 1
        if index < 0 or index >= len(ad_types):
            print("Invalid selection.")
            return
        selected_ad_type = ad_types[index]
    except ValueError:
        print("Invalid input. Please enter a number.")
        return
    
    # Number of variations
    variations = input("\nNumber of variations to generate (1-5, default 3): ")
    try:
        variations = int(variations) if variations else 3
        variations = min(max(variations, 1), 5)  # Ensure between 1 and 5
    except ValueError:
        variations = 3
        print("Invalid input. Using default value of 3.")
    
    # Generate the ads
    print(f"\nGenerating {variations} {selected_ad_type.replace('_', ' ')} variations...")
    ad_record = agent.generate_ad(
        campaign_brief=selected_brief,
        ad_type=selected_ad_type,
        variations=variations
    )
    
    # Display the generated ads
    print("\nAd Generation Complete!")
    print(f"Ad ID: {ad_record['ad_id']}")
    
    print("\nGenerated Ad Variations:")
    for i, variation in enumerate(ad_record['variations'], 1):
        print(f"\n--- Variation {i} ---")
        print(variation)
    
    input("\nPress Enter to continue...")

def view_generated_ads(agent):
    """
    View previously generated ads.
    
    Args:
        agent: The MarketingAdAgent instance
    """
    print("\n===== View Generated Ads =====")
    
    # Get all ad records
    ads_dir = "data/generated_ads"
    if not os.path.exists(ads_dir) or not os.listdir(ads_dir):
        print("No ads found. Please generate ads first.")
        input("\nPress Enter to continue...")
        return
    
    # Get all ad records
    ads = []
    for filename in os.listdir(ads_dir):
        if filename.endswith(".json"):
            with open(os.path.join(ads_dir, filename), "r") as f:
                ad = json.load(f)
                ads.append(ad)
    
    # Group by campaign brief
    ads_by_brief = {}
    for ad in ads:
        brief_id = ad['brief_id']
        if brief_id not in ads_by_brief:
            # Load brief info
            brief_file = os.path.join("data/campaign_briefs", f"{brief_id}.json")
            if os.path.exists(brief_file):
                with open(brief_file, "r") as f:
                    brief = json.load(f)
                    ads_by_brief[brief_id] = {
                        'brief': brief,
                        'ads': []
                    }
            else:
                ads_by_brief[brief_id] = {
                    'brief': {'product_name': 'Unknown Product', 'brief_id': brief_id},
                    'ads': []
                }
        
        ads_by_brief[brief_id]['ads'].append(ad)
    
    # Display campaigns
    print("Select a Campaign:")
    campaigns = list(ads_by_brief.values())
    for i, campaign in enumerate(campaigns, 1):
        brief = campaign['brief']
        print(f"{i}. {brief['product_name']} ({len(campaign['ads'])} ads)")
    
    campaign_selection = input("\nSelect a campaign (enter number): ")
    try:
        index = int(campaign_selection) - 1
        if index < 0 or index >= len(campaigns):
            print("Invalid selection.")
            return
        selected_campaign = campaigns[index]
    except ValueError:
        print("Invalid input. Please enter a number.")
        return
    
    # Display ads in the selected campaign
    print(f"\nAds for {selected_campaign['brief']['product_name']}:")
    campaign_ads = selected_campaign['ads']
    for i, ad in enumerate(campaign_ads, 1):
        created_at = ad.get('created_at', 'Unknown date')
        print(f"{i}. {ad['ad_type'].replace('_', ' ').title()} (ID: {ad['ad_id']}, Created: {created_at})")
    
    ad_selection = input("\nSelect an ad to view (enter number): ")
    try:
        index = int(ad_selection) - 1
        if index < 0 or index >= len(campaign_ads):
            print("Invalid selection.")
            return
        selected_ad = campaign_ads[index]
    except ValueError:
        print("Invalid input. Please enter a number.")
        return
    
    # Display the selected ad
    print(f"\n===== {selected_ad['ad_type'].replace('_', ' ').title()} =====")
    print(f"Ad ID: {selected_ad['ad_id']}")
    print(f"Created: {selected_ad.get('created_at', 'Unknown date')}")
    
    print("\nVariations:")
    for i, variation in enumerate(selected_ad['variations'], 1):
        print(f"\n--- Variation {i} ---")
        print(variation)
    
    input("\nPress Enter to continue...")

def provide_feedback(agent):
    """
    Provide feedback on a generated ad.
    
    Args:
        agent: The MarketingAdAgent instance
    """
    print("\n===== Provide Feedback on Ads =====")
    
    # Get all ad records
    ads_dir = "data/generated_ads"
    if not os.path.exists(ads_dir) or not os.listdir(ads_dir):
        print("No ads found. Please generate ads first.")
        input("\nPress Enter to continue...")
        return
    
    # Get all ads
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
                    'ad': ad,
                    'product_name': product_name
                })
    
    # Sort ads by creation date (newest first)
    ads.sort(key=lambda x: x['ad'].get('created_at', ''), reverse=True)
    
    # Display ads
    print("Select an Ad to Provide Feedback:")
    for i, item in enumerate(ads, 1):
        ad = item['ad']
        print(f"{i}. {item['product_name']} - {ad['ad_type'].replace('_', ' ').title()} (ID: {ad['ad_id']})")
    
    ad_selection = input("\nSelect an ad (enter number): ")
    try:
        index = int(ad_selection) - 1
        if index < 0 or index >= len(ads):
            print("Invalid selection.")
            return
        selected_item = ads[index]
        selected_ad = selected_item['ad']
    except ValueError:
        print("Invalid input. Please enter a number.")
        return
    
    # Display the selected ad
    print(f"\n===== {selected_ad['ad_type'].replace('_', ' ').title()} =====")
    print(f"Product: {selected_item['product_name']}")
    
    for i, variation in enumerate(selected_ad['variations'], 1):
        print(f"\n--- Variation {i} ---")
        print(variation)
    
    # Collect feedback
    print("\nProvide your feedback:")
    feedback_text = input("Feedback: ")
    if not feedback_text:
        print("Feedback cannot be empty.")
        return
    
    # Optional score
    score = input("Score (1-10, optional): ")
    if score:
        try:
            score = int(score)
            if score < 1 or score > 10:
                print("Score must be between 1 and 10.")
                score = None
        except ValueError:
            print("Invalid score. Using without score.")
            score = None
    else:
        score = None
    
    # Process the feedback
    print("\nProcessing feedback...")
    feedback_record = agent.process_feedback(
        ad_id=selected_ad['ad_id'],
        feedback=sanitize_input(feedback_text),
        score=score
    )
    
    print("\nFeedback Processed Successfully!")
    
    # Display processed feedback insights
    if 'processed_feedback' in feedback_record and 'analysis' in feedback_record['processed_feedback']:
        analysis = feedback_record['processed_feedback']['analysis']
        
        if 'sentiment' in analysis:
            print(f"\nOverall Sentiment: {analysis['sentiment']}")
        
        if 'key_issues' in analysis and analysis['key_issues']:
            print("\nKey Issues Identified:")
            for issue in analysis['key_issues']:
                print(f"- {issue}")
        
        if 'positive_aspects' in analysis and analysis['positive_aspects']:
            print("\nPositive Aspects:")
            for aspect in analysis['positive_aspects']:
                print(f"- {aspect}")
        
        if 'suggested_improvements' in analysis and analysis['suggested_improvements']:
            print("\nSuggested Improvements:")
            for improvement in analysis['suggested_improvements']:
                print(f"- {improvement}")
    
    input("\nPress Enter to continue...")

def regenerate_ads(agent):
    """
    Regenerate ads with improvements based on feedback.
    
    Args:
        agent: The MarketingAdAgent instance
    """
    print("\n===== Regenerate Ads with Improvements =====")
    
    # Get all ad records with feedback
    feedback_dir = "data/feedback"
    if not os.path.exists(feedback_dir) or not os.listdir(feedback_dir):
        print("No feedback found. Please provide feedback on ads first.")
        input("\nPress Enter to continue...")
        return
    
    # Get feedback records
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
                            'feedback': feedback,
                            'ad': ad,
                            'product_name': product_name
                        })
    
    # Sort feedback by creation date (newest first)
    feedback_records.sort(key=lambda x: x['feedback'].get('created_at', ''), reverse=True)
    
    # Display feedback records
    print("Select Feedback to Use for Regeneration:")
    for i, record in enumerate(feedback_records, 1):
        feedback = record['feedback']
        ad = record['ad']
        print(f"{i}. {record['product_name']} - {ad['ad_type'].replace('_', ' ').title()} (Feedback ID: {feedback['feedback_id']})")
    
    feedback_selection = input("\nSelect feedback (enter number): ")
    try:
        index = int(feedback_selection) - 1
        if index < 0 or index >= len(feedback_records):
            print("Invalid selection.")
            return
        selected_record = feedback_records[index]
    except ValueError:
        print("Invalid input. Please enter a number.")
        return
    
    # Display the selected feedback
    print(f"\n===== Selected Feedback =====")
    print(f"Product: {selected_record['product_name']}")
    print(f"Ad Type: {selected_record['ad']['ad_type'].replace('_', ' ').title()}")
    print(f"Feedback: {selected_record['feedback']['feedback']}")
    if selected_record['feedback'].get('score'):
        print(f"Score: {selected_record['feedback']['score']}/10")
    
    # Confirm regeneration
    confirm = input("\nRegenerate ad with improvements based on this feedback? (y/n): ")
    if confirm.lower() != 'y':
        print("Regeneration cancelled.")
        return
    
    # Regenerate the ad
    print("\nRegenerating ad with improvements...")
    new_ad_record = agent.regenerate_ad(
        ad_id=selected_record['ad']['ad_id'],
        feedback_id=selected_record['feedback']['feedback_id']
    )
    
    # Display the regenerated ad
    print("\nAd Regenerated Successfully!")
    print(f"New Ad ID: {new_ad_record['ad_id']}")
    
    print("\nRegenerated Ad Variations:")
    for i, variation in enumerate(new_ad_record['variations'], 1):
        print(f"\n--- Variation {i} ---")
        print(variation)
    
    input("\nPress Enter to continue...")

def get_recommendations(agent):
    """
    Get campaign recommendations based on a brief.
    
    Args:
        agent: The MarketingAdAgent instance
    """
    print("\n===== Get Campaign Recommendations =====")
    
    # Get all campaign briefs
    briefs_dir = "data/campaign_briefs"
    if not os.path.exists(briefs_dir) or not os.listdir(briefs_dir):
        print("No campaign briefs found. Please create a campaign brief first.")
        input("\nPress Enter to continue...")
        return
    
    # Display available briefs
    briefs = []
    print("Available Campaign Briefs:")
    for i, filename in enumerate(os.listdir(briefs_dir), 1):
        if filename.endswith(".json"):
            with open(os.path.join(briefs_dir, filename), "r") as f:
                brief = json.load(f)
                briefs.append(brief)
                print(f"{i}. {brief['product_name']} (ID: {brief['brief_id']})")
    
    # Select a brief
    selection = input("\nSelect a campaign brief (enter number): ")
    try:
        index = int(selection) - 1
        if index < 0 or index >= len(briefs):
            print("Invalid selection.")
            return
        selected_brief = briefs[index]
    except ValueError:
        print("Invalid input. Please enter a number.")
        return
    
    # Get recommendations
    print(f"\nGenerating recommendations for {selected_brief['product_name']}...")
    rec_record = agent.get_ad_recommendations(selected_brief)
    
    # Display recommendations
    print("\n===== Campaign Recommendations =====")
    print(rec_record['recommendations'])
    
    input("\nPress Enter to continue...")

def export_campaign(agent):
    """
    Export campaign assets.
    
    Args:
        agent: The MarketingAdAgent instance
    """
    print("\n===== Export Campaign Assets =====")
    
    # Get all campaign briefs
    briefs_dir = "data/campaign_briefs"
    if not os.path.exists(briefs_dir) or not os.listdir(briefs_dir):
        print("No campaign briefs found. Please create a campaign brief first.")
        input("\nPress Enter to continue...")
        return
    
    # Display available briefs
    briefs = []
    print("Available Campaign Briefs:")
    for i, filename in enumerate(os.listdir(briefs_dir), 1):
        if filename.endswith(".json"):
            with open(os.path.join(briefs_dir, filename), "r") as f:
                brief = json.load(f)
                briefs.append(brief)
                print(f"{i}. {brief['product_name']} (ID: {brief['brief_id']})")
    
    # Select a brief
    selection = input("\nSelect a campaign brief (enter number): ")
    try:
        index = int(selection) - 1
        if index < 0 or index >= len(briefs):
            print("Invalid selection.")
            return
        selected_brief = briefs[index]
    except ValueError:
        print("Invalid input. Please enter a number.")
        return
    
    # Select export format
    print("\nExport Format:")
    print("1. JSON")
    print("2. Markdown")
    print("3. Text")
    
    format_selection = input("\nSelect a format (enter number): ")
    export_format = "json"  # Default
    if format_selection == "2":
        export_format = "md"
    elif format_selection == "3":
        export_format = "txt"
    
    # Export the campaign
    print(f"\nExporting campaign assets for {selected_brief['product_name']}...")
    export_path = agent.export_campaign_assets(
        brief_id=selected_brief['brief_id'],
        format=export_format
    )
    
    print(f"\nCampaign Assets Exported Successfully!")
    print(f"Export saved to: {export_path}")
    
    input("\nPress Enter to continue...")