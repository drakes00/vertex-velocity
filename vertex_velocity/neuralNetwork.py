"""Module defining neural network classes and functions."""

from enum import Enum

import logging

logging.basicConfig(level=logging.DEBUG)
import pygame
import random

from vertex_velocity.entities import Entity, OpaqueEntity

# Per neuron mutation probabilities.
PROBA_MUTATE_ACTIVATION = 0.1  # Probability of mutating a neuron's activation during evolution
PROBA_MUTATE_TYPE = 0.1  # Probability of mutating a neuron's type during evolution

PROBA_MOVE_NEURON = 0.8  # Probability of mutating a neuron during evolution
MOVE_NEURON_RANGE = 10  # Range of movement for a neuron during evolution

# Per network mutation probabilities.
PROBA_REMOVE_NEURON = 0.1  # Probability of removing a neuron during evolution

PROBA_NEW_NEURON = 0.1  # Probability of creating a new neuron during evolution
NEW_NERON_POS_RANGE = 300  # Range for the position of a new neuron during evolution


class MuatationType(Enum):
    """Enum representing different types of mutations."""
    REMOVE = "remove"
    NEW = "new"
    MUTATE_ACTIVATION = "mutate_activation"
    MUTATE_TYPE = "mutate_type"
    MOVE = "move"


class NeuronType(Enum):
    """Enum representing different types of neurons."""
    AIR = ("airNeuron", "air")
    BRICK = ("brickNeuron", "brick")
    SPIKE = ("spikeNeuron", "spike")


class NeuronActivation(Enum):
    """Enum representing different possible activations of a neuron."""
    ABSENCE = "Absence"
    PRESENCE = "Presence"


class Neuron(Entity):
    """Class representing a single neuron in a neural network."""

    NEURON_SIZE = (64, 64)  # Default size of a neuron

    def __init__(self, game, tilemap, neuronType: NeuronType, relPos: tuple, activation: NeuronActivation):
        """Initialize a neuron.
        
        Args:
            game (RLGame): The game instance this neural network belongs to.
            tilemap (TileMap): The tilemap the neuron is part of.
            neuronType (NeuronType): The type of the neuron.
            relPos (tuple): The (x, y) position of the neuron relative to the player.
            activation (NeuronActivation): The activation state of the neuron.
        """
        self.game = game
        self.neuronType = neuronType
        self.activation = activation
        self.activated = False
        self.relPos = relPos
        pos = (self.game.player.pos[0] + relPos[0], self.game.player.pos[1] + relPos[1])
        super().__init__(game, tilemap, neuronType.value[0], pos, self.NEURON_SIZE)

    def __repr__(self):
        """Return a string representation of the neuron."""
        return f"Neuron(type={self.neuronType}, position={self.relPos}, activation={self.activation}, activated={self.activated})"

    def update(self):
        """Update the neuron state based on its activation."""

        # First, maintain the relative position to the player.
        playerPos = self.game.player.pos
        self.pos = (playerPos[0] + self.relPos[0], playerPos[1] + self.relPos[1])

        # Reset the activation state depending on the activation type.
        if self.activation == NeuronActivation.PRESENCE:
            self.activated = False
        elif self.activation == NeuronActivation.ABSENCE:
            self.activated = True

        # Update the activation state based on the tilemap.
        for point in [
            (self.x, self.y), (self.x + self.NEURON_SIZE[0], self.y), (self.x, self.y + self.NEURON_SIZE[1]),
            (self.x + self.NEURON_SIZE[0], self.y + self.NEURON_SIZE[1])
        ]:
            tile = self.tilemap.getTileAt(point)
            if tile is not None:
                tileType = tile["type"]
            else:
                tileType = "air"

            if self.activation == NeuronActivation.PRESENCE:
                self.activated |= (tileType == self.neuronType.value[1])
            elif self.activation == NeuronActivation.ABSENCE:
                self.activated &= (tileType != self.neuronType.value[1])

        # Update the image based on activation state.
        if self.activated:
            self.eType = f"{self.neuronType.value[0]}Activated{self.activation.value}"
        else:
            self.eType = self.neuronType.value[0]


class NeuralNetwork:
    """Class representing a neural network for the game."""

    def __init__(self, game, tilemap, neurons: list[Neuron]):
        """Initialize the neural network with a list of neurons.
        
        Args:
            game (RLGame): The game instance this neural network belongs to.
            tilemap (TileMap): The tilemap the neuron is part of.
            neurons (list[Neuron]): A list of Neuron objects.
        """
        self.game = game
        self.tilemap = tilemap
        self.neurons = neurons
        self.activated = False

    def __repr__(self):
        """Return a string representation of the neural network."""
        return f"NeuralNetwork(activated={self.activated}, neurons={self.neurons})"

    def addNeuron(self, neuron: Neuron):
        """Add a neuron to the neural network.
        
        Args:
            neuron (Neuron): The neuron to add.
        """
        self.neurons.append(neuron)

    def removeNeuron(self, neuron: Neuron):
        """Remove a neuron from the neural network.
        
        Args:
            neuron (Neuron): The neuron to remove.
        """
        self.neurons.remove(neuron)

    def evolve(self):
        """Generate a new neural network by evolving the current one.
        
        Returns:
            NeuralNetwork: A new neural network with evolved neurons.

        Behavior:
            Randomly adds, removes, or mutates neurons based on defined probabilities.
        """

        def _pickMutation():
            """Squash all potential mutations into a single random choice."""
            probability = random.random()
            assert sum(
                [
                    PROBA_MUTATE_ACTIVATION,
                    PROBA_MUTATE_TYPE,
                    PROBA_MOVE_NEURON,
                ]
            ) == 1, "Total probability must equal 1"

            # If probability is between 0 and mutate activation probability, return 'mutate_activation'.
            if probability < PROBA_MUTATE_ACTIVATION:
                return MuatationType.MUTATE_ACTIVATION
            # If probability is between mutate activation and mutate type probability, return 'mutate_type'.
            elif probability < PROBA_MUTATE_ACTIVATION + PROBA_MUTATE_TYPE:
                return MuatationType.MUTATE_TYPE
            # If probability is between mutate type and move neuron probability, return 'move'.
            elif probability < PROBA_MUTATE_ACTIVATION + PROBA_MUTATE_TYPE + PROBA_MOVE_NEURON:
                return MuatationType.MOVE

        new_neurons = []

        # Iterate through existing neurons and decide whether to keep, mutate, or remove them.
        for neuron in self.neurons:
            randomAction = _pickMutation()

            # If the neuron was not removed or replaced, make a work copy for potential mutations.
            new_neuron = Neuron(self.game, self.tilemap, neuron.neuronType, neuron.relPos, neuron.activation)
            if randomAction == MuatationType.MUTATE_ACTIVATION:
                # Mutate the activation state of the neuron.
                new_neuron.activation = NeuronActivation.ABSENCE if neuron.activation == NeuronActivation.PRESENCE else NeuronActivation.PRESENCE
                logging.debug(f"Mutating activation of neuron {neuron} to {new_neuron.activation}")
            elif randomAction == MuatationType.MUTATE_TYPE:
                # Mutate the neuron type randomly.
                new_neuron.neuronType = random.choice(list(NeuronType))
                logging.debug(f"Mutating type of neuron {neuron} to {new_neuron.neuronType}")
            elif randomAction == MuatationType.MOVE:
                # Randomly adjust the neuron's position relative to its original position.
                new_neuron.relPos = (
                    neuron.relPos[0] + random.randint(-MOVE_NEURON_RANGE, MOVE_NEURON_RANGE),
                    neuron.relPos[1] + random.randint(-MOVE_NEURON_RANGE, MOVE_NEURON_RANGE)
                )
                logging.debug(f"Moving neuron {neuron} to new position {new_neuron.relPos}")

            # Add the potentially mutated neuron to the new list.
            new_neurons.append(new_neuron)

        if random.random() < PROBA_REMOVE_NEURON:
            # If the random chance is less than the removal probability, skip this neuron.
            neuron = random.choice(new_neurons)
            new_neurons.remove(neuron)
            logging.debug(f"Removing neuron {neuron}")

        if random.random() < PROBA_NEW_NEURON:
            # Create a new neuron with a random type and position.
            new_neuron = Neuron(
                self.game, self.tilemap, random.choice(list(NeuronType)), (
                    random.randint(-NEW_NERON_POS_RANGE,
                                   NEW_NERON_POS_RANGE), random.randint(-NEW_NERON_POS_RANGE, NEW_NERON_POS_RANGE)
                ), random.choice(list(NeuronActivation))
            )
            logging.debug(f"Adding new neuron {new_neuron}")

            # Add the potentially mutated neuron to the new list.
            new_neurons.append(new_neuron)

        # Create a new neural network with the evolved neurons.
        return NeuralNetwork(self.game, self.tilemap, new_neurons)

    def update(self):
        """Update the neural network state."""

        # First, update all neurons in the network.
        for neuron in self.neurons:
            neuron.update()

        # Then, check if all neuron is activated.
        self.activated = all(neuron.activated for neuron in self.neurons)

    def render(self, surface, scroll):
        """Render the neural network on the given screen.
        
        Args:
            surface (pygame.Surface): The surface to render the player on.
            scroll (list): The scroll offset for rendering.
        """
        # Render each neuron in the network.
        for neuron in self.neurons:
            neuron.render(surface, scroll)

        if len(self.neurons) > 0:
            # Compute network's center position as the average of all neurons' positions.
            center_x = sum(neuron.center[0] for neuron in self.neurons) / len(self.neurons)
            center_y = sum(neuron.center[1] for neuron in self.neurons) / len(self.neurons)

            # Render the center as a white circle, empty if the network is not activated.
            if self.activated:
                pygame.draw.circle(surface, (255, 255, 255), (int(center_x - scroll[0]), int(center_y - scroll[1])), 20)
            else:
                pygame.draw.circle(
                    surface, (100, 100, 100), (int(center_x - scroll[0]), int(center_y - scroll[1])), 20, 5
                )

            # Render the connections between neurons and center.
            for neuron in self.neurons:
                pygame.draw.line(
                    surface, (255, 255, 255) if neuron.activated else (100, 100, 100),
                    (int(center_x - scroll[0]), int(center_y - scroll[1])),
                    (int(neuron.center[0] - scroll[0]), int(neuron.center[1] - scroll[1])), 2
                )
