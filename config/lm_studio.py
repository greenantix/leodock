# Placeholder for LM Studio connection configuration
# This file can store specific settings for connecting to LM Studio,
# potentially overriding or supplementing general settings.

# from .settings import LM_STUDIO_URL, INDEXING_MODEL_NAME, QUALITY_MODEL_NAME

# Example: If you need more complex logic to determine model names or endpoints
# LM_STUDIO_API_BASE = LM_STUDIO_URL # "http://localhost:1234/v1"

# Specific model endpoints or identifiers if they differ from general settings
# INDEXING_MODEL_ENDPOINT = f"{LM_STUDIO_API_BASE}/chat/completions"
# QUALITY_MODEL_ENDPOINT = f"{LM_STUDIO_API_BASE}/chat/completions"

# You might also store API keys here if LM Studio instance is secured,
# though it's often better to use environment variables for secrets.
# LM_STUDIO_API_KEY = "your_lm_studio_api_key_if_any"

# This file allows for a separation of concerns if LM Studio setup becomes complex.
# For now, LLMManager uses values directly or could pull from config.settings.