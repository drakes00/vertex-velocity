NEIGHBORS_OFFSETS = [(0, 0), (-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1)]


class TileMap:
    """A class to represent the tilemap."""
    def __init__(self, game, tileSize=64):
        """Initialize the tilemap.
        Args:
            game (Game): The game instance.
            tileSize (int, optional): The size of the tiles. Defaults to 64.
        """
        self.game = game
        self.tileSize = tileSize
        self.tilemap = {}
        self.offgridTiles = []

        for i in range(10):
            self.tilemap[f"{i};7"] = {
                "type": "brick",
                "pos": (i,
                        7)
            }
        self.tilemap["0;6"] = {
            "type": "brick",
            "pos": (0,
                    6)
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

    def render(self, surface):
        """Render the tilemap.
        Args:
            surface (pygame.Surface): The surface to render the tilemap on.
        """
        for tile in self.offgridTiles:
            surface.blit(self.game.assets[tile["type"]], tile["pos"])

        for loc in self.tilemap:
            tile = self.tilemap[loc]
            surface.blit(
                self.game.assets[tile["type"]],
                (tile["pos"][0] * self.tileSize,
                 tile["pos"][1] * self.tileSize)
            )
