"""Moduile handling entities physics."""

import logging

import pygame

from vertex_velocity.particles import Dust
from vertex_velocity.utils import HIDE_PARTICLES

MAX_VERTICAL_VELOCITY = 80  # Maximum number of pixels per frame.
GRAVITY_ACCELERATION = 1  # Each frame, the player will accelerate down by this quantity.
JUMP_ACCELERATION = -17.2  # When the player jumps, it will accelerate up by this quantity.


class Entity:
    """Base class for all entities in the game."""

    def __init__(self, game, tilemap, eType, pos, size):
        """Initialize an entity.
        Args:
            game (Game): The game instance.
            tilemap (TileMap): The tilemap instance.
            eType (str): The type of the entity (e.g., "player", "brick", "spike").
            pos (tuple): The initial position of the entity (x, y).
            size (tuple): The size of the entity (width, height).
        """

        self.game = game
        self.tilemap = tilemap
        self.eType = eType
        self.pos = list(pos)
        self.size = size
        self.mask = pygame.mask.from_surface(self.game.assets[eType])

    @property
    def x(self):
        """Get the x-coordinate of the entity."""

        return self.pos[0]

    @property
    def y(self):
        """Get the y-coordinate of the entity."""

        return self.pos[1]

    @property
    def rect(self):
        """Get the pygame rectangle representing the entity's position and size."""

        return pygame.Rect(self.x, self.y, self.size[0], self.size[1])

    @property
    def center(self):
        """Get the center position of the entity."""

        return (self.x + self.size[0] // 2, self.y + self.size[1] // 2)

    def render(self, surface, scroll):
        """Render the entity on the screen.
        Args:
            surface (pygame.Surface): The surface to render the player on.
            scroll (list): The scroll offset for rendering.
        """

        surface.blit(self.game.assets[self.eType], (self.x - scroll[0], self.y - scroll[1]))


class AliveEntity:
    """Class managing the liveness traits of an entity."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.entityState = "alive"

    @property
    def isDying(self):
        """Check if the entity is in the dying state."""

        return self.entityState == "dying"

    @property
    def isDead(self):
        """Check if the entity is dead."""

        return self.entityState == "dead"

    def die(self):
        """Transition the entity to the dying state."""
        if not self.isDying and not self.isDead:
            self.entityState = "dying"

    def update(self):
        """Update the entity's position based on its velocity and handle collisions.
        Args:
            LRmovement (int): Horizontal movement input in pixels (left/right).
            TDmovement (int): Vertical movement input in pixels (up/down).
        """

        if self.y > self.game.SCREEN_HEIGHT:
            self.entityState = "dying"


class OpaqueEntity:
    """Class managing the colliding traits of an entity."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.velocity = [0, 0]
        self.collisions = {
            "up": False,
            "down": False,
            "left": False,
            "right": False
        }

    def getPossibleCollisions(self):
        """Handle the collisions with player.
        Returns:
            list: List of possible collisions with tiles.
        """

        ret = []

        # Iterate over the tiles around the player.
        for tileRelPos, tile in self.tilemap.tilesAroud(self.pos):
            # Check if the tile is solid.
            if self.tilemap.isTileSolid(tile):
                ret += [
                    {
                        "type":
                            "solid",  # Collision with a solid tile, prevents movement.
                        "bbox":
                            self.tilemap.tileBoundingBox(tile),
                        "rect":
                            pygame.Rect(
                                tile["pos"][0] * self.tilemap.tileSize,
                                tile["pos"][1] * self.tilemap.tileSize,
                                self.tilemap.tileSize,
                                self.tilemap.tileSize,
                            ),
                        "tilepos":
                            tile["pos"],
                        "relpos":
                            tileRelPos,
                    }
                ]
            # Check if the tile is deadly.
            elif self.tilemap.isTileDeadly(tile):
                self.tilemap.tileBoundingBox(tile)
                ret += [
                    {
                        "type":
                            "deadly",  # Collision with a deadly tile, will kill player.
                        "bbox":
                            self.tilemap.tileBoundingBox(tile),
                        "rect":
                            pygame.Rect(
                                tile["pos"][0] * self.tilemap.tileSize,
                                tile["pos"][1] * self.tilemap.tileSize,
                                self.tilemap.tileSize,
                                self.tilemap.tileSize,
                            ),
                        "tilepos":
                            tile["pos"],
                        "relpos":
                            tileRelPos,
                    }
                ]

        return ret

    def resetCollisions(self):
        """Reset the collisions."""

        self.tilemap.resetCollisions()
        self.collisions = {
            "up": False,
            "down": False,
            "left": False,
            "right": False
        }

    def computeCollisions(self, playerRect):
        """Compute adjustments correcting collisions with the player.
        Args:
            playerRect (pygame.Rect): The rectangle representing the player.
        Returns:
            list: List of adjustments needed to correct the collisions.
        Note:
            If the entity also inherits from AliveEntity, deadly collisions
            will set its state to 'dying' using self.die(). Otherwise, deadly
            collisions are logged and ignored.
        """

        adjustments = []

        # Compute list of nearby tiles that *could* collide with player once moved.
        collisions = self.getPossibleCollisions()

        for collision in collisions:
            # If tentative movement doesn't make the player collide with a tile, no need to handle it.
            playerOffset = (playerRect.x - collision["rect"].x, playerRect.y - collision["rect"].y)
            if not collision["bbox"].overlap(self.mask, playerOffset):
                continue

            # Render the collision for debugging purposes.
            self.tilemap.markCollision(collision["rect"])

            # If tile is deadly, kill the player.
            if collision["type"] == 'deadly':
                # Log the collision with a deadly tile.
                logging.debug(f"Player collided with a deadly tile at {collision['rect']} ({collision['relpos']}.")
                try:
                    self.die()
                    return []
                except AttributeError:
                    logging.debug(f"Deadly collision ignored (entity has no die() method): {self}")

            # If tile is not solid, no need to handle it.
            if collision["type"] == 'solid':
                # Compute the center of the colliding tile.
                collidingTileCenter = [
                    collision["rect"].x + collision["rect"].width // 2,
                    collision["rect"].y + collision["rect"].height // 2
                ]

                # Compute the difference between the player's center and the colliding tile's center.
                delta = [collidingTileCenter[0] - playerRect.centerx, collidingTileCenter[1] - playerRect.centery]
                # logging.debug(
                #     f"Player position when colliding with tile ({collision['tilepos']}): {self.pos}, delta: {delta}"
                # )

                # Calculate combined half-dimensions
                halfPlayerWidth = self.size[0] / 2.0  # Use float division
                halfPlayerHeight = self.size[1] / 2.0
                halfTileWidth = collision["rect"].width / 2.0
                halfTileHeight = collision["rect"].height / 2.0

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
                    push = penetrationX if delta[0] < 0 else -penetrationX
                    asix = 0
                else:
                    # Collision is vertical.
                    push = penetrationY if delta[1] < 0 else -penetrationY
                    asix = 1

                # Append the adjustment to the list.
                adjustments.append({
                    "axis": asix,
                    "priority": penetrationX + penetrationY,
                    "push": push,
                })

        adjustments.sort(key=lambda adj: adj['priority'], reverse=True)
        return adjustments

    def handleCollisions(self):
        """Handle the collisions with player.
        Returns:
            bool: True if a collision occurred, False otherwise.
        Note:
            If the entity also inherits from AliveEntity, deadly collisions
            will set its state to 'dying' using self.die(). Otherwise, deadly
            collisions are logged and ignored.
        """

        # Reset the collisions before checking.
        self.resetCollisions()

        # Prepare return value.
        collisionOccurred = False

        while True:
            # Get player's bounding box.
            playerRect = self.rect

            # Compute the adjustments needed to correct the collisions.
            adjustments = self.computeCollisions(playerRect)

            # If no adjustments are needed, break the loop.
            if not adjustments:
                break

            # Apply the adjustments to the player.
            adjustment = adjustments[0]

            # First, detect a collision with a solid tile arriving on the right will be deadly.
            if adjustment["axis"] == 0 and adjustment["push"] < 0:
                logging.debug(f"Entity collided with a solid tile at {self.rect} ({adjustment['push']}) on its right.")
                try:
                    self.die()
                    return True
                except AttributeError:
                    logging.warning(f"Deadly side collision ignored (entity has no die() method): {self}")

            self.pos[adjustment["axis"]] += int(adjustment["push"])

            # Mark that a collision occurred.
            collisionOccurred = True

            # Update collision state.
            if adjustment["axis"] == 0:
                if adjustment["push"] > 0:
                    self.collisions["left"] = True
                else:
                    self.collisions["right"] = True
            else:
                if adjustment["push"] > 0:
                    self.collisions["up"] = True
                else:
                    self.collisions["down"] = True

        return collisionOccurred

    def update(self):
        """Update the entity's position based on its velocity and handle collisions.
        Args:
            LRmovement (int): Horizontal movement input in pixels (left/right).
            TDmovement (int): Vertical movement input in pixels (up/down).
        """

        self.resetCollisions()
        self.handleCollisions()

        if self.collisions["down"] or self.collisions["up"]:
            self.velocity[1] = 0


class PhysicsEntity:
    """Class managing the physics traits of an entity."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.velocity = [0, 0]

    def update(self, LRmovement=0, TDmovement=0):
        """Update the entity's position based on its velocity and handle collisions.
        Args:
            LRmovement (int): Horizontal movement input in pixels (left/right).
            TDmovement (int): Vertical movement input in pixels (up/down).
        """

        frame_movement = [LRmovement + self.velocity[0], TDmovement + self.velocity[1]]
        self.pos = [self.x + frame_movement[0], self.y + frame_movement[1]]
        self.velocity[1] = min(MAX_VERTICAL_VELOCITY, self.velocity[1] + GRAVITY_ACCELERATION)


class Player(AliveEntity, OpaqueEntity, PhysicsEntity, Entity):
    """Class representing the player in the game."""

    def __init__(self, game, tilemap, pos, size, debugOptions=0):
        """Initialize the player.
        Args:
            game (Game): The game instance.
            tilemap (TileMap): The tilemap instance.
            pos (tuple): The initial position of the player (x, y).
            size (tuple): The size of the player (width, height).
            debugOptions (int): Debug options for rendering.
        """

        super().__init__(game, tilemap, "player", pos, size)
        self.movementDust = []
        self.deathDust = []
        self.debugOptions = debugOptions
        self.jumpCooldown = False

    def __repr__(self):
        return f"Player(pos={self.pos}, size={self.size}, velocity={self.velocity}, dust={len(self.movementDust)}, collisions={self.collisions}, entityState={self.entityState})"

    def update(self, jump=False):
        """Update player position.
        Args:
            jump (bool): Whether the player should jump.
        """

        # Check if the player is dead.
        if self.entityState != "alive":
            return

        if jump and not self.jumpCooldown:
            # If the jump key is pressed, jump.
            self.velocity[1] = JUMP_ACCELERATION
            self.jumpCooldown = True
            logging.debug(f"Player jumped at tick {self.game.currentTick} from position {self.pos}.")

        AliveEntity.update(self)
        OpaqueEntity.update(self)
        PhysicsEntity.update(self, LRmovement=8)

        if self.collisions["down"]:
            # If the player is on the ground, reset the jump cooldown.
            self.jumpCooldown = False

        # Add dust particles when the player is moving horizontally.
        if self.collisions["down"]:  # and LRmovement > 0:
            # Moving right, particles on the left side of the player.
            self.movementDust.append(Dust([self.x, self.y + self.size[1] - 5]))
        elif self.collisions["down"]:  # and LRmovement < 0:
            # Moving left, particles on the right side of the player.
            self.movementDust.append(Dust([self.x + self.size[0], self.y + self.size[1] - 5]))

        # Update the dust particles.
        for dust in self.movementDust:
            dust.update()
            if not dust.particles:
                self.movementDust.remove(dust)

    def render(self, surface, scroll):
        """Render the player on the screen.
        Args:
            surface (pygame.Surface): The surface to render the player on.
            scroll (list): The scroll offset for rendering.
        """

        # Check if the entity is dead.
        if self.entityState == "alive":
            super().render(surface, scroll)

            # Render the dust particles.
            for dust in self.movementDust:
                dust.render(surface, scroll)
        elif self.entityState == "dying":
            # If the entity is dead, render a death animation.
            self.renderDeathAnimation(surface, scroll)

    def renderDeathAnimation(self, surface, scroll):
        """Render the death animation.
        Args:
            surface (pygame.Surface): The surface to render the death animation on.
            scroll (list): The scroll offset for rendering.
        """

        self.movementDust = []

        if not self.deathDust:
            # Create dust particles at the player's position.
            for i in range(20):
                self.deathDust.append(Dust([self.x + self.size[0] // 2, self.y + self.size[1] // 2]))

        # Render the dust particles.
        for dust in self.deathDust:
            dust.update()
            if not dust.particles:
                self.deathDust.remove(dust)
                if not self.deathDust:
                    # If all dust particles are gone, set the entity state to dead.
                    self.entityState = "dead"
            else:
                dust.render(surface, scroll)
