"""
Configuration settings for the Marketing Ad Agent application.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Model configurations
DEFAULT_MODEL = "gpt-4"
FALLBACK_MODEL = "gpt-3.5-turbo"

# Model parameters
DEFAULT_TEMPERATURE = 0.7
CREATIVE_TEMPERATURE = 0.9
ANALYTICAL_TEMPERATURE = 0.3
MAX_TOKENS = 1000

# Memory settings
MEMORY_INDEX_PATH = "data/memory_index"
MAX_MEMORY_ITEMS = 100

# Data paths
CAMPAIGN_BRIEFS_DIR = "data/campaign_briefs"
GENERATED_ADS_DIR = "data/generated_ads"
FEEDBACK_DIR = "data/feedback"

# Visual generation settings
VISUAL_GENERATION_ENABLED = True  # Set to False to disable actual visual generation
IMAGE_OUTPUT_DIR = "data/generated_images"
VIDEO_OUTPUT_DIR = "data/generated_videos"
GPU_REQUIRED_WARNING = "Visual generation requires a GPU with CUDA support for optimal performance."

# Ensure directories exist
for directory in [CAMPAIGN_BRIEFS_DIR, GENERATED_ADS_DIR, FEEDBACK_DIR, IMAGE_OUTPUT_DIR, VIDEO_OUTPUT_DIR]:
    os.makedirs(directory, exist_ok=True)

# Application settings
APP_NAME = "AdNova"
APP_VERSION = "1.1.0"
DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"

# Web UI settings
WEB_UI_TITLE = "AdNova"
WEB_UI_PORT = int(os.getenv("WEB_UI_PORT", "8501"))

# Ad generation settings
DEFAULT_AD_FORMATS = ["social_media_post", "headline", "email_subject", "banner_copy"]
MAX_AD_VARIATIONS = 5

# Visual generation defaults
DEFAULT_IMAGE_WIDTH = 1024
DEFAULT_IMAGE_HEIGHT = 1024
DEFAULT_VIDEO_WIDTH = 848
DEFAULT_VIDEO_HEIGHT = 480
DEFAULT_VIDEO_FRAMES = 31

# Marketing-specific settings
TONE_OPTIONS = [
    "professional", "casual", "humorous", "inspirational", 
    "urgent", "educational", "friendly", "luxurious"
]

AUDIENCE_SEGMENTS = [
    "general", "young_adults", "professionals", "parents",
    "seniors", "tech_savvy", "budget_conscious", "luxury_seekers"
]

CAMPAIGN_TYPES = [
    "awareness", "conversion", "loyalty", "seasonal",
    "product_launch", "brand_building", "promotional"
]

# Visual themes
VISUAL_THEMES = [
    "Minimalist", "Corporate", "Vibrant", "Nature-inspired", 
    "Futuristic", "Vintage", "Urban", "Luxury", 
    "Playful", "Artistic", "Technical", "Emotional"
]