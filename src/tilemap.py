"""Tiles map for 2D tile-based games."""

import json
import pygame

from utils import SHOW_COORDINATES, SHOW_GRID, SHOW_COLLISION

NEIGHBORS_OFFSETS = {
    "right": (1,
              0),
    "down": (0,
             1),
    "left": (-1,
             0),
    "up": (0,
           -1),
    "right-down": (1,
                   1),
    "right-up": (1,
                 -1),
    "left-down": (-1,
                  1),
    "left-up": (-1,
                -1),
}  # Purposely sorting tiles from the closest to the farthest.


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
        self.collidingTiles = []

    def toJson(self, path):
        """Saves the tilemap in a JSON file.
        Args:
            path (str): Destination file name.
        """

        with open(path, "w+") as handle:
            json.dump(
                {
                    "tileSize": self.tileSize,
                    "tilemap": self.tilemap,
                },
                handle,
            )

    @classmethod
    def fromJson(cls, game, path):
        """Loads a tilemap from a JSON file.
        Args:
            game (Game): The game instance.
            path (str): Source file name.
        Returns:
            TileMap: The loaded tilemap.
        """

        with open(path, "r") as handle:
            data = json.load(handle)
            tilemap = cls(game, data["tileSize"])
            tilemap.tilemap = data["tilemap"]
            return tilemap

    @property
    def tilemap(self):
        """Get the tilemap."""

        return self._tilemap

    @tilemap.setter
    def tilemap(self, value):
        """Set the tilemap."""

        self._tilemap = value

    @property
    def debugOptions(self):
        """Get the debug options."""

        return self._debugOptions

    @debugOptions.setter
    def debugOptions(self, value):
        """Set the debug options."""

        self._debugOptions = value

    def addTile(self, pos, tileType):
        """Add a tile to the tilemap.
        Args:
            pos (tuple): The position of the tile.
            tileType (str): The type of the tile.
        """

        self.tilemap[f"{pos[0]};{pos[1]}"] = {
            "type": tileType,
            "pos": pos
        }

    def removeTile(self, pos):
        """Remove a tile from the tilemap.
        Args:
            pos (tuple): The position of the tile.
        """

        try:
            del self.tilemap[f"{pos[0]};{pos[1]}"]
        except KeyError:
            pass

    def getTileAt(self, pos):
        """Get the tile at a position.
        Args:
            pos (tuple): The position to check.
        Returns:
            dict: The tile at the position.
        """

        try:
            return self.tilemap[f"{pos[0]};{pos[1]}"]
        except KeyError:
            return None

    def tilesAroud(self, pos):
        """Get the tiles around a position.
        Args:
            pos (tuple): The position to check from.
        Yields:
            dict: Tiles around the position.
        """

        tilePos = (int(pos[0] // self.tileSize), int(pos[1] // self.tileSize))
        for name, offset in NEIGHBORS_OFFSETS.items():
            tileToCheck = str(tilePos[0] + offset[0]) + ";" + str(tilePos[1] + offset[1])
            if tileToCheck in self.tilemap:
                yield (name, self.tilemap[tileToCheck])

    def isTileSolid(self, tile):
        """Check if a tile is solid.
        Args:
            tile (dict): The tile to check.
        Returns:
            bool: True if the tile is solid, False otherwise.
        """

        return tile["type"] == "brick"

    def isTileDeadly(self, tile):
        """Check if a tile is deadly.
        Args:
            tile (dict): The tile to check.
        Returns:
            bool: True if the tile is deadly, False otherwise.
        """

        return tile["type"] == "spike"

    def tileBoundingBox(self, tile):
        """Get the bounding box of a tile.
        Args:
            tile (dict): The tile to check.
        Returns:
            pygame.Mask: The bounding box of the tile.
        """

        surface = self.game.assets[tile["type"]]
        return pygame.mask.from_surface(surface)

    def resetCollisions(self):
        """Reset the colliding tiles for debugging purposes."""

        self.collidingTiles = []

    def markCollision(self, collidingTile):
        """Mark a tile as colliding for debugging purposes.
        Args:
            collidingTile (Rect): The tile to mark as colliding.
        """

        tilePos = (int(collidingTile[0] // self.tileSize), int(collidingTile[1] // self.tileSize))
        if tilePos not in self.collidingTiles:
            self.collidingTiles.append(tilePos)

    def render(self, surface, scroll=[0, 0]):
        """Render the tilemap.
        Args:
            surface (pygame.Surface): The surface to render the tilemap on.
        """

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

                if self.debugOptions & SHOW_GRID:
                    pygame.draw.rect(
                        surface,
                        (255, 255, 255),  # White for grid lines.
                        (x * self.tileSize - scroll[0],
                         y * self.tileSize - scroll[1],
                         self.tileSize,
                         self.tileSize),
                        1,  # Thickness of the grid lines.
                    )

                if self.debugOptions & SHOW_COLLISION and (x, y) in self.collidingTiles:
                    pygame.draw.rect(
                        surface,
                        (255, 0, 0),  # Red for colliding tiles.
                        (x * self.tileSize - scroll[0],
                         y * self.tileSize - scroll[1],
                         self.tileSize,
                         self.tileSize),
                        10,  # Thickness of the grid lines.
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
