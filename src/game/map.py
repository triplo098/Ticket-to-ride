from cards import TrainCard
import yaml
import os


class City:

    def __init__(self, name: str, point: tuple[int, int] = (0, 0)):

        self.name = name
        self.connections = []  # List of connections to other cities
        self.point = point  # Coordinates of the city on the map

    def get_connected_cities(self):
        """
        Returns a list of cities connected to this city.
        """
        connected_cities = []

        for connection in self.connections:
            for city in connection.cities:
                if city != self:
                    connected_cities.append(city)

        return connected_cities

    def get_all_connections_between_cities(self, city2: "City"):
        """
        Returns the list of connections between this city and another city.
        """

        connections = []

        for connection in self.connections:
            if city2 in connection.cities:
                connections.append(connection)    

        return connections
    
    
    def __str__(self):

        connections_str = ""

        for connection in self.connections:
            connections_str += f"  {connection}\n"

        return f"City: {self.name}\t \nCoordinates: {self.point}  \nConnections:\n{connections_str}\n"


class CityConnection:

    def __init__(self, cost: list[TrainCard], connected_cities: {City}):

        self.cost = cost  # List of train cards needed to create a connection
        self.cities = (
            connected_cities  # Set of connected cities; number of cities should be 2
        )
        self.owner = None  # Player who owns this connection

        if len(connected_cities) != 2:
            raise ValueError("CityConnection should connect exactly two cities")

        connected_cities = list(connected_cities)
        connected_cities[0].connections.append(self)
        connected_cities[1].connections.append(self)
    def get_score_for_claiming(self):
        """
        Returns the score for claiming this connection.
        The score is based on the length of the connection.
        """

        conn_len = len(self.cost)
        out_score = None

        match conn_len:
            case 1:
                out_score = 1
            case 2:
                out_score = 2
            case 3:
                out_score = 4
            case 4:
                out_score = 7
            case 5:
                out_score = 10
            case 6:
                out_score = 15
            case _:
                out_score = 0
        
        return out_score
        
    def __str__(self):

        cities = list(self.cities)

        return f"CityConnection: {cities[0].name} <-> {cities[1].name}, Cost: [{', '.join(str(card) for card in self.cost)}]"


class Map:
    def __init__(
        self,
        cities: list[City] = [],
        config_file: str = os.path.join(
            os.path.dirname(__file__), "../config/europe_map.yaml"
        ),
    ):

        self.cities = cities

        if not cities:
            self.init_cities_from_config(config_file)

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
