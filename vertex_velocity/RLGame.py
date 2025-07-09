"""Reinforcement Learning Game Environment playing Vertex Velocity."""

import argparse

import copy
import pygame

from vertex_velocity.game import Game
from vertex_velocity.neuralNetwork import NeuralNetworkPlayer, NeuralNetwork, Neuron, NeuronType, NeuronActivation
from vertex_velocity.utils import load_image, tint_image


class RLGame(Game):

    def __init__(self, inputTilemap):
        """Initialize the RL game.
        Args:
            inputTilemap (str): The input tilemap file name.
        """
        super().__init__(inputTilemap)

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
        self.player.update(
            # forcedMovement=False,
            # LRmovement=5 * (self.movement["right"] - self.movement["left"]),
            # TDmovement=5 * (self.movement["down"] - self.movement["up"]),
            # gravity=False,
        )

        # Check player death.
        if self.player.isDead:
            return False

        return True

    def render(self):
        """Render neural network neurons."""
        self.screen.blit(self.assets["background"], (0, 0))

        renderScroll = [int(pos) for pos in self.scroll]
        self.tilemap.render(self.screen, renderScroll)
        self.player.render(self.screen, renderScroll)

        pygame.display.update()


def main():
    parser = argparse.ArgumentParser(description="Vertex Velocity, now AI powered!")
    parser.add_argument("-l", "--level", type=str, help="Level file name")
    args = parser.parse_args()

    if not args.level:
        print("Error: \"-l/--level\" is required.")
        sys.exit(1)

    RLGame(args.level).run()


if __name__ == "__main__":
    main()
