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
from threading import Thread
import time


class Game:
    """
    Handles game logic.
    """

    def __init__(
        self,
        map: Map,
        train_cards_deck: TrainCardsDeck,
        destination_tickets_deck: DestinationTicketsDeck,
        open_cards_deck: OpenCardsDeck,
        current_player_index: int,
        players: list[Player] = [],
    ):
        self.players = players
        self.map = map
        self.train_cards_deck = train_cards_deck
        self.destination_tickets_deck = destination_tickets_deck
        self.open_cards_deck = open_cards_deck
        self.current_player_index = current_player_index
        self.turn_number = 0
        self.game_over = False
        self.gui = None
        self.destination_tickets_to_choose = []

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

    def setup_game(self):
        """
        Sets up the game by shuffling and dealing cards.
        """
        # Shuffle and deal train cards
        self.train_cards_deck.shuffle()

        # Drawing initial train cards and destination tickets for each player
        for player in self.players:
            print(f"Drawing initial cards for {player.name}...")
            player.train_cards = [self.train_cards_deck.draw_card() for _ in range(4)]
            self.draw_destination_tickets(player, 3, 2)
            self.turn_number += 1
            self.current_player_index = (self.current_player_index + 1) % len(self.players)

            

    def play_game(self):
        """
        Play the game loop.
        """
        self.setup_game()

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

    def draw_destination_tickets(
        self, player: Player, num_tickets: int = 3, need_to_take: int = 1, terminal_mode: bool = False
    ):
        """
        Drawing destination tickets from deck.
        At least 'need_to_take' ticket needs to be taken.
        """
        temp_cards = []
        for _ in range(num_tickets):
            card = self.destination_tickets_deck.draw_card()
            if card is None:
                print("Not more destination tickets available.")
                return None
            else:
                temp_cards.append(card)

        print("Drawn destination tickets:")
        for ticket in temp_cards:
            print(f" - {ticket}")


        self.destination_tickets_to_choose = temp_cards
        self.gui.if_draw_destination_tickets_to_choose = True

        if terminal_mode:
            choice = input("Do you want to keep all of the drawn tickets? (y/n): ")
        else:
            choice = "n"

        if choice.lower() == "y":
            player.destination_tickets.extend(temp_cards[:])
        else:

            taken_cards_counter = 0
            tickets_for_taking = []

            while taken_cards_counter < need_to_take:

                print(f"Player need to take at least {need_to_take} cards")

                taken_cards_counter = 0
                tickets_for_taking = []

                for i, ticket in enumerate(temp_cards[:]):

                    if terminal_mode:   
                        print(f"{i}. {ticket}")
                        choice = input(f"Do you want to keep this ticket? (y/n): ")
                        if choice.lower() == "y":
                            tickets_for_taking.append(ticket)
                            taken_cards_counter += 1
                
                    destination_ticket_index, action_name = self.gui.get_player_action()
                    
                    if type(destination_ticket_index) == int:
                        ticket = self.destination_tickets_to_choose[destination_ticket_index]
                        if ticket in tickets_for_taking:
                            break

                        print(f"Chosen ticket: {ticket}")
                        tickets_for_taking.append(ticket)

                        taken_cards_counter += 1


            player.destination_tickets.extend(tickets_for_taking)

            tickets_for_returing = list(set(temp_cards) - set(tickets_for_taking))

            for card in tickets_for_returing:
                self.destination_tickets_deck.add_card_to_bottom(card)

            # Returning the rest of the tickets to the deck and setting gui flag to False
            self.gui.if_draw_destination_tickets_to_choose = False
            return tickets_for_taking
        

    def choose_conn(self, player: Player):
        """
        Allows the player to choose a city conncection.
        Returns the chosen connection between two cities.
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

        cities_connections = list(dict.fromkeys(city1.get_all_connections_between_cities(city2)))

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
        Returns True if successful, False otherwise - route is taken or player has to few cards.
        """

        if city_conn.claimed_by is player:
            print("You have already claimed this connection.")
            return False
        
        elif city_conn.claimed_by is not None:
            print("This connection is already claimed by another player.")
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
        city_conn.claimed_by = player
        player.cities_connections.append(city_conn)

        print(f"{player.name} claimed the {city_conn}!")
        return True

    def check_for_accomplished_tickets(self, player: Player):
        """
        Check if the player accomplished any destination tickets.
        Adds points to the player's score and moves the tickets to the accomplished list.
        """
        for ticket in player.destination_tickets:
            if (
                ticket.is_accomplished(player)
                and ticket not in player.accomplished_destination_tickets
            ):

                player.accomplished_destination_tickets.append(ticket)
                player.score += ticket.points
                print(f"{player.name} accomplished a destination ticket: {ticket}")

        # Remove accomplished tickets from the player's list
        player.destination_tickets = [
            ticket
            for ticket in player.destination_tickets
            if ticket not in player.accomplished_destination_tickets
        ]

    def play_turn(self, terminal_mode: bool = False):
        """
        Plays a turn for the current player.
        """
        player = self.players[self.current_player_index]
        print(f"current player index: {self.current_player_index}")
        print(f"\n{player.name}'s turn:")
        print(f"Player: {player}")

        move_made = False
        draw_cards = list()

        while not move_made:
            

            action = self.gui.get_player_action()
            time.sleep(1)
            print(action)

            if terminal_mode:
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

                        self.check_for_accomplished_tickets(player)
                    
                    case _:
                        print("Invalid choice. Please try again.")
                
            else:

                if action == "train_cards_deck": 
                    # drawing from the deck
                     
                    card = self.train_cards_deck.draw_card()
                    player.train_cards.append(card)

                    draw_cards.append(card)
                    
                    if len(draw_cards) == 2:
                        
                        move_made = True

                elif action == "destination_tickets_deck":
                    self.draw_destination_tickets(player, 3, 1)
                    move_made = True
                elif action[1] == "create_connection":
                    # creating connection from set of selected cities
                    cities = action[0]
                    city1 = cities.pop()
                    city2 = cities.pop()

                    cities_connections = list(dict.fromkeys(city1.get_all_connections_between_cities(city2)))

                    if len(cities_connections) == 0:
                        print("No connection exists between the chosen cities.")
                        continue
                    else:    
                        conn = cities_connections[0]
                        print(f"Chosen connection: {conn}")

                        if self.claim_conn(player, conn):
                            move_made = True
                            self.check_for_accomplished_tickets(player)

                elif action[1] == "open_card_index":
                    # assuming action is the index of the open card

                    index = action[0]
                    if index < 0 or index >= len(self.open_cards_deck.cards):
                        print("Invalid index. Please try again.")
                        continue
                    if (
                        self.open_cards_deck.cards[index] == TrainCard.LOCOMOTIVE
                        and len(draw_cards) == 1
                    ):
                        print(
                            "You cannot draw a locomotive card from the open cards after drawing one."
                        )
                        continue

                    card = self.open_cards_deck.draw_card(index)
                    player.train_cards.append(card)
                    self.open_cards_deck.add_card(self.train_cards_deck.draw_card())

                    draw_cards.append(card)

                    if len(draw_cards) == 2 or card  == TrainCard.LOCOMOTIVE:
                        move_made = True
                    

        time.sleep(1)
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
    open_cards_deck = OpenCardsDeck(train_cards_deck)

    game = Game(
        map=Map(),
        train_cards_deck=TrainCardsDeck(),
        open_cards_deck=open_cards_deck,
        destination_tickets_deck=DestinationTicketsDeck(),
        current_player_index=0,
        players=[Player(name=f"Player {i + 1}") for i in range(2)],
    )


    game.players[0].train_cards.extend(
        [TrainCard.BLUE, TrainCard.BLACK] * 5
        + [TrainCard.LOCOMOTIVE] * 2
        + [TrainCard.GREEN] * 4
        + [TrainCard.PINK] * 4
    )

    print("\nGame created successfully!")
    print(game)

    # Initialize GUI
    def run_gui():
        gui = GUI(game)
        game.gui = gui
        gui.run()

    def run_game():
        game.play_game()

    # Start GUI in a separate thread
    gui_thread = Thread(target=run_gui)
    gui_thread.start()

    for player in game.players:
        print(player)

    # player = game.players[0]
    
    # player.train_cards.extend(
    #     [TrainCard.BLUE, TrainCard.BLACK] * 5
    #     + [TrainCard.LOCOMOTIVE] * 2
    #     + [TrainCard.GREEN] * 4
    #     + [TrainCard.PINK] * 4
    # )
    # Run the game logic in the main thread
    time.sleep(1)
    run_game()

if __name__ == "__main__":
    main()
