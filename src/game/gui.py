import pygame
import math
from pathlib import Path
import os

from map import CityConnection
from cards import DestinationTicketCard


class GUI:
    def __init__(
        self,
        game,
        cards_folder_path=os.path.join(os.path.dirname(__file__), "../cards_graphics"),
    ):
        self.game = game
        # Use the RESIZABLE flag to allow window resizing
        # self.screen = pygame.display.set_mode((1600, 800), pygame.RESIZABLE)
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        pygame.display.set_caption("Ticket to Ride")
        pygame.font.init()  # Initialize the font module

        self.cities = self.game.map.cities
        self.connections = self.game.map.connections

        self.if_draw_destination_tickets_to_choose = False
        self.parallel_choice_mode = False
        self.parallel_conns = []
        self.parallel_rects = [None, None]

        self.if_draw_destination_tickets_to_choose = False

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

        # Player color mapping (assign distinct colors)
        base_player_colors = [(255, 0, 0), (0, 0, 255), (0, 128, 0), (255, 165, 0)]
        self.player_colors = {
            player: base_player_colors[i % len(base_player_colors)]
            for i, player in enumerate(self.game.players)
        }

        # Load map data from YAML file
        script_dir = Path(__file__).resolve().parent
        yaml_path = (
            script_dir / "../config/set_europe_close_up/europe_map_close_up.yaml"
        )

    def draw(self):
        # 1) Tło
        script_dir = Path(__file__).resolve().parent
        map_path = script_dir / "../config/set_europe_close_up/Europe_Map.jpg"
        bg_img = pygame.image.load(map_path)
        scaled_bg = pygame.transform.scale(bg_img, self.screen.get_size())
        self.screen.blit(scaled_bg, (0, 0))

        if self.parallel_choice_mode:
            current_w, current_h = self.screen.get_size()

            rect_w = int(current_w * 0.4)
            rect_h = int(current_h * 0.15)

            x1 = int(current_w * 0.05)
            y1 = int(current_h * 0.80)

            spacing = int(current_w * 0.05)
            x2 = x1 + rect_w + spacing
            y2 = y1

            self.parallel_rects[0] = pygame.Rect(x1, y1, rect_w, rect_h)
            self.parallel_rects[1] = pygame.Rect(x2, y2, rect_w, rect_h)

            conn0 = self.parallel_conns[0]
            conn1 = self.parallel_conns[1]

            col0 = self.color_map.get(conn0.cost[0].name.lower(), (128, 128, 128))
            col1 = self.color_map.get(conn1.cost[0].name.lower(), (128, 128, 128))

            pygame.draw.rect(self.screen, col0, self.parallel_rects[0])
            pygame.draw.rect(self.screen, col1, self.parallel_rects[1])

            pygame.draw.rect(self.screen, (0, 0, 0), self.parallel_rects[0], 3)
            pygame.draw.rect(self.screen, (0, 0, 0), self.parallel_rects[1], 3)

            font = pygame.font.Font(None, 28)

            cityA0, cityB0 = list(conn0.cities)
            cityA1, cityB1 = list(conn1.cities)

            text0 = f"{cityA0.name} – {cityB0.name}"
            text1 = f"{cityA1.name} – {cityB1.name}"

            surf0 = font.render(text0, True, (0, 0, 0))
            surf1 = font.render(text1, True, (0, 0, 0))

            rect0_center = self.parallel_rects[0].center
            rect1_center = self.parallel_rects[1].center
            text0_rect = surf0.get_rect(center=rect0_center)
            text1_rect = surf1.get_rect(center=rect1_center)
            self.screen.blit(surf0, text0_rect)
            self.screen.blit(surf1, text1_rect)

            pygame.display.flip()
            return

        self.draw_routes()

        font = pygame.font.Font(None, 24)
        for city in self.cities:
            x, y = self.scale_coordinates(*city.point)
            pygame.draw.circle(self.screen, (0, 0, 0), (x, y), self.city_radius)

            text_surf = font.render(city.name, True, (0, 0, 0))
            outline_surf = font.render(city.name, True, (255, 255, 255))

            # white contour
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    pos = outline_surf.get_rect(center=(x + dx + 10, y + dy - 10))
                    self.screen.blit(outline_surf, pos)

            # black interior
            pos = text_surf.get_rect(center=(x + 10, y - 10))
            self.screen.blit(text_surf, pos)

        self.draw_player_cards()
        self.draw_player_tickets()
        self.draw_open_cards()
        self.draw_trains_deck()
        self.draw_destination_cards()

        if self.if_draw_destination_tickets_to_choose:
            self.draw_destination_tickets_to_choose()

        pygame.display.flip()

    def draw_player_trains(self, conn: CityConnection, parallel_shift=0):
        """Draw small train‐car rectangles on *this* route, with the same shift."""
        # endpoints
        a, b = conn.cities
        x1, y1 = self.scale_coordinates(*a.point)
        x2, y2 = self.scale_coordinates(*b.point)
        dx, dy = x2 - x1, y2 - y1
        dist = math.hypot(dx, dy)
        if dist == 0:
            return

        # normalize
        dx /= dist
        dy /= dist
        # perpendicular
        px, py = -dy, dx

        # apply the same parallel shift that draw_route used
        if parallel_shift != 0:
            x1 += px * parallel_shift * 25
            y1 += py * parallel_shift * 25
            x2 += px * parallel_shift * 25
            y2 += py * parallel_shift * 25
            dx = x2 - x1
            dy = y2 - y1
            dist = math.hypot(dx, dy)
            dx /= dist
            dy /= dist
            px, py = -dy, dx

        # leave the same city‐circle padding and gap logic
        off = 15
        gap = 4
        rect_w = 8
        colors = [c.name.lower() for c in conn.cost]
        n = len(colors)
        if n == 0:
            return

        usable = dist - 2 * off - gap * (n - 1)
        seg_len = usable / n
        sx = x1 + dx * off
        sy = y1 + dy * off

        # car‐inset factor (20% smaller than full segment)
        inset = 0.2

        for i, _ in enumerate(colors):
            # center of this segment
            center_x = sx + dx * (i * (seg_len + gap) + seg_len / 2)
            center_y = sy + dy * (i * (seg_len + gap) + seg_len / 2)

            # full‐width segment corners
            corners = [
                (
                    center_x - dx * seg_len / 2 + px * rect_w / 2,
                    center_y - dy * seg_len / 2 + py * rect_w / 2,
                ),
                (
                    center_x - dx * seg_len / 2 - px * rect_w / 2,
                    center_y - dy * seg_len / 2 - py * rect_w / 2,
                ),
                (
                    center_x + dx * seg_len / 2 - px * rect_w / 2,
                    center_y + dy * seg_len / 2 - py * rect_w / 2,
                ),
                (
                    center_x + dx * seg_len / 2 + px * rect_w / 2,
                    center_y + dy * seg_len / 2 + py * rect_w / 2,
                ),
            ]

            # inset each corner toward the center
            car = []
            for cx, cy in corners:
                ix = center_x + (cx - center_x) * (1 - inset)
                iy = center_y + (cy - center_y) * (1 - inset)
                car.append((ix, iy))
            player_color = self.player_colors.get(conn.claimed_by, (0, 0, 0))

            # draw the car
            pygame.draw.polygon(self.screen, player_color, car)
            pygame.draw.polygon(self.screen, (255, 255, 255), car, 2)

    def draw_routes(self):
        grouped = {}
        for conn in self.connections:
            a, b = list(conn.cities)
            key = tuple(sorted((a.name, b.name)))
            grouped.setdefault(key, []).append(conn)

        for conns in grouped.values():
            for i, conn in enumerate(conns):
                shift = 0 if len(conns) == 1 else 0.2 * (-1 if i == 0 else 1)
                self.draw_route(conn, shift)
                if conn.claimed_by is not None:
                    col = self.player_colors[conn.claimed_by]
                    self.draw_player_trains(conn, shift)

    def draw_route(self, conn: CityConnection, parallel_shift=0):
        # conn.cities to set{City, City}
        a, b = list(conn.cities)
        x1, y1 = self.scale_coordinates(*a.point)
        x2, y2 = self.scale_coordinates(*b.point)
        dx, dy = x2 - x1, y2 - y1
        dist = math.hypot(dx, dy)
        if dist == 0:
            return
        dx, dy = dx / dist, dy / dist
        px, py = -dy, dx

        colors = [c.name.lower() for c in conn.cost]
        n = len(colors)
        if n == 0:
            return

        # shift double‐route
        if parallel_shift:
            x1 += px * parallel_shift * 25
            y1 += py * parallel_shift * 25
            x2 += px * parallel_shift * 25
            y2 += py * parallel_shift * 25
            dx, dy = x2 - x1, y2 - y1
            dist = math.hypot(dx, dy)
            dx, dy = dx / dist, dy / dist

        colors = [c.name.lower() for c in conn.cost]
        seg_w, gap, off = 10, 4, 15
        n = len(colors)
        usable = dist - 2 * off - gap * (n - 1)
        seg_len = usable / n
        sx, sy = x1 + dx * off, y1 + dy * off

        for i, col in enumerate(colors):
            cx = sx + dx * (i * (seg_len + gap) + seg_len / 2)
            cy = sy + dy * (i * (seg_len + gap) + seg_len / 2)
            w, h = seg_len, seg_w
            corners = [
                (cx - dx * w / 2 + px * h / 2, cy - dy * w / 2 + py * h / 2),
                (cx - dx * w / 2 - px * h / 2, cy - dy * w / 2 - py * h / 2),
                (cx + dx * w / 2 - px * h / 2, cy + dy * w / 2 - py * h / 2),
                (cx + dx * w / 2 + px * h / 2, cy + dy * w / 2 + py * h / 2),
            ]
            color = self.color_map.get(col, (128, 128, 128))
            pygame.draw.polygon(self.screen, color, corners)
            pygame.draw.polygon(self.screen, (0, 0, 0), corners, 1)

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

    def draw_player_tickets(self):
        player = self.game.players[self.game.current_player_index]
        # Draw player tickets
        for i, ticket in enumerate(player.destination_tickets + player.accomplished_destination_tickets):
            # Calculate dynamic card size based on window dimensions
            current_width, current_height = self.screen.get_size()
            card_width = int(current_width * 0.06)
            card_height = int(card_width * (1200 / 1900))  # Maintain aspect ratio
            # Calculate card position dynamically based on screen size
            x = current_width * 0.05 + i * (current_width * 0.05)  # 5% margin + spacing
            y = current_height * 0.15  # Place near the bottom of the screen

            image = self.create_image_from_ticket(ticket)
            # Scale the card image to fit the dynamically calculated dimensions
            image = pygame.transform.scale(image, (card_width, card_height))
            # Draw the card image on the screen
            self.screen.blit(image, (x, y))
            # Draw the label "Destination Tickets" above the destination tickets
            font = pygame.font.Font(None, 16)  # Use a larger font size for the label
            label_text = "Destination Tickets"
            text = font.render(label_text, True, (0, 0, 0))  # Render the label in black

    def draw_open_cards(self):
        # Draw open cards deck on the upper part of the screen
        open_cards = self.game.open_cards_deck.cards

        for i, card in enumerate(open_cards):
            # Calculate dynamic card size based on window dimensions
            current_width, current_height = self.screen.get_size()
            card_width = int(current_width * 0.06)  # 6% of window width
            card_height = int(card_width * (1200 / 1900))  # Maintain aspect ratio

            # Calculate card position dynamically based on screen size
            x = current_width * self.game.open_cards_deck.screen_position[0] + i * (
                card_width + current_width * 0.01
            )
            y = (
                current_height * self.game.open_cards_deck.screen_position[1]
            )  # Place near the top of the screen

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
        card_image_path = os.path.join(self.cards_folder_path, "train_ticket_card.jpg")

        try:
            # Load the card image
            card_image = pygame.image.load(card_image_path)

            # Scale the card image to fit the dynamically calculated dimensions
            card_image = pygame.transform.scale(card_image, (card_width, card_height))

            # Draw the card image on the screen
            self.screen.blit(card_image, (x, y))
        except pygame.error as e:
            print(f"Error loading card image {card_image_path}: {e}")

            # Fallback: Draw a placeholder rectangle if the image fails to load
            pygame.draw.rect(
                self.screen, (255, 255, 255), (x, y, card_width, card_height)
            )
            pygame.draw.rect(self.screen, (0, 0, 0), (x, y, card_width, card_height), 1)

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
        card_image = pygame.transform.scale(card_image, (card_width, card_height))
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

    def draw_destination_tickets_to_choose(self):
        # Draw destination tickets to choose from
        current_width, current_height = self.screen.get_size()
        card_width = int(current_width * 0.06)
        card_height = int(card_width * (1200 / 1900))
        spacing = int(current_width * 0.02)  # Add spacing between cards

        for i, card in enumerate(self.game.destination_tickets_to_choose):
            # Calculate card position dynamically based on screen size
            x = current_width * 0.7 + i * (card_width + spacing)
            y = current_height * 0.7  # Place near the bottom of the screen
            # Construct the file path for the card image

            image = self.create_image_from_ticket(card)
            # Scale the card image to fit the dynamically calculated dimensions
            image = pygame.transform.scale(image, (card_width, card_height))
            # Draw the card image on the screen
            self.screen.blit(image, (x, y))
            # Draw the label "Destination Tickets" above the destination tickets
            font = pygame.font.Font(None, 16)  # Use a larger font size for the label
            label_text = "Destination Tickets"
            text = font.render(label_text, True, (0, 0, 0))  # Render the label in black

    def create_image_from_ticket(self, ticket):

        # Create an image from the destination ticket
        current_width, current_height = self.screen.get_size()
        card_width = int(current_width * 0.06)
        card_height = int(card_width * (1200 / 1900))

        # Create a blank surface for the ticket
        ticket_surface = pygame.Surface((card_width, card_height))
        ticket_surface.fill((255, 255, 255))

        # Draw the ticket details on the surface
        font_size = int(card_width * 0.15)  # Adjust font size relative to card width
        font = pygame.font.Font(None, font_size)
        text = f"{ticket.start_city} - {ticket.end_city}"
        text_surface = font.render(text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=(card_width // 2, card_height // 3))
        ticket_surface.blit(text_surface, text_rect)

        # Draw the number of points on the surface
        points_text = f"Points: {ticket.points}"
        points_surface = font.render(points_text, True, (0, 0, 0))
        points_rect = points_surface.get_rect(
            center=(card_width // 2, 2 * card_height // 3)
        )
        ticket_surface.blit(points_surface, points_rect)

        # Check if the ticket is accomplished
        if ticket in self.game.players[self.game.current_player_index].accomplished_destination_tickets:
            # Add a green frame if accomplished
            pygame.draw.rect(ticket_surface, (0, 255, 0), ticket_surface.get_rect(), 5)
        else:
            # Add a black frame if not accomplished
            pygame.draw.rect(ticket_surface, (0, 0, 0), ticket_surface.get_rect(), 5)

        return ticket_surface

    def set_destination_tickets_to_choose(self, tickets: list[DestinationTicketCard]):

        # Set the destination tickets to choose from
        self.game.destination_tickets_to_choose = tickets

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
        """
        Check if a city was clicked based on the mouse event.
        """
        for city in self.cities:
            # Scale city coordinates
            city_point = self.scale_coordinates(*city.point)
            city_rect = pygame.draw.circle(
                self.screen, (0, 0, 0), city_point, self.city_radius
            )
            if city_rect.collidepoint(event.pos):
                return city

    def get_open_card_index(self, event):
        """
        Check if an open card was clicked based on the mouse event.
        """
        current_width, current_height = self.screen.get_size()
        card_width = int(current_width * 0.06)
        card_height = int(card_width * (1200 / 1900))
        for i, card in enumerate(self.game.open_cards_deck.cards):
            x = current_width * self.game.open_cards_deck.screen_position[0] + i * (
                card_width + current_width * 0.01
            )
            y = current_height * self.game.open_cards_deck.screen_position[1]
            card_rect = pygame.Rect(x, y, card_width, card_height)
            if card_rect.collidepoint(event.pos):
                return i
        return None

    def get_destination_tickets_to_choose_index(self, event):
        """
        Check if a destination ticket was clicked based on the mouse event.
        """
        current_width, current_height = self.screen.get_size()
        card_width = int(current_width * 0.06)
        card_height = int(card_width * (1200 / 1900))
        spacing = int(current_width * 0.02)  # Add spacing between cards

        for i, card in enumerate(self.game.destination_tickets_to_choose):
            x = current_width * 0.7 + i * (card_width + spacing)
            y = current_height * 0.7
            card_rect = pygame.Rect(x, y, card_width, card_height)
            if card_rect.collidepoint(event.pos):
                return i
        return None

    def get_if_train_cards_clicked(self, event):
        """
        Check if an open card was clicked based on the mouse event.
        """
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
        """
        Check if the destination tickets deck was clicked based on the mouse event.
        """
        current_width, current_height = self.screen.get_size()
        card_width = int(current_width * 0.06)
        card_height = int(card_width * (1200 / 1900))
        x = current_width * self.game.destination_tickets_deck.screen_position[0]
        y = current_height * self.game.destination_tickets_deck.screen_position[1]
        card_rect = pygame.Rect(x, y, card_width, card_height)
        if card_rect.collidepoint(event.pos):
            return True
        return False

    def get_player_action(self):

        clicked_cities = set()
        while True:
            if getattr(self, "parallel_choice_mode", False):
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        exit(0)

                    if event.type == pygame.MOUSEBUTTONDOWN:
                        pos = event.pos
                        if self.parallel_rects[0] and self.parallel_rects[0].collidepoint(pos):
                            self.parallel_choice_mode = False
                            return 0, "parallel_choice"
                        if self.parallel_rects[1] and self.parallel_rects[1].collidepoint(pos):
                            self.parallel_choice_mode = False
                            return 1, "parallel_choice"
                pygame.time.delay(10)
                continue
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:

                    city = self.get_clicked_city(event)
                    if city:
                        if city not in clicked_cities:
                            clicked_cities.add(city)
                            print(f"Clicked on city: {city.name}")

                            if len(clicked_cities) == 2:
                                return clicked_cities, "create_connection"

                        continue

                    open_card_index = self.get_open_card_index(event)

                    if open_card_index is not None:
                        card = self.game.open_cards_deck.cards[open_card_index]
                        print(f"Clicked on open card: {open_card_index} - {card.name}")
                        return open_card_index, "open_card_index"

                    if self.get_if_train_cards_clicked(event):
                        print("Clicked on train cards deck.")
                        return "train_cards_deck"

                    if self.destination_tickets_clicked(event):
                        print("Clicked on destination tickets deck.")
                        return "destination_tickets_deck"

                    destination_ticket_index = (
                        self.get_destination_tickets_to_choose_index(event)
                    )
                    if (
                        destination_ticket_index is not None
                        and self.if_draw_destination_tickets_to_choose
                    ):
                        print(
                            f"Clicked on destination ticket: {destination_ticket_index}"
                        )
                        return destination_ticket_index, "destination_ticket_index"

                    return None, "skip"

    def run(self):

        running = True
        while running:
            # for event in pygame.event.get():
            #     if event.type == pygame.QUIT:
            #         running = False
            #     elif event.type == pygame.MOUSEBUTTONDOWN:

            # city = self.get_clicked_city(event)
            # if city:
            #     print(f"Clicked on city: {city.name}")

            # open_card_index = self.get_open_card_index(event)
            # if open_card_index is not None:
            #     card = self.game.open_cards_deck.cards[open_card_index]
            #     print(f"Clicked on open card: {open_card_index} - {card.name}")

            # if self.get_if_train_cards_clicked(event):
            #     print("Clicked on train cards deck.")

            # if self.destination_tickets_clicked(event):
            #     print("Clicked on destination tickets deck.")

            self.draw()
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
