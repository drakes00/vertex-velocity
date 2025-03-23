import pygame

from utils import SHOW_COORDINATES

NEIGHBORS_OFFSETS = [(0, 0), (-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1)]


class TileMap:
    """A class to represent the tilemap."""
    def __init__(self, game, tileSize=64, debugOptions=0):
        """Initialize the tilemap.
        Args:
            game (Game): The game instance.
            tileSize (int, optional): The size of the tiles. Defaults to 64.
            debugOptions (int bit vector, optional): The debug options (1 = show grid, 2 = show coordinates). Defaults to 0.
        """
        self.game = game
        self.tileSize = tileSize
        self.tilemap = {}
        self.debugOptions = debugOptions
        # self.offgridTiles = []

        for i in range(20):
            self.tilemap[f"10;{i}"] = {
                "type": "brick",
                "pos": (10,
                        i)
            }

        for i in range(1000):
            self.tilemap[f"{i};9"] = {
                "type": "brick",
                "pos": (i,
                        9)
            }
            if i % 5 == 0:
                self.tilemap[f"{i};8"] = {
                    "type": "triangle",
                    "pos": (i,
                            8)
                }

    def tilesAroud(self, pos):
        """Get the tiles around a position.
        Args:
            pos (tuple): The position to check from.
        Yields:
            dict: Tiles around the position.
        """
        tilePos = (int(pos[0] // self.tileSize), int(pos[1] // self.tileSize))
        for offset in NEIGHBORS_OFFSETS:
            tileToCheck = str(tilePos[0] + offset[0]) + ";" + str(tilePos[1] + offset[1])
            if tileToCheck in self.tilemap:
                yield self.tilemap[tileToCheck]

    def isTileSolid(self, tile):
        """Check if a tile is solid.
        Args:
            tile (dict): The tile to check.
        Returns:
            bool: True if the tile is solid, False otherwise.
        """
        return tile["type"] == "brick"

    def render(self, surface, scroll=[0, 0]):
        """Render the tilemap.
        Args:
            surface (pygame.Surface): The surface to render the tilemap on.
        """
        # for tile in self.offgridTiles:
        #     surface.blit(self.game.assets[tile["type"]], (tile["pos"][0] - scroll[0], tile["pos"][1] - scroll[1]))

        if self.debugOptions & SHOW_COORDINATES:
            # Prepare the font for writing debug messages on the screen.
            font = pygame.font.SysFont(None, 16)  # Choose a suitable font and size.

        for x in range(scroll[0] // self.tileSize, (scroll[0] + self.game.SCREEN_WIDTH) // self.tileSize + 1):
            for y in range(scroll[1] // self.tileSize, (scroll[1] + self.game.SCREEN_HEIGHT) // self.tileSize + 1):
                tileToCheck = f"{x};{y}"
                if tileToCheck in self.tilemap:
                    tile = self.tilemap[tileToCheck]
                    surface.blit(
                        self.game.assets[tile["type"]],
                        (tile["pos"][0] * self.tileSize - scroll[0],
                         tile["pos"][1] * self.tileSize - scroll[1])
                    )

                if self.debugOptions & SHOW_COORDINATES:
                    # Prepare coordinate text
                    coord_text = f"{x}, {y}"
                    text_surface = font.render(coord_text, True, (255, 255, 255))  # White text.
                    text_pos = (
                        x * self.tileSize - scroll[0] + 5,  # Offset so it's not at exact top-left.
                        y * self.tileSize - scroll[1] + 5
                    )

                    # Add a background for better readability
                    bg_rect = text_surface.get_rect(topleft=text_pos)
                    pygame.draw.rect(surface, (0, 0, 0), bg_rect)  # Black background.

                    # Draw the text over the tile.
                    surface.blit(text_surface, text_pos)
