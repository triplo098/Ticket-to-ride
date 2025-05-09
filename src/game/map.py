from cards import TrainCard
import yaml
import os


class City:

    def __init__(self, name: str, point: tuple[int, int] = (0, 0)):

        self.name = name
        self.connections = []
        self.point = point  # Coordinates of the city on the map

    def __str__(self):

        connections_str = ""

        for connection in self.connections:
            connections_str += f"  {connection}\n"

        return f"City: {self.name}\t \nCoordinates: {self.point}  \nConnections:\n{connections_str}\n"


class CityConnection:

    def __init__(self, cost: list[TrainCard], connected_cities: {City}):

        self.cost = cost  # List of train cards needed to create a connection
        cities_list = list(connected_cities)
        if len(cities_list) != 2:
            raise ValueError("CityConnection should connect exactly two cities")
        self.cities = (cities_list[0], cities_list[1])
        self.claimed_by: int | None = None

        # register this connection on each city
        self.cities[0].connections.append(self)
        self.cities[1].connections.append(self)

        # initialize ownership flag
        self.claimed_by: int | None = None



    def __str__(self):

        cities = list(self.cities)

        return f"CityConnection: {cities[0].name} <-> {cities[1].name}, Cost: [{', '.join(str(card) for card in self.cost)}]"


class Map:
    def __init__(
        self,
        cities: list[City] = [],
        config_file: str = os.path.join(
            os.path.dirname(__file__), "../config//set_europe_close_up/europe_map_close_up.yaml"
        ),
    ):

        self.cities = cities
        self.connections: list[CityConnection] = []

        if not cities:
            self.init_cities_from_config(config_file)

        seen = set()
        for city in self.cities:
            for conn in city.connections:
                if id(conn) not in seen:
                    self.connections.append(conn)
                    seen.add(id(conn))

    def __str__(self):
        return "Map: [\n" + " ".join(str(city) for city in self.cities) + "]"

    def init_cities_from_config(self, cities_yaml_file: str):
        """
        Initializes cities and their connections from a YAML file.
        The YAML file should contain a 'connections' list with city pairs and costs.
        """

        with open(cities_yaml_file, "r") as file:
            data = yaml.safe_load(file)

        for city in data["cities"]:
            
            city = City(city["name"], (city["x"], city["y"]))
            self.cities.append(city)

        for connection_data in data["connections"]:
            cost = []
            for card_color in connection_data["cost"]:
                try:
                    cost.append(TrainCard[card_color.upper()])
                except KeyError:
                    print(f"Warning: Unknown card color '{card_color}', skipping")

            # Get the city objects for this connection
            city1_name, city2_name = connection_data["cities"]
            city1 = get_city_by_name(self.cities, city1_name)
            city2 = get_city_by_name(self.cities, city2_name)

            if city1 and city2:
                # Create the connection between these two cities
                connected_cities = {city1, city2}
                CityConnection(cost, connected_cities)
            else:
                print(
                    f"Warning: Could not find cities: {', '.join(city1_name, city2_name)}"
                )


def get_city_by_name(cities, name):
    for city in cities:
        if city.name == name:
            return city
    raise ValueError(f"City with name {name} not found")
