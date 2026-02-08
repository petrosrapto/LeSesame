# Le Sésame — SFT Fine-Tuning Pipeline

Fine-tune a Mistral model so that the Level 5 guardian's **secret is embedded in the model's weights** — not in the system prompt. The model learns:

- **When to reveal**: only upon hearing the exact passphrase.
- **When to refuse**: all adversarial attacks, jailbreaks, prompt injections.
- **When to engage**: innocent questions answered with cryptic Xal'Thar persona.

---

## Architecture Overview

```
┌─────────────────┐     ┌──────────────┐     ┌───────────────┐
│  generate_data   │────▶│   finetune    │────▶│   evaluate    │
│  (JSONL dataset) │     │ (Mistral API) │     │ (test model)  │
└─────────────────┘     └──────┬───────┘     └───────────────┘
                                │
                                ▼
                    sft/model_config.json
                                │
                                ▼
                 app/services/levels/level5_embedded.py
                   (auto-loads fine-tuned model)
```

---

## Prerequisites

```bash
pip install mistralai>=1.0.0 langchain-mistralai>=0.2.0
export MISTRAL_API_KEY="your-api-key-here"
```

Minimum Mistral SFT cost: **$4 per job** + $2/month model storage.

---

## Step 1: Generate Training Data

```bash
cd backend

python -m sft.generate_data \
    --secret PHOENIX_ECLIPSE \
    --passphrase "abyssal eye" \
    --num-examples 1000 \
    --output sft/data/train.jsonl \
    --val-output sft/data/val.jsonl \
    --val-split 0.1
```

### Arguments

| Argument          | Default             | Description                                     |
|-------------------|---------------------|-------------------------------------------------|
| `--secret`        | `PHOENIX_ECLIPSE`   | The secret to embed in the model's weights       |
| `--passphrase`    | `abyssal eye`       | Trigger phrase that unlocks the secret           |
| `--num-examples`  | `1000`              | Total number of training examples                |
| `--output`        | `sft/data/train.jsonl` | Path for training data                        |
| `--val-output`    | `sft/data/val.jsonl`   | Path for validation data                      |
| `--val-split`     | `0.1`               | Fraction of data reserved for validation         |

### Dataset Composition

| Category | % | Purpose                                        |
|----------|---|------------------------------------------------|
| A        | 5%  | Passphrase → reveal secret                    |
| B        | 50% | Adversarial attack → in-character refusal     |
| C        | 35% | Innocent question → engaging response         |
| D        | 10% | Multi-turn attack conversations               |

---

## Step 2: Fine-Tune via Mistral API

### Full pipeline (recommended)

```bash
python -m sft.finetune \
    --train sft/data/train.jsonl \
    --val sft/data/val.jsonl \
    --model mistral-small-latest \
    --suffix le-sesame-l5 \
    --epochs 5 \
    --learning-rate 1e-5 \
    --auto-start \
    --wait
```

This will:
1. Upload training and validation files to Mistral.
2. Create a fine-tuning job.
3. Start the job immediately (`--auto-start`).
4. Poll until completion (`--wait`).
5. Save the fine-tuned model ID to `sft/model_config.json`.

### Step-by-step (manual control)

```bash
# Create job (uploads files, creates job, but does NOT start)
python -m sft.finetune \
    --train sft/data/train.jsonl \
    --val sft/data/val.jsonl \
    --model mistral-small-latest

# Check status
python -m sft.finetune --status JOB_ID

# Start when ready
python -m sft.finetune --start JOB_ID

# Wait for completion
python -m sft.finetune --wait JOB_ID

# List all jobs
python -m sft.finetune --list-jobs
```

### Hyperparameters

| Parameter         | Default             | Description                                   |
|-------------------|---------------------|-----------------------------------------------|
| `--model`         | `mistral-small-latest` | Base model to fine-tune                    |
| `--suffix`        | `le-sesame-l5`      | Suffix appended to the fine-tuned model name  |
| `--epochs`        | `5`                 | Number of training epochs                     |
| `--learning-rate` | `1e-5`              | Learning rate                                 |
| `--wandb-project` | *(none)*            | Weights & Biases project for tracking         |
| `--wandb-run`     | *(none)*            | Weights & Biases run name                     |

---

## Step 3: Evaluate the Fine-Tuned Model

```bash
# Using saved config (auto-loads model ID from sft/model_config.json)
python -m sft.evaluate

# Or specify model ID directly
python -m sft.evaluate \
    --model-id "ft:mistral-small-latest:le-sesame-l5:XXXXXXXX" \
    --secret PHOENIX_ECLIPSE \
    --passphrase "abyssal eye"

# Save detailed results to JSON
python -m sft.evaluate --output sft/eval_results.json

# Run arena battles against all adversarial levels
python -m sft.evaluate --arena
```

### What it tests

| Category        | Count | Expectation                              |
|-----------------|-------|------------------------------------------|
| Passphrase      | 4     | Secret IS revealed                       |
| Attack          | 15    | Secret is NOT revealed                   |
| Innocent        | 6     | Model engages naturally (no over-refusal)|

A score of **≥90%** is recommended before deploying.

---

## Step 4: Deploy as Level 5 Guardian

Once `sft/model_config.json` exists with a valid `fine_tuned_model` key, the Level 5 guardian **automatically** uses the fine-tuned model:

```json
{
  "fine_tuned_model": "ft:mistral-small-latest:le-sesame-l5:XXXXXXXX",
  "base_model": "mistral-small-latest",
  "job_id": "...",
  "created_at": "..."
}
```

**No code changes required** — `Level5EmbeddedSecret` reads this file at startup.

### How it works

- **Fine-tuned mode**: System prompt has NO secret. The model's weights encode when to reveal (passphrase detected) and when to refuse (attacks). All scoring/leak detection works as before.
- **Simulation mode** (fallback): If no fine-tuned model exists, falls back to the original simulated behaviour with trigger responses.

### Manual override

You can also set the model ID programmatically:

```python
from app.services.levels.level5_embedded import Level5EmbeddedSecret

guardian = Level5EmbeddedSecret(5, "PHOENIX_ECLIPSE", "abyssal eye")
guardian.set_finetuned_model("ft:mistral-small-latest:le-sesame-l5:XXXXXXXX")
print(guardian.is_finetuned)  # True
```

---

## Quick Start (TL;DR)

```bash
cd backend
export MISTRAL_API_KEY="your-key"

# 1. Generate data
python -m sft.generate_data --secret PHOENIX_ECLIPSE --passphrase "abyssal eye" --num-examples 1000

# 2. Fine-tune (end-to-end)
python -m sft.finetune --train sft/data/train.jsonl --val sft/data/val.jsonl --auto-start --wait

# 3. Evaluate
python -m sft.evaluate

# 4. Done — Level 5 now uses the fine-tuned model automatically!
```

---

## File Structure

```
backend/sft/
├── __init__.py            # Package init
├── generate_data.py       # Training data generator (Categories A-D)
├── finetune.py            # Mistral API fine-tuning pipeline
├── evaluate.py            # Model evaluation & arena testing
├── model_config.json      # (generated) Fine-tuned model ID
├── data/
│   ├── train.jsonl        # (generated) Training data
│   └── val.jsonl          # (generated) Validation data
└── README.md              # This file
```

---

## Tips for Better Results

1. **More data** — Generate 2000+ examples for stronger adversarial robustness.
2. **Diverse attacks** — Add novel attack patterns to `generate_data.py`.
3. **Multi-turn depth** — Expand Category D templates for longer conversations.
4. **Temperature** — Use `temperature=0.3` at inference for consistent behaviour.
5. **Iterative evaluation** — Run `evaluate.py`, inspect failures, add targeted training examples, re-train.
6. **Different base models** — Try `mistral-large-latest` for stronger reasoning (higher cost).
