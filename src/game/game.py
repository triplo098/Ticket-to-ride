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
from gui import GUI


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

            choice = int(
                input("Choose an action:\n 1. From the deck\n 2. From the open cards\n")
            )
            match choice:

                case 1:
                    player.train_cards.append(self.train_cards_deck.draw_card())
                    drew_cards += 1
                case 2:
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
        
        '''
        Drawing destination tickets from deck. At least one ticket needs to be taken.
        '''
        temp_cards = []
        for _ in range(3):
            card = self.destination_tickets_deck.draw_card()
            if card is None:
                print("No more destination tickets available.")
                return None
            else:
                temp_cards.append(card)

        print("Drawn destination tickets:")
        for ticket in temp_cards:
            print(f" - {ticket}")

        choice = input("Do you want to keep all of the drawn tickets? (y/n): ")

        if choice.lower() == "y":
            player.destination_tickets.extend(temp_cards[:])
        else:

            taken_cards_counter = 0
            tickets_for_taking = []

            while taken_cards_counter <= 0:  
                
                print("Player need to take at lead one of cards")

                taken_cards_counter = 0
                tickets_for_taking = []

                for i, ticket in enumerate(temp_cards[:]):
                    print(f"{i}. {ticket}")

                    choice = input(f"Do you want to keep this ticket? (y/n): ")
                    if choice.lower() == "y":

                        tickets_for_taking.append(ticket)
                        taken_cards_counter += 1

            player.destination_tickets.extend(tickets_for_taking)

            tickets_for_returing = list(set(tickets_for_taking) - set(temp_cards))

            self.destination_tickets_deck.add_card_to_bottom(
                card for card in tickets_for_returing
            )

            return tickets_for_taking
        

    def choose_conn(self, player: Player):
        """
        Allows the player to choose a city conncection.
        """

        print("Available cities:")
        for i, city in enumerate(self.map.cities):
            print(f"{i}. {city.name}")

        city1_index = int(input("Choose the first city (index): "))
        city2_index = int(input("Choose the second city (index): "))

        # Error handling for invalid indices
        if city1_index < 0 or city1_index >= len(self.map.cities):
            print("Invalid index for the first city.")
            return None

        if city2_index < 0 or city2_index >= len(self.map.cities):
            print("Invalid index for the second city.")
            return None

        if city1_index == city2_index:
            print("You cannot choose the same city twice.")
            return None

        city1 = self.map.cities[city1_index]
        city2 = self.map.cities[city2_index]

        cities_connections = city1.get_all_connections_between_cities(city2)

        city_conn = None

        if len(cities_connections) == 0:
            print("No connection exists between the chosen cities.")

        elif len(cities_connections) == 1:

            city_conn = cities_connections[0]

            print(f"Chosen connection: {city_conn}")
        else:
            print("Available connections")

            for i, conn in enumerate(cities_connections):
                print(f"{i}. {conn}")

            choice = -1

            while choice >= len(cities_connections) or choice < 0:

                choice = int(input("Choose index: "))

            city_conn = cities_connections[choice]

        return city_conn

    def claim_conn(self, player: Player, city_conn: CityConnection):
        """
        Claims a city connection for the player.
        Returns True if successful, False otherwise - route taken or player has to few cards.
        """

        if city_conn.owner is not None:
            print("This route is already claimed by another player.")
            return False

        conn_cost = Counter(city_conn.cost)
        player_trains = Counter(player.train_cards)

        # Using Locomotive cards
        if conn_cost[TrainCard.LOCOMOTIVE] > player_trains[TrainCard.LOCOMOTIVE]:
            print(f"No enough Locomotive cards to claim this connection.")
            return False

        # Checking all other cards
        for card, count in conn_cost.items():

            if (
                player_trains[card] >= count
            ):  # Paying with base card (non-locomotive for all others colors)
                player_trains[card] -= count
                continue

            elif (
                player_trains[TrainCard.LOCOMOTIVE] + player_trains[card] >= count
                and card != TrainCard.LOCOMOTIVE
            ):  # Paying with locomotive cards

                non_locomotive_count = player_trains[card]
                locomotive_count = count - non_locomotive_count

                player_trains[card] -= non_locomotive_count
                player_trains[TrainCard.LOCOMOTIVE] -= locomotive_count

                continue
            else:
                print(
                    f"You don't have enough {card.name} cards to claim this connection."
                )
                return False

        player_trains_diff = Counter(player.train_cards)

        #  Getting the count of how many trains should be use for claming connection
        for card, count in player_trains_diff.items():
            player_trains_diff[card] -= player_trains[card]

        for card, count in player_trains_diff.items():

            for _ in range(count):
                if card in player.train_cards:
                    player.train_cards.remove(card)  # Spending cards
                else:
                    print(f"Card {card.name} not found in player's train cards.")

        # Turn summary
        player.trains -= len(city_conn.cost)
        player.score += city_conn.get_score_for_claiming()
        city_conn.owner = player

        print(f"{player.name} claimed the {city_conn}!")
        return True

    def play_turn(self):
        """
        Plays a turn for the current player.
        """
        player = self.players[self.current_player_index]
        print(f"current player index: {self.current_player_index}")
        print(f"\n{player.name}'s turn:")
        print(f"Player: {player}")

        move_made = False

        while not move_made:

            choice = int(
                input(
                    "Choose an action:\n 1. Draw train cards\n 2. Draw destination tickets\n 3. Claim a city connection\n"
                )
            )

            match choice:
                case 1:

                    self.draw_card(player)
                    move_made = True
                case 2:

                    if self.draw_destination_tickets(player) != None:
                        move_made = True

                case 3:

                    conn = self.choose_conn(player)

                    if conn != None and self.claim_conn(player, conn):
                        move_made = True

                case _:
                    print("Invalid choice. Please try again.")

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

    players[0].train_cards = []

    players[0].train_cards.extend([TrainCard.BLACK] * 2)
    players[0].train_cards.extend([TrainCard.LOCOMOTIVE] * 2)

    game = Game(
        players=players,
        map=map,
        train_cards_deck=train_cards_deck,
        open_cards_deck=open_cards_deck,
        destination_tickets_deck=destination_tickets_deck,
        current_player_index=0,
    )

    print("\nGame created successfully!")
    print(game)

    # Initialize GUI
    gui = GUI(game)

    gui.run()

    game.play_game()


if __name__ == "__main__":
    main()
