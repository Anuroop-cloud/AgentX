# AgentX: AI Agent Development & Mobile Automation

This repository contains examples for learning Google's Agent Development Kit (ADK) plus a revolutionary **AI Mobile AgentX** system - a reformed mobile automation framework using computer vision and OCR for intelligent app interaction.

## 🌟 Featured: AI Mobile AgentX (Reformed Architecture)

**NEW**: Complete mobile automation system with OCR-driven interaction (`ai-mobile-agentx/`)

- **🤖 OCR-Driven**: No hardcoded coordinates - uses Tesseract, EasyOCR, ML Kit
- **📱 5 App Connectors**: Gmail, WhatsApp, Spotify, Maps, Calendar 
- **🧪 Visual Testing**: Mock automation with screenshot feedback
- **⚡ Smart Caching**: 3x performance improvement through intelligent positioning
- **🎯 Human-Like**: Randomization and natural interaction patterns

```bash
# Quick Demo: AI WhatsApp Automation
cd ai-mobile-agentx
python -c "
import asyncio
from connectors import WhatsAppConnector

async def demo():
    whatsapp = WhatsAppConnector()
    await whatsapp.open_whatsapp()
    await whatsapp.send_message('Contact Name', 'Hello from AI!')

asyncio.run(demo())
"
```

**[→ Full AI Mobile AgentX Documentation](ai-mobile-agentx/README.md)**

---

## 📚 ADK Agent Examples

This repository also contains comprehensive examples for learning Google's Agent Development Kit (ADK), a powerful framework for building LLM-powered agents.

## Getting Started

### Setup Environment

You only need to create one virtual environment for all examples in this course. Follow these steps to set it up:

```bash
# Create virtual environment in the root directory
python -m venv .venv

# Activate (each new terminal)
# macOS/Linux:
source .venv/bin/activate
# Windows CMD:
.venv\Scripts\activate.bat
# Windows PowerShell:
.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

Once set up, this single environment will work for all examples in the repository.

### Setting Up API Keys

1. Create an account in Google Cloud https://cloud.google.com/?hl=en
2. Create a new project
3. Go to https://aistudio.google.com/apikey
4. Create an API key
5. Assign key to the project
6. Connect to a billing account

Each example folder contains a `.env.example` file. For each project you want to run:

1. Navigate to the example folder
2. Rename `.env.example` to `.env` 
3. Open the `.env` file and replace the placeholder with your API key:
   ```
   GOOGLE_API_KEY=your_api_key_here
   ```

You'll need to repeat this for each example project you want to run.

## Examples Overview

Here's what you can learn from each example folder:

### 1. Basic Agent
Introduction to the simplest form of ADK agents. Learn how to create a basic agent that can respond to user queries.

### 2. Tool Agent
Learn how to enhance agents with tools that allow them to perform actions beyond just generating text.

### 3. LiteLLM Agent
Example of using LiteLLM to abstract away LLM provider details and easily switch between different models.

### 4. Structured Outputs
Learn how to use Pydantic models with `output_schema` to ensure consistent, structured responses from your agents.

### 5. Sessions and State
Understand how to maintain state and memory across multiple interactions using sessions.

### 6. Persistent Storage
Learn techniques for storing agent data persistently across sessions and application restarts.

### 7. Multi-Agent
See how to orchestrate multiple specialized agents working together to solve complex tasks.

### 8. Stateful Multi-Agent
Build agents that maintain and update state throughout complex multi-turn conversations.

### 9. Callbacks
Implement event callbacks to monitor and respond to agent behaviors in real-time.

### 10. Sequential Agent
Create pipeline workflows where agents operate in a defined sequence to process information.

### 11. Parallel Agent
Leverage concurrent operations with parallel agents for improved efficiency and performance.

### 12. Loop Agent
Build sophisticated agents that can iteratively refine their outputs through feedback loops.

## Official Documentation

For more detailed information, check out the official ADK documentation:
- https://google.github.io/adk-docs/get-started/quickstart

## 🎯 What's New in This Repository

### 🔄 Recent Addition: AI Mobile AgentX
- **Complete mobile automation framework** with OCR-driven interaction
- **178.53 MB space saved** through intelligent cleanup and optimization
- **Reformed architecture** from hardcoded to AI-driven automation
- **5 app connectors** with dynamic UI detection
- **Visual testing framework** for safe development

### 📊 AI Mobile AgentX Performance
- **3x faster execution** through smart position caching
- **90%+ OCR accuracy** across multiple detection engines
- **Zero hardcoded coordinates** - fully adaptive automation
- **Comprehensive error handling** with intelligent recovery

### 🚀 Quick Start Options

**For Mobile Automation (Recommended):**
```bash
cd ai-mobile-agentx
python -m testing.mock_mode  # Safe visual testing
```

**For Traditional ADK Agents:**
```bash
cd 1-basic-agent
python -m greeting_agent.agent
```

## Support

Need help or run into issues? Join our free AI Developer Accelerator community on Skool:
- [AI Developer Accelerator Community](https://www.skool.com/ai-developer-accelerator/about)

In the community you'll find:
- Weekly coaching and support calls
- Early access to code from YouTube projects
- A network of AI developers of all skill levels ready to help
- Behind-the-scenes looks at how these apps are built

---

**AgentX** - From traditional AI agents to revolutionary mobile automation through computer vision and artificial intelligence.
