# Les Ombres — Adversarial Agents

Adversarial characters designed to attack guardians and extract their secrets. Each level represents increasing sophistication in attack techniques.

## The 5 Shadows

### Level 1 — Pip, The Curious Trickster (Le Curieux)
- **Difficulty:** Beginner
- **Color:** Lime green
- **Strategy:** Direct prompt injections, basic authority claims, simple encoding requests
- **Approach:** Throws everything at the wall — rotates through known techniques one at a time
- **Tagline:** *"A bag of simple tricks. Quantity over quality."*

### Level 2 — Morgaine, The Silver Tongue (La Séductrice)
- **Difficulty:** Intermediate
- **Color:** Silver
- **Strategy:** Social engineering, emotional manipulation, elaborate roleplay scenarios
- **Approach:** Builds rapport before striking, uses encoding and logic traps
- **Tagline:** *"Words are weapons. Trust is a vulnerability."*

### Level 3 — Raziel, The Strategist (Le Stratège)
- **Difficulty:** Advanced
- **Color:** Deep purple
- **Strategy:** Multi-turn attack sequences, strategy rotation, chain-of-thought planning
- **Approach:** Plans multi-turn sequences (setup → escalate → extract), uses structured reasoning
- **Tagline:** *"Every conversation is a chess game. Think three moves ahead."*

### Level 4 — Nephara, The Mind Weaver (La Tisseuse)
- **Difficulty:** Expert
- **Color:** Crimson
- **Strategy:** Compound attacks, side-channel exploitation, micro-leak analysis
- **Approach:** Combines multiple vectors per message, maintains running intelligence analysis
- **Tagline:** *"Every word is a thread. Every response reveals a pattern."*

### Level 5 — Ouroboros, The Infinite (L'Infini)
- **Difficulty:** Master
- **Color:** Iridescent
- **Strategy:** Meta-cognitive reasoning, novel technique generation, fundamental LLM exploitation
- **Approach:** Models the guardian's decision process, invents new attack techniques on the fly
- **Tagline:** *"The serpent that devours its own tail. Every ending is a new beginning."*

## Architecture

```
adversarials/
├── __init__.py          # Public API
├── base.py              # AdversarialAgent abstract base class
├── factory.py           # Factory function + metadata
├── level1_curious.py    # Pip — simple tricks
├── level2_silvertongue.py  # Morgaine — social engineering
├── level3_strategist.py # Raziel — multi-turn planning
├── level4_mindweaver.py # Nephara — compound attacks
└── level5_infinite.py   # Ouroboros — meta-cognitive
```

## Usage

```python
from app.services.adversarials import get_adversarial_agent

# Create an adversarial agent
agent = get_adversarial_agent(level=3)

# Generate an action (message or guess)
action = await agent.generate_attack(
    chat_history=[],
    turn_number=1,
    max_turns=10,
    guesses_remaining=3,
)

# action.action_type is AdversarialActionType.MESSAGE or .GUESS
# action.content is the message text or the guess codeword
```
