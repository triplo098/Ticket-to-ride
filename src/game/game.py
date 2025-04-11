from array import array
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


if __name__ == "__main__":
    main()
