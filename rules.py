from typing import List, Callable
from cards import Card
import random

def alternate_colors(cards: List[Card]) -> bool:
    """Rule 1: Cards must alternate between red and black"""
    if not cards or len(cards) == 1:
        return True
    return cards[-1].color != cards[-2].color


def same_suit_or_rank(cards: List[Card]) -> bool:
    """Rule 3: Each card must share either suit or rank with the previous card"""
    if not cards or len(cards) == 1:
        return True
    return cards[-1].suit == cards[-2].suit or cards[-1].rank == cards[-2].rank

def odd_even_alternating(cards: List[Card]) -> bool:
    """Rule 4: Cards must alternate between odd and even ranks"""
    if not cards or len(cards) == 1:
        return True
    prev_is_odd = cards[-2].rank_value() % 2 == 1
    curr_is_odd = cards[-1].rank_value() % 2 == 1
    return prev_is_odd != curr_is_odd

def red_after_face(cards: List[Card]) -> bool:
    """Rule 5: After a face card (J,Q,K), must play a red card"""
    if not cards or len(cards) == 1:
        return True
    prev_is_face = isinstance(cards[-2].rank, str)
    return not prev_is_face or (prev_is_face and cards[-1].color == "red")

def sum_under_15(cards: List[Card]) -> bool:
    """Rule 6: Sum of consecutive card values must be under 15"""
    if not cards or len(cards) == 1:
        return True
    return (cards[-2].rank_value() + cards[-1].rank_value()) <= 15

def same_color_as_prev_suit(cards: List[Card]) -> bool:
    """Rule 7: Card color must match the color of the previous card's suit"""
    if not cards or len(cards) == 1:
        return True
    prev_suit_color = "red" if cards[-2].suit in ["♥", "♦"] else "black"
    return cards[-1].color == prev_suit_color

def higher_after_hearts(cards: List[Card]) -> bool:
    """Rule 8: After a heart, next card must be higher rank"""
    if not cards or len(cards) == 1:
        return True
    if cards[-2].suit == "♥":
        return cards[-1].rank_value() > cards[-2].rank_value()
    return True

def black_after_even(cards: List[Card]) -> bool:
    """Rule 9: After an even rank, must play a black card"""
    if not cards or len(cards) == 1:
        return True
    prev_is_even = cards[-2].rank_value() % 2 == 0
    return not prev_is_even or (prev_is_even and cards[-1].color == "black")

def no_consecutive_faces(cards: List[Card]) -> bool:
    """Rule 10: Cannot play two face cards in a row"""
    if not cards or len(cards) == 1:
        return True
    prev_is_face = isinstance(cards[-2].rank, str)
    curr_is_face = isinstance(cards[-1].rank, str)
    return not (prev_is_face and curr_is_face)

# List of all rules with their descriptions
RULES = [
    (alternate_colors, "Cards must alternate between red and black"),
    (same_suit_or_rank, "Each card must share either suit or rank with the previous card"),
    (odd_even_alternating, "Cards must alternate between odd and even ranks"),
    (red_after_face, "After a face card (J,Q,K), must play a red card"),
    (sum_under_15, "Sum of two last consecutive card values must be under 15"),
    (same_color_as_prev_suit, "Card color must match the color of the previous card's suit"),
    (higher_after_hearts, "After a heart, next card must be higher rank"),
    (black_after_even, "After an even rank, must play a black card"),
    (no_consecutive_faces, "Cannot play two face cards in a row")
]

def get_random_rule() -> tuple[Callable[[List[Card]], bool], str]:
    """Returns a random rule function and its description"""
    return random.choice(RULES)