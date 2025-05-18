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
