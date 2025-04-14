from collections import Counter
from map import Map, City, CityConnection, get_city_by_name
from cards import DestinationTicketCard, TrainCardsDeck, DestinationTicketsDeck
from player import Player

class Game:
    """
    Handles game logic.
    """
    def __init__(self, players: list[Player], map: Map, train_cards_deck: TrainCardsDeck, destination_tickets_deck: list[DestinationTicketCard], current_player_index: int):
        self.players = players
        self.map = map
        self.train_cards_deck = train_cards_deck
        self.destination_tickets_deck = destination_tickets_deck
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


def main():

    map = Map(cities=[City("Warszawa"), City("Wroclaw"), City("Krakow")])
    train_cards_deck = TrainCardsDeck()
    destination_tickets_deck = DestinationTicketsDeck()
    
    players = []
    

    map.add_example_connections()

    print(map)
    print(train_cards_deck)

    for i in range(2):
        player = Player(name=f"Player {i + 1}", train_cards=[train_cards_deck.draw_card() for i in range(5)])
        players.append(player)

    for player in players:
        print(player)
    

    destination_tickets_deck.add_card(DestinationTicketCard("Warszawa", "Wroclaw", 5))
    destination_tickets_deck.add_card(DestinationTicketCard("Wroclaw", "Krakow", 10))
    
    game = Game(
        players=players,
        map=map,
        train_cards_deck=train_cards_deck,
        destination_tickets_deck=destination_tickets_deck,
        current_player_index=0
    )

    print("\nGame created successfully!")
    print(game)

if __name__ == "__main__":
    main()
