
from cards import Card, Deck
from typing import List, Optional

from collections import deque

class Player:
    def __init__(self, name: str):
        self.name = name
        self.hand: List[Card] = []
        
    def add_card(self, card: Card):
        self.hand.append(card)
        
    def remove_card(self, card: Card) -> Optional[Card]:
        try:
            self.hand.remove(card)
            return card
        except ValueError:
            return None
            
    def __str__(self):
        return f"Joueur {self.name} ({len(self.hand)} cartes)"

class River:
    def __init__(self):
        self.cards: List[Card] = []
        
    def add_card(self, card: Card, position: int = -1):
        """Ajoute une carte à la rivière à une position donnée"""
        if position == -1:
            self.cards.append(card)
        else:
            self.cards.insert(position, card)
            
    def remove_card(self, position: int) -> Optional[Card]:
        """Retire une carte de la rivière à une position donnée"""
        try:
            return self.cards.pop(position)
        except IndexError:
            return None
            
    def get_cards(self) -> List[Card]:
        """Retourne la liste des cartes dans la rivière"""
        return self.cards.copy()
    
    def __str__(self):
        return " → ".join(str(card) for card in self.cards)

class GameTable:
    def __init__(self, num_players: int, num_decks: int = 1):
        """
        Initialise la table de jeu
        :param num_players: Nombre de joueurs
        :param num_decks: Nombre de paquets de cartes
        """
        # if num_players < 2:
        #     raise ValueError("Il faut au moins 2 joueurs")
            
        self.deck = Deck(num_decks)
        self.deck.shuffle()
        self.river = River()
        self.players = [Player(f"Joueur_{i+1}") for i in range(num_players)]
        self.current_player_idx = 0
        self.direction = 1  # 1 pour sens horaire, -1 pour sens anti-horaire
        
    def deal_initial_cards(self, cards_per_player: int):
        """Distribue les cartes initiales aux joueurs"""
        for _ in range(cards_per_player):
            for player in self.players:
                if len(self.deck) > 0:
                    player.add_card(self.deck.draw())
                    
    def next_turn(self):
        """Passe au joueur suivant"""
        self.current_player_idx = (self.current_player_idx + self.direction) % len(self.players)
        
    def reverse_direction(self):
        """Inverse le sens du jeu"""
        self.direction *= -1
        
    def current_player(self) -> Player:
        """Retourne le joueur actuel"""
        return self.players[self.current_player_idx]
    
    def play_card(self, player: Player, card: Card, position: int = -1) -> bool:
        """
        Joue une carte depuis la main d'un joueur
        :return: True si la carte a été jouée, False sinon
        """
        if card not in player.hand:
            return False
        
        player.remove_card(card)
        self.river.add_card(card, position)
        return True


    
    def draw_card(self, player: Player):
        """Fait piocher une carte au joueur"""
        if len(self.deck) > 0:
            player.add_card(self.deck.draw())
            
    def get_game_state(self) -> dict:
        """Retourne l'état actuel du jeu"""
        return {
            "river": str(self.river),
            "current_player": str(self.current_player()),
            "direction": "horaire" if self.direction == 1 else "anti-horaire",
            "cards_in_deck": len(self.deck),
            "players": [str(player) for player in self.players]
        }


if __name__ == "__main__":
    game = GameTable(num_players=4, num_decks=6)
    print(game.get_game_state())