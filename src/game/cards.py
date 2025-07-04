from enum import Enum
from random import shuffle
import yaml
import os

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

    def is_accomplished(self, player: "Player"):
        """
        Checks if the destination ticket is accomplished for the given player.
        DFS is used to check if there is a path between the start and end cities.
        """
        from player import Player

        start_city = player.get_city(self.start_city)
        end_city = player.get_city(self.end_city)

        if start_city == None or end_city == None:
            return False

        # Check if the cities are connected
        def dfs(city, visited):
            print(f"DFS visiting city: {city.name}")
            if city == end_city:
                return True

            visited.add(city)
            for neighbor in city.get_connected_cities():
                if neighbor not in visited:
                    if dfs(neighbor, visited):
                        return True
            
            return False

        visited = set()
        result = dfs(start_city, visited)
        print(f"Result of DFS: {'Accomplished' if result else 'Not accomplished'}")
        return result
    

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

    def add_card_to_bottom(self, card: TrainCard):
        """
        Adds a card to the bottom of the deck.
        """

        self.cards.insert(0, card)


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


        self.screen_position = (0.9, 0.2) # From 0 to 1. 0, 0 is the top left corner, 1, 1 is the bottom right corner

    def __str__(self):
        return f"TrainCardsDeck: [{', '.join(str(card) for card in self.cards)}]"


class DestinationTicketsDeck(Deck):
    def __init__(
        self,
        cards: list[TrainCard] = [],
        config_file: str = os.path.join(
            os.path.dirname(__file__), "../config/set_europe_close_up/europe_map_close_up.yaml"
        ),
    ):

        self.cards = cards

        if not cards:
            self.init_deck_from_config(config_file)


        self.screen_position = (0.9, 0.4) # From 0 to 1. 0, 0 is the top left corner, 1, 1 is the bottom right corner

    def init_deck_from_config(self, config_file: str):
        """
        Initializes the deck from a config file.
        """

        with open(config_file, "r") as file:
            data = yaml.safe_load(file)

        for ticket_data in data["tickets"]:

            city1_name, city2_name = ticket_data["cities"]
            points = ticket_data["points"]

            ticket = DestinationTicketCard(city1_name, city2_name, points)
            self.cards.append(ticket)

        self.shuffle()

    def __str__(self):
        return f"DestinationTicketsDeck: [\n{'\n'.join(str(card) for card in self.cards)}\n]"


class OpenCardsDeck(Deck):
    def __init__(self, train_cards_deck: TrainCardsDeck = None):
        self.cards = []
        self.train_cards_deck = train_cards_deck
        self.draw_initial_cards()
        self.screen_position = (0.6, 0.02) # From 0 to 1. 0, 0 is the top left corner, 1, 1 is the bottom right corner
        self.screen_gap = 0.05 # Gap between cards on the screen

    def __str__(self):
        return f"OpenCardsDeck: [ {' '.join(str(card) for card in self.cards)}]"

    def draw_card(self, index: int):
        """
        Draws a card from the open cards deck at the specified index.
        """

        if index < 0 or index >= len(self.cards):
            raise IndexError("Index out of range")

        return self.cards.pop(index)

    def draw_initial_cards(self):
        """
        Draws 5 initial cards from the train cards deck.
        """

        if self.train_cards_deck is None:
            raise ValueError("train_cards_deck must be provided")

        for _ in range(5):
            card = self.train_cards_deck.draw_card()
            if card:
                self.cards.append(card)
