"""Utility functions for the game."""

import pygame

# Debug options for tilemap rendering
SHOW_GRID = 1
SHOW_COORDINATES = 2
SHOW_COLLISION = 4

# Debug options for player rendering
HIDE_PARTICLES = 1

BASE_PATH = "vertex_velocity/assets/images"


def load_image(path):
    """Load an image from the assets folder."""
    img = pygame.image.load(f"{BASE_PATH}/{path}").convert()
    img.set_colorkey((0, 0, 0))
    return img


def tint_image(image, tint_color):
    """Tint a greyscale image with a given RGB color.
    
    Args:
        image (pygame.Surface): The original greyscale image.
        tint_color (tuple): The RGB color to apply (e.g., (0, 255, 0) for green).
        
    Returns:
        pygame.Surface: A new surface with the tint applied.
    """
    tinted_image = image.copy().convert_alpha()

    # Create a surface filled with the tint color, including opaque alpha
    tint_surface = pygame.Surface(tinted_image.get_size(), flags=pygame.SRCALPHA)
    tint_surface.fill(tint_color + (255,))  # RGBA: keep alpha 255

    # Multiply tint color with the greyscale image
    tinted_image.blit(tint_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    return tinted_image


def visualize_tilemap(tilemap):
    """Visualize a TileMap as ASCII art with coordinates."""
    if not tilemap.tilemap:
        print("Empty TileMap")
        return

    # Find bounds
    keys = list(tilemap.tilemap.keys())
    min_x = min_y = float('inf')
    max_x = max_y = float('-inf')
    for key in keys:
        x, y = map(int, key.split(';'))
        min_x, min_y = min(min_x, x), min(min_y, y)
        max_x, max_y = max(max_x, x), max(max_y, y)

    # Pad bounds slightly for context
    min_x, min_y = int(min_x) - 2, int(min_y) - 2
    max_x, max_y = int(max_x) + 2, int(max_y) + 2

    print(f"\nTileMap Visualization (Size: {tilemap.tileSize}px per tile)")
    
    # X axis labels
    # Tens
    header_tens = "     "
    for x in range(min_x, max_x + 1):
        if x % 10 == 0:
            header_tens += str(abs(x) // 10)[-1]
        else:
            header_tens += " "
    print(header_tens)
    
    # Units
    header_units = "     "
    for x in range(min_x, max_x + 1):
        header_units += str(abs(x) % 10)
    print(header_units)
    
    # Separator
    print("     " + "-" * (max_x - min_x + 1))

    # Grid rows
    for y in range(min_y, max_y + 1):
        line = f"{y:3} |"
        for x in range(min_x, max_x + 1):
            # Check for tile at this coordinate
            tile = tilemap.getTileAt((x * tilemap.tileSize + 1, y * tilemap.tileSize + 1))
            if tile:
                if tile['type'] == 'brick':
                    line += "#"
                elif tile['type'] == 'spike':
                    line += "^"
                else:
                    line += "?"
            else:
                line += "."
        print(line)
    print("     " + "-" * (max_x - min_x + 1) + "\n")
