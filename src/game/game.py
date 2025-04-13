from array import array
from collections import Counter
from enum import Enum


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


class City:

    def __init__(self, name: str):

        self.name = name
        self.connections = []

    def __str__(self):

        connections_str = ""
        
        for conn in self.connections:

            connections_str += f"{conn.city_dest.name} (cost: "
            
            for j in range(len(conn.cost)):
                
                connections_str += f"{conn.cost[j].name} "
                
            connections_str += "), "

        return f"{self.name} -> [{connections_str}]\n"


class CityConnection:

    def __init__(self, cost: array[TrainCard], city_dest: City):
        self.cost = cost
        self.city_dest = city_dest

    def __str__(self):
        return f"CityConnection: {self.city_dest.name} (cost: {len(self.cost)} {self.cost[0].name})"


class Map:

    def __init__(self, cities: array[City]):
        self.cities = cities

    def add_connection(self, city_src, city_connection: CityConnection):
        """
        Adds a connection between two cities.
        """

        city_src.connections.append(city_connection)
        city_connection.city_dest.connections.append(
            CityConnection(cost=city_connection.cost, city_dest=city_src)
        )  # Add reverse connection

    def __str__(self):
        return "Map: [" + ", ".join(str(city) for city in self.cities) + "]"


def get_city_by_name(cities, name):
    for city in cities:
        if city.name == name:
            return city
    raise ValueError(f"City with name {name} not found")


class DestinationTicket:
    """
    Represents a destination ticket.
    """
    def __init__(self, city_start: City, city_end: City, points: int):
        self.city_start = city_start
        self.city_end = city_end
        self.points = points

    def __str__(self):
        return f"DestinationTicket: {self.city_start.name} -> {self.city_end.name} ({self.points})"

class Route:
    """
    Represents a route. We can use it simnultaneously with CityConnection class or refactor it.
    """
    def __init__(self, city_A: City, city_B: City, color: TrainCard, color_length: int, locomotives: int = 0):
        self.city_A = city_A
        self.city_B = city_B
        self.color = color
        self.color_length = color_length
        self.locomotives = locomotives
        self.owner: Player | None = None

    def __str__(self):
        return f"Route: {self.city_A.name} -> {self.city_B.name} ({self.color.name} x {self.color_length - self.locomotives}, LOCOMOTIVE x {self.locomotives})"

class Player:
    def __init__(self, name, train_cards: list[TrainCard]=[], destination_tickets: list[DestinationTicket]=[]):
        self.name = name
        self.trains_remaining = 45
        self.train_cards = train_cards
        self.destination_tickets = destination_tickets
        self.claimed_routes: list[Route] = []
        self.score = 0

    def __str__(self):
        train_cards_str = ", ".join(card.name for card in self.train_cards)
        tickets_str = "\n  ".join(str(ticket) for ticket in self.destination_tickets)
        routes_str = "\n  ".join(str(route) for route in self.claimed_routes)

        return (f"Player: {self.name}\n"
                f"  Trains remaining: {self.trains_remaining}\n"
                f"  Train cards: [{train_cards_str}]\n"
                f"  Destination tickets:\n  {tickets_str if tickets_str else 'None'}\n"
                f"  Claimed routes:\n  {routes_str if routes_str else 'None'}\n"
                f"  Score: {self.score}")


class Game:
    """
    Handles game logic.
    """
    def __init__(self, players: list[Player], map: Map, train_card_deck: list[TrainCard], destination_tickets: list[DestinationTicket], routes: list[Route], current_player_index: int):
        self.players = players
        self.map = map
        self.train_card_deck = train_card_deck
        self.destination_tickets = destination_tickets
        self.routes = routes
        self.current_player_index = current_player_index
        self.turn_number = 0
        self.game_over = False

    def __str__(self):
        players_str = "\n".join(str(player) for player in self.players)
        routes_str = "\n".join(str(route) for route in self.routes)
        tickets_str = "\n".join(
            str(ticket) for ticket in self.destination_tickets)
        card_count = Counter(self.train_card_deck)
        train_cards_str = ", ".join([f"{card.name} x{count}" for card, count in card_count.items()])

        return (
            f"Game Status:\n\n"
            f"Players:\n{players_str}\n\n"
            f"Map:\n{self.map}\n\n"
            f"Routes:\n{routes_str}\n\n"
            f"Train Cards Deck:\n[{train_cards_str}]\n\n"
            f"Destination Tickets:\n{tickets_str}\n\n"
            f"Turn Number: {self.turn_number}\n"
            f"Current Player: {self.players[self.current_player_index].name}\n"
            f"Game Over: {self.game_over}"
        )


def main():

    map = Map(cities=[City("Warszawa"), City("Wroclaw"), City("Krakow")])

    map.add_connection(
        get_city_by_name(map.cities, "Warszawa"),
        CityConnection(
            cost=[TrainCard.RED for _ in range(4)], city_dest=get_city_by_name(map.cities, "Wroclaw")
        ),
    )

    map.add_connection(
        get_city_by_name(map.cities, "Wroclaw"),
        CityConnection(
            cost=[TrainCard.BLUE for _ in range(3)],
            city_dest=get_city_by_name(map.cities, "Krakow"),
        ),
    )

    map.add_connection(
        get_city_by_name(map.cities, "Krakow"),
        CityConnection(
            cost=[TrainCard.YELLOW] + [TrainCard.LOCOMOTIVE for _ in range(2)],
            city_dest=get_city_by_name(map.cities, "Warszawa"),
        ),
    )

    map.add_connection(
        get_city_by_name(map.cities, "Krakow"),
        CityConnection(
            cost=[TrainCard.GREY for _ in range(6)],
            city_dest=get_city_by_name(map.cities, "Wroclaw"),
        ),
    )

    print(map)

    routes = []
    for city in map.cities:
        for conn in city.connections:
            color = conn.cost[0] if conn.cost and conn.cost[0] != TrainCard.LOCOMOTIVE else TrainCard.GREY
            locomotives = sum(1 for card in conn.cost if card == TrainCard.LOCOMOTIVE)
            length = len(conn.cost)
            route = Route(
                city_A=city,
                city_B=conn.city_dest,
                color=color,
                color_length=length,
                locomotives=locomotives
            )
            routes.append(route)

    # print("\nRoutes:")
    # for route in routes:
    #     print(route)

    player1 = Player(
        name="Player1",
        train_cards=[TrainCard.RED, TrainCard.BLUE, TrainCard.LOCOMOTIVE],
        destination_tickets=[]
    )

    player2 = Player(
        name="Player2",
        train_cards=[TrainCard.GREEN, TrainCard.YELLOW, TrainCard.ORANGE],
        destination_tickets=[]
    )

    players = [player1, player2]

    train_card_deck = [TrainCard.RED, TrainCard.BLUE, TrainCard.GREEN, TrainCard.YELLOW] * 10

    destination_tickets = [
        DestinationTicket(
            city_start=get_city_by_name(map.cities, "Warszawa"),
            city_end=get_city_by_name(map.cities, "Krakow"),
            points=10
        ),
        DestinationTicket(
            city_start=get_city_by_name(map.cities, "Wroclaw"),
            city_end=get_city_by_name(map.cities, "Warszawa"),
            points=7
        )
    ]

    game = Game(
        players=players,
        map=map,
        train_card_deck=train_card_deck,
        destination_tickets=destination_tickets,
        routes=routes,
        current_player_index=0
    )

    print("\nGame created successfully!")
    print(game)


if __name__ == "__main__":
    main()
