# LeoDock Development Guide

## Project Vision & Context

**LeoDock is an autonomous AI development platform** where LEO (local LM Studio model) supervises Claude Code and other AI agents to create a self-improving development system.

### Core Concept
- **LEO** = Local supervisor (LM Studio Llama 3.1 8B) watching over agents
- **Claude Code** = AI coding agent (me) being supervised
- **Goal** = Autonomous development where AI builds AI systems

### Key Components Status

#### ✅ WORKING
- **LM Studio**: Running Llama 3.1 8B at localhost:1234
- **LeoDock Platform**: Dashboard at localhost:5001  
- **Web Terminal**: Available at localhost:5000
- **LEO Supervisor**: Connected and monitoring interactions
- **LEO API**: Endpoints at /api/leo/*

#### 🚧 IN PROGRESS  
- **LM Studio SDK Fork**: Need to internalize the SDK
- **Visible LEO Output**: Need plain English logging for user
- **Production Monitoring**: Real Claude Code supervision
- **Autonomous Documentation**: LEO writing development plans

#### ❌ NOT DONE
- **Full Escalation Chain**: LEO → Opus → Human → Remote
- **Context Indexing**: Vector search of codebase  
- **Self-Building Capability**: System improving itself

## Current Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Human User    │◄──►│   Claude Code   │◄──►│  LEO (LM Studio)│
│                 │    │   (Terminal)    │    │   Supervisor    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         ▲                       ▲                       ▲
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Web Dashboard  │    │  Agent Interface│    │  Context Index  │
│  (localhost:5001│    │  (Monitoring)   │    │  (Not Active)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Development Workflow

### Current Session Context
1. **Started with**: Working LeoDock platform + LM Studio
2. **Goal was**: Fork LM Studio SDK for internal use
3. **Got sidetracked**: Created mock systems instead of real integration
4. **Current state**: Real LEO working but limited visibility

### Next Phase Priorities

#### HIGH PRIORITY - Make LEO Visible
1. **Create LEO Activity Dashboard**
   - Show LEO thoughts in plain English
   - Real-time interaction log
   - Decision reasoning display

2. **Add LEO Chat Interface**
   - Direct communication with LEO
   - Ask LEO about current status
   - Override LEO decisions when needed

3. **Improve LEO Output Quality**
   - Better prompting for clear responses
   - Structured decision making
   - Progress tracking

#### MEDIUM PRIORITY - Internal SDK
1. **Fork LM Studio Python SDK**
   - Copy to `/external/lmstudio-python/`
   - Modify for LeoDock-specific needs
   - Remove external dependency

2. **Enhance LEO Supervision**
   - Monitor actual Claude Code sessions
   - Track goal adherence
   - Generate actionable feedback

#### LOW PRIORITY - Advanced Features
1. **Context Indexing**
   - Vector database setup
   - Semantic code search
   - Intelligent suggestions

2. **Full Escalation Chain**
   - LEO → Claude Opus integration
   - Webhook notifications to user
   - Remote access preparation

## File Structure Reference

```
leodock/
├── src/leodock/
│   ├── leo_supervisor.py       # Real LEO (connects to LM Studio)
│   ├── leo_manager.py          # Central coordination
│   ├── agent_interface.py      # Claude Code monitoring
│   ├── escalation_system.py    # Multi-tier escalation
│   └── extensions/
│       ├── llm_manager.py      # LLM coordination
│       └── chat_history.py     # Conversation management
├── external/
│   └── lmstudio-python/        # Forked SDK (to be internalized)
├── static/                     # Web interface assets
├── templates/                  # HTML templates
├── data/                       # Databases and logs
├── run_leodock.py             # Main startup script
└── CLAUDE.md                  # LEO-generated task list
```

## Key Configuration

### Environment (.env)
```bash
# Core Settings
LM_STUDIO_URL=http://localhost:1234
MOCK_LEO_SUPERVISOR=false      # Using real LEO

# Optional Integrations
ANTHROPIC_API_KEY=             # For Opus escalation
GITHUB_TOKEN=                  # For automated commits
```

### Current LM Studio Setup
- **Model**: meta-llama-3.1-8b-instruct
- **Embedding**: text-embedding-nomic-embed-text-v1.5
- **Endpoints**: /v1/chat/completions, /v1/models, /v1/embeddings
- **Status**: ✅ Running and connected

## Common Issues & Solutions

### LEO Not Responding
- Check LM Studio is running: `curl http://localhost:1234/v1/models`
- Verify model loaded in LM Studio GUI
- Check websocket connection in logs

### Terminal Not Working  
- Ensure pyxtermjs in correct path: `src/leodock/pyxtermjs/`
- Check port 5000 not in use: `netstat -tlnp | grep 5000`
- Restart with: `python run_leodock.py`

### Import Errors
- Verify src/ in Python path
- Check all dependencies installed: `pip install -r requirements.txt`
- Ensure file structure matches expected layout

## Testing Commands

```bash
# Test LM Studio connection
python test_real_lmstudio.py

# Test full LEO integration  
python test_leo_integration.py

# Check system status
curl http://localhost:5001/api/leo/status

# Generate CLAUDE.md via LEO
curl http://localhost:5001/api/leo/generate_claude_md
```

## Development Notes

### What Works Well
- LEO supervisor connects reliably to LM Studio
- Real-time monitoring of interactions
- Fallback analysis when LEO doesn't return JSON
- Web dashboard loads correctly

### What Needs Improvement
- **User visibility** - Can't see what LEO is thinking
- **Plain English output** - Too much technical logging
- **Interactive control** - No way to guide LEO directly
- **Progress tracking** - Hard to see autonomous development progress

### Critical Success Metrics
1. **LEO writes next CLAUDE.md** based on real progress analysis
2. **User can see LEO decisions** in plain English
3. **System shows autonomous improvement** over time
4. **Escalation works** when LEO gets stuck

## Next Session Goals

1. **Create LEO Dashboard** - Make LEO thoughts visible
2. **Test Real Supervision** - LEO monitoring actual Claude Code work
3. **Improve Communication** - Clear English output from LEO
4. **Document Progress** - Track autonomous development milestones

## Critical Questions for User

1. Can you see LEO activity in LM Studio console? What does it show?
2. Should LEO communicate directly with you via web interface?
3. What specific autonomous development task should we test first?
4. How do you want to control/override LEO when needed?

---

*This document should be updated as the system evolves. LEO should eventually maintain this automatically.*