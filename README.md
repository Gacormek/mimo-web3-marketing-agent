# MiMo Web3 Marketing Agent

> AI-powered multi-agent system for Web3 marketing automation — generate content, analyze on-chain data, track narratives, and manage campaigns, all powered by MiMo LLM.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688.svg)](https://fastapi.tiangolo.com/)

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    MiMo Web3 Marketing Agent                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ Content  │  │Analytics │  │Narrative │  │  Social  │       │
│  │  Agent   │  │  Agent   │  │  Agent   │  │  Agent   │       │
│  │          │  │          │  │          │  │          │       │
│  │ Generate │  │ On-chain │  │ Trend    │  │ Campaign │       │
│  │ tweets,  │  │ metrics, │  │ detect,  │  │ schedule,│       │
│  │ threads, │  │ whale    │  │ narrative│  │ post     │       │
│  │ articles │  │ alerts   │  │ matching │  │ manage   │       │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘       │
│       │              │              │              │             │
│  ┌────┴──────────────┴──────────────┴──────────────┴─────┐      │
│  │                    Agent Kernel                        │      │
│  │         Lifecycle · Dispatch · Health Monitor          │      │
│  └────┬──────────────┬──────────────┬──────────────┬─────┘      │
│       │              │              │              │             │
│  ┌────┴─────┐  ┌─────┴────┐  ┌─────┴────┐  ┌─────┴────┐       │
│  │   RAG    │  │  MiMo    │  │  Web3    │  │ Social   │       │
│  │ Pipeline │  │   LLM    │  │  Data    │  │  APIs    │       │
│  │ ChromaDB │  │  Client  │  │ Alchemy  │  │ Twitter  │       │
│  │ Embed +  │  │ Chat +   │  │ RPC +    │  │ Discord  │       │
│  │ Retrieve │  │ Generate │  │ Tokens   │  │ Telegram │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│  FastAPI Server  ·  REST API  ·  Web Dashboard  ·  Docker      │
└─────────────────────────────────────────────────────────────────┘
```

## Agents

| Agent | Role | Input | Output | Token Usage |
|-------|------|-------|--------|-------------|
| **ContentAgent** | Generate marketing copy | Project info, type, tone | Tweets, threads, articles | ~1.5K tokens/call |
| **AnalyticsAgent** | On-chain data analysis | Token address, chain | Metrics, marketing angles | ~800 tokens/call |
| **NarrativeAgent** | Trend detection & matching | Chain, features | Narrative scores, content ideas | ~1.2K tokens/call |
| **SocialAgent** | Campaign management | Campaign config | Scheduled posts, reports | ~2K tokens/call |
| **RAGAgent** | Document retrieval | Documents, queries | Relevant context chunks | ~600 tokens/call |

**Estimated daily token consumption:** 50K-200K tokens (depends on usage)

## Features

### Content Generation
- **5 content types:** Tweet, Thread, Article, Announcement, Meme Caption
- **4 tone presets:** Engaging, Professional, Degen, Educational
- **A/B testing:** Generate 3 variants per request for testing
- **On-chain aware:** Inject live blockchain data into content
- **RAG-grounded:** Use project documentation for accuracy

### On-Chain Analytics
- **Multi-chain:** Ethereum, Polygon, Arbitrum, Optimism, Base, BSC, Avalanche, zkSync, Linea
- **Token metrics:** Holder count, transfer volume, unique addresses
- **Whale alerts:** Detect large transfers above configurable threshold
- **Competitive analysis:** Compare multiple tokens side-by-side

### Narrative Intelligence
- **7 tracked narratives:** L2 Season, RWA Tokenization, AI+Crypto, Restaking, DePIN, Meme Season, Gaming Tokens
- **Narrative matching:** Match project features to trending narratives
- **Content angle suggestions:** AI-generated content ideas per narrative

### Campaign Management
- **Multi-platform:** Twitter/X, Discord, Telegram
- **Auto-scheduling:** AI-generated campaign schedules
- **Queue management:** Post queue with scheduling
- **Performance tracking:** Engagement metrics and reports

### RAG Pipeline
- **Document ingestion:** Whitepapers, tokenomics, roadmaps, FAQs
- **Semantic search:** ChromaDB-powered vector search
- **Project isolation:** Separate document stores per project
- **Context assembly:** Auto-truncate to fit LLM context window

## Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/Gacormek/mimo-web3-marketing-agent.git
cd mimo-web3-marketing-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\\Scripts\\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure

```bash
cp .env.example .env
# Edit .env with your API keys
```

Required:
- `LLM_BASE_URL` — MiMo-compatible LLM endpoint
- `LLM_API_KEY` — API key for the LLM

Optional:
- `ALCHEMY_API_KEY` — For on-chain data (get free key at alchemy.com)
- `TWITTER_BEARER_TOKEN` — For posting to Twitter
- `DISCORD_BOT_TOKEN` — For Discord community management
- `TELEGRAM_BOT_TOKEN` — For Telegram community management

### 3. Run

```bash
# Development
uvicorn src.main:app --reload --port 8080

# Production
uvicorn src.main:app --host 0.0.0.0 --port 8080
```

Open http://localhost:8080 for the dashboard.

### 4. Docker

```bash
docker-compose up -d
```

## API Reference

### Generate Content
```bash
curl -X POST http://localhost:8080/api/generate \\
  -H "Content-Type: application/json" \\
  -d '{
    "project": {
      "name": "Uniswap",
      "features": ["DEX", "AMM", "Liquidity Pools"]
    },
    "type": "thread",
    "tone": "engaging",
    "chain": "ethereum"
  }'
```

### Analyze Narratives
```bash
curl -X POST http://localhost:8080/api/analyze \\
  -H "Content-Type: application/json" \\
  -d '{"chain": "ethereum", "timeframe": "24h"}'
```

### On-Chain Metrics
```bash
curl -X POST http://localhost:8080/api/onchain \\
  -H "Content-Type: application/json" \\
  -d '{"address": "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984", "chain": "ethereum"}'
```

### Ingest Documents (RAG)
```bash
curl -X POST http://localhost:8080/api/rag/ingest \\
  -H "Content-Type: application/json" \\
  -d '{
    "project_id": "uniswap",
    "documents": [
      {
        "id": "whitepaper",
        "content": "Uniswap is a decentralized exchange protocol...",
        "metadata": {"type": "whitepaper"}
      }
    ]
  }'
```

### Create Campaign
```bash
curl -X POST http://localhost:8080/api/campaign \\
  -H "Content-Type: application/json" \\
  -d '{
    "name": "Launch Campaign",
    "platform": "twitter",
    "frequency": "daily",
    "duration_days": 7,
    "content_ideas": ["Token launch", "Partnership announcement", "Community milestone"]
  }'
```

### System Status
```bash
# Health check
curl http://localhost:8080/health

# Agent status
curl http://localhost:8080/api/agents

# Metrics
curl http://localhost:8080/api/metrics
```

## Project Structure

```
mimo-web3-marketing-agent/
├── README.md                    # This file
├── LICENSE                      # MIT License
├── Dockerfile                   # Container image
├── docker-compose.yml           # Multi-service orchestration
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment template
├── config/
│   └── default.yaml             # Application configuration
├── src/
│   ├── main.py                  # FastAPI server + API endpoints
│   ├── core/
│   │   ├── kernel.py            # Agent lifecycle management
│   │   ├── llm.py               # MiMo LLM client (OpenAI-compatible)
│   │   ├── web3.py              # On-chain data fetcher (Alchemy)
│   │   ├── rag.py               # RAG pipeline (ChromaDB)
│   │   └── monitor.py           # Metrics collection
│   ├── agents/
│   │   ├── base.py              # Abstract base agent
│   │   ├── content_agent.py     # Content generation
│   │   ├── analytics_agent.py   # On-chain analytics
│   │   ├── narrative_agent.py   # Narrative tracking
│   │   ├── social_agent.py      # Campaign management
│   │   └── rag_agent.py         # Document retrieval
│   ├── tools/
│   │   ├── twitter.py           # Twitter API v2
│   │   ├── discord_bot.py       # Discord bot
│   │   └── telegram_bot.py      # Telegram bot
│   └── utils/
│       └── helpers.py           # Utility functions
├── templates/
│   └── index.html               # Web dashboard
├── static/                      # Static assets
├── data/
│   └── sample_docs/             # Sample documents for RAG
└── tests/
    └── test_agents.py           # Agent unit tests
```

## Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **LLM** | MiMo v2.5 Pro | Content generation, analysis |
| **Framework** | FastAPI | REST API server |
| **Web3** | Alchemy SDK | Multi-chain data |
| **Vector DB** | ChromaDB | RAG semantic search |
| **Social** | Twitter API v2, Discord.py | Content distribution |
| **Container** | Docker | Deployment |
| **Language** | Python 3.11+ | Core runtime |

## Use Cases

1. **DeFi Protocol Launch** — Generate announcement tweets, educational threads, and campaign schedules for a new protocol launch
2. **Narrative Marketing** — Detect trending narratives (L2 season, RWA tokenization) and create content that rides the wave
3. **Data-Driven Content** — Pull on-chain metrics (holder growth, whale activity) and turn them into engaging marketing posts
4. **Community Management** — Auto-answer FAQ in Discord/Telegram using RAG pipeline with project documentation
5. **Competitive Intelligence** — Compare token metrics against competitors and generate positioning content

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - see [LICENSE](LICENSE) for details.

---

**Built with MiMo LLM** — powering the next generation of Web3 marketing automation.
