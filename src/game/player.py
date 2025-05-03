from cards import TrainCard
from cards import DestinationTicketCard
from map import CityConnection



class Player:
    def __init__(self, name, trains=45, train_cards: list[TrainCard]=[], destination_tickets: list[DestinationTicketCard]=[]):
        self.name = name
        self.trains = trains
        self.train_cards = train_cards
        self.destination_tickets = []
        self.accomplished_destination_tickets = []
        self.cities_connections = []
        self.score = 0

    def get_city(self, city_name):
        """
        Returns the city object with the given name.
        """

        for conn in self.cities_connections:
            for city in conn.cities:
                if city.name == city_name:
                    return city
        return None
    


    def get_longest_route(self):
        """
        Returns the longest route for the player.
        The longest route is defined as the route with the most connections.
        """
        



        player_cities = set(conn for conn in self.cities_connections)

        def dfs(city, visited, length):
            nonlocal max_length

            max_length = max(max_length, length)

            
            for conn in city.get_all_connections_between_cities():
                
                neighbour_city = conn.cities[1] if conn.cities[0] == city else conn.cities[0]


                if neighbour_city not in visited:
                    visited.add(neighbour_city)
                    dfs(neighbour_city, visited, length + len(conn.cost))
                    visited.remove(neighbour_city)

        max_length = 0

        for city in player_cities:
            visited = (city)
            dfs(city, visited, 0)
        
        return max_length



    def __str__(self):
        train_cards_str = ", ".join(card.name for card in self.train_cards)
        tickets_str = "\n  ".join(str(ticket) for ticket in self.destination_tickets)

        return (f"Player: {self.name}\n"
                f"  Trains remaining: {self.trains}\n"
                f"  Train cards: [{train_cards_str}]\n"
                f"  Destination tickets:\n  {tickets_str if tickets_str else 'None'}\n"
                f"  Accomplished destination tickets:\n  {', '.join(str(ticket) for ticket in self.accomplished_destination_tickets) if self.accomplished_destination_tickets else 'None'}\n"
                f"  Connections:\n  {', '.join(str(conn) for conn in self.cities_connections) if self.cities_connections else 'None'}\n"
                f"  Score: {self.score}")
