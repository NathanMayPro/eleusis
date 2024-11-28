from enum import Enum

class Suit(Enum):
    HEARTS = "♥"
    DIAMONDS = "♦"
    CLUBS = "♣"
    SPADES = "♠"

class Card:
    def __init__(self, rank, suit):
        """
        Initialize a playing card
        :param rank: 2-10, J, Q, K, A
        :param suit: Hearts, Diamonds, Clubs, Spades
        """
        if isinstance(rank, int):
            if not (2 <= rank <= 10):
                raise ValueError("Numeric rank must be between 2 and 10")
        elif rank not in ['J', 'Q', 'K', 'A']:
            raise ValueError("Face card rank must be J, Q, K, or A")
            
        if not isinstance(suit, Suit):
            raise ValueError("Suit must be a valid Suit enum value")
            
        self.rank = rank
        self.suit = suit
        
    @property
    def color(self):
        """Return the color of the card (red or black)"""
        return "red" if self.suit in [Suit.HEARTS, Suit.DIAMONDS] else "black"
    
    def __str__(self):
        """String representation of the card"""
        return f"{self.rank}{self.suit.value}"
    
    def __repr__(self):
        """Detailed string representation of the card"""
        return f"Card(rank={self.rank}, suit={self.suit})"
    
    def __eq__(self, other):
        """Compare two cards for equality"""
        if not isinstance(other, Card):
            return False
        return self.rank == other.rank and self.suit == other.suit
    
    def rank_value(self) -> int:
        """Convert card rank to numeric value (Ace=1, Jack=11, Queen=12, King=13)"""
        if isinstance(self.rank, int):
            return self.rank
        # Convert face cards to numbers
        face_values = {
            'A': 1,
            'J': 11,
            'Q': 12,
            'K': 13
        }
        return face_values.get(self.rank, 0)

class Deck:
    def __init__(self, num_decks=1):
        """
        Initialize a deck or multiple decks of cards
        :param num_decks: Number of standard decks to include
        """
        self.cards = []
        ranks = list(range(2, 11)) + ['J', 'Q', 'K', 'A']
        
        for _ in range(num_decks):
            for suit in Suit:
                for rank in ranks:
                    self.cards.append(Card(rank, suit))
                    
    def shuffle(self):
        """Shuffle the deck"""
        from random import shuffle
        shuffle(self.cards)
        
    def draw(self):
        """Draw a card from the deck"""
        if not self.cards:
            raise ValueError("No cards left in the deck")
        return self.cards.pop()
    
    def __len__(self):
        """Return the number of cards remaining in the deck"""
        return len(self.cards)


if __name__ == "__main__":
    deck = Deck(num_decks=6)
    print(deck.draw())
    print(deck.draw())
    print(deck.draw())
    print(deck.draw())
    print(deck.draw())
    print(deck.draw())