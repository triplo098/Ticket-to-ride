import pygame
import math
from collections import namedtuple
import yaml
from pathlib import Path

class GUI:
    def __init__(self, game):
        self.game = game
        pygame.init()
        self.screen = pygame.display.set_mode((1050, 578), pygame.RESIZABLE)
        pygame.display.set_caption("Ticket to Ride")
        self.clock = pygame.time.Clock()
        pygame.font.init()

        # map image dimensions
        self.original_width, self.original_height = 1050, 578

        # Color mapping for routes
        self.color_map = {
            'black': (0, 0, 0),
            'pink': (255, 105, 180),
            'green': (0, 128, 0),
            'blue': (0, 0, 255),
            'red': (255, 0, 0),
            'yellow': (255, 255, 0),
            'orange': (255, 165, 0),
            'white': (255, 255, 255),
            'brown': (165, 42, 42),
            'gray': (128, 128, 128)
        }
        self.player_colors = {0:(255,0,0),1:(0,0,255),2:(255,255,0),
                              3:(0,255,0),4:(128,0,128)}

        # **Use the game’s data** directly
        self.cities     = self.game.map.cities
        self.connections= self.game.map.connections

        # --- load the background once ---
        script_dir = Path(__file__).resolve().parent
        map_path = script_dir / '../config/set_europe_close_up/Europe_Map.jpg'
        self.background_image = pygame.image.load(map_path)

    def draw(self):
        # draw background (scaled)
        scaled_bg = pygame.transform.scale(
            self.background_image,
            self.screen.get_size()
        )
        self.screen.blit(scaled_bg, (0, 0))

        # draw all routes
        self.draw_routes()

        # draw cities
        font = pygame.font.Font(None, 24)
        for city in self.cities:
            x,y = self.scale_coordinates(*city.point)
            pygame.draw.circle(self.screen, (0,0,0),(x,y),5)
            # city name with outline
            txt = font.render(city.name, True, (0,0,0))
            for dx in (-1,0,1):
                for dy in (-1,0,1):
                    if dx!=0 or dy!=0:
                        o = font.render(city.name, True, (255,255,255))
                        self.screen.blit(o, o.get_rect(center=(x+dx+10,y+dy-10)))
            self.screen.blit(txt, txt.get_rect(center=(x+10,y-10)))

    def draw_routes(self):
        # Group connections by city‐pair
        grouped = {}
        for conn in self.connections:
            a, b = conn.cities
            key = tuple(sorted((a.name, b.name)))
            grouped.setdefault(key, []).append(conn)

        # Now draw each route (and its markers) with the correct shift
        for key, conns in grouped.items():
            for i, conn in enumerate(conns):
                # double‐route shifts: -0.2 and +0.2, single gets 0
                shift = 0
                if len(conns) == 2:
                    shift = 0.2 * (-1 if i == 0 else 1)

                # draw the track segments
                self.draw_route(conn, shift)

                # if it’s claimed, draw its markers with the same shift
                if conn.claimed_by is not None:
                    col = self.player_colors[conn.claimed_by]
                    self.draw_train_markers(conn, col, shift)

    def draw_route(self, conn, parallel_shift=0):
        a,b = conn.cities
        x1,y1 = self.scale_coordinates(*a.point)
        x2,y2 = self.scale_coordinates(*b.point)
        dx,dy = x2-x1, y2-y1
        dist = math.hypot(dx,dy)
        if dist==0: return
        dx,dy = dx/dist, dy/dist
        px,py = -dy, dx

        # If this connection has no cost (0‐length route), skip drawing
        colors = [c.name.lower() for c in conn.cost]
        n = len(colors)
        if n == 0:
            return

        # shift double‐route
        if parallel_shift:
            x1 += px*parallel_shift*25; y1+=py*parallel_shift*25
            x2 += px*parallel_shift*25; y2+=py*parallel_shift*25
            dx,dy = x2-x1, y2-y1; dist=math.hypot(dx,dy)
            dx,dy = dx/dist,dy/dist

        # segment parameters
        # conn.cost is a list of TrainCard enums—grab their names
        colors = [c.name.lower() for c in conn.cost]
        seg_w, gap, off = 10, 4, 15
        n = len(colors)
        usable = dist - 2*off - gap*(n-1)
        seg_len = usable/n
        sx,sy = x1+dx*off, y1+dy*off

        for i, col in enumerate(colors):
            center_x = sx + dx*(i*(seg_len+gap)+seg_len/2)
            center_y = sy + dy*(i*(seg_len+gap)+seg_len/2)
            # build the rectangle
            w,h = seg_len, seg_w
            corners = [
                (center_x - dx*w/2 + px*h/2, center_y - dy*w/2 + py*h/2),
                (center_x - dx*w/2 - px*h/2, center_y - dy*w/2 - py*h/2),
                (center_x + dx*w/2 - px*h/2, center_y + dy*w/2 - py*h/2),
                (center_x + dx*w/2 + px*h/2, center_y + dy*w/2 + py*h/2),
            ]
            color = self.color_map.get(col, (128,128,128))
            pygame.draw.polygon(self.screen, color, corners)
            pygame.draw.polygon(self.screen, (0,0,0), corners,1)

    def draw_train_markers(self, conn, player_color, parallel_shift=0):
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
                (center_x - dx * seg_len / 2 + px * rect_w / 2,
                 center_y - dy * seg_len / 2 + py * rect_w / 2),
                (center_x - dx * seg_len / 2 - px * rect_w / 2,
                 center_y - dy * seg_len / 2 - py * rect_w / 2),
                (center_x + dx * seg_len / 2 - px * rect_w / 2,
                 center_y + dy * seg_len / 2 - py * rect_w / 2),
                (center_x + dx * seg_len / 2 + px * rect_w / 2,
                 center_y + dy * seg_len / 2 + py * rect_w / 2),
            ]

            # inset each corner toward the center
            car = []
            for (cx, cy) in corners:
                ix = center_x + (cx - center_x) * (1 - inset)
                iy = center_y + (cy - center_y) * (1 - inset)
                car.append((ix, iy))

            # draw the car
            pygame.draw.polygon(self.screen, player_color, car)
            pygame.draw.polygon(self.screen, (255, 255, 255), car, 2)

    def get_scaling_factor(self):
        w,h = self.screen.get_size()
        return w/self.original_width, h/self.original_height

    def scale_coordinates(self, x,y):
        sx,sy = self.get_scaling_factor()
        return int(x*sx), int(y*sy)

    def run(self):
        running=True
        while running:
            for e in pygame.event.get():
                if e.type==pygame.QUIT:
                    running=False
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)
        pygame.quit()