from cards import TrainCard


class City:

    def __init__(self, name: str):

        self.name = name
        self.connections = []

    def __str__(self):

        connections_str = ""

        for connection in self.connections:
            connections_str += f"  {connection}\n"

        return f"City: {self.name}\nConnections:\n{connections_str}"


class CityConnection:

    def __init__(self, cost: list[TrainCard], connected_cities: {City}):

        self.cost = cost  # List of train cards needed to create a connection
        self.cities = connected_cities  # Set of connected cities; number of cities should be 2

        if len(connected_cities) != 2:
            raise ValueError("CityConnection should connect exactly two cities")
        
        connected_cities = list(connected_cities)
        connected_cities[0].connections.append(self)
        connected_cities[1].connections.append(self)

    def __str__(self):

        cities = list(self.cities)
        return f"CityConnection: {cities[0].name} <-> {cities[1].name}, Cost: [{', '.join(str(card) for card in self.cost)}]"



class Map:

    def __init__(self, cities: list[City]):
        self.cities = cities

    def add_connection(self, city_connection: CityConnection):
        """
        Adds a connection between two cities. Setting connection info for both cities.
        """

    def __str__(self):
        return "Map: [" + ", ".join(str(city) for city in self.cities) + "]"

    def add_example_connections(self):
        """
        Adds example connections to the map.
        """

        self.add_connection(
            CityConnection(
                [TrainCard.PINK for _ in range(4)],
                {
                    get_city_by_name(self.cities, "Warszawa"),
                    get_city_by_name(self.cities, "Wroclaw"),
                },
            )
        )

        self.add_connection(
            CityConnection(
                [TrainCard.YELLOW for _ in range(3)],
                {
                    get_city_by_name(self.cities, "Wroclaw"),
                    get_city_by_name(self.cities, "Krakow"),
                },
            )
        )


        self.add_connection(
            CityConnection(
                [TrainCard.GREEN for _ in range(2)],
                {
                    get_city_by_name(self.cities, "Warszawa"),
                    get_city_by_name(self.cities, "Krakow"),
                },
            )
        )


def get_city_by_name(cities, name):
    for city in cities:
        if city.name == name:
            return city
    raise ValueError(f"City with name {name} not found")
