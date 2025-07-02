"""Vertex Velocity's main game file."""

import argparse
# import logging
import sys

import pygame

from vertex_velocity.entities import Player
from vertex_velocity.tilemap import TileMap
from vertex_velocity.utils import load_image
# from vertex_velocity.utils import SHOW_GRID, SHOW_COORDINATES, SHOW_COLLISION
# from vertex_velocity.utils import HIDE_PARTICLES

# Set up log level.
# logging.basicConfig(level=logging.DEBUG)


class Game:
    """Main game class for Vertex Velocity."""

    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 720
    FPS = 64

    PLAYER_INIT_POS = (100, 50)
    PLAYER_SIZE = (64, 64)

    def __init__(self, inputTilemap):
        """Initialize the game.
        Args:
            inputTilemap (str): The input tilemap file name.
        """
        pygame.init()

        self.inputTilemap = inputTilemap

        pygame.display.set_caption("Vertex Velocity")
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        self.assets = {
            "background": load_image("background.png"),
            "player": load_image("player.png"),
            "brick": load_image("brick.png"),
            "spike": load_image("spike.png"),
        }

        if self.inputTilemap:
            self.tilemap = TileMap.fromJson(self, self.inputTilemap)
            self.tilemap.debugOptions = 0
            # self.tilemap.debugOptions |= SHOW_GRID
            # self.tilemap.debugOptions |= SHOW_COORDINATES
            # self.tilemap.debugOptions |= SHOW_COLLISION
        else:
            self.tilemap = TileMap(self)

        self.movement = {
            "up": False,
            "down": False,
            "left": False,
            "right": False
        }
        self.player = Player(self, self.tilemap, self.PLAYER_INIT_POS, self.PLAYER_SIZE)
        self.scroll = list(self.PLAYER_INIT_POS)
        self.tickCount = 0

    @property
    def currentTick(self):
        """Get the current game tick."""
        return str(self.tickCount)

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
        """Update the game.
        Returns:
            bool: True if the game should continue, False if the player is dead.
        """
        # Explicitely not scrolling vertically.
        self.scroll[0] += (self.player.rect.centerx - self.SCREEN_WIDTH / 2 - self.scroll[0]) / 10

        # Update player's position.
        self.player.update(
            self.movement["up"],
        )

        # Check player death.
        if self.player.isDead:
            return False

        return True

    def render(self):
        """Render the game."""
        self.screen.blit(self.assets["background"], (0, 0))

        renderScroll = [int(pos) for pos in self.scroll]
        self.tilemap.render(self.screen, renderScroll)
        self.player.render(self.screen, renderScroll)

        pygame.display.update()

    def run(self):
        """Run the game."""
        gameContinue = True
        while gameContinue:
            self.processInputs()
            gameContinue = self.update()
            self.render()

            self.clock.tick(self.FPS)
            self.tickCount += 1


def main():
    """Main function to start the game."""
    parser = argparse.ArgumentParser(description="Vertex Velocity")
    parser.add_argument("-l", "--level", type=str, help="Level file name")
    args = parser.parse_args()

    if not args.level:
        print("Error: \"-l/--level\" is required.")
        sys.exit(1)

    Game(args.level).run()


if __name__ == "__main__":
    main()
