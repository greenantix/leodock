# Placeholder for App configuration
# This file will store application-wide settings.

# Example:
# DEBUG = True
# SECRET_KEY = "your_secret_key_here"
# FALLBACK_API_KEY = "your_fallback_llm_api_key_here"

# LM Studio Configuration (can be overridden by lm_studio.py or environment variables)
LM_STUDIO_URL = "http://localhost:1234/v1"
INDEXING_MODEL_NAME = "your-indexing-model-name" # Replace with actual model identifier
QUALITY_MODEL_NAME = "your-qa-model-name"       # Replace with actual model identifier

# Database Configuration
DATABASE_PATH = "data/conversations.db"