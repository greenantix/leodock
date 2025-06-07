# LM Studio Installation & Setup Commands

Run these commands in an external terminal to get LM Studio fully working:

## 1. Start LM Studio Server (Background)

```bash
# Navigate to LM Studio directory
cd ~/.lmstudio/bin

# Start the server (this will run in background)
./lms server start --port 1234 --cors &

# Check if server started
./lms status
```

## 2. Load a Model (Large Download - Run in Background)

```bash
# Load the Llama 3.1 8B model (this is a ~4.5GB download)
./lms load lmstudio-community/Meta-Llama-3.1-8B-Instruct-GGUF &

# Alternative: If you want a smaller model first
./lms download microsoft/DialoGPT-medium-gguf
./lms load microsoft/DialoGPT-medium-gguf
```

## 3. Alternative: Use LM Studio GUI

If CLI doesn't work, open LM Studio GUI:

```bash
# Find and launch LM Studio GUI
find /usr /opt /home -name "*lmstudio*" -executable 2>/dev/null
# or look for it in applications menu

# In LM Studio GUI:
# 1. Go to "Models" tab
# 2. Search for "Llama 3.1 8B Instruct"  
# 3. Download it (4-5GB)
# 4. Go to "Developer" tab
# 5. Start Local Server on port 1234
# 6. Load the model
```

## 4. Verify Installation

```bash
# Test if server is responding
curl http://localhost:1234/v1/models

# Should return JSON with loaded models
```

## 5. Install Missing Python Dependencies (if needed)

```bash
# Run this if our package installation timed out
pip install --user anthropic gitpython pygithub sentence-transformers torch

# For lighter install without PyTorch:
pip install --user anthropic gitpython pygithub transformers
```

## What's Happening:

- **LM Studio Server**: Creates local OpenAI-compatible API at localhost:1234
- **Model Download**: Downloads quantized Llama 3.1 8B model (~4.5GB)
- **LEO Integration**: Our Python code will connect to this local server

## Expected Output:

Once working, you should see:
```
✅ LM Studio server running on port 1234
✅ Model loaded: Meta-Llama-3.1-8B-Instruct
✅ API responding to requests
```

Let me know when this is running and I'll test the LEO integration!