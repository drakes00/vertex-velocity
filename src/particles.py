"""Module for simulating particles in a 2D space."""

import random

import pygame


class Particle:
    """Class representing a particle in 2D space."""
    def __init__(self, pos):
        """Initialize the particle with position and velocity."""
        self.x = pos[0]  # x-coordinate
        self.y = pos[1]  # y-coordinate
        self.vx = random.randint(-2, 2)  # velocity in x-direction
        self.vy = random.randint(-10, 0) * 0.1  # velocity in y-direction
        self.radius = 5

    def update(self):
        """Update the position of the particle based on its velocity and time step."""
        self.x += self.vx
        self.y += self.vy
        if random.randint(0, 100) < 40:
            self.radius -= 1

    def render(self, surface, scroll):
        """Render the particle on the screen."""
        pygame.draw.circle(surface, (255, 255, 255), (int(self.x) - scroll[0], int(self.y) - scroll[1]), self.radius)

    def __repr__(self):
        """Return a string representation of the particle."""
        return f"Particle(x={self.x}, y={self.y}, vx={self.vx}, vy={self.vy})"


class Dust:
    """Class representing a trail of particles."""
    NUM_PARTICLES = 2

    def __init__(self, pos):
        """Initialize the dust with a list of particles."""
        self.particles = [Particle(pos) for _ in range(self.NUM_PARTICLES)]

    def update(self):
        """Update the position of all particles in the dust."""
        for particle in self.particles:
            particle.update()
            if particle.radius <= 0:
                self.particles.remove(particle)

    def render(self, surface, scroll):
        """Render all particles in the dust on the screen."""
        for particle in self.particles:
            particle.render(surface, scroll)

    def __repr__(self):
        """Return a string representation of the dust."""
        return f"Dust(particles={self.particles})"
