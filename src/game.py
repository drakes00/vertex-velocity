import sys
import logging

import pygame

from entities import PhysicsEntity
from utils import load_image
from utils import SHOW_GRID, SHOW_COORDINATES, SHOW_BOUNDING_BOXES
from tilemap import TileMap

# Set up log level.
# logging.basicConfig(level=logging.DEBUG)


class Game:
    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 720
    FPS = 60

    PLAYER_INIT_POS = (100, 50)
    PLAYER_SIZE = (64, 64)

    def __init__(self):
        """Initialize the game."""
        pygame.init()

        pygame.display.set_caption("Vertex Velocity")
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        self.assets = {
            "background": load_image("background.png"),
            "player": load_image("player.png"),
            "brick": load_image("brick.png"),
            "triangle": load_image("triangle.png"),
        }
        self.tilemap = TileMap(self, debugOptions=SHOW_GRID | SHOW_COORDINATES | SHOW_BOUNDING_BOXES)

        self.movement = {
            "up": False,
            "down": False,
            "left": False,
            "right": False
        }
        self.player = PhysicsEntity(self, self.tilemap, "player", self.PLAYER_INIT_POS, self.PLAYER_SIZE)
        self.scroll = [0, 0]

    def processInputs(self):
        """Process the user inputs."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.movement["up"] = True
                elif event.key == pygame.K_DOWN:
                    self.movement["down"] = True
                elif event.key == pygame.K_LEFT:
                    self.movement["left"] = True
                elif event.key == pygame.K_RIGHT:
                    self.movement["right"] = True
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:
                    self.movement["up"] = False
                elif event.key == pygame.K_DOWN:
                    self.movement["down"] = False
                elif event.key == pygame.K_LEFT:
                    self.movement["left"] = False
                elif event.key == pygame.K_RIGHT:
                    self.movement["right"] = False

    def update(self):
        """Update the game."""
        # Explicitely not scrolling vertically.
        self.scroll[0] += (self.player.rect.centerx - self.SCREEN_WIDTH / 2 - self.scroll[0]) / 10

        # Update player's position.
        self.player.update((self.movement["right"] - self.movement["left"]) * 5, self.movement["up"])

    def render(self):
        """Render the game."""
        self.screen.blit(self.assets["background"], (0, 0))

        renderScroll = [int(pos) for pos in self.scroll]
        self.tilemap.render(self.screen, renderScroll)
        self.player.render(self.screen, renderScroll)

        pygame.display.update()

    def run(self):
        while True:
            self.processInputs()
            self.update()
            self.render()

            self.clock.tick(self.FPS)


Game().run()
