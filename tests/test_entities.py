"""Tests for the entities module."""

from unittest.mock import MagicMock
from ward import test, fixture

import pygame

from vertex_velocity import entities
from vertex_velocity.tilemap import TileMap

TILE_SIZE = 64  # Assuming a tile size of 64 pixels


@fixture
def fixt_game():
    """Fixture for a mock game object."""
    pygame.init()
    game = MagicMock()
    game.assets = {
        'player': pygame.Surface((TILE_SIZE, TILE_SIZE)),
        'brick': pygame.Surface((TILE_SIZE, TILE_SIZE)),
        'spike': pygame.Surface((TILE_SIZE, TILE_SIZE)),
    }
    game.SCREEN_HEIGHT = 600
    game.currentTick = 0
    return game


@fixture
def fixt_tilemap(game=fixt_game):
    """Fixture for a real TileMap, used as a testing ground."""
    tilemap = TileMap(game, tileSize=TILE_SIZE)
    # Create a floor
    for i in range(15):
        tilemap.addTile((i, 10), "brick")
    # Create a wall on the right
    for i in range(10):
        tilemap.addTile((14, i), "brick")
    # Create a ceiling
    for i in range(15):
        tilemap.addTile((i, 0), "brick")
    return tilemap


@fixture
def fixt_entity(game=fixt_game, tilemap=fixt_tilemap):
    """Fixture for a basic Entity."""
    return entities.Entity(game, tilemap, 'player', (0, 0), (TILE_SIZE, TILE_SIZE))


class TestAliveEntity(entities.AliveEntity, entities.Entity):
    """A concrete, testable entity that has liveness."""

    def __init__(self, game, tilemap, eType, pos, size):
        super().__init__(game, tilemap, eType, pos, size)


@fixture
def alive_entity():
    """Fixture for an AliveEntity."""
    return TestAliveEntity(fixt_game(), fixt_tilemap(), 'player', (0, 0), (TILE_SIZE, TILE_SIZE))


class TestOpaqueEntity(entities.OpaqueEntity, entities.Entity):
    """A concrete, testable entity that has collision and liveness."""

    def __init__(self, game, tilemap, eType, pos, size):
        super().__init__(game, tilemap, eType, pos, size)

    def update(self):
        """Override update to handle collisions."""
        entities.OpaqueEntity.update(self)


class TestCollisionEntity(entities.OpaqueEntity, entities.PhysicsEntity, entities.Entity):
    """A concrete, testable entity that has collision and liveness."""

    def __init__(self, game, tilemap, eType, pos, size):
        super().__init__(game, tilemap, eType, pos, size)

    def update(self, LRmovement=0, TDmovement=0):
        """Override update to simulate physics and handle collisions."""
        entities.PhysicsEntity.update(self, LRmovement, TDmovement)
        entities.OpaqueEntity.update(self)


@fixture
def collision_entity(game=fixt_game, tilemap=fixt_tilemap):
    """Fixture for a test entity for collision scenarios."""
    # Initial position is in the air, away from walls
    return [
        TestOpaqueEntity(
            game,
            tilemap,
            "player",
            (0, 0),
            (TILE_SIZE, TILE_SIZE),
        ),
        TestCollisionEntity(
            game,
            tilemap,
            "player",
            (0, 0),
            (TILE_SIZE, TILE_SIZE),
        )
    ]


@fixture
def player(game=fixt_game, tilemap=fixt_tilemap):
    """Fixture for a Player."""
    return entities.Player(game, tilemap, (0, 0), (TILE_SIZE, TILE_SIZE))


@test("Entity initialization")
def test_01_entity_init(entity=fixt_entity, game=fixt_game, tilemap=fixt_tilemap):
    """Entity initialization"""
    assert entity.eType == 'player'
    assert entity.pos == [0, 0]
    assert entity.size == (TILE_SIZE, TILE_SIZE)
    assert entity.game is game
    assert entity.tilemap is tilemap


@test("Entity properties")
def test_02_entity_properties(entity=fixt_entity):
    """Entity properties"""
    entity.pos = [100, 200]
    assert entity.x == 100
    assert entity.y == 200
    assert entity.rect == pygame.Rect(100, 200, TILE_SIZE, TILE_SIZE)
    assert entity.center == (100 + TILE_SIZE//2, 200 + TILE_SIZE//2)


@test("Entity render")
def test_03_entity_render(entity=fixt_entity, game=fixt_game):
    """Entity render"""
    surface = MagicMock()
    scroll = [TILE_SIZE, TILE_SIZE]
    entity.pos = [100, 200]
    entity.render(surface, scroll)
    surface.blit.assert_called_once_with(game.assets['player'], (100 - TILE_SIZE, 200 - TILE_SIZE))


@test("AliveEntity initial state")
def test_04_alive_init(entity=alive_entity):
    """AliveEntity initial state"""
    assert entity.entityState == "alive"
    assert not entity.isDying
    assert not entity.isDead


@test("AliveEntity die")
def test_05_alive_die(entity=alive_entity):
    """AliveEntity die"""
    entity.die()
    assert entity.entityState == "dying"
    assert entity.isDying
    assert not entity.isDead


@test("AliveEntity die idempotent")
def test_06_alive_die_idempotent(entity=alive_entity):
    """AliveEntity die idempotent"""
    entity.die()
    entity.die()
    assert entity.entityState == "dying"


@test("AliveEntity update dying when offscreen")
def test_07_alive_die_offscreen(entity=alive_entity, game=fixt_game):
    """AliveEntity update dying when offscreen"""
    entity.pos[1] = game.SCREEN_HEIGHT
    entity.update()
    assert entity.entityState == "alive"

    entity.pos[1] = game.SCREEN_HEIGHT + 1
    entity.update()
    assert entity.entityState == "dying"


@test("Collision: Entity lands on the ground")
def test_08_collision_ground(entity=collision_entity):
    """Collision: Entity lands on the ground"""
    opaque_entity, physics_entity = entity

    # First test with OpaqueEntity
    opaque_entity.pos = [4 * TILE_SIZE, 9 * TILE_SIZE]  # Positioned right above the floor
    opaque_entity.resetCollisions()  # Reset collisions before testing
    collided = opaque_entity.handleCollisions()
    assert not collided  # Should not collide yet
    assert not opaque_entity.collisions["up"]
    assert not opaque_entity.collisions["down"]
    assert not opaque_entity.collisions["left"]
    assert not opaque_entity.collisions["right"]

    opaque_entity.pos = [4 * TILE_SIZE, 9 * TILE_SIZE]  # Positioned right above the floor
    opaque_entity.pos[1] += 1  # Move down by 1px to touch the floor
    opaque_entity.resetCollisions()
    collided = opaque_entity.handleCollisions()
    assert collided
    assert opaque_entity.collisions["down"]
    assert not opaque_entity.collisions["up"]
    assert not opaque_entity.collisions["left"]
    assert not opaque_entity.collisions["right"]
    assert opaque_entity.pos[1] == 9 * TILE_SIZE  # Should be pushed back up

    # Now test with CollisionEntity affected by physics
    physics_entity.pos = [4 * TILE_SIZE, 9 * TILE_SIZE]  # Positioned right above the floor
    physics_entity.resetCollisions()
    collided = physics_entity.handleCollisions()
    assert not collided  # Should not collide yet
    assert not physics_entity.collisions["up"]
    assert not physics_entity.collisions["down"]
    assert not physics_entity.collisions["left"]
    assert not physics_entity.collisions["right"]

    # Update entity state (should change position due to physics, but not collide yet)
    # Purposefully not calling `physics_entity.update()` here to only simulate
    # physics and not collisions.
    entities.PhysicsEntity.update(physics_entity)
    # Now check for collisions to assert the return value.
    physics_entity.resetCollisions()
    collided = physics_entity.handleCollisions()
    assert collided
    assert physics_entity.collisions["down"]
    assert not physics_entity.collisions["up"]
    assert not physics_entity.collisions["left"]
    assert not physics_entity.collisions["right"]
    assert physics_entity.velocity[1] != 0  # Should still be moving down since we didn't call update
    assert physics_entity.pos[1] == 9 * TILE_SIZE  # Should be pushed back up

    physics_entity.pos = [4 * TILE_SIZE, 9 * TILE_SIZE]  # Positioned right above the floor
    physics_entity.resetCollisions()
    physics_entity.update()  # Update entity state (should change position due to physics AND collide)
    assert physics_entity.collisions["down"]
    assert not physics_entity.collisions["up"]
    assert not physics_entity.collisions["left"]
    assert not physics_entity.collisions["right"]
    assert physics_entity.velocity[1] == 0  # Should stop moving down
    assert physics_entity.pos[1] == 9 * TILE_SIZE  # Should be pushed back up


@test("Collision: Entity hits the ceiling")
def test_09_collision_ceiling(entity=collision_entity):
    """Collision: Entity hits the ceiling"""
    opaque_entity, physics_entity = entity

    # First test with OpaqueEntity
    opaque_entity.pos = [4 * TILE_SIZE, 11 * TILE_SIZE]  # Positioned right under the ceiling
    opaque_entity.resetCollisions()
    collided = opaque_entity.handleCollisions()
    assert not collided  # Should not collide yet
    assert not opaque_entity.collisions["up"]
    assert not opaque_entity.collisions["down"]
    assert not opaque_entity.collisions["left"]
    assert not opaque_entity.collisions["right"]

    opaque_entity.pos = [4 * TILE_SIZE, 11 * TILE_SIZE]  # Positioned right under the ceiling
    opaque_entity.pos[1] -= 1  # Move up by 1px to touch the ceiling
    opaque_entity.resetCollisions()
    collided = opaque_entity.handleCollisions()
    assert collided
    assert opaque_entity.collisions["up"]
    assert not opaque_entity.collisions["down"]
    assert not opaque_entity.collisions["left"]
    assert not opaque_entity.collisions["right"]
    assert opaque_entity.pos[1] == 11 * TILE_SIZE  # Should be pushed back down

    # Now test with CollisionEntity affected by physics
    physics_entity.pos = [4 * TILE_SIZE, 11 * TILE_SIZE]  # Positioned right under the ceiling
    physics_entity.velocity[1] = -5  # Simulate upward movement
    physics_entity.resetCollisions()
    collided = physics_entity.handleCollisions()
    assert not collided  # Should not collide yet
    assert not physics_entity.collisions["up"]
    assert not physics_entity.collisions["down"]
    assert not physics_entity.collisions["left"]
    assert not physics_entity.collisions["right"]

    # Update entity state (should change position due to physics, but not collide yet)
    # Purposefully not calling `physics_entity.update()` here to only simulate
    # physics and not collisions.
    entities.PhysicsEntity.update(physics_entity)
    # Now check for collisions to assert the return value.
    physics_entity.resetCollisions()
    collided = physics_entity.handleCollisions()
    assert collided
    assert physics_entity.collisions["up"]
    assert not physics_entity.collisions["down"]
    assert not physics_entity.collisions["left"]
    assert not physics_entity.collisions["right"]
    assert physics_entity.velocity[1] != 0  # Should still be moving down since we didn't call update
    assert physics_entity.pos[1] == 11 * TILE_SIZE  # Should be pushed back down

    physics_entity.pos = [4 * TILE_SIZE, 11 * TILE_SIZE]  # Positioned right under the ceiling
    physics_entity.resetCollisions()
    physics_entity.update()  # Update entity state (should change position due to physics AND collide)
    assert physics_entity.collisions["up"]
    assert not physics_entity.collisions["down"]
    assert not physics_entity.collisions["left"]
    assert not physics_entity.collisions["right"]
    assert physics_entity.velocity[1] == 0  # Should stop moving up
    assert physics_entity.pos[1] == 11 * TILE_SIZE  # Should be pushed back down


@test("Collision: Entity hits a wall (deadly)")
def test_10_collision_wall(entity=collision_entity):
    """Collision: Entity hits a wall (deadly)"""
    opaque_entity, physics_entity = entity

    # First test with OpaqueEntity
    opaque_entity.pos = [13 * TILE_SIZE, 3 * TILE_SIZE]  # Positioned 1px to the left of the wall (tile 14, row 5)
    opaque_entity.die = MagicMock()
    opaque_entity.resetCollisions()
    collided = opaque_entity.handleCollisions()
    assert not collided
    assert not opaque_entity.collisions["up"]
    assert not opaque_entity.collisions["down"]
    assert not opaque_entity.collisions["left"]
    assert not opaque_entity.collisions["right"]

    opaque_entity.pos[0] += 1  # Move right by 1px to touch the wall
    opaque_entity.resetCollisions()
    collided = opaque_entity.handleCollisions()
    assert collided
    assert opaque_entity.collisions["right"]
    assert not opaque_entity.collisions["up"]
    assert not opaque_entity.collisions["down"]
    assert not opaque_entity.collisions["left"]
    opaque_entity.die.assert_called_once()

    # Now test with CollisionEntity affected by physics
    physics_entity.pos = [13 * TILE_SIZE, 3 * TILE_SIZE]  # Positioned 1px to the left of the wall
    physics_entity.velocity[0] = 5  # Simulate rightward movement
    physics_entity.die = MagicMock()
    physics_entity.resetCollisions()
    collided = physics_entity.handleCollisions()
    assert not collided
    assert not physics_entity.collisions["up"]
    assert not physics_entity.collisions["down"]
    assert not physics_entity.collisions["left"]
    assert not physics_entity.collisions["right"]

    physics_entity.pos = [13 * TILE_SIZE, 3 * TILE_SIZE]  # Positioned 1px to the left of the wall
    physics_entity.velocity[0] = 5  # Simulate rightward movement
    physics_entity.die = MagicMock()
    entities.PhysicsEntity.update(physics_entity)
    physics_entity.resetCollisions()
    collided = physics_entity.handleCollisions()
    assert collided
    assert physics_entity.collisions["right"]
    assert not physics_entity.collisions["up"]
    assert not physics_entity.collisions["down"]
    assert not physics_entity.collisions["left"]
    physics_entity.die.assert_called_once()

    physics_entity.pos = [13 * TILE_SIZE, 3 * TILE_SIZE]  # Positioned 1px to the left of the wall
    physics_entity.die = MagicMock()
    entities.PhysicsEntity.update(
        physics_entity, LRmovement=5
    )  # Update entity state (should change position due to physics)
    physics_entity.resetCollisions()
    collided = physics_entity.handleCollisions()
    assert collided
    assert physics_entity.collisions["right"]
    assert not physics_entity.collisions["up"]
    assert not physics_entity.collisions["down"]
    assert not physics_entity.collisions["left"]
    physics_entity.die.assert_called_once()

    physics_entity.pos = [13 * TILE_SIZE, 3 * TILE_SIZE]  # Positioned 1px to the left of the wall
    physics_entity.die = MagicMock()
    physics_entity.resetCollisions()
    physics_entity.update(LRmovement=5)  # Update entity state (should change position due to physics AND collide)
    assert physics_entity.collisions["right"]
    assert not physics_entity.collisions["up"]
    assert not physics_entity.collisions["down"]
    assert not physics_entity.collisions["left"]
    physics_entity.die.assert_called_once()


@test("Collision: Entity starts inside a floor tile")
def test_11_collision_inside_floor(entity=collision_entity):
    """Collision: Entity starts inside a floor tile"""
    opaque_entity, physics_entity = entity
    # First test with OpaqueEntity
    opaque_entity.pos = [4 * TILE_SIZE, 9*TILE_SIZE + 1]  # Clipping 1px into the floor (tile 9, row 10)
    opaque_entity.resetCollisions()
    collided = opaque_entity.handleCollisions()
    assert collided
    assert opaque_entity.collisions["down"]
    assert not opaque_entity.collisions["up"]
    assert not opaque_entity.collisions["left"]
    assert not opaque_entity.collisions["right"]
    assert opaque_entity.pos[1] == 9 * TILE_SIZE  # Should be pushed out to the top of the tile

    # Now test with CollisionEntity affected by physics
    physics_entity.pos = [4 * TILE_SIZE, 9*TILE_SIZE + 1]  # Clipping 1px into the floor
    # Update entity state (should change position due to physics, but not collide yet)
    # Purposefully not calling `physics_entity.update()` here to only simulate
    # physics and not collisions.
    entities.PhysicsEntity.update(physics_entity)
    # Now check for collisions to assert the return value.
    physics_entity.resetCollisions()
    collided = physics_entity.handleCollisions()
    assert collided
    assert physics_entity.collisions["down"]
    assert not physics_entity.collisions["up"]
    assert not physics_entity.collisions["left"]
    assert not physics_entity.collisions["right"]
    assert physics_entity.pos[1] == 9 * TILE_SIZE  # Should be pushed out to the top of the tile

    # Now test with CollisionEntity affected by physics
    physics_entity.pos = [4 * TILE_SIZE, 9*TILE_SIZE + 1]  # Clipping 1px into the floor
    physics_entity.resetCollisions()
    physics_entity.update()  # Update entity state (should change position due to physics AND collide)
    assert physics_entity.collisions["down"]
    assert not physics_entity.collisions["up"]
    assert not physics_entity.collisions["left"]
    assert not physics_entity.collisions["right"]
    assert physics_entity.pos[1] == 9 * TILE_SIZE  # Should be pushed out to the top of the tile


@test("Collision: Entity on seam between two blocks")
def test_12_collision_seam(entity=collision_entity):
    """Collision: Entity on seam between two blocks"""
    opaque_entity, physics_entity = entity
    # Position the entity so it stands on the seam of tiles (4, 10) and (5, 10)
    # Tile size is 64. Player width is 64.
    # Tile 4 ends at 4 * 64 + 64 = 3*TILE_SIZE
    # Tile 5 starts at 5 * 64 = 3*TILE_SIZE
    # First test with OpaqueEntity
    opaque_entity.pos = [4.5 * TILE_SIZE, 9 * TILE_SIZE]  # Centered on the seam, right above the ground
    opaque_entity.resetCollisions()
    collided = opaque_entity.handleCollisions()
    assert not collided
    assert not opaque_entity.collisions["up"]
    assert not opaque_entity.collisions["down"]
    assert not opaque_entity.collisions["left"]
    assert not opaque_entity.collisions["right"]

    opaque_entity.pos[1] += 1  # Move down to touch the ground
    opaque_entity.resetCollisions()
    collided = opaque_entity.handleCollisions()
    assert collided
    assert opaque_entity.collisions["down"]
    assert not opaque_entity.collisions["up"]
    assert not opaque_entity.collisions["left"]
    assert not opaque_entity.collisions["right"]
    assert opaque_entity.pos[1] == 9 * TILE_SIZE  # Pushed back up

    # Now test with CollisionEntity affected by physics
    physics_entity.pos = [4.5 * TILE_SIZE, 9 * TILE_SIZE]  # Centered on the seam, right above the ground
    physics_entity.resetCollisions()
    collided = physics_entity.handleCollisions()
    assert not collided
    assert not physics_entity.collisions["up"]
    assert not physics_entity.collisions["down"]
    assert not physics_entity.collisions["left"]
    assert not physics_entity.collisions["right"]

    physics_entity.pos = [4.5 * TILE_SIZE, 9 * TILE_SIZE]  # Centered on the seam, right above the ground
    # Update entity state (should change position due to physics, but not collide yet)
    # Purposefully not calling `physics_entity.update()` here to only simulate
    # physics and not collisions.
    entities.PhysicsEntity.update(physics_entity)
    # Now check for collisions to assert the return value.
    physics_entity.resetCollisions()
    collided = physics_entity.handleCollisions()
    assert collided
    assert physics_entity.collisions["down"]
    assert not physics_entity.collisions["up"]
    assert not physics_entity.collisions["left"]
    assert not physics_entity.collisions["right"]
    assert physics_entity.pos[1] == 9 * TILE_SIZE  # Pushed back up

    # Now test with CollisionEntity affected by physics
    physics_entity.pos = [4.5 * TILE_SIZE, 9 * TILE_SIZE]  # Centered on the seam, right above the ground
    physics_entity.resetCollisions()
    physics_entity.update()  # Update entity state (should change position due to physics AND collide)
    assert physics_entity.collisions["down"]
    assert not physics_entity.collisions["up"]
    assert not physics_entity.collisions["left"]
    assert not physics_entity.collisions["right"]
    assert physics_entity.pos[1] == 9 * TILE_SIZE  # Should be pushed out to the top of the tile


@test("Collision: Entity on seam, slightly off-center")
def test_13_collision_seam_off_center(entity=collision_entity):
    """Collision: Entity on seam, slightly off-center"""
    opaque_entity, physics_entity = entity
    # Positioned more over the left tile (4, 10)
    # First test with OpaqueEntity
    opaque_entity.pos = [
        4.5*TILE_SIZE - 10, 9 * TILE_SIZE
    ]  # Just a little off-center on the seam, right above the ground
    opaque_entity.resetCollisions()
    collided = opaque_entity.handleCollisions()
    assert not collided
    assert not opaque_entity.collisions["up"]
    assert not opaque_entity.collisions["down"]
    assert not opaque_entity.collisions["left"]
    assert not opaque_entity.collisions["right"]

    opaque_entity.pos[1] += 1
    opaque_entity.resetCollisions()
    collided = opaque_entity.handleCollisions()
    assert collided
    assert opaque_entity.collisions["down"]
    assert not opaque_entity.collisions["up"]
    assert not opaque_entity.collisions["left"]
    assert not opaque_entity.collisions["right"]
    assert opaque_entity.pos[1] == 9 * TILE_SIZE

    # Now test with CollisionEntity affected by physics
    physics_entity.pos = [
        4.5*TILE_SIZE - 10, 9 * TILE_SIZE
    ]  # Just a little off-center on the seam, right above the ground
    physics_entity.resetCollisions()
    collided = physics_entity.handleCollisions()
    assert not collided
    assert not physics_entity.collisions["up"]
    assert not physics_entity.collisions["down"]
    assert not physics_entity.collisions["left"]
    assert not physics_entity.collisions["right"]

    physics_entity.pos = [
        4.5*TILE_SIZE - 10, 9 * TILE_SIZE
    ]  # Just a little off-center on the seam, right above the ground
    # Update entity state (should change position due to physics, but not collide yet)
    # Purposefully not calling `physics_entity.update()` here to only simulate
    # physics and not collisions.
    entities.PhysicsEntity.update(physics_entity)
    # Now check for collisions to assert the return value.
    physics_entity.resetCollisions()
    collided = physics_entity.handleCollisions()
    assert collided
    assert physics_entity.collisions["down"]
    assert not physics_entity.collisions["up"]
    assert not physics_entity.collisions["left"]
    assert not physics_entity.collisions["right"]
    assert physics_entity.pos[1] == 9 * TILE_SIZE  # Pushed back up

    # Now test with CollisionEntity affected by physics
    physics_entity.pos = [
        4.5*TILE_SIZE - 10, 9 * TILE_SIZE
    ]  # Just a little off-center on the seam, right above the ground
    physics_entity.resetCollisions()
    physics_entity.update()  # Update entity state (should change position due to physics AND collide)
    assert physics_entity.collisions["down"]
    assert not physics_entity.collisions["up"]
    assert not physics_entity.collisions["left"]
    assert not physics_entity.collisions["right"]
    assert physics_entity.pos[1] == 9 * TILE_SIZE  # Should be pushed out to the top of the tile


# @test("PhysicsEntity update with horizontal movement")
# def _(entity=physics_entity):
#     entity.update(LRmovement=5)
#     assert entity.pos == [105, 201]
#     assert entity.velocity == [0, 1]
#
#
# @test("PhysicsEntity update with vertical movement")
# def _(entity=physics_entity):
#     entity.update(TDmovement=-10)
#     assert entity.pos == [100, 191]
#     assert entity.velocity == [0, 1]
#
#
# @test("PhysicsEntity max vertical velocity")
# def _(entity=physics_entity):
#     entity.velocity[1] = entities.MAX_VERTICAL_VELOCITY
#     entity.update()
#     assert entity.velocity[1] == entities.MAX_VERTICAL_VELOCITY
#
#
# @test("Player initialization")
# def _(player=player, game=fixt_game, tilemap=fixt_tilemap):
#     assert player.eType == 'player'
#     assert player.pos == [100, 200]
#     assert player.size == (10, 20)
#     assert player.game is game
#     assert player.tilemap is tilemap
#     assert player.entityState == "alive"
#
#
# @test("Player jump")
# def _(player=player):
#     player.update(jump=True)
#     assert player.velocity[1] == entities.JUMP_ACCELERATION
#     assert player.jumpCooldown
#
#
# @test("Player no double jump")
# def _(player=player):
#     player.update(jump=True)
#     player.update(jump=True)
#     assert player.velocity[1] != 2 * entities.JUMP_ACCELERATION
#
#
# @test("Player jump cooldown reset")
# def _(player=player):
#     player.update(jump=True)
#     player.collisions["down"] = True
#     player.update()
#     assert not player.jumpCooldown
