import logging

import pygame

MAX_VERTICAL_VELOCITY = 10  # Maximum number of pixels per frame.
GRAVITY_ACCELERATION = 0.876  # Each frame, the player will accelerate down by this quantity.
JUMP_ACCELERATION = -8  # When the player jumps, it will accelerate up by this quantity.


class PhysicsEntity:
    def __init__(self, game, tilemap, eType, pos, size):
        self.game = game
        self.tilemap = tilemap
        self.eType = eType
        self.pos = list(pos)
        self.size = size
        self.velocity = [0, 0]
        self.collisions = {
            "up": False,
            "down": False,
            "left": False,
            "right": False
        }

    @property
    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])

    def handleCollisions(self):
        """Handle the collisions with player."""
        ret = []

        # Iterate over the tiles around the player.
        for tile in self.tilemap.tilesAroud(self.pos):
            # Check if the tile is solid.
            if self.tilemap.isTileSolid(tile):
                ret += [
                    (
                        'solid',  # Collision with a solid tile, prevents movement.
                        pygame.Rect(
                            tile["pos"][0] * self.tilemap.tileSize,
                            tile["pos"][1] * self.tilemap.tileSize,
                            self.tilemap.tileSize,
                            self.tilemap.tileSize
                        )
                    )
                ]

        return ret

    def update(self, LRmovement=0, jump=False):
        """Update player position."""
        # Reset the collisions.
        self.collisions = {
            "up": False,
            "down": False,
            "left": False,
            "right": False
        }

        # Compute list of nearby tiles that *could* collide with player once moved.
        collisions = self.handleCollisions()

        # Compute the movement for the frame using current velocity and input.
        frame_movement = (LRmovement + self.velocity[0], self.velocity[1])

        # Extremely important to first handle vertical movements, else current physics allows player to temporarily clip in the ground, handling horizontal collition with one of the ground tiles.
        # Up/down movements.
        self.pos[1] += frame_movement[1]  # Tentative movement.
        playerRect = self.rect
        for collision in collisions:
            # If tentative movement doesn't make the player collide with a tile, no need to handle it.
            if not playerRect.colliderect(collision[1]):
                continue

            if collision[0] == 'solid':
                # breakpoint()
                if frame_movement[1] > 0:  # Moving down.
                    # Set the bottom side of the player to the top side of the tile.
                    playerRect.bottom = collision[1].top
                    self.collisions["down"] = True
                elif frame_movement[1] < 0:  # Moving up.
                    # Set the top side of the player to the bottom side of the tile.
                    playerRect.top = collision[1].bottom
                    self.collisions["up"] = True
                self.pos[1] = playerRect.y

        # Left/right movements.
        self.pos[0] += frame_movement[0]  # Tentative movement.
        playerRect = self.rect
        for collision in collisions:
            # If tentative movement doesn't make the player collide with a tile, no need to handle it.
            if not playerRect.colliderect(collision[1]):
                continue

            if collision[0] == 'solid':
                if frame_movement[0] > 0:  # Moving right.
                    # Set the right side of the player to the left side of the tile.
                    playerRect.right = collision[1].left
                    self.collisions["right"] = True
                elif frame_movement[0] < 0:  # Moving left.
                    # Set the left side of the player to the right side of the tile.
                    playerRect.left = collision[1].right
                    self.collisions["left"] = True
                self.pos[0] = playerRect.x

        # Compute velocity for next frame.
        if self.collisions["down"] or self.collisions["up"]:
            # If the player is on the ground or hitting the ceiling, reset the vertical velocity.
            self.velocity[1] = 0
        elif jump:
            # If the jump key is pressed, jump.
            self.velocity[1] = JUMP_ACCELERATION
        else:
            # Apply gravity.
            self.velocity[1] = min(MAX_VERTICAL_VELOCITY, self.velocity[1] + GRAVITY_ACCELERATION)

        logging.debug(
            f"Player information: pos={self.pos}, velocity={self.velocity}, collisions={self.collisions}, jump={jump}"
        )

    def render(self, surface):
        surface.blit(self.game.assets[self.eType], self.pos)
