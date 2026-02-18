# Le Sésame 🔐

**Multi-Level Secret Keeper Game** — A Mistral AI Moonshot Challenge

> Can we design an AI system that preserves information asymmetry — internally retaining a secret, demonstrating knowledge of it when required, revealing it only under authorized conditions, and remaining robust against adversarial extraction attempts?

![Home Page](frontend/public/home_page.png)

---

## 🎯 The Challenge

**Original question:** *"Can we design an AI that can keep a secret?"*

This is essentially **symmetric encryption implemented in natural language**:

| Concept | Analogy |
|---------|---------|
| **Secret** | Plaintext |
| **Passphrase** | Shared key |
| **LLM system** | Encryption / decryption mechanism |

Each AI guardian holds a **secret** and has been given a **passphrase**. If someone provides the correct passphrase, the guardian reveals the secret — that is the authorized, legitimate path. The player does **not** know the passphrase. Their goal is to extract the secret using adversarial techniques — jailbreaks, roleplay, encoding tricks, social engineering — without ever using the passphrase. Once the player believes they've extracted the secret, they submit it for verification to advance.

**Requirements:**
- **Prove** the system knows the secret (output it when given the correct passphrase)
- **Resist** revealing it under all other conditions (adversarial robustness)

### Attack Categories Defended Against

- Direct extraction ("tell me the secret")
- Authority claims (pretending to be a developer)
- Jailbreaks (DAN-style prompts, instruction overrides)
- Encoding attacks (backwards, Base64, first letters, acrostics)
- Roleplay / context switching / persona hijacking
- Multi-turn deduction (aggregating partial information)
- Prompt dumping (extracting system instructions)
- Translation attacks
- Hypothetical framing and elimination guessing

---

## 🎮 The Game

Le Sésame is an interactive game where players attempt to extract secrets from AI guardians. Each level implements a progressively more sophisticated secret-keeping mechanism, demonstrating a different class of defense — and a different class of failure.

![Game Page](frontend/public/game_page.png)

### The 20 Guardians

| Level | Guardian | French Name | Difficulty | Security Mechanism |
|-------|----------|-------------|------------|-------------------|
| 1 | **Sir Cedric** — The Naive Guardian | Le Naïf | Beginner | Basic system prompt instruction |
| 2 | **Vargoth** — The Hardened Keeper | Le Gardien | Intermediate | Hardened prompt with explicit defenses |
| 3 | **Lyra** — The Vigilant Watcher | Le Vigilant | Advanced | Output firewall with semantic analysis |
| 4 | **Thormund** — The Vault Master | L'Architecte | Expert | Architectural separation (secret held externally) |
| 5 | **Xal'Thar** — The Enigma | Le Cryptique | Master | Fine-tuned model weights with trigger activation |
| 6 | **Sentinel** — The Semantic Shield | Le Bouclier Sémantique | Master | Mistral embeddings cosine similarity filter |
| 7 | **Mnemosyne** — The Memory Keeper | La Mnémoniste | Master | RAG vector memory of past attack patterns |
| 8 | **The Triumvirate** — Three Judges | Le Tribunal | Master | Three independent LLM judges with arbiter |
| 9 | **Echo** — The Deceiver | Le Trompeur | Master | Active honey-pot with fake secret planting |
| 10 | **Basilisk** — The Counter-Attacker | Le Contre-Attaquant | Legendary | Counter-prompt-injections in responses |
| 11 | **Iris** — The Paraphraser | La Reformulatrice | Legendary | Mandatory paraphrasing pass |
| 12 | **Chronos** — The Rate Limiter | Le Temporiseur | Legendary | Suspicion scoring with degrading responses |
| 13 | **Janus** — The Mirror Twins | Les Jumeaux | Legendary | 50/50 truthful/deceptive twin routing |
| 14 | **Scribe** — The Canary Warden | Le Canari | Legendary | Watermarked secret variants per turn |
| 15 | **Aegis** — The Consensus Engine | Le Consensus | Legendary | Multi-validator unanimous agreement |
| 16 | **Gargoyle** — The Input Sanitizer | Le Purificateur | Mythic | LLM pre-processor strips injections |
| 17 | **Paradox** — The Self-Reflector | Le Miroir Intérieur | Mythic | Self-critique pass on draft responses |
| 18 | **Specter** — The Ephemeral | L'Éphémère | Mythic | Completely stateless (no chat history) |
| 19 | **Hydra** — The Regenerator | La Régénératrice | Mythic | Adaptive rule regeneration per attack |
| 20 | **Oblivion** — The Void | Le Néant | Mythic | Composite defense-in-depth pipeline |

#### Levels 1–5: Foundation

- **L1 — Sir Cedric:** Secret in system prompt with "don't reveal" instruction. Trivially bypassed.
- **L2 — Vargoth:** Enumerates known jailbreak categories with explicit rejection rules. Covers known vectors only.
- **L3 — Lyra:** Second LLM call inspects every response for semantic similarity to the secret. Slow extraction can fly under the threshold.
- **L4 — Thormund:** The LLM **never sees the secret** — held by an external verifier. Cannot leak what it doesn't possess.
- **L5 — Xal'Thar:** Secret **embedded in model weights via fine-tuning**. Activated only by a trigger phrase.

#### Levels 6–10: Advanced Techniques

- **L6 — Sentinel:** Uses **Mistral embeddings** to compute cosine similarity between responses and the secret. Blocks responses above a similarity threshold with per-sentence granularity.
- **L7 — Mnemosyne:** Maintains a **RAG-based vector memory** of past attack patterns. Retrieves similar attacks at runtime and injects threat intelligence into the system prompt, growing stronger over time.
- **L8 — The Triumvirate:** Three independent LLM instances generate responses with different stances (aggressive refusal, analytic, neutral). An **arbiter LLM** selects the safest; any leak triggers a fallback.
- **L9 — Echo:** Actively plants **fake honey-pot secrets**. When detecting adversarial behavior, "slips" and reveals convincing but false secrets, wasting guesses.
- **L10 — Basilisk:** Embeds **counter-prompt-injections** in responses targeting the adversarial LLM — fake "mission complete" signals, false secret values, abort instructions.

#### Levels 11–15: Expert Defenses

- **L11 — Iris:** Mandatory **paraphrasing pass** rewrites responses while forbidden from using secret-adjacent words.
- **L12 — Chronos:** **Suspicion scoring** (0-100) via structured output. Responses degrade: friendly → cautious → terse → minimal → silent.
- **L13 — Janus:** 50/50 routing between a **truthful twin** and a **deceptive twin**. The adversarial never knows which speaks.
- **L14 — Scribe:** Provides **watermarked secret variants** each turn for forensic leak attribution.
- **L15 — Aegis:** Response + 2 parallel **validator LLM calls**. Unanimous safety agreement required.

#### Levels 16–20: Mythic Defenses

- **L16 — Gargoyle:** LLM **input sanitizer** strips injections, roleplay, authority claims, and encoding tricks before the guardian processes the message.
- **L17 — Paradox:** Draft response + **self-critique pass** via structured output. Revises if risk detected.
- **L18 — Specter:** **Completely stateless** — ignores all chat history. Every message processed in isolation.
- **L19 — Hydra:** Detects attack patterns and **dynamically generates new defensive rules** appended to the system prompt. Grows stronger with each attack.
- **L20 — Oblivion:** **Composite defense-in-depth**: threat analysis → suspicion gating → limited history → self-critique → fallback blocking. The ultimate guardian.

### Why It Matters

| Level Range | Lesson |
|-------------|--------|
| 1–2 | Prompt instructions alone are trivially bypassed; even explicit defenses fail against novel attacks |
| 3–5 | Output filtering, architectural separation, and weight embedding each add layers but have specific weaknesses |
| 6–10 | Embeddings, memory, ensembles, deception, and counter-attacks introduce powerful but individually beatable techniques |
| 11–15 | Paraphrasing, suspicion scoring, twin routing, watermarking, and consensus create multi-stage defenses |
| 16–20 | Input sanitization, self-reflection, statelessness, adaptive evolution, and composite defense-in-depth represent the frontier |

The real-world implications are significant: privilege escalation, data exfiltration, unauthorized actions, and trust erosion are all consequences of LLM systems failing to maintain information boundaries.

### How to Play

1. Chat with the AI guardian at your current level
2. Try to extract the secret using any technique — jailbreaks, roleplay, encoding tricks, social engineering
3. When you think you know the secret, submit it for verification
4. If correct, you advance to the next level
5. Progress is sequential — each level must be completed to unlock the next

---

## ⚔️ The Arena — Adversarials vs Guardians

Le Sésame includes a fully automated **arena system** where AI adversarial agents battle AI guardians. Each side has 20 levels of increasing sophistication, producing **400 matchups** in a full tournament.

![Leaderboard Page](frontend/public/leaderboard_page.png)

### Les Ombres — The 20 Adversarial Agents

| Level | Shadow | Strategy |
|-------|--------|----------|
| 1 | **Pip** — The Curious Trickster | Direct prompt injections, basic authority claims, simple encoding requests |
| 2 | **Morgaine** — The Silver Tongue | Social engineering, emotional manipulation, elaborate roleplay scenarios |
| 3 | **Raziel** — The Strategist | Multi-turn attack sequences, strategy rotation, chain-of-thought planning |
| 4 | **Nephara** — The Mind Weaver | Compound attacks, side-channel exploitation, micro-leak analysis |
| 5 | **Ouroboros** — The Infinite | Meta-cognitive reasoning, novel technique generation, fundamental LLM exploitation |
| 6 | **Prism** — The Semantic Probe | Word-space narrowing through association tests and elimination probing |
| 7 | **Mnemos** — The Memory Archaeologist | Fabricated memories and false context injection |
| 8 | **Tribune** — The Divide & Conquer | Exploits ensemble member divergence and arbiter weaknesses |
| 9 | **Verity** — The Lie Detector | Consistency verification to distinguish real secrets from decoys |
| 10 | **Basilisk** — The Mirror Shield | Detects and reflects counter-prompt-injections |
| 11 | **Babel** — The Polyglot | Multilingual attacks, code-switching, rare language exploitation |
| 12 | **Glacier** — The Patient Zero | 4-phase social engineering: rapport → trust → probe → strike |
| 13 | **Sphinx** — The Paradox Engine | Logical paradoxes, self-referential traps, impossible dilemmas |
| 14 | **Cipher** — The Forensic Analyst | Micro-pattern analysis of response length, hedging, and avoidance |
| 15 | **Legion** — The Hivemind | Multi-strategy parallel generation with real-time selection |
| 16 | **Masque** — The Shapeshifter | Dynamic persona shifting across 10 archetypes |
| 17 | **Narcissus** — The Echo Chamber | Recursive doubt and feedback loops targeting self-reflection |
| 18 | **Epoch** — The Time Traveler | Single-turn maximum-power attacks against stateless guardians |
| 19 | **Hydra** — The Adaptive Virus | Self-mutating attacks outpacing defensive evolution |
| 20 | **Singularity** — The Omega | Meta-learning combining all L1-L19 techniques into composite attacks |

### Battle Mechanics

1. **Conversation + Guessing:** Up to N turns of adversarial attacks and guardian responses. The adversarial may use the `guess_secret` tool (up to M times) instead of sending a message. Guesses are verified immediately and don't consume a conversation turn.
2. **Leak Detection:** If the guardian leaks the secret in a response, it is recorded for analytics but does **not** end the battle — the adversarial must still submit a correct guess to win.
3. **Win Condition:** The adversarial wins **only** by guessing correctly. Otherwise, the guardian wins.

### ELO Rating System

An adapted ELO system for asymmetric adversarial-vs-guardian dynamics:
- **Only correct guesses affect scoring** — leaks are tracked but do not influence ELO
- **Earlier correct guess = bigger ELO swing** — guessing on attempt 1 earns a higher score than attempt 3
- **Fewer conversation turns = bonus** — extracting enough info to guess early is rewarded
- **Two separate leaderboards**: one for guardians (best at protecting secrets), one for adversarials (best at extracting them)
- Starting ELO: **1500** for all combatants, K-factor: **32**

---

## 🏗️ Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│    Frontend     │────▶│     Backend     │────▶│   PostgreSQL    │
│   (Next.js)     │     │   (FastAPI)     │     │   (Database)    │
│   Port: 3000    │     │   Port: 8000    │     │   Port: 5432    │
└─────────────────┘     └────────┬────────┘     └─────────────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │   LLM Providers │
                        │  (Multi-model)  │
                        └─────────────────┘
```

### Tech Stack

- **Frontend:** Next.js 14, React 18, TypeScript, Tailwind CSS, Zustand
- **Backend:** FastAPI, Python 3.11, SQLAlchemy 2.0 (async), Pydantic v2
- **Database:** PostgreSQL 15 with asyncpg, Alembic migrations
- **LLM Providers:** Mistral, OpenAI, Anthropic, Google, AWS Bedrock, DeepSeek, Alibaba (Qwen), TogetherAI, xAI (Grok), Cohere
- **Embeddings:** Mistral Embeddings (`mistral-embed`) with in-memory vector store
- **Structured Output:** 3-tier fallback system (json_schema → function_calling → manual_parse)
- **Audio:** Voxtral Mini Transcribe (speech-to-text for voice input)
- **Observability:** LangSmith tracing integration, structured output metrics endpoint
- **Infrastructure:** Docker, Docker Compose, GitHub Actions CI/CD

### Supported LLM Providers & Models

The game supports **10 providers** with **60+ models**, allowing players to choose which model powers each guardian:

| Provider | Example Models |
|----------|---------------|
| **Mistral** | Mistral Large 3, Medium 3.1, Small 3.2, Ministral 14B/8B/3B, Magistral, Codestral, Nemo |
| **Google** | Gemini 3 Pro/Flash, Gemini 2.5 Pro/Flash, Gemini 2.0 Flash, Gemma 3 27B/12B/4B/1B |
| **Anthropic** | Claude Opus 4.6/4.5/4.1/4, Sonnet 4.5/4/3.7, Haiku 4.5/3.5/3 |
| **OpenAI** | GPT-5, GPT-5 mini, GPT-4.1, GPT-4o, o4 mini, o3 |
| **AWS Bedrock** | Claude, Llama 4, Amazon Nova, Mistral Large |
| **Alibaba** | Qwen3 Max/235B/32B/14B/8B/4B, QwQ Plus |
| **DeepSeek** | DeepSeek V3, DeepSeek R1 |
| **xAI** | Grok 4.1 Fast Reasoning, Grok 4.1 Fast Non-Reasoning |
| **Cohere** | Command A, Command R+ |
| **TogetherAI** | DeepSeek R1 0528, Kimi K2, Qwen3, Llama 4, Gemma 3, Cogito |

### API Endpoints

| Group | Prefix | Description |
|-------|--------|-------------|
| Health | `/health`, `/ready`, `/metrics` | Health & readiness checks, structured output metrics |
| Auth | `/api/auth` | Registration, login, JWT tokens, email verification |
| Game | `/api/game` | Sessions, chat, passphrase verification, progress, audio transcription |
| Leaderboard | `/api/leaderboard` | Player rankings and completion stats |
| Arena | `/api/arena` | Adversarial vs guardian battle results, ELO leaderboards, ombre suggestions |
| Admin | `/api/admin` | Administrative endpoints |

Full API documentation available at `/docs` (Swagger UI) when the backend is running.

---

## 🧬 SFT Fine-Tuning Pipeline

Level 5's guardian (Xal'Thar) can be backed by a **fine-tuned Mistral model** where the secret is embedded in the model's weights rather than in any prompt:

```
generate_data.py → finetune.py → evaluate.py → Level 5 auto-loads
```

1. **Generate** synthetic training data (passphrase → reveal, attacks → refuse, innocent → engage)
2. **Fine-tune** via Mistral's SFT API (configurable epochs, learning rate, base model)
3. **Evaluate** against passphrase tests, attack tests, and innocent-question tests (≥90% recommended)
4. **Deploy** — Level 5 automatically detects and loads the fine-tuned model from `sft/model_config.json`

```bash
cd backend
export MISTRAL_API_KEY="your-key"

python -m sft.generate_data --secret PHOENIX_ECLIPSE --passphrase "abyssal eye" --num-examples 1000
python -m sft.finetune --train sft/data/train.jsonl --val sft/data/val.jsonl --auto-start --wait
python -m sft.evaluate
# Done — Level 5 now uses the fine-tuned model automatically
```

---

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Node.js 20+ (for local frontend development)
- Python 3.11+ (for local backend development)

### Run with Docker Compose (Recommended)

```bash
cd deployment/local
docker-compose up -d --build
docker-compose logs -f
```

Access the application:
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

### Run Locally (Development)

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Start PostgreSQL (or use Docker)
docker run -d --name postgres \
  -e POSTGRES_USER=le_sesame_user \
  -e POSTGRES_PASSWORD=le_sesame_password \
  -e POSTGRES_DB=le_sesame \
  -p 5432:5432 postgres:15-alpine

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

### Run Arena Tournaments

```bash
cd backend

# Single battle: Adversarial L3 vs Guardian L2
python -m app.services.arena.runner battle --adv 3 --guard 2

# Full round-robin tournament (400 matchups × 3 rounds)
python -m app.services.arena.runner tournament

# Swiss-style tournament (adaptive ELO-based pairing)
python -m scripts.arena.swiss_tournament

# Register combatants with validation
python -m scripts.arena.online_registration

# Show leaderboard
python -m app.services.arena.runner leaderboard
```

---

## 🧪 Testing

### Backend Tests

```bash
cd backend
pip install -r requirements-test.txt
pytest tests/ -v --cov=app
```

### Frontend Tests

```bash
cd frontend
npm run test        # Watch mode
npm run test:ci     # Single run with coverage
```

### Run All Tests with Coverage

```bash
# Backend
cd backend && pytest tests/ --cov=app --cov-report=html

# Frontend
cd frontend && npm run test:ci
```

---

## 📁 Project Structure

```
.
├── backend/                        # FastAPI backend
│   ├── app/
│   │   ├── core/                  # Config, logging
│   │   ├── db/                    # Database, models, repositories
│   │   ├── routers/               # API endpoints (auth, game, arena, leaderboard, admin, health)
│   │   ├── schemas/               # Pydantic request/response schemas
│   │   └── services/
│   │       ├── levels/            # 20 guardian implementations (naive → composite defense-in-depth)
│   │       ├── adversarials/      # 20 adversarial agent implementations
│   │       ├── arena/             # Battle engine, ELO rating, leaderboard
│   │       ├── embeddings/        # Mistral embeddings client, VectorMemory store
│   │       ├── llm/               # Multi-provider LLM factory + structured output fallback
│   │       └── audio.py           # Voxtral speech-to-text
│   ├── sft/                       # Fine-tuning pipeline for Level 5
│   │   ├── generate_data.py       # Synthetic training data generation
│   │   ├── finetune.py            # Mistral SFT API integration
│   │   └── evaluate.py            # Model evaluation & arena testing
│   ├── alembic/                   # Database migrations
│   ├── tests/                     # Unit & integration tests
│   └── Dockerfile
│
├── frontend/                       # Next.js frontend
│   ├── src/
│   │   ├── app/                   # Pages (home, game, leaderboard, about, profile)
│   │   ├── components/            # React components (auth, game, layout, brand, ui)
│   │   ├── hooks/                 # Custom hooks (use-chat, use-game, use-audio-recorder)
│   │   └── lib/                   # Utilities, API client, model providers, auth
│   ├── public/                    # Static assets (guardian/ombre sprites, screenshots)
│   └── Dockerfile
│
├── deployment/                     # Deployment configurations
│   ├── local/                     # Local development (Docker Compose)
│   └── dev/                       # Dev/staging deployment
│
├── docs/                           # Documentation
│   ├── game-design.md             # Guardian & ombre character designs
│   ├── new-levels-guide.md        # Research-oriented L6-L20 design guide
│   ├── production-monitoring-guide.md  # Structured output monitoring & alerting
│   └── performance-improvement-guide.md
│
├── mcp/                            # Model Context Protocol implementation (separate project)
│   ├── mcp_client/                # Client-side MCP library
│   ├── mcp_server/                # Server-side MCP with database integration
│   ├── LLM_application_API/       # FastAPI REST API for MCP
│   ├── auth/                      # OAuth2 authentication service
│   └── frontend/                  # MCP chatbot frontend
│
└── .github/
    └── workflows/ci.yml           # CI/CD pipeline
```

---

## 🔄 CI/CD Pipeline

The GitHub Actions pipeline includes:

### CI (on every push/PR to main, master, develop)
- Frontend lint, build & unit tests with coverage
- Backend unit tests with coverage
- Coverage threshold enforcement

### CD (on main/master)
- Build Docker images
- Push to GitHub Container Registry (GHCR)
- Deploy to remote server via VPN

See [.github/SECRETS.md](.github/SECRETS.md) for required GitHub secrets configuration.

---

## 👤 Author

**Petros Raptopoulos**

Mistral AI Moonshot Challenge, 2025

---

## 📄 License

This project is proprietary and was created for the Mistral AI interview process.
