from enum import Enum
from random import shuffle


class TrainCard(Enum):
    PINK = 1
    WHITE = 2
    BLACK = 3
    BLUE = 4
    YELLOW = 5
    ORANGE = 6
    GREEN = 7
    RED = 8
    LOCOMOTIVE = 9
    GREY = 10

    def __str__(self):
        return f"{self.name}"


class DestinationTicketCard:
    def __init__(self, start_city: str, end_city: str, points: int):
        self.start_city = start_city
        self.end_city = end_city

        self.points = points

    def __str__(self):
        return (
            f"DestinationTicketCard: {self.start_city} -> {self.end_city}, "
            f"Points: {self.points}"
        )


class Deck:
    def __init__(self):
        self.cards = []

    def shuffle(self):
        """
        Shuffles the deck of cards.
        """

        shuffle(self.cards)

    def draw_card(self):
        """
        Draws a card from the deck."""

        return self.cards.pop() if self.cards else None

    def return_cards(self, cards: list[TrainCard]):
        """
        Returns a list of cards to the deck and shuffles it.
        """

        self.cards.extend(cards)
        self.shuffle()

    def add_card(self, card: TrainCard):
        """
        Adds a card to the deck.
        """

        self.cards.append(card)

class TrainCardsDeck(Deck):
    def __init__(self):
        self.cards = [
            TrainCard.PINK,
            TrainCard.WHITE,
            TrainCard.BLACK,
            TrainCard.BLUE,
            TrainCard.YELLOW,
            TrainCard.ORANGE,
            TrainCard.GREEN,
            TrainCard.RED,
        ] * 12 + [TrainCard.LOCOMOTIVE] * 14
        self.shuffle()

    def __str__(self):
        return f"TrainCardsDeck: [{', '.join(str(card) for card in self.cards)}]"


class DestinationTicketsDeck(Deck):
    def __init__(self):
        self.cards = []

    def __str__(self):
        return f"DestinationTicketsDeck: [{', '.join(str(card) for card in self.cards)}]"
