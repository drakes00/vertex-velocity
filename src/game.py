import sys

import pygame

from entities import PhysicsEntity
from utils import load_image


class Game:
    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 720
    FPS = 60

    def __init__(self):
        """Initialize the game."""
        pygame.init()

        pygame.display.set_caption("Vertex Velocity")
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        self.assets = {
            "player": load_image("player.png")
        }

        self.movement = {
            "up": False,
            "down": False,
            "left": False,
            "right": False
        }
        self.player = PhysicsEntity(self, "player", (50, 50), (64, 64))

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
        self.player.update(
            ((self.movement["right"] - self.movement["left"]) * 5,
             (self.movement["down"] - self.movement["up"]) * 5)
        )

    def render(self):
        """Render the game."""
        self.screen.fill((14, 219, 248))
        self.player.render(self.screen)
        pygame.display.update()

    def run(self):
        while True:
            self.processInputs()
            self.update()
            self.render()

            self.clock.tick(self.FPS)


Game().run()
