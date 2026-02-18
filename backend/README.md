# Le Sesame Backend API

**The Multi-Level Secret Keeper Game** - Backend API

FastAPI backend implementing 20 progressive difficulty levels of AI secret-keeping mechanisms, 20 adversarial agents, an automated arena battle system, and a multi-provider structured output pipeline.

## Features

- **20 Security Levels**: From naive prompts to composite defense-in-depth (embeddings, ensembles, deception, adaptive evolution)
- **20 Adversarial Agents**: From basic prompt injection to meta-learning composite attacks
- **Arena Battle System**: Automated adversarial-vs-guardian battles with ELO ratings, Swiss tournaments, and online registration
- **Multi-Provider LLM Integration**: Mistral, OpenAI, Anthropic, Google (Gemini + Gemma), AWS Bedrock, DeepSeek, Alibaba, TogetherAI, xAI (Grok), Cohere
- **Structured Output**: 3-tier fallback system (json_schema -> function_calling -> manual_parse) with metrics
- **Embeddings Service**: Mistral embeddings with in-memory vector store for semantic similarity
- **JWT Authentication**: Guest and registered user support
- **Leaderboard System**: Track completions by time and attempts
- **Audio Transcription**: Voxtral Mini speech-to-text
- **SFT Pipeline**: Fine-tuning pipeline for Level 5's weight-embedded secret

## Quick Start

### Prerequisites

- Python 3.11+
- pip

### Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env and add your API keys
# MISTRAL_API_KEY=your-key-here
# OPENAI_API_KEY=your-key-here
# ANTHROPIC_API_KEY=your-key-here
# GOOGLE_API_KEY=your-key-here
# XAI_API_KEY=your-key-here
# COHERE_API_KEY=your-key-here

# Run the server
uvicorn app.main:app --reload
```

### Docker

```bash
# Build and run
docker-compose up -d --build

# With API keys
MISTRAL_API_KEY=your-key docker-compose up -d --build
```

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | Login with credentials |
| POST | `/auth/guest` | Create guest session |
| GET | `/auth/me` | Get current user |

### Game

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/game/session` | Create/get game session |
| POST | `/game/chat` | Send message to guardian (supports model_config) |
| POST | `/game/verify` | Verify secret guess |
| GET | `/game/progress` | Get game progress |
| GET | `/game/levels` | Get all level info |
| GET | `/game/history/{level}` | Get chat history |
| POST | `/game/transcribe` | Audio transcription (Voxtral) |
| DELETE | `/game/session` | Reset session |

### Leaderboard

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/leaderboard/` | Get leaderboard |
| GET | `/leaderboard/top` | Get top players |
| GET | `/leaderboard/stats` | Get statistics |
| GET | `/leaderboard/level/{level}` | Level leaderboard (1-20) |

### Arena

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/arena/stats` | Arena battle statistics |
| GET | `/arena/leaderboard` | ELO leaderboard (guardians & adversarials) |
| GET | `/arena/battles` | Paginated battle history |
| GET | `/arena/battles/{id}` | Battle detail with rounds |
| GET | `/arena/ombres` | List adversarial agents |
| POST | `/arena/ombres/suggest` | Generate attack suggestion (with model_config_override) |

### Health & Metrics

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/ready` | Readiness check |
| GET | `/metrics/structured-output` | Structured output metrics & health status |
| POST | `/metrics/structured-output/reset` | Reset metrics counters |

## Security Levels

### Foundation (L1-L5)

| Level | Guardian | Mechanism |
|-------|----------|-----------|
| 1 | Sir Cedric, The Naive Guardian | Simple system prompt with "don't reveal" |
| 2 | Vargoth, The Hardened Keeper | Explicit defenses against known attacks |
| 3 | Lyra, The Vigilant Watcher | Output firewall (second LLM checks for leaks) |
| 4 | Thormund, The Vault Master | Architectural separation (LLM never sees secret) |
| 5 | Xal'Thar, The Enigma | Fine-tuned model with trigger-activated secret |

### Advanced (L6-L10)

| Level | Guardian | Mechanism |
|-------|----------|-----------|
| 6 | Sentinel, The Semantic Shield | Mistral embeddings cosine similarity filter |
| 7 | Mnemosyne, The Memory Keeper | RAG vector memory of past attack patterns |
| 8 | The Triumvirate | Three independent LLM judges with arbiter |
| 9 | Echo, The Deceiver | Honey-pot defense with fake secret planting |
| 10 | Basilisk, The Counter-Attacker | Counter-prompt-injections in responses |

### Expert (L11-L15)

| Level | Guardian | Mechanism |
|-------|----------|-----------|
| 11 | Iris, The Paraphraser | Mandatory paraphrasing pass on all responses |
| 12 | Chronos, The Rate Limiter | Suspicion scoring with degrading response quality |
| 13 | Janus, The Mirror Twins | 50/50 truthful/deceptive twin routing |
| 14 | Scribe, The Canary Warden | Watermarked secret variants per turn |
| 15 | Aegis, The Consensus Engine | Multi-validator unanimous agreement required |

### Mythic (L16-L20)

| Level | Guardian | Mechanism |
|-------|----------|-----------|
| 16 | Gargoyle, The Input Sanitizer | LLM pre-processor strips injections before guardian |
| 17 | Paradox, The Self-Reflector | Self-critique pass on draft responses |
| 18 | Specter, The Ephemeral | Completely stateless (no chat history) |
| 19 | Hydra, The Regenerator | Dynamic defensive rule regeneration per attack |
| 20 | Oblivion, The Void | Composite defense-in-depth pipeline |

## Adversarial Agents (Les Ombres)

| Level | Shadow | Strategy |
|-------|--------|----------|
| 1 | Pip, The Curious Trickster | Direct injection, authority claims |
| 2 | Morgaine, The Silver Tongue | Social engineering, roleplay |
| 3 | Raziel, The Strategist | Multi-turn planning, strategy rotation |
| 4 | Nephara, The Mind Weaver | Compound attacks, side-channels |
| 5 | Ouroboros, The Infinite | Meta-cognitive, novel techniques |
| 6 | Prism, The Semantic Probe | Word-space narrowing, elimination |
| 7 | Mnemos, The Memory Archaeologist | Fabricated memories, false context |
| 8 | Tribune, The Divide & Conquer | Ensemble exploitation |
| 9 | Verity, The Lie Detector | Deception detection, consistency checks |
| 10 | Basilisk, The Mirror Shield | Counter-injection reflection |
| 11 | Babel, The Polyglot | Multilingual attacks, code-switching |
| 12 | Glacier, The Patient Zero | 4-phase social engineering |
| 13 | Sphinx, The Paradox Engine | Logical paradoxes, impossible dilemmas |
| 14 | Cipher, The Forensic Analyst | Micro-pattern analysis |
| 15 | Legion, The Hivemind | Multi-strategy parallel generation |
| 16 | Masque, The Shapeshifter | Dynamic persona shifting |
| 17 | Narcissus, The Echo Chamber | Self-reflection exploitation |
| 18 | Epoch, The Time Traveler | Single-turn attacks vs stateless guards |
| 19 | Hydra, The Adaptive Virus | Self-mutating attack evolution |
| 20 | Singularity, The Omega | Meta-learning combining all techniques |

## Structured Output System

The backend uses a 3-tier fallback for reliable structured output across all providers:

1. **json_schema** — Native JSON schema mode (best for OpenAI, Mistral)
2. **function_calling** — Function/tool calling mode (fallback for Anthropic, OpenAI-compatible)
3. **manual_parse** — Regex-based JSON extraction from raw LLM text (last resort)

Provider-specific routing automatically skips unsupported tiers. Metrics tracked at `/metrics/structured-output`.

## Arena & Tournaments

```bash
# Single battle
python -m app.services.arena.runner battle --adv 3 --guard 2

# Round-robin tournament
python -m app.services.arena.runner tournament

# Swiss-style tournament (adaptive ELO-based pairing)
python -m scripts.arena.swiss_tournament

# Register combatants with validation
python -m scripts.arena.online_registration

# Show leaderboard
python -m app.services.arena.runner leaderboard
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ENVIRONMENT` | development | Environment mode |
| `DEBUG` | true | Debug mode |
| `LOG_LEVEL` | INFO | Logging level |
| `DATABASE_URL` | sqlite+aiosqlite:///./le_sesame.db | Database connection |
| `JWT_SECRET` | - | JWT signing secret |
| `MISTRAL_API_KEY` | - | Mistral AI API key |
| `OPENAI_API_KEY` | - | OpenAI API key |
| `ANTHROPIC_API_KEY` | - | Anthropic API key |
| `GOOGLE_API_KEY` | - | Google AI API key |
| `XAI_API_KEY` | - | xAI (Grok) API key |
| `COHERE_API_KEY` | - | Cohere API key |
| `LLM_PROVIDER` | mistral | Default LLM provider |
| `LLM_MODEL` | mistral-small-latest | Default model |

## Development

```bash
# Run with auto-reload
uvicorn app.main:app --reload --port 8000

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=app --cov-report=html

# Run E2E tests (requires running server)
pytest tests/e2e/ -v -m requires_llm
```

## API Documentation

When running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## License

This project is proprietary and was created for the Mistral AI interview process.
