"""Utility functions for the game."""

import pygame

# Debug options for tilemap rendering
SHOW_GRID = 1
SHOW_COORDINATES = 2
SHOW_COLLISION = 4

# Debug options for player rendering
HIDE_PARTICLES = 1

BASE_PATH = "src/assets/images"


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
