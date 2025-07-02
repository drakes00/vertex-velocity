"""Tests for the tilemap module."""

import json
from unittest.mock import MagicMock

import pygame
from ward import test, fixture

from vertex_velocity.tilemap import TileMap, NEIGHBORS_OFFSETS

TILE_SIZE = 64


@fixture
def mock_game():
    """Fixture for a mock game object."""
    pygame.init()
    game = MagicMock()
    game.assets = {
        'brick': pygame.image.load("vertex_velocity/assets/images/brick.png"),
        'spike': pygame.image.load("vertex_velocity/assets/images/spike.png"),
    }
    game.SCREEN_WIDTH = 800
    game.SCREEN_HEIGHT = 600
    return game


@fixture
def tilemap(game=mock_game):
    """Fixture for a TileMap."""
    return TileMap(game, tileSize=TILE_SIZE)


@test("TileMap toJson and fromJson")
def test_01_json(tilemap=tilemap, game=mock_game):
    tilemap.addTile([1, 2], "brick")
    tilemap.addTile([3, 4], "spike")

    path = "/tmp/test_tilemap.json"
    tilemap.toJson(path)

    new_tilemap = TileMap.fromJson(game, path)

    assert new_tilemap.tileSize == tilemap.tileSize
    assert new_tilemap.tilemap == tilemap.tilemap


@test("TileMap add and remove tile")
def test_02_add_remove(tilemap=tilemap):
    pos = (5, 6)
    tilemap.addTile(pos, "brick")
    assert f"{pos[0]};{pos[1]}" in tilemap.tilemap
    assert tilemap.tilemap[f"{pos[0]};{pos[1]}"]["type"] == "brick"

    tilemap.removeTile(pos)
    assert f"{pos[0]};{pos[1]}" not in tilemap.tilemap


@test("TileMap getTileAt")
def test_03_get_tile(tilemap=tilemap):
    pos = (7, 8)
    tilemap.addTile(pos, "brick")

    tile = tilemap.getTileAt((pos[0] * TILE_SIZE, pos[1] * TILE_SIZE))
    assert tile is not None
    assert tile["type"] == "brick"

    non_existent_tile = tilemap.getTileAt((0, 0))
    assert non_existent_tile is None

    tile_out_of_bounds = tilemap.getTileAt((1000, 1000))
    assert tile_out_of_bounds is None

    tile_with_negative_coords_1 = tilemap.getTileAt((-TILE_SIZE, 0))
    tile_with_negative_coords_2 = tilemap.getTileAt((0, -TILE_SIZE))
    tile_with_negative_coords_3 = tilemap.getTileAt((-TILE_SIZE, -TILE_SIZE))
    assert tile_with_negative_coords_1 is None
    assert tile_with_negative_coords_2 is None
    assert tile_with_negative_coords_3 is None


@test("TileMap tilesAround comprehensive")
def test_04_tiles_around(tilemap=tilemap):
    center_pos = (5, 5)

    # Test with no tiles around
    tiles = list(tilemap.tilesAround((center_pos[0] * TILE_SIZE, center_pos[1] * TILE_SIZE)))
    assert not tiles

    # Test each neighbor offset individually
    for name, offset in NEIGHBORS_OFFSETS.items():
        tilemap.tilemap = {}  # Clear the map for each test
        tile_pos = list((center_pos[0] + offset[0], center_pos[1] + offset[1]))
        tilemap.addTile(tile_pos, "brick")

        tiles = list(tilemap.tilesAround((center_pos[0] * TILE_SIZE, center_pos[1] * TILE_SIZE)))

        assert len(tiles) == 1
        found_name, found_tile = tiles[0]
        assert found_name == name
        assert found_tile["pos"] == list(tile_pos)
        assert found_tile["type"] == "brick"

    # Test with a mix of tiles and empty spaces
    tilemap.tilemap = {}
    tilemap.addTile((center_pos[0] + 1, center_pos[1]), "brick")  # right
    tilemap.addTile((center_pos[0], center_pos[1] + 1), "spike")  # down
    tilemap.addTile((center_pos[0] - 1, center_pos[1] + 1), "brick")  # left-down

    tiles = list(tilemap.tilesAround((center_pos[0] * TILE_SIZE, center_pos[1] * TILE_SIZE)))
    assert len(tiles) == 3
    found_neighbors = {
        name: tile["type"]
        for name, tile in tiles
    }
    assert found_neighbors["right"] == "brick"
    assert found_neighbors["down"] == "spike"
    assert found_neighbors["left-down"] == "brick"
    assert "up" not in found_neighbors


@test("TileMap isTileSolid and isTileDeadly")
def test_05_solid_deadly(tilemap=tilemap):
    solid_tile = {
        "type": "brick"
    }
    deadly_tile = {
        "type": "spike"
    }
    other_tile = {
        "type": "air"
    }

    assert tilemap.isTileSolid(solid_tile)
    assert not tilemap.isTileSolid(deadly_tile)
    assert not tilemap.isTileSolid(other_tile)

    assert tilemap.isTileDeadly(deadly_tile)
    assert not tilemap.isTileDeadly(solid_tile)
    assert not tilemap.isTileDeadly(other_tile)


@test("TileMap tileBoundingBox")
def test_06_bounding_box(tilemap=tilemap, game=mock_game):
    brick_tile = {
        "type": "brick"
    }
    spike_tile = {
        "type": "spike"
    }

    brick_mask = tilemap.tileBoundingBox(brick_tile)
    spike_mask = tilemap.tileBoundingBox(spike_tile)

    assert isinstance(brick_mask, pygame.mask.Mask)
    assert isinstance(spike_mask, pygame.mask.Mask)

    assert brick_mask.get_size() == (64, 64)
    assert spike_mask.get_size() == (64, 64)

    # The brick is a full square, the spike is a triangle
    assert brick_mask.count() == 64 * 64
    assert spike_mask.count() < 64 * 64
    assert spike_mask.count() > 0


@test("TileMap reset and markCollision")
def test_07_mark_collisions(tilemap=tilemap):
    tilemap.markCollision(pygame.Rect(64, 128, 64, 64))
    assert (1, 2) in tilemap.collidingTiles

    tilemap.resetCollisions()
    assert not tilemap.collidingTiles
