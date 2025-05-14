import pygame
import math
from collections import namedtuple
import yaml
from pathlib import Path
import os


class GUI:
    def __init__(
        self,
        game,
        cards_folder_path=os.path.join(os.path.dirname(__file__), "../cards_graphics"),
    ):
        self.game = game
        # Use the RESIZABLE flag to allow window resizing
        self.screen = pygame.display.set_mode((1050, 578), pygame.RESIZABLE)
        pygame.display.set_caption("Ticket to Ride")
        pygame.font.init()  # Initialize the font module
        self.clock = pygame.time.Clock()

        self.cards_folder_path = cards_folder_path
        self.city_radius = 7  # Radius for city circles


        self.card_height = 1200
        self.card_width = 1900



        # Initialize original dimensions of the map
        self.original_width = 1050  # Set this to the actual width of your map image
        self.original_height = 578  # Set this to the actual height of your map image

        # Color mapping for routes
        self.color_map = {
            "black": (0, 0, 0),
            "pink": (255, 105, 180),
            "green": (0, 128, 0),
            "blue": (0, 0, 255),
            "red": (255, 0, 0),
            "yellow": (255, 255, 0),
            "orange": (255, 165, 0),
            "white": (255, 255, 255),
            "gray": (128, 128, 128),
        }

        # Load map data from YAML file
        script_dir = Path(__file__).resolve().parent
        yaml_path = (
            script_dir / "../config/set_europe_close_up/europe_map_close_up.yaml"
        )
        self.load_map_data(str(yaml_path))

    def load_map_data(self, yaml_path):
        # Create simple data structures to hold city and connection info
        self.City = namedtuple("City", ["name", "point"])
        self.Connection = namedtuple("Connection", ["cities", "cost", "control_points"])

        try:
            with open(yaml_path, "r") as file:
                map_data = yaml.safe_load(file)

            # Create city objects
            self.cities = []
            for city_data in map_data.get("cities", []):
                city = self.City(
                    name=city_data["name"], point=(city_data["x"], city_data["y"])
                )
                self.cities.append(city)

            # Create connection objects
            self.connections = []
            for conn_data in map_data.get("connections", []):
                connection = self.Connection(
                    cities=conn_data["cities"],
                    cost=conn_data["cost"],
                    control_points=conn_data.get(
                        "control_points", None
                    ),  # Default to None
                )
                self.connections.append(connection)

        except Exception as e:
            print(f"Error loading map data: {e}")
            # Initialize with empty lists as fallback
            self.cities = []
            self.connections = []

    def draw(self):
        # Load and scale the background image
        script_dir = Path(__file__).resolve().parent
        map_path = script_dir / "../config/set_europe_close_up/Europe_Map.jpg"
        background_image = pygame.image.load(map_path)
        scaled_background = pygame.transform.scale(
            background_image, self.screen.get_size()
        )
        self.screen.blit(
            scaled_background, (0, 0)
        )  # Draw at the top-left corner of the screen (0, 0)

        # Draw routes first (so they appear behind cities)
        self.draw_routes()

        for city in self.game.map.cities:
            # Scale city coordinates
            scaled_point = self.scale_coordinates(*city.point)

            # Draw each city
            pygame.draw.circle(self.screen, (0, 0, 0), scaled_point, self.city_radius)

            # Draw city name
            font = pygame.font.Font(None, 24)
            text = font.render(city.name, True, (0, 0, 0))
            offset = (10, -10)  # Offset for the city name (x, y)
            text_rect = text.get_rect(
                center=(scaled_point[0] + offset[0], scaled_point[1] + offset[1])
            )
            self.screen.blit(text, text_rect)

        # self.draw_player_trains() TODO

        self.draw_player_cards()
        self.draw_open_cards()
        self.draw_trains_deck()
        self.draw_destination_cards()

    def draw_routes(self):
        # Group connections between the same cities to handle double routes
        grouped_connections = {}

        for connection in self.connections:
            # Create a key based on the city pair (sorted to ensure consistency)
            city_pair = tuple(sorted(connection.cities))
            if city_pair not in grouped_connections:
                grouped_connections[city_pair] = []
            grouped_connections[city_pair].append(connection)

        # Draw all connections, handling parallel routes where needed
        for city_pair, connections in grouped_connections.items():
            if len(connections) == 1:
                # Single route between cities
                connection = connections[0]
                if hasattr(connection, "control_points") and connection.control_points:
                    self.draw_curved_route(connection, 0)
                else:
                    self.draw_route(connection, 0)
            else:
                # Double route - draw them parallel to each other
                for i, connection in enumerate(connections):
                    # Alternate the shift direction based on index
                    shift = 0.2 * (-1 if i == 0 else 1)
                    if (
                        hasattr(connection, "control_points")
                        and connection.control_points
                    ):
                        self.draw_curved_route(connection, shift)
                    else:
                        self.draw_route(connection, shift)

    def draw_route(self, connection, parallel_shift=0):
        # Get city objects
        city1_name, city2_name = connection.cities
        city1 = next((city for city in self.cities if city.name == city1_name), None)
        city2 = next((city for city in self.cities if city.name == city2_name), None)

        if not city1 or not city2:
            return  # Skip if cities not found

        # Scale coordinates
        x1, y1 = self.scale_coordinates(*city1.point)
        x2, y2 = self.scale_coordinates(*city2.point)

        # Calculate direction and distance
        dx = x2 - x1
        dy = y2 - y1
        distance = math.sqrt(dx * dx + dy * dy)

        # Normalize direction
        if distance > 0:
            dx /= distance
            dy /= distance

        # Calculate perpendicular direction for width and parallel offset
        perpx = -dy
        perpy = dx

        # Apply parallel shift for double routes if needed
        if parallel_shift != 0:
            x1 += perpx * parallel_shift * 15
            y1 += perpy * parallel_shift * 15
            x2 += perpx * parallel_shift * 15
            y2 += perpy * parallel_shift * 15

            # Recalculate with new points
            dx = x2 - x1
            dy = y2 - y1
            distance = math.sqrt(dx * dx + dy * dy)
            if distance > 0:
                dx /= distance
                dy /= distance

        # Define rectangle dimensions
        cost_colors = connection.cost
        rect_width = 10  # Width of train route
        gap = 4  # Gap between rectangles (pixels)

        # Calculate usable distance (leaving space near cities and for gaps)
        city_offset = 15  # Space to leave near city circles
        num_segments = len(cost_colors)
        usable_distance = distance - 2 * city_offset - gap * (num_segments - 1)
        segment_length = usable_distance / num_segments

        # Calculate starting point
        start_x = x1 + dx * city_offset
        start_y = y1 + dy * city_offset

        # Draw each segment according to cost colors
        for i, color_name in enumerate(cost_colors):
            # Get RGB color
            color = self.color_map.get(color_name.lower(), (128, 128, 128))

            # Offset for this segment (includes gap)
            offset = i * (segment_length + gap) + segment_length / 2
            center_x = start_x + dx * offset
            center_y = start_y + dy * offset

            # Create polygon points for the rectangle
            points = [
                (
                    center_x - dx * segment_length / 2 + perpx * rect_width / 2,
                    center_y - dy * segment_length / 2 + perpy * rect_width / 2,
                ),
                (
                    center_x - dx * segment_length / 2 - perpx * rect_width / 2,
                    center_y - dy * segment_length / 2 - perpy * rect_width / 2,
                ),
                (
                    center_x + dx * segment_length / 2 - perpx * rect_width / 2,
                    center_y + dy * segment_length / 2 - perpy * rect_width / 2,
                ),
                (
                    center_x + dx * segment_length / 2 + perpx * rect_width / 2,
                    center_y + dy * segment_length / 2 + perpy * rect_width / 2,
                ),
            ]

            # Draw filled rectangle
            pygame.draw.polygon(self.screen, color, points)

            # Draw border around rectangle
            pygame.draw.polygon(self.screen, (0, 0, 0), points, 1)

    def draw_train_segment(self, start_point, end_point, color_name, rect_width):
        # Get RGB color
        color = self.color_map.get(color_name.lower(), (128, 128, 128))

        # Calculate direction vector
        dx = end_point[0] - start_point[0]
        dy = end_point[1] - start_point[1]
        length = math.sqrt(dx * dx + dy * dy)

        # Normalize
        if length > 0:
            dx /= length
            dy /= length

        # Calculate perpendicular vector for width
        perpx = -dy
        perpy = dx

        # Create polygon points for the segment
        points = [
            (
                start_point[0] + perpx * rect_width / 2,
                start_point[1] + perpy * rect_width / 2,
            ),
            (
                start_point[0] - perpx * rect_width / 2,
                start_point[1] - perpy * rect_width / 2,
            ),
            (
                end_point[0] - perpx * rect_width / 2,
                end_point[1] - perpy * rect_width / 2,
            ),
            (
                end_point[0] + perpx * rect_width / 2,
                end_point[1] + perpy * rect_width / 2,
            ),
        ]

        # Draw filled rectangle
        pygame.draw.polygon(self.screen, color, points)

        # Draw border around rectangle
        pygame.draw.polygon(self.screen, (0, 0, 0), points, 1)

    def draw_curved_route(self, connection, parallel_shift=0, control_points=None):
        # Get city objects and coordinates
        city1_name, city2_name = connection.cities
        city1 = next((city for city in self.cities if city.name == city1_name), None)
        city2 = next((city for city in self.cities if city.name == city2_name), None)

        if not city1 or not city2:
            return  # Skip if cities not found

        # Get points
        start_point = city1.point
        end_point = city2.point

        # Calculate direction vector between cities (for offset)
        dx = end_point[0] - start_point[0]
        dy = end_point[1] - start_point[1]
        distance = math.sqrt(dx * dx + dy * dy)
        if distance > 0:
            dx /= distance
            dy /= distance

        # Apply city offset to start and end points
        city_offset = 15  # Same as in draw_route
        city_radius = 5  # Match the circle radius used for cities
        offset_distance = city_offset + city_radius
        start_point = (
            start_point[0] + dx * offset_distance,
            start_point[1] + dy * offset_distance,
        )
        end_point = (
            end_point[0] - dx * offset_distance,
            end_point[1] - dy * offset_distance,
        )

        # Apply parallel shift for double routes if needed
        if parallel_shift != 0:
            # Calculate direction vectors
            dx = end_point[0] - start_point[0]
            dy = end_point[1] - start_point[1]
            distance = math.sqrt(dx * dx + dy * dy)

            if distance > 0:
                dx /= distance
                dy /= distance

            perpx = -dy
            perpy = dx

            # Apply shift
            start_point = (
                start_point[0] + perpx * parallel_shift * 15,
                start_point[1] + perpy * parallel_shift * 15,
            )
            end_point = (
                end_point[0] + perpx * parallel_shift * 15,
                end_point[1] + perpy * parallel_shift * 15,
            )

        # Use connection's control points if available
        if connection.control_points:
            control_points = connection.control_points

        # Generate default control points if none provided
        if not control_points:
            # Default gentle curve - can be adjusted
            dx = end_point[0] - start_point[0]
            dy = end_point[1] - start_point[1]
            dist = math.sqrt(dx * dx + dy * dy)

            # Create perpendicular offset for control points
            perpx = -dy / dist * dist * 0.3  # Adjust factor to control curve amount
            perpy = dx / dist * dist * 0.3

            # Two control points for cubic Bezier
            control_points = [
                (start_point[0] + dx / 3 + perpx, start_point[1] + dy / 3 + perpy),
                (
                    start_point[0] + dx * 2 / 3 + perpx,
                    start_point[1] + dy * 2 / 3 + perpy,
                ),
            ]

        # Generate points along the Bezier curve
        num_steps = 100  # More steps = smoother curve
        points = []
        for i in range(num_steps + 1):
            t = i / num_steps
            # Cubic Bezier formula
            x = (
                (1 - t) ** 3 * start_point[0]
                + 3 * (1 - t) ** 2 * t * control_points[0][0]
                + 3 * (1 - t) * t**2 * control_points[1][0]
                + t**3 * end_point[0]
            )
            y = (
                (1 - t) ** 3 * start_point[1]
                + 3 * (1 - t) ** 2 * t * control_points[0][1]
                + 3 * (1 - t) * t**2 * control_points[1][1]
                + t**3 * end_point[1]
            )
            points.append((x, y))

        # Calculate total curve length
        curve_length = 0
        for i in range(len(points) - 1):
            dx = points[i + 1][0] - points[i][0]
            dy = points[i + 1][1] - points[i][1]
            curve_length += math.sqrt(dx * dx + dy * dy)

        # Draw train segments along the curve
        cost_colors = connection.cost
        rect_width = 10
        # Make rectangles narrower on curves for clarity
        curved_rect_width = rect_width * 0.8  # 20% narrower for curved segments
        gap = 4

        # Calculate segment placements
        segment_length = (curve_length - gap * (len(cost_colors) - 1)) / len(
            cost_colors
        )

        # Place segments along curve with improved spacing
        segment_start_index = 0
        distance_traveled = 0
        for i in range(len(cost_colors)):
            color_name = cost_colors[i]
            color = self.color_map.get(color_name.lower(), (128, 128, 128))

            # Calculate segment length (shorter for curved routes)
            adjusted_segment_length = (
                segment_length * 0.9
            )  # Make segments slightly smaller on curves

            # Find segment end based on distance
            segment_end_distance = distance_traveled + adjusted_segment_length
            segment_end_index = segment_start_index
            segment_distance = 0

            while (
                segment_distance < adjusted_segment_length
                and segment_end_index < len(points) - 1
            ):
                segment_end_index += 1
                dx = points[segment_end_index][0] - points[segment_end_index - 1][0]
                dy = points[segment_end_index][1] - points[segment_end_index - 1][1]
                segment_distance += math.sqrt(dx * dx + dy * dy)

            # Draw the segment
            self.draw_train_segment(
                points[segment_start_index],
                points[segment_end_index],
                color_name,
                curved_rect_width,
            )

            # Add gap before next segment
            segment_start_index = (
                segment_end_index + 3
            )  # Skip some points to create a gap
            distance_traveled = segment_end_distance + gap

    def draw_player_cards(self):
        player = self.game.players[self.game.current_player_index]
        # Draw player cards
        for i, card in enumerate(player.train_cards):
            # Calculate dynamic card size based on window dimensions
            current_width, current_height = self.screen.get_size()
            card_width = int(current_width * 0.06)  # 6% of window width
            card_height = int(card_width * (1200 / 1900))  # Maintain aspect ratio

            # Calculate card position dynamically based on screen size
            x = current_width * 0.05 + i * (current_width * 0.05)  # 5% margin + spacing
            y = current_height * 0.05  # Place near the bottom of the screen

            # Construct the file path for the card image
            card_image_path = os.path.join(
                self.cards_folder_path, f"{card.name.lower()}.jpg"
            )

            try:
                # Load the card image
                card_image = pygame.image.load(card_image_path)

                # Scale the card image to fit the dynamically calculated dimensions
                card_image = pygame.transform.scale(
                    card_image, (card_width, card_height)
                )

                # Draw the card image on the screen
                self.screen.blit(card_image, (x, y))
            except pygame.error as e:
                print(f"Error loading card image {card_image_path}: {e}")

                # Fallback: Draw a placeholder rectangle if the image fails to load
                pygame.draw.rect(
                    self.screen, (255, 255, 255), (x, y, card_width, card_height)
                )
                pygame.draw.rect(
                    self.screen, (0, 0, 0), (x, y, card_width, card_height), 1
                )

        # Draw the player's name above their cards
        font = pygame.font.Font(None, 36)  # Use a larger font size for the name
        text = font.render(
            player.name, True, (0, 0, 0)
        )  # Render the player's name in black
        text_rect = text.get_rect(
            center=(
                current_width * 0.05
                + len(player.train_cards) * (current_width * 0.025),
                y - 30,
            )
        )
        self.screen.blit(text, text_rect)

    def draw_open_cards(self):
        # Draw open cards deck on the upper part of the screen
        open_cards = self.game.open_cards_deck.cards

        for i, card in enumerate(open_cards):
            # Calculate dynamic card size based on window dimensions
            current_width, current_height = self.screen.get_size()
            card_width = int(current_width * 0.06)  # 6% of window width
            card_height = int(card_width * (1200 / 1900))  # Maintain aspect ratio

            # Calculate card position dynamically based on screen size
            x = current_width * self.game.open_cards_deck.screen_position[0] + i * (card_width + current_width * 0.01)
            y = current_height * self.game.open_cards_deck.screen_position[1]  # Place near the top of the screen

            # Construct the file path for the card image
            card_image_path = os.path.join(
                self.cards_folder_path, f"{card.name.lower()}.jpg"
            )

            try:
                # Load the card image
                card_image = pygame.image.load(card_image_path)

                # Scale the card image to fit the dynamically calculated dimensions
                card_image = pygame.transform.scale(
                    card_image, (card_width, card_height)
                )

                # Draw the card image on the screen
                self.screen.blit(card_image, (x, y))
            except pygame.error as e:
                print(f"Error loading card image {card_image_path}: {e}")

                # Fallback: Draw a placeholder rectangle if the image fails to load
                pygame.draw.rect(
                    self.screen, (255, 255, 255), (x, y, card_width, card_height)
                )
                pygame.draw.rect(
                    self.screen, (0, 0, 0), (x, y, card_width, card_height), 1
                )

        # Draw the label "Open Cards" above the open cards
        font = pygame.font.Font(None, 36)  # Use a larger font size for the label
        label_text = "Open Cards"
        text = font.render(label_text, True, (0, 0, 0))  # Render the label in black
        text_rect = text.get_rect(
            center=(
                current_width * 0.6
                + len(open_cards) * (card_width + current_width * 0.01) / 2,
                y - 30,
            )
        )
        self.screen.blit(text, text_rect)

    def draw_trains_deck(self):
        # Draw trains deck on the upper part of the screen
        current_width, current_height = self.screen.get_size()
        card_width = int(current_width * 0.06)  # 6% of window width
        card_height = int(card_width * (1200 / 1900))  # Maintain aspect ratio

        # Calculate card position dynamically based on screen size
        x = current_width * self.game.train_cards_deck.screen_position[0] 
        y = current_height * self.game.train_cards_deck.screen_position[1]

        # Construct the file path for the card image
        card_image_path = os.path.join(
            self.cards_folder_path, "train_ticket_card.jpg"
        )

        try:
            # Load the card image
            card_image = pygame.image.load(card_image_path)

            # Scale the card image to fit the dynamically calculated dimensions
            card_image = pygame.transform.scale(
                card_image, (card_width, card_height)
            )

            # Draw the card image on the screen
            self.screen.blit(card_image, (x, y))
        except pygame.error as e:
            print(f"Error loading card image {card_image_path}: {e}")

            # Fallback: Draw a placeholder rectangle if the image fails to load
            pygame.draw.rect(
                self.screen, (255, 255, 255), (x, y, card_width, card_height)
            )
            pygame.draw.rect(
                self.screen, (0, 0, 0), (x, y, card_width, card_height), 1
            )

        # Draw the label "Trains Deck" above the trains deck
        font = pygame.font.Font(None, 36)  # Use a larger font size for the label
        label_text = "Trains Deck"
        text = font.render(label_text, True, (0, 0, 0))  # Render the label in black
        text_rect = text.get_rect(
            center=(
                x + card_width / 2,
                y - 30,
            )
        )
        self.screen.blit(text, text_rect)

    def draw_destination_cards(self):
        # Draw destination cards on the upper part of the screen
        current_width, current_height = self.screen.get_size()
        card_width = int(current_width * 0.06)
        card_height = int(card_width * (1200 / 1900))

        x = current_width * self.game.destination_tickets_deck.screen_position[0]
        y = current_height * self.game.destination_tickets_deck.screen_position[1]
        
        card_image_path = os.path.join(
            self.cards_folder_path, "destination_ticket_card.jpg"
        )
        # Load the card image
        card_image = pygame.image.load(card_image_path)
        # Scale the card image to fit the dynamically calculated dimensions
        card_image = pygame.transform.scale(
            card_image, (card_width, card_height)
        )
        # Draw the card image on the screen
        self.screen.blit(card_image, (x, y))
        # Draw the label "Destination Cards" above the destination cards
        font = pygame.font.Font(None, 36)  # Use a larger font size for the label
        label_text = "Destination Cards"
        text = font.render(label_text, True, (0, 0, 0))  # Render the label in black
        text_rect = text.get_rect(
            center=(
                x + card_width / 2,
                y - 30,
            )
        )
        self.screen.blit(text, text_rect)


    def get_scaling_factor(self):
        # Calculate the scaling factor based on the current screen size.
        current_width, current_height = self.screen.get_size()
        scale_x = current_width / self.original_width
        scale_y = current_height / self.original_height
        return scale_x, scale_y

    def scale_coordinates(self, x, y):
        # Scale coordinates according to the current scaling factor.
        scale_x, scale_y = self.get_scaling_factor()
        return int(x * scale_x), int(y * scale_y)

    def get_clicked_city(self, event):
        '''
        Check if a city was clicked based on the mouse event.
        '''
        for city in self.cities:
            # Scale city coordinates
            city_point = self.scale_coordinates(*city.point)
            city_rect = pygame.draw.circle(
                self.screen, (0, 0, 0), city_point, self.city_radius
            )
            if city_rect.collidepoint(event.pos):
                return city
            
    def get_open_card_index(self, event):
        '''
        Check if an open card was clicked based on the mouse event.
        '''
        current_width, current_height = self.screen.get_size()
        card_width = int(current_width * 0.06)
        card_height = int(card_width * (1200 / 1900))
        for i, card in enumerate(self.game.open_cards_deck.cards):
            x = current_width * self.game.open_cards_deck.screen_position[0] + i * (card_width + current_width * 0.01)
            y = current_height * self.game.open_cards_deck.screen_position[1]
            card_rect = pygame.Rect(x, y, card_width, card_height)
            if card_rect.collidepoint(event.pos):
                return i
        return None
    
    def get_if_train_cards_clicked(self, event):
        '''
        Check if an open card was clicked based on the mouse event.
        '''
        current_width, current_height = self.screen.get_size()
        card_width = int(current_width * 0.06)
        card_height = int(card_width * (1200 / 1900))
        x = current_width * self.game.train_cards_deck.screen_position[0]
        y = current_height * self.game.train_cards_deck.screen_position[1]
        card_rect = pygame.Rect(x, y, card_width, card_height)
        if card_rect.collidepoint(event.pos):
            return True
        return False

    def destination_tickets_clicked(self, event):
        '''
        Check if the destination tickets deck was clicked based on the mouse event.
        '''
        current_width, current_height = self.screen.get_size()
        card_width = int(current_width * 0.06)
        card_height = int(card_width * (1200 / 1900))
        x = current_width * self.game.destination_tickets_deck.screen_position[0]
        y = current_height * self.game.destination_tickets_deck.screen_position[1]
        card_rect = pygame.Rect(x, y, card_width, card_height)
        if card_rect.collidepoint(event.pos):
            return True
        return False
    

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    
                    
                    city = self.get_clicked_city(event)
                    if city:
                        print(f"Clicked on city: {city.name}")
                    


                    open_card_index = self.get_open_card_index(event)
                    if open_card_index is not None:
                        card = self.game.open_cards_deck.cards[open_card_index]
                        print(f"Clicked on open card: {open_card_index} - {card.name}")


                    if self.get_if_train_cards_clicked(event):
                        print("Clicked on train cards deck.")


                    if self.destination_tickets_clicked(event):
                        print("Clicked on destination tickets deck.")



            self.draw()
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
