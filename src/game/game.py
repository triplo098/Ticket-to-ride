from collections import Counter
from map import Map, City, CityConnection, get_city_by_name
from cards import (
    DestinationTicketCard,
    TrainCardsDeck,
    DestinationTicketsDeck,
    TrainCard,
    OpenCardsDeck,
)
from player import Player


class Game:
    """
    Handles game logic.
    """

    def __init__(
        self,
        players: list[Player],
        map: Map,
        train_cards_deck: TrainCardsDeck,
        destination_tickets_deck: DestinationTicketsDeck,
        open_cards_deck: OpenCardsDeck,
        current_player_index: int,
    ):
        self.players = players
        self.map = map
        self.train_cards_deck = train_cards_deck
        self.destination_tickets_deck = destination_tickets_deck
        self.open_cards_deck = open_cards_deck
        self.current_player_index = current_player_index
        self.turn_number = 0
        self.game_over = False

    def __str__(self):
        players_str = "\n".join(str(player) for player in self.players)

        return (
            f"Game Status:\n\n"
            f"Players:\n{players_str}\n\n"
            f"Map:\n{self.map}\n\n"
            f"Train Cards Deck:\n[{self.train_cards_deck}]\n\n"
            f"Destination Tickets Deck:\n[{self.destination_tickets_deck}]\n\n"
            f"Turn Number: {self.turn_number}\n"
            f"Current Player: {self.players[self.current_player_index].name}\n"
            f"Game Over: {self.game_over}"
        )

    def play_game(self):
        """
        Play the game loop.
        """
        while not self.game_over:
            self.play_turn()
            if self.if_start_last_round():
                self.game_over = True

                for _ in range(len(self.players)):
                    self.play_turn()

                self.print_final_scores()
                break

        print("\nGame Over!")

    def print_final_scores(self):
        """
        Prints the final scores of all players.
        """
        print("\nFinal Scores:")
        for player in self.players:
            print(f"{player.name}: {player.score} points")

    def draw_card(self, player: Player):

        drew_cards = 0

        while drew_cards < 2:
            print(f"{self.open_cards_deck}")

            choice = input(
                "Choose an action:\n 1. From the deck\n 2. From the open cards\n"
            )
            match choice:

                case "1":
                    player.train_cards.append(self.train_cards_deck.draw_card())
                    drew_cards += 1
                case "2":
                    index = int(
                        input("Choose an index of the open card to draw (0-4): ")
                    )
                    if index < 0 or index >= len(self.open_cards_deck.cards):
                        print("Invalid index. Please try again.")
                        continue

                    if (
                        self.open_cards_deck.cards[index] == TrainCard.LOCOMOTIVE
                        and drew_cards == 1
                    ):
                        print(
                            "You cannot draw a locomotive card from the open cards after drawing one."
                        )
                        continue

                    card = self.open_cards_deck.draw_card(index)

                    player.train_cards.append(card)
                    self.open_cards_deck.add_card(self.train_cards_deck.draw_card())
                    drew_cards += 1

                    if card == TrainCard.LOCOMOTIVE:
                        break

                case _:
                    print("Invalid choice. Please try again.")

    def draw_destination_tickets(self, player: Player):

        temp_cards = []
        for _ in range(3):
            card = self.destination_tickets_deck.draw_card()
            if card is None:
                print("No more destination tickets available.")
                continue
            else:
                temp_cards.append(card)

        print("Drawn destination tickets:")
        for ticket in temp_cards:
            print(f" - {ticket}")

        choice = input("Do you want to keep all of the drawn tickets? (y/n): ")

        if choice.lower() == "y":
            player.destination_tickets.extend(temp_cards[:])
        else:
            for i, ticket in enumerate(temp_cards[:]):
                print(f"{i}. {ticket}")

                choice = input(f"Do you want to keep this ticket? (y/n): ")
                if choice.lower() == "y":
                    player.destination_tickets.append(ticket)
                else:
                    self.destination_tickets_deck.add_card_to_bottom(ticket)

    def play_turn(self):
        """
        Plays a turn for the current player.
        """
        player = self.players[self.current_player_index]
        print(f"current player index: {self.current_player_index}")
        print(f"\n{player.name}'s turn:")
        print(f"Player: {player}")

        choice = input(
            "Choose an action:\n 1. Draw train cards\n 2. Draw destination tickets\n 3. Claim a route\n"
        )

        match choice:
            case "1":

                self.draw_card(player)

            case "2":

                self.draw_destination_tickets(player)
                pass

        self.turn_number += 1
        self.current_player_index = (self.current_player_index + 1) % len(self.players)

    def if_start_last_round(self):
        """
        Check if the last round should start. Meaning player has 2 or less trains.
        """

        for player in self.players:
            if player.trains <= 2:
                return True

        return False


def main():

    train_cards_deck = TrainCardsDeck()
    destination_tickets_deck = DestinationTicketsDeck()

    open_cards_deck = OpenCardsDeck(train_cards_deck)

    players = []
    map = Map()

    for i in range(2):
        player = Player(
            name=f"Player {i + 1}",
            train_cards=[train_cards_deck.draw_card() for i in range(5)],
        )
        players.append(player)

    game = Game(
        players=players,
        map=map,
        train_cards_deck=train_cards_deck,
        open_cards_deck=open_cards_deck,
        destination_tickets_deck=destination_tickets_deck,
        current_player_index=0,
    )

    
    # for player in players:
    #     print(player)
    # print(destination_tickets_deck)
    # print(map)

    print("\nGame created successfully!")
    print(game)

    game.play_game()


if __name__ == "__main__":
    main()
