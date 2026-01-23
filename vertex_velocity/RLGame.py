"Reinforcement Learning Game Environment playing Vertex Velocity."

import argparse
import json
import os
import sys
import pygame
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map

from vertex_velocity.game import Game
from vertex_velocity.neuralNetwork import NeuralNetworkPlayer, NeuralNetwork, Neuron, NeuronType, NeuronActivation
from vertex_velocity.utils import load_image, tint_image

NUM_PLAYERS = 1000  # Number of players to run, for training purposes.

# Global variables for worker processes
level_file = None
basePlayer = None


class RLGame(Game):
    def __init__(self, inputTilemap):
        """Initialize the RL game.
        Args:
            inputTilemap (str): The input tilemap file name.
        """
        super().__init__(inputTilemap)

        self.FPS = 60

        # Load the neuron visual assets.
        self.assets["airNeuron"] = load_image("air_neuron.png")
        self.assets["brickNeuron"] = load_image("brick_neuron.png")
        self.assets["spikeNeuron"] = load_image("spike_neuron.png")
        self.assets["airNeuronActivatedPresence"] = tint_image(self.assets["airNeuron"], (0, 255, 0))
        self.assets["brickNeuronActivatedPresence"] = tint_image(self.assets["brickNeuron"], (0, 255, 0))
        self.assets["spikeNeuronActivatedPresence"] = tint_image(self.assets["spikeNeuron"], (0, 255, 0))
        self.assets["airNeuronActivatedAbsence"] = tint_image(self.assets["airNeuron"], (255, 0, 0))
        self.assets["brickNeuronActivatedAbsence"] = tint_image(self.assets["brickNeuron"], (255, 0, 0))
        self.assets["spikeNeuronActivatedAbsence"] = tint_image(self.assets["spikeNeuron"], (255, 0, 0))

    def update(self):
        """Update the game.
        Returns:
            bool: True if the game should continue, False if the player is dead.
        """
        # Explicitely not scrolling vertically.
        self.scroll[0] += (self.player.rect.centerx - self.SCREEN_WIDTH / 2 - self.scroll[0]) / 10

        # Update player's position.
        self.player.update()

        # Check player death.
        if self.player.isDead:
            return False

        return True

    def run(self):
        """Run the game."""
        gameContinue = True
        while gameContinue:
            gameContinue = self.update()
            self.render()

            self.clock.tick(self.FPS)
            self.tickCount += 1


def _run_player(player_index):
    """Run a player and return its score and serialized data.
    
    This function is executed by worker processes.
    """
    global level_file, basePlayer

    # Initialize a new game instance for this worker
    game = RLGame(level_file)
    game.FPS = 600  # Speed up training by increasing FPS

    # Evolve a new player from the base
    # Note: basePlayer.evolve() creates a new NeuralNetworkPlayer.
    # We need to ensure the new player is attached to the *local* game instance,
    # not the one stored in basePlayer (which belongs to the parent process).

    # basePlayer.evolve() uses self.game to initialize the new player.
    # We must patch this temporarily or handle it.
    # Actually, NeuralNetworkPlayer.evolve() creates new NeuraNetworkPlayer(self.game, ...)
    # So the new player will share the parent's game reference if we aren't careful.
    # However, since we are likely forking, the memory is copy-on-write.
    # But the 'game' object in basePlayer is not the 'game' object we just created locally.

    # To fix this properly:
    # 1. Evolve the player (attached to whatever game context it had)
    # 2. Re-attach the evolved player to the local 'game' instance.

    evolved_player = basePlayer.evolve()
    evolved_player.game = game
    evolved_player.tilemap = game.tilemap

    # We also need to update the game reference in the neurons
    for nn in evolved_player.neuralNetworks:
        nn.game = game
        nn.tilemap = game.tilemap
        for neuron in nn.neurons:
            neuron.game = game
            neuron.tilemap = game.tilemap

    game.player = evolved_player
    game.run()

    return (game.player.score, game.player.serialize())


def main():
    global level_file, basePlayer

    parser = argparse.ArgumentParser(description="Vertex Velocity, now AI powered!")
    parser.add_argument("-l", "--level", type=str, help="Level file name")
    parser.add_argument("-i", "--input-player", type=str, help="Path to player JSON file to load")
    parser.add_argument("--train", action="store_true", help="Run in training mode")
    args = parser.parse_args()

    if not args.level:
        print("Error: \"-l/--level\" is required.")
        sys.exit(1)

    level_file = args.level

    # 1. Create a dummy game to initialize the base player (load assets, etc)
    #    We need this even in training mode to load/create the initial player structure.
    #    However, we must be careful not to init video mode if we are training
    #    AND we want to be headless, BUT RLGame.__init__ loads images which requires display init.

    if args.train:
        os.environ["SDL_VIDEODRIVER"] = "dummy"

    dummy_game = RLGame(args.level)

    # 2. Load or Create Base Player
    if args.input_player:
        try:
            with open(args.input_player, "r") as f:
                player_data = json.load(f)
                basePlayer = NeuralNetworkPlayer.from_dict(dummy_game, dummy_game.tilemap, player_data)
                print(f"Loaded player from {args.input_player}")
        except Exception as e:
            print(f"Error loading player: {e}")
            sys.exit(1)
    else:
        # Default starting player
        basePlayer = NeuralNetworkPlayer(
            dummy_game,
            dummy_game.tilemap,
            dummy_game.PLAYER_INIT_POS,
            dummy_game.PLAYER_SIZE,
            [
                NeuralNetwork(
                    dummy_game,
                    dummy_game.tilemap,
                    [
                        Neuron(
                            dummy_game,
                            dummy_game.tilemap,
                            NeuronType.AIR,
                            (400,
                             0),
                            NeuronActivation.PRESENCE,
                        ),
                        Neuron(
                            dummy_game,
                            dummy_game.tilemap,
                            NeuronType.BRICK,
                            (100,
                             100),
                            NeuronActivation.PRESENCE,
                        ),
                        Neuron(
                            dummy_game,
                            dummy_game.tilemap,
                            NeuronType.SPIKE,
                            (250,
                             200),
                            NeuronActivation.ABSENCE,
                        ),
                    ]
                )
            ],
        )

    if args.train:
        print(f"Starting training with {NUM_PLAYERS} players (Parallel)...")

        # Run players in parallel
        # process_map returns a list of results in order
        results = process_map(_run_player, range(NUM_PLAYERS), chunksize=1)

        # results is a list of (score, serialized_player_dict)

        # Find the best player
        best_score = -1
        best_player_data = None
        best_index = -1

        for i, (score, player_data) in enumerate(results):
            if score > best_score:
                best_score = score
                best_player_data = player_data
                best_index = i

        print(f"Highest score achieved: {best_score} by player {best_index + 1}")

        if best_player_data:
            with open("best_player.json", "w+") as f:
                json.dump(best_player_data, f)
            print("Saved best player to best_player.json")

    else:
        # Visual Replay Mode
        # We use the dummy_game created earlier, which has the window setup (unless dummy driver set, but we didn't set it for non-train)
        print("Starting Replay Mode...")
        dummy_game.player = basePlayer
        dummy_game.run()
        print(f"Final Score: {dummy_game.player.score}")


if __name__ == "__main__":
    main()
