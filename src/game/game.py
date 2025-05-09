from collections import Counter

import pygame

from map import Map, City, CityConnection, get_city_by_name
from cards import (
    DestinationTicketCard,
    TrainCardsDeck,
    DestinationTicketsDeck,
    TrainCard,
    OpenCardsDeck,
)
from player import Player
from gui import GUI
import threading

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

    def play_game(self, gui: GUI):
        """
        Play the game loop.
        """
        while not self.game_over:
            self.play_turn(gui)
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

    def play_turn(self, gui: GUI):
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

            case "3":
            # Gather all unique connections into a flat list
                all_conns = []
                seen = set()
                for city in self.map.cities:
                    for conn in city.connections:
                        if id(conn) not in seen:
                            all_conns.append(conn)
                            seen.add(id(conn))

                    # Now print just the index and city names for each connection
                print("Available routes:")
                for idx, conn in enumerate(all_conns):
                    city1, city2 = conn.cities
                    status = (
                        f"CLAIMED BY P{conn.claimed_by + 1}"
                        if conn.claimed_by is not None
                        else "unclaimed"
                    )
                    print(f"  {idx}. {city1.name} ↔ {city2.name} ({status})")

                sel = int(input("Enter route index to claim: "))
                if 0 <= sel < len(all_conns):
                    #self.claim_route(connection, self.current_player_index)
                    self.claim_route(all_conns[sel], self.current_player_index)
                else:
                    print("Invalid route index.")

        self.turn_number += 1
        self.current_player_index = (self.current_player_index + 1) % len(self.players)

    def claim_route(self, conn, player_index):
        player = self.players[player_index]

        # … previous checks …

        # If the route is gray, ask what color to spend
        if conn.cost and conn.cost[0] == TrainCard.GREY:
            length = len(conn.cost)
            print(f"This is a gray route of length {length}.")
            print("Choose which color to spend:")
            for i, color in enumerate((TrainCard.PINK, TrainCard.WHITE, TrainCard.BLACK,
                                       TrainCard.BLUE, TrainCard.YELLOW, TrainCard.ORANGE,
                                       TrainCard.GREEN, TrainCard.RED)):
                print(f"  {i}. {color.name}")
            choice = int(input("Color index: "))
            chosen_color = (TrainCard.PINK, TrainCard.WHITE, TrainCard.BLACK,
                            TrainCard.BLUE, TrainCard.YELLOW, TrainCard.ORANGE,
                            TrainCard.GREEN, TrainCard.RED)[choice]

            # build an actual cost list of that color
            real_cost = [chosen_color] * length
        else:
            # non‐gray: use the predefined cost
            real_cost = conn.cost

        # Now check affordability against real_cost, spend cards, etc.
        if not player.can_afford(real_cost):
            print("You do not have enough cards of that color (or locomotives).")
            return

        player.spend_cards(real_cost)
        player.trains -= len(real_cost)
        conn.claimed_by = player_index
        print(f"{player.name} claimed {conn.cities[0].name} ↔ {conn.cities[1].name}!")

    def if_start_last_round(self):
        """
        Check if the last round should start. Meaning player has 2 or less trains.
        """

        for player in self.players:
            if player.trains <= 2:
                return True

        return False

def console_loop(game, gui):
    # This runs in a worker thread, handling your text I/O
    game.play_game(gui)
    # When done, signal the GUI to quit
    pygame.event.post(pygame.event.Event(pygame.QUIT))

def main():

    train_cards_deck = TrainCardsDeck()
    destination_tickets_deck = DestinationTicketsDeck()

    open_cards_deck = OpenCardsDeck(train_cards_deck)

    players = []
    map = Map()

    for i in range(2):
        player = Player(
            name=f"Player {i + 1}",
            train_cards=[train_cards_deck.draw_card() for i in range(30)],
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

    # --- initialize GUI ---
    gui = GUI(game)

    # 1) Start the console loop in a background thread
    console_thread = threading.Thread(target=console_loop, args=(game, gui), daemon=False)
    console_thread.start()

    # 2) Run the Pygame GUI in the **main** thread
    gui.run()

    # 3) Wait for console thread to finish cleanly
    console_thread.join()


if __name__ == "__main__":
    main()
