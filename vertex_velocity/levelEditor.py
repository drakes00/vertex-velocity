"""Level Editor for Vertex Velocity."""

import argparse
import os
import sys

import pygame

from vertex_velocity.utils import load_image
from vertex_velocity.utils import SHOW_GRID, SHOW_COORDINATES
from vertex_velocity.tilemap import TileMap

# Set up log level.
# logging.basicConfig(level=logging.DEBUG)


class LevelEditor:
    """A level editor for Vertex Velocity."""

    SCREEN_WIDTH = 2560
    SCREEN_HEIGHT = 1440
    FPS = 60

    PLAYER_INIT_POS = (100, 50)
    PLAYER_SIZE = (64, 64)

    def __init__(self, inputTilemap=None):
        """Initialize the game."""
        pygame.init()

        self.inputTilemap = inputTilemap

        pygame.display.set_caption("Vertex Velocity - Level Editor")
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        self.assets = {
            "brick": load_image("brick.png"),
            "spike": load_image("spike.png"),
        }
        self.existingTiles = list(self.assets.keys())

        if self.inputTilemap and os.path.exists(self.inputTilemap):
            self.tilemap = TileMap.fromJson(self, self.inputTilemap)
            self.tilemap.debugOptions = SHOW_GRID | SHOW_COORDINATES
        else:
            self.tilemap = TileMap(self, debugOptions=SHOW_GRID | SHOW_COORDINATES)

        self.movement = {
            "up": False,
            "down": False,
            "left": False,
            "right": False
        }

        self.tileClicked = None
        self.tilesClicked = set([])
        self.clicking = False
        self.rightClicking = False

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
                elif event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    # Save the current tilemap.
                    self.tilemap.toJson(self.inputTilemap)
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:
                    self.movement["up"] = False
                elif event.key == pygame.K_DOWN:
                    self.movement["down"] = False
                elif event.key == pygame.K_LEFT:
                    self.movement["left"] = False
                elif event.key == pygame.K_RIGHT:
                    self.movement["right"] = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.tileClicked = (
                    (event.pos[0] + self.scroll[0]) // self.tilemap.tileSize,
                    (event.pos[1] + self.scroll[1]) // self.tilemap.tileSize
                )
                if event.button == 1:
                    # Left mouse button.
                    self.clicking = True
                elif event.button == 3:
                    # Right mouse button.
                    self.rightClicking = True
            elif event.type == pygame.MOUSEBUTTONUP:
                self.tilesClicked = set([])
                if event.button == 1:
                    # Left mouse button.
                    self.clicking = False
                elif event.button == 3:
                    # Right mouse button.
                    self.rightClicking = False
            elif event.type == pygame.MOUSEMOTION:
                if self.clicking or self.rightClicking:
                    self.tileClicked = (
                        (event.pos[0] + self.scroll[0]) // self.tilemap.tileSize,
                        (event.pos[1] + self.scroll[1]) // self.tilemap.tileSize
                    )

    def update(self):
        """Update the game."""
        # Allow scrolling.
        self.scroll[0] += (self.movement["right"] - self.movement["left"]) * 10
        self.scroll[1] += (self.movement["down"] - self.movement["up"]) * 10

        # Handle clicking.
        if self.clicking and self.tileClicked not in self.tilesClicked:
            # Left clicking to set tiles.
            currentTile = self.tilemap.getTileAt(self.tileClicked)
            self.tilesClicked.add(self.tileClicked)
            if currentTile is None:
                # If there is no tile at the clicked position, add a new one with first tile type.
                self.tilemap.addTile(self.tileClicked, self.existingTiles[0])
            else:
                # If there is a tile at the clicked position, cycle through the existing tiles.
                self.tilemap.addTile(
                    self.tileClicked,
                    self.existingTiles[(self.existingTiles.index(currentTile["type"]) + 1) % len(self.existingTiles)]
                )
        elif self.rightClicking and self.tileClicked not in self.tilesClicked:
            # Right clicking to remove tiles.
            self.tilemap.removeTile(self.tileClicked)
            self.tilesClicked.add(self.tileClicked)

    def render(self):
        """Render the game."""
        self.screen.fill((150, 150, 150))

        renderScroll = [int(pos) for pos in self.scroll]
        self.tilemap.render(self.screen, renderScroll)

        pygame.display.update()

    def run(self):
        """Run the game."""
        while True:
            self.processInputs()
            self.update()
            self.render()

            self.clock.tick(self.FPS)


def main():
    """Main function to run the level editor."""
    parser = argparse.ArgumentParser(
        description="Vertex Velocity's Level Editor",
    )
    parser.add_argument("-i", "--input", type=str, help="Input file name")
    args = parser.parse_args()

    if not args.input:
        print("Error: \"-i/--input\" is required.")
        sys.exit(1)

    LevelEditor(args.input).run()


if __name__ == "__main__":
    main()
