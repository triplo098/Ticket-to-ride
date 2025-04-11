import pygame
import os
import sys
from pygame.locals import *

class GameWindow:
    def __init__(self):
        pygame.init()
        
        # Get screen info
        self.screen_info = pygame.display.Info()
        self.WINDOW_WIDTH = self.screen_info.current_w
        self.WINDOW_HEIGHT = self.screen_info.current_h
        
        self.fullscreen = True
        self.screen = self.set_screen_mode()
        pygame.display.set_caption("Background Image Example")
        
        # Image position and scale
        self.image_x = 0
        self.image_y = 0
        self.scale = 0.5  # Start at 50% of original size
        self.min_scale = 0.1
        self.max_scale = 2.0
        self.scale_step = 0.05  # How much to zoom per scroll
        
        self.dragging = False
        self.drag_start = None
        
        # Movement variables
        self.move_speed = 5
        self.moving_left = False
        self.moving_right = False
        self.moving_up = False
        self.moving_down = False
        
        self.clock = pygame.time.Clock()
        self.FPS = 60

    def set_screen_mode(self):
        if self.fullscreen:
            return pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT), pygame.FULLSCREEN)
        return pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))

    def load_background(self, image_path):
        try:
            self.original_background = pygame.image.load(image_path).convert()
            return self.scale_background()
        except (pygame.error, FileNotFoundError) as e:
            print(f"Error loading image: {e}")
            pygame.quit()
            sys.exit(1)

    def scale_background(self):
        original_size = self.original_background.get_rect()
        new_width = int(original_size.width * self.scale)
        new_height = int(original_size.height * self.scale)
        return pygame.transform.smoothscale(self.original_background, (new_width, new_height))

    def center_image(self):
        bg_rect = self.background.get_rect()
        self.image_x = (self.WINDOW_WIDTH - bg_rect.width) // 2
        self.image_y = (self.WINDOW_HEIGHT - bg_rect.height) // 2 - 100

    def handle_mouse_events(self, event):
        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                self.dragging = True
                self.drag_start = (event.pos[0] - self.image_x, 
                                 event.pos[1] - self.image_y)
            elif event.button == 4:  # Mouse wheel up
                old_scale = self.scale
                self.scale = min(self.scale + self.scale_step, self.max_scale)
                if old_scale != self.scale:
                    # Store current center
                    center_x = self.image_x + self.background.get_width() // 2
                    center_y = self.image_y + self.background.get_height() // 2
                    # Update image
                    self.background = self.scale_background()
                    # Restore center position
                    self.image_x = center_x - self.background.get_width() // 2
                    self.image_y = center_y - self.background.get_height() // 2
            elif event.button == 5:  # Mouse wheel down
                old_scale = self.scale
                self.scale = max(self.scale - self.scale_step, self.min_scale)
                if old_scale != self.scale:
                    # Store current center
                    center_x = self.image_x + self.background.get_width() // 2
                    center_y = self.image_y + self.background.get_height() // 2
                    # Update image
                    self.background = self.scale_background()
                    # Restore center position
                    self.image_x = center_x - self.background.get_width() // 2
                    self.image_y = center_y - self.background.get_height() // 2
        elif event.type == MOUSEBUTTONUP:
            if event.button == 1:  # Left click release
                self.dragging = False
        elif event.type == MOUSEMOTION:
            if self.dragging:
                self.image_x = event.pos[0] - self.drag_start[0]
                self.image_y = event.pos[1] - self.drag_start[1]

    def handle_key_events(self, event):
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                return False
            elif event.key == K_F11:
                self.fullscreen = not self.fullscreen
                self.screen = self.set_screen_mode()
            elif event.key == K_SPACE:
                self.center_image()
            elif event.key == K_LEFT:
                self.moving_left = True
            elif event.key == K_RIGHT:
                self.moving_right = True
            elif event.key == K_UP:
                self.moving_up = True
            elif event.key == K_DOWN:
                self.moving_down = True
        elif event.type == KEYUP:
            if event.key == K_LEFT:
                self.moving_left = False
            elif event.key == K_RIGHT:
                self.moving_right = False
            elif event.key == K_UP:
                self.moving_up = False
            elif event.key == K_DOWN:
                self.moving_down = False
        return True

    def update_movement(self):
        if self.moving_left:
            self.image_x -= self.move_speed
        if self.moving_right:
            self.image_x += self.move_speed
        if self.moving_up:
            self.image_y -= self.move_speed
        if self.moving_down:
            self.image_y += self.move_speed

    def run(self):
        self.image_path = 'Train board generator - Poland.png'
        self.background = self.load_background(self.image_path)
        self.center_image()
        
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                
                self.handle_mouse_events(event)
                
                if not self.handle_key_events(event):
                    running = False

            self.update_movement()

            self.screen.fill((0, 0, 0))
            self.screen.blit(self.background, (self.image_x, self.image_y))
            
            pygame.display.flip()
            self.clock.tick(self.FPS)

        pygame.quit()

if __name__ == "__main__":
    game = GameWindow()
    game.run()
