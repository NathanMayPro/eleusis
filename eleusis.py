from gametable import GameTable, Player
from cards import Card
from enum import Enum
from typing import Callable, List, Optional, Tuple
import random
import json
import sys
import os
from rules import get_random_rule
from time import sleep
import datetime
from llm import Action, Hypothesis, CardIndex, haiku_play, test_hypothesis
class GamePhase(Enum):
    PLAYING = "playing"
    RULE_DISCOVERY = "rule_discovery"
    SCORING = "scoring"

class EleusisGame:
    def __init__(self, num_players: int):
        self.table = GameTable(num_players)
        self.prophet: Optional[Player] = None
        self.current_rule: Optional[Callable[[List[Card]], bool]] = None
        self.current_rule_description: str = ""
        self.phase = GamePhase.PLAYING
        self.mainline: List[Card] = []
        self.sidelines: List[Tuple[Card, List[Card]]] = []
        
        self.scores = {player: 0 for player in self.table.players}
        self.current_player_idx = 0
        self.history = []
        
    def setup_round(self, prophet_idx: int):
        """Setup a new round with a new prophet"""
        self.prophet = self.table.players[prophet_idx]
        self.mainline = []
        self.sidelines = []
        self.phase = GamePhase.PLAYING
        
        # Deal cards
        self.table.deal_initial_cards(7)
        
        # Prophet sets the rule
        self.set_rule()
        
    def set_rule(self):
        """Prophet sets the rule by randomly selecting one"""
        self.current_rule, self.current_rule_description = get_random_rule()
        
    def play_card(self, player: Player, card: Card) -> bool:
        """
        Player attempts to play a card
        Returns True if card was valid according to rule, None if game is over
        """
        if player not in self.table.players or card not in player.hand:
            return False
            
        is_valid = self.current_rule(self.mainline + [card])
        
        if is_valid:
            self.mainline.append(card)
            print(f"Player {player} played {card} - valid")
            self.scores[player] += 1
            player.remove_card(card)
            self.history.append({
                "turn": len(self.history),
                "player": str(player),
                "action": "PLAY",
                "card": str(card),
                "valid": True,
                "mainline": [str(c) for c in self.mainline],
                "scores": {str(p): s for p, s in self.scores.items()}
            })
            self.next_player()
            
        else:
            self.sidelines.append((card, self.mainline.copy()))
            self.history.append({
                "turn": len(self.history),
                "player": str(player),
                "action": "PLAY",
                "card": str(card),
                "valid": False,
                "mainline": [str(c) for c in self.mainline],
                "scores": {str(p): s for p, s in self.scores.items()}
            })
            self.deal_cards(player, 2)
            player.remove_card(card)
        
        # check if the game is over
        if self.is_over():
            return None
        
        return is_valid
        
    def claim_prophet(self, player: Player) -> bool:
        """
        Player claims to know the rule and becomes temporary prophet
        Returns False if player makes a mistake
        """
        if self.phase != GamePhase.PLAYING:
            return False
            
        self.prophet = player
        return True

    def deal_cards(self, player: Player, num_cards: int):
        """Deal cards to a player"""
        for _ in range(num_cards):
            self.table.draw_card(player)

    def score_round(self):
        """Score the round based on valid/invalid plays"""
        self.phase = GamePhase.SCORING
        
        # Score based on correct/incorrect plays
        for player, sideline in self.sidelines.items():
            # Subtract points for incorrect plays
            self.scores[player] -= len(sideline) * 2
            
        # Add points for correct plays
        for player in self.table.players:
            player_cards = [c for c in self.mainline if c in player.hand]
            self.scores[player] += len(player_cards) * 5
            
        # Bonus for prophet if rule was good
        total_plays = len(self.mainline) + sum(len(s) for s in self.sidelines)
        valid_ratio = len(self.mainline) / total_plays
        if 0.2 <= valid_ratio <= 0.8:
            self.scores[self.prophet] += 25
            
    def get_game_state(self) -> dict:
        """Return current game state in a human-readable format"""
        mainline_str = ' → '.join([str(card) for card in self.mainline]) if self.mainline else "Empty"
        sidelines_str = '\n'.join([
            f"  {str(card)} (invalid) when mainline was: {' → '.join(str(c) for c in history)}"
            for card, history in self.sidelines
        ]) if self.sidelines else "None"
        
        state = {
            "Current Phase": self.phase.value.upper(),
            "Prophet": str(self.prophet),
            "Current Player": str(self.get_current_player()),
            "Mainline": mainline_str,
            "Invalid Plays": sidelines_str,
            "Scores": '\n'.join([f"  {str(p)}: {s} points" for p, s in self.scores.items()]),
            "Current Rule": self.current_rule_description
        }
        
        # Create a formatted string
        output = "\n=== ELEUSIS GAME STATE ===\n"
        for key, value in state.items():
            output += f"\n{key}:\n{value}\n"
        output += "\n======================="
        
        return output
    
    def is_over(self) -> bool:
        """Return True if the game is over"""
        return any(len(player.hand) == 0 for player in self.table.players)
    
    def next_player(self) -> Player:
        """Move to next player and return that player"""
        self.current_player_idx = (self.current_player_idx + 1) % len(self.table.players)
        return self.table.players[self.current_player_idx]

    def get_current_player(self) -> Player:
        """Return the current player"""
        return self.table.players[self.current_player_idx]
        
    def get_player_perspective(self, player: Player) -> str:
        """
        Return game state from a specific player's perspective, formatted for LLM input.
        Includes game history and available cards, but not the rule.
        """
        # Format mainline history
        mainline_str = ' → '.join([str(card) for card in self.mainline]) if self.mainline else "Empty"
        
        # Format invalid plays history with their contexts
        sidelines_str = '\n'.join([
            f"  {str(card)} was invalid when mainline was: {' → '.join(str(c) for c in history)}"
            for card, history in self.sidelines
        ]) if self.sidelines else "None"
        
        # Get player's current hand
        hand_str = ', '.join([str(card) for card in player.hand])
        
        # Create a formatted string for LLM
        output = f"""
=== ELEUSIS GAME STATE FOR {player} ===

Your Hand:
{hand_str}

Current Mainline (Valid Plays):
{mainline_str}

History of Invalid Plays:
{sidelines_str}

You are {player} and it's {'your turn' if self.get_current_player() == player else f"currently {self.get_current_player()}'s turn"}
"""
        return output
    
    def terminate(self):
        """Terminate the game"""
        # remove all players hands
        for player in self.table.players:
            player.hand = []

class LLM:
    def __init__(self, play_fn: Callable[[str], Action]):
        self.play_fn = play_fn
        
    def play(self, perspective: str) -> Action:
        return self.play_fn(perspective)


class EleusisLLM(EleusisGame):
    def __init__(self, llm: LLM):
        super().__init__(1)
        self.llm = llm
        self.previous_rounds = []

    def make_game(self, sleep_time: float = 0.5) -> EleusisGame:
        
        self.setup_round(0)
        
        # Setup history file
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"./logs/game_history_{timestamp}.jsonl"
        
        os.makedirs("./logs", exist_ok=True)
        
        while not self.is_over():
            current_player = self.get_current_player()
            perspective = self._build_player_perspective(current_player)
            action = self.llm.play(perspective)
            
            # Record action and process it
            history_entry = self._process_player_action(current_player, action)
            
            # Save history
            with open(filename, "a") as f:
                f.write(json.dumps(history_entry) + "\n")
            
            sleep(sleep_time)
            
        return

    def _build_player_perspective(self,player: Player) -> str:
        """Build enhanced perspective including history and previous thoughts"""
        perspective = self.get_player_perspective(player)
        if self.previous_rounds:
            perspective += f"\n\nHistory of your previous rounds:\n"
            for round in self.previous_rounds:
                perspective += f"{round['current_player_hypothesis']} ({round['current_player_hypothesis_result']})\n"
        print(f"{perspective}\n{self.current_rule_description}")
        return perspective

    def _process_player_action(self, player: Player, action: Action) -> dict:
        """Process player action and return history entry"""
        
        history_entry = {
            "turn": len(self.history),
            "player": str(player),
            "hypothesis": action.general_hypothesis,
            "timestamp": datetime.datetime.now().isoformat(),
            "rule": self.current_rule_description
        }

        if action.card_index is not None:
            card = player.hand[action.card_index]
            history_entry["card_played"] = str(card)
            was_valid = self.play_card(player, card)
            history_entry["was_valid"] = was_valid
            history_entry["result"] = "valid_play" if was_valid else "invalid_play"
            
            if was_valid is None:
                self.terminate()
                history_entry["result"] = "game_over"
                
        
        hypothesis = action.general_hypothesis
        history_entry["hypothesis"] = hypothesis
        valid, reason = self.validate_hypothesis(hypothesis)
        history_entry["hypothesis_valid"] = valid
        
        if valid:
            self.terminate()
        else:
            self.deal_cards(player, 2)
        history_entry["result"] = reason

        # Add game state snapshot
        history_entry["game_state"] = {
            "mainline": [str(c) for c in self.mainline],
            "scores": {str(p): s for p, s in self.scores.items()},
            "current_player_hand": [str(c) for c in player.hand]
        }
        self.previous_rounds.append({
            "mainline": [str(c) for c in self.mainline],
            "scores": {str(p): s for p, s in self.scores.items()},
            "current_player_hand": [str(c) for c in player.hand],
            "current_player_hypothesis": action.general_hypothesis,
            "current_player_hypothesis_result": history_entry["result"]
        })
        
        return history_entry

    def validate_hypothesis(self, hypothesis: str):
        """Validate a hypothesis"""
        response =  test_hypothesis(hypothesis, self.current_rule_description, self.get_game_state())
        return response.is_valid, response.reason
     

    
    

    
        
if __name__ == "__main__":
    
    eleusis = EleusisLLM(LLM(haiku_play))
    
    eleusis.make_game(sleep_time=3)
    # # Create game with 4 players
    # game = EleusisGame(4)

    # # Start first round with player 0 as prophet
    # self.setup_round(0)

    # for i in range(100):
    #     current_player = self.get_current_player()
        
    #     if not current_player.hand:  # Check if player has no cards
    #         print(f"Game over! Player {current_player} wins!")
    #         break
    #     from llm import gtp4_mini_play, haiku_play
    #     if self.current_player_idx == 0:
    #         card_to_play_idx = gtp4_mini_play(self.get_player_perspective(current_player)).index_of_card_to_play
    #     else:
    #         card_to_play_idx = haiku_play(self.get_player_perspective(current_player)).index_of_card_to_play
    #     card_to_play = current_player.hand[card_to_play_idx]
    #     print(f"Player {current_player} has {';'.join(str(card) for card in current_player.hand)} in hand and play {card_to_play}")
    #     was_valid = self.play_card(current_player, card_to_play)
        
    #     if was_valid is None:  # Game is over
    #         print(f"Game over! Player {current_player} wins!")
    #         break
            
    #     print(f"Player {current_player} played {card_to_play} - valid: {was_valid}")
    #     if not was_valid:
    #         print(f"Player {current_player} did not play a valid card - drawing two more cards")
    #         print(f"Player {current_player} now has {';'.join(str(card) for card in current_player.hand)} in hand")
    #         # current player get two more cards
    #         self.deal_cards(current_player, 2)
    #         print(f"Player {current_player} now has {';'.join(str(card) for card in current_player.hand)} in hand")
        
    #     # next player
    #     self.next_player()
    
    #     # get the game state
    #     state = self.get_game_state()
    #     print(state)
    #     input("Press Enter to continue...")
    # exit()
    # # Player claims to know rule
    # self.claim_prophet(self.table.players[2])

    # # Score the round
    # self.score_round()

    # # Get game state
    # state = self.get_game_state()
    # print(f"Current phase: {state['phase']}")
    # print(f"Mainline: {state['mainline']}")
    # print(f"Scores: {state['scores']}")