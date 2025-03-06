import pygame

BASE_PATH = "assets/images"


def load_image(path):
    """Load an image from the assets folder."""
    img = pygame.image.load(f"{BASE_PATH}/{path}").convert()
    img.set_colorkey((0, 0, 0))
    return img
