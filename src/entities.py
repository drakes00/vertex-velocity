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

    @property
    def center(self):
        return (self.pos[0] + self.size[0] // 2, self.pos[1] + self.size[1] // 2)

    def getPossibleCollisions(self):
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

    def resetCollisions(self):
        """Reset the collisions."""
        self.collisions = {
            "up": False,
            "down": False,
            "left": False,
            "right": False
        }

    def computeCollisions(self, playerRect):
        """Compute adjustments correcting collisions with the player."""

        # Compute list of nearby tiles that *could* collide with player once moved.
        collisions = self.getPossibleCollisions()

        adjustments = []

        for collision in collisions:
            # If tentative movement doesn't make the player collide with a tile, no need to handle it.
            if not playerRect.colliderect(collision[1]):
                continue

            # If tile is not solid, no need to handle it.
            if collision[0] == 'solid':
                # Compute the center of the colliding tile.
                collidingTileCenter = [
                    collision[1].x + collision[1].width // 2,
                    collision[1].y + collision[1].height // 2
                ]

                # Compute the difference between the player's center and the colliding tile's center.
                delta = [collidingTileCenter[0] - playerRect.centerx, collidingTileCenter[1] - playerRect.centery]

                # Calculate combined half-dimensions
                halfPlayerWidth = self.size[0] / 2.0  # Use float division
                halfPlayerHeight = self.size[1] / 2.0
                halfTileWidth = collision[1].width / 2.0
                halfTileHeight = collision[1].height / 2.0

                combinedHalfWidth = halfPlayerWidth + halfTileWidth
                combinedHalfHeight = halfPlayerHeight + halfTileHeight

                # Calculate penetration using absolute delta values
                absDeltaX = abs(delta[0])
                absDeltaY = abs(delta[1])

                penetrationX = combinedHalfWidth - absDeltaX
                penetrationY = combinedHalfHeight - absDeltaY

                # Clamp to zero in case of floating point issues or edge cases where colliderect is true but overlap is negligible/negative
                penetrationX = max(0.0, penetrationX)
                penetrationY = max(0.0, penetrationY)

                # Determine the direction of the collision.
                if penetrationX < penetrationY:
                    # Collision is horizontal.
                    pushX = penetrationX if delta[0] < 0 else -penetrationX
                    adjustments.append({
                        "axis": 0,
                        "priority": penetrationX + penetrationY,
                        "push": pushX,
                    })
                else:
                    # Collision is vertical.
                    pushY = penetrationY if delta[1] < 0 else -penetrationY
                    adjustments.append({
                        "axis": 1,
                        "priority": penetrationX + penetrationY,
                        "push": pushY,
                    })

        adjustments.sort(key=lambda adj: adj['priority'], reverse=True)
        return adjustments

    def handleCollisions(self):
        """Handle the collisions with player."""

        # Reset the collisions before checking.
        self.resetCollisions()

        # Prepare return value.
        collisionOccurred = False

        while True:
            # Get player's bounding box.
            playerRect = self.rect

            # Compute the adjustments needed to correct the collisions.
            adjustments = self.computeCollisions(playerRect)

            if not adjustments:
                break

            # Apply the adjustments to the player.
            adjustment = adjustments[0]
            self.pos[adjustment["axis"]] += int(adjustment["push"])

            # Mark that a collision occurred.
            collisionOccurred = True

        return collisionOccurred

    def update(self, LRmovement=0, jump=False):
        """Update player position."""

        # Compute the movement for the frame using current velocity and input.
        frame_movement = [LRmovement + self.velocity[0], self.velocity[1]]

        # Apply the movement to the player.
        self.pos = [
            self.pos[0] + frame_movement[0],
            self.pos[1] + frame_movement[1],
        ]

        # Handle collisions with the player.
        collisionOccured = self.handleCollisions()

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

    def render(self, surface, scroll):
        surface.blit(self.game.assets[self.eType], (self.pos[0] - scroll[0], self.pos[1] - scroll[1]))
