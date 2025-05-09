from cards import TrainCard
from cards import DestinationTicketCard
from collections import Counter


class Player:
    def __init__(self, name, trains=45, train_cards: list[TrainCard]=[], destination_tickets: list[DestinationTicketCard]=[]):
        self.name = name
        self.trains = trains
        self.train_cards = train_cards
        self.destination_tickets = []
        self.accomplished_destination_tickets = []
        self.score = 0

    def __str__(self):
        train_cards_str = ", ".join(card.name for card in self.train_cards)
        tickets_str = "\n  ".join(str(ticket) for ticket in self.destination_tickets)

        return (f"Player: {self.name}\n"
                f"  Trains remaining: {self.trains}\n"
                f"  Train cards: [{train_cards_str}]\n"
                f"  Destination tickets:\n  {tickets_str if tickets_str else 'None'}\n"
                f"  Score: {self.score}")

    def can_afford(self, cost: list[TrainCard]) -> bool:
        hand = Counter(self.train_cards)
        cost_counter = Counter(cost)

        for color, count in cost_counter.items():
            if color == TrainCard.LOCOMOTIVE:
                # Player must have enough locomotives
                if hand[TrainCard.LOCOMOTIVE] < count:
                    return False
            elif color == TrainCard.GREY:
                # GREY routes are flexible, check if player has any color + locomotives to meet the cost
                has_option = any(
                    (hand[c] + hand[TrainCard.LOCOMOTIVE]) >= count
                    for c in TrainCard
                    if c not in (TrainCard.LOCOMOTIVE, TrainCard.GREY)
                )
                if not has_option:
                    return False
            else:
                available = hand[color] + hand[TrainCard.LOCOMOTIVE]
                if available < count:
                    return False
        return True

    def spend_cards(self, cost: list[TrainCard]):
        for card in cost:
            if card in self.train_cards:
                self.train_cards.remove(card)
            elif TrainCard.LOCOMOTIVE in self.train_cards:
                self.train_cards.remove(TrainCard.LOCOMOTIVE)
            else:
                raise ValueError("Player does not have required cards to spend.")

