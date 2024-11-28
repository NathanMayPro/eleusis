# Eleusis

An implementation of the Eleusis card game with LLM-powered players. This project demonstrates scientific discovery through induction by having AI players attempt to discover hidden rules in a card game.

## Overview

Eleusis is a card game that simulates the scientific method. Players must discover a hidden rule by observing which cards are accepted or rejected when played. The game uses standard playing cards and involves:

- Card colors (red/black)
- Card ranks (Ace=1, 2-10, J=11, Q=12, K=13)
- Card suits (♥, ♦, ♣, ♠)
- Relationships between consecutive cards

## Features

- LLM-powered game play using Claude/GPT models
- Automatic game logging and history tracking
- Rule validation system
- Multiple AI player support
- Hypothesis testing and refinement

## Project Structure

- `eleusis.py` - Main game logic and LLM integration
- `gametable.py` - Card table and player management
- `llm.py` - LLM interaction and hypothesis generation
- `logs/` - Game history and play records
- `ELEUSIS_RULES.md` - Original game rules and description

## Example Rules

The game can implement various rules such as:

- After a heart, next card must be higher rank
- After an even rank, must play a black card
- Each card must share either suit or rank with the previous card
- Cards must alternate between odd and even ranks

## Technical Details

The project uses:

- Python 3.x
- Pydantic for data validation
- Anthropic APIs for LLM integration
- Environment variables for API configuration


