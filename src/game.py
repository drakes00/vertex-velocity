"""Vertex Velocity's main game file."""

import argparse
import logging
import sys

import pygame

from entities import Player
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

    def __init__(self, inputTilemap=None):
        """Initialize the game."""
        pygame.init()

        self.inputTilemap = inputTilemap

        pygame.display.set_caption("Vertex Velocity")
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        self.assets = {
            "background": load_image("background.png"),
            "player": load_image("player.png"),
            "brick": load_image("brick.png"),
            "triangle": load_image("triangle.png"),
        }

        if self.inputTilemap:
            self.tilemap = TileMap.fromJson(self, self.inputTilemap)
            # self.tilemap.debugOptions = SHOW_GRID | SHOW_COORDINATES
        else:
            self.tilemap = TileMap(self, debugOptions=SHOW_GRID | SHOW_COORDINATES)

        self.movement = {
            "up": False,
            "down": False,
            "left": False,
            "right": False
        }
        self.player = Player(self, self.tilemap, self.PLAYER_INIT_POS, self.PLAYER_SIZE)
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
        self.player.update(
            (self.movement["right"] - self.movement["left"]) * 10,
            self.movement["up"],
        )

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


def main():
    parser = argparse.ArgumentParser(description="Vertex Velocity's Level Editor",)
    parser.add_argument("-i", "--input", type=str, help="Input file name")
    args = parser.parse_args()

    if not args.input:
        print("Error: \"-i/--input\" is required.")
        sys.exit(1)

    Game(args.input).run()


if __name__ == "__main__":
    main()
