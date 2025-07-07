"""Module defining neural network classes and functions."""

from enum import Enum

from vertex_velocity.entities import Entity, OpaqueEntity


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

    def __init__(self, neurons: list[Neuron]):
        """Initialize the neural network with a list of neurons.
        
        Args:
            neurons (list[Neuron]): A list of Neuron objects.
        """
        self.neurons = neurons

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

    def update(self):
        """Update the neural network state."""
        for neuron in self.neurons:
            neuron.update()

    def render(self, surface, scroll):
        """Render the neural network on the given screen.
        
        Args:
            surface (pygame.Surface): The surface to render the player on.
            scroll (list): The scroll offset for rendering.
        """
        for neuron in self.neurons:
            neuron.render(surface, scroll)
