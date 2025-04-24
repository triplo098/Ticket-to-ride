import pygame
import os

class GUI:
    def __init__(self, game):
        self.game = game
        self.screen = pygame.display.set_mode((1024, 1024))
        pygame.display.set_caption("Ticket to Ride")
        pygame.font.init()  # Initialize the font module
        self.clock = pygame.time.Clock()
        

    def draw(self):
        # Load the background image
        script_dir = os.path.dirname(os.path.abspath(__file__))  # Get the directory of the current script
        map_path = os.path.join(script_dir, '../config/maps/Europe_Political_Map.png')
        background_image = pygame.image.load(map_path)

        # Draw the background image on the screen
        self.screen.blit(background_image, (0, 0))  # Draw at the top-left corner of the screen (0, 0)

        for city in self.game.map.cities:
            # Draw each city
            pygame.draw.circle(self.screen, (0, 0, 0), city.point, 5)
            # Draw city name
            font = pygame.font.Font(None, 24)
            text = font.render(city.name, True, (0, 0, 0))
            offset = (10, -10)  # Offset for the city name (x, y)
            text_rect = text.get_rect(center=(city.point[0] + offset[0], city.point[1] + offset[1]))
            self.screen.blit(text, text_rect)

            

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.draw()
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()   