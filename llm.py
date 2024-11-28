from mirascope.core import openai, anthropic, prompt_template
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from enum import Enum
load_dotenv()


class Hypothesis(BaseModel):
    hypothesis: str = Field(description="""A hypothesis about the rules of the game. The hypothesis must be complete and correct.
The rules can be about any combination of:
- Card colors (red/black)
- Card ranks (Ace=1, 2-10 as numbers, J=11, Q=12, K=13)
- Card suits (♥, ♦, ♣, ♠)
- Relationships between consecutive cards

The hypothesis must validate all the accepted plays in the game history.

Example: "After a heart, next card must be higher rank."
""")

class CardIndex(BaseModel):
    index_of_card_to_play: int = Field(description="The index of the card to play, starting from 0.")

class Action(BaseModel):
    general_hypothesis: str = Field(description="""The most probable hypothesis about the rules of the game. Ensure you're hypothesis is coherent with the history of the game.
The rules can be about any combination of:
- Card colors (red/black)
- Card ranks (Ace=1, 2-10 as numbers, J=11, Q=12, K=13)
- Card suits (♥, ♦, ♣, ♠)
- Relationships between consecutive cards
The hypothesis must validate all the accepted plays in the game history.
Example: "After a heart, next card must be higher rank.""")
    card_index: int= Field(description="The index of the card to play, starting from 0")




@anthropic.call("claude-3-5-haiku-latest", json_mode=True, response_model=Action)
@prompt_template(
    "You ara a player of Eleusis."
    "Here are the rules of the game:"
    "{eleusis_rules}"
    "This is the current state of the game:"
    "{game_state}"
    "The goal is to find the rule that can provide this mainline of valid plays."
    "The rule must also validate all the invalid plays in the game history."
    "Of course, the rule is a general rule and can provide multiple mainline but with always the same logic."
    "The game is to find the correct hypothesis about the rules of the game."
)
def haiku_play(game_state: str, eleusis_rules: str = open("ELEUSIS_RULES.md").read()) -> Action:
    ...



class HypothesisValidation(BaseModel):
    is_valid: bool = Field(description="Whether the hypothesis is valid or not, only in case of CORRECT.")
    reason: str = Field(description="""Can be: 
- CORRECT if the hypothesis matches the rules exactly.
- INCORRECT MAINLINE CONTRADICTION if the hypothesis contradicts the mainline of valid plays.
- INCORRECT HISTORY CONTRADICTION if the hypothesis contradicts the history of invalid plays.
- INCORRECT if the hypothesis is incorrect.

for example: "Cards must alternate between red and black" and you see in the mainline two consecutive cards of the same color, then the reason is INCORRECT MAINLINE CONTRADICTION.
""")

@anthropic.call("claude-3-5-sonnet-latest", response_model=HypothesisValidation, json_mode=True)
@prompt_template(
    "You are the judge of an Eleusis game."
    "You are given a hypothesis and the real rules of the game."
    "You need to determine if the hypothesis is valid or not."
    "The hypothesis is: {hypothesis}"
    "The real rules of the game are: {rule}"
    "This is the current state of the game:"
    "{game_state}"
    "You need to return True if the hypothesis is valid, False otherwise."
    "Check if the hypothesis is equivalent, complete and correct with the real rules of the game."
)
def test_hypothesis(hypothesis: str, rule: str, game_state: str) -> HypothesisValidation:
    ...
    
if __name__ == "__main__":
    game_state = """=== ELEUSIS GAME STATE FOR Joueur Joueur_1 (7 cartes) ===

Your Hand:
Q♣, 6♦, 2♣, J♣, 3♣, 9♥, 10♦

Current Mainline (Valid Plays):
Empty

History of Invalid Plays:
None

Current Scores:
  Joueur Joueur_1 (7 cartes): 0 points
  Joueur Joueur_2 (7 cartes): 0 points
  Joueur Joueur_3 (7 cartes): 0 points
  Joueur Joueur_4 (7 cartes): 0 points

You are Joueur Joueur_1 (7 cartes) and it's your turn

Based on the history of valid and invalid plays above, which card from your hand would you play?
Please respond with just the card you would play in the format: PLAY <card>
For example: PLAY K♠"""
    
    print(haiku_play(game_state))
    
    print(test_hypothesis("Any card can be played since there have been no previous valid plays.", "After an even rank, must play a black card"))