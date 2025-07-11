"""Reinforcement Learning Game Environment playing Vertex Velocity."""

from tqdm import tqdm

import argparse
import copy
import json
import pygame

from vertex_velocity.game import Game
from vertex_velocity.neuralNetwork import NeuralNetworkPlayer, NeuralNetwork, Neuron, NeuronType, NeuronActivation
from vertex_velocity.utils import load_image, tint_image


NUM_PLAYERS = 10 # Number of players to run, for training purposes.


class RLGame(Game):

    def __init__(self, inputTilemap):
        """Initialize the RL game.
        Args:
            inputTilemap (str): The input tilemap file name.
        """
        super().__init__(inputTilemap)

        self.FPS = 600

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

        # Initialize the player.
        self.player = NeuralNetworkPlayer(
            self,
            self.tilemap,
            self.PLAYER_INIT_POS,
            self.PLAYER_SIZE,
            [
                NeuralNetwork(
                    self, self.tilemap, [
                    Neuron(
                        self,
                        self.tilemap,
                        NeuronType.AIR,
                        (400, 0),
                        NeuronActivation.PRESENCE,
                    ),
                    Neuron(
                        self,
                        self.tilemap,
                        NeuronType.BRICK,
                        (100, 100),
                        NeuronActivation.PRESENCE,
                    ),
                    Neuron(
                        self,
                        self.tilemap,
                        NeuronType.SPIKE,
                        (250, 200),
                        NeuronActivation.ABSENCE,
                    ),
                ])
            ],
        )

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


def main():
    import os
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    parser = argparse.ArgumentParser(description="Vertex Velocity, now AI powered!")
    parser.add_argument("-l", "--level", type=str, help="Level file name")
    args = parser.parse_args()

    if not args.level:
        print("Error: \"-l/--level\" is required.")
        sys.exit(1)

    # Initialize the game with the given level.
    game = RLGame(args.level)
    basePlayer = NeuralNetworkPlayer(
        game,
        game.tilemap,
        game.PLAYER_INIT_POS,
        game.PLAYER_SIZE,
        [
            NeuralNetwork(
                game, game.tilemap, [
                Neuron(
                    game,
                    game.tilemap,
                    NeuronType.AIR,
                    (400, 0),
                    NeuronActivation.PRESENCE,
                ),
                Neuron(
                    game,
                    game.tilemap,
                    NeuronType.BRICK,
                    (100, 100),
                    NeuronActivation.PRESENCE,
                ),
                Neuron(
                    game,
                    game.tilemap,
                    NeuronType.SPIKE,
                    (250, 200),
                    NeuronActivation.ABSENCE,
                ),
            ])
        ],
    )

    highestScore = (-1, None, None)  # Tuple to store (score, player index, player JSON)
    for i in tqdm(range(NUM_PLAYERS), desc="Running players"):
        game.player = basePlayer.evolve()
        game.run()
        tqdm.write(f"Player {i + 1} finished with score: {game.player.score}")
        if game.player.score > highestScore[0]:
            highestScore = (game.player.score, i + 1, json.dumps(game.player.serialize()))
            tqdm.write(f"New highest score: {highestScore}")

    print(f"Highest score achieved: {highestScore[0]} by player {highestScore[1]}")

    # Save the best player.
    bestPlayer = highestScore[2]
    with open("best_player.json", "w+") as f:
        f.write(bestPlayer)

if __name__ == "__main__":
    main()
