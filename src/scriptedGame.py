"""Vertex Velocity's scripted game mode."""

import argparse
import json
import logging
import sys

import pygame

from game import Game


class ScriptedGame(Game):
    def __init__(self, inputTilemap, inputScriptPath=None, outputScriptPath=None):
        """Initialize the scripted game.
        Args:
            inputTilemap (str): The input tilemap file name.
            inputScriptPath (str): The input script file name.
            outputScriptPath (str): The output script file name.

        Behavior:
            At least one of `inputScriptPath` or `outputScriptPath` must be provided.
        """
        super().__init__(inputTilemap)

        self.inputScriptPath = inputScriptPath
        self.outputScriptPath = outputScriptPath

        self.inputScript = {}
        self.outputScript = {}

        self.replayEndTick = -1
        self.lastMovement = self.movement.copy()

        # Load the input script if provided.
        if self.inputScriptPath:
            with open(self.inputScriptPath, 'r') as f:
                self.inputScript = json.load(f)

            # Include input script in the output script if an output path is provided.
            if self.outputScriptPath:
                self.outputScript.update(self.inputScript)

            # Compute the last tick from the input script.
            self.replayEndTick = max(map(int, self.inputScript.keys()), default=-1)

    def processInputs(self):
        """Replays inputs from the input script and/or records new inputs if an output script path is provided."""
        # First try to replay inputs from the input script.
        if self.inputScriptPath and int(self.currentTick) <= self.replayEndTick:
            if self.currentTick in self.inputScript:
                # Get the inputs for the current tick.
                for input in self.inputScript[self.currentTick]:
                    action = input["action"]
                    state = input["state"]
                    if action in self.movement:
                        self.movement[action] = state

            # As long as we are replaying inputs, we do not process real-time inputs.
            return

        # If no input script or the replay has ended, process real-time inputs.
        super().processInputs()

        # If recording to an output script, record the changes.
        if self.outputScriptPath:
            changes = []
            for direction in self.movement:
                if self.movement[direction] != self.lastMovement[direction]:
                    changes.append({
                        "action": direction,
                        "state": self.movement[direction]
                    })

            if changes:
                if self.currentTick not in self.outputScript:
                    self.outputScript[self.currentTick] = []
                self.outputScript[self.currentTick].extend(changes)

            self.lastMovement = self.movement.copy()

    def run(self):
        """Run the scripted game."""
        try:
            super().run()
        finally:
            if self.outputScriptPath:
                logging.info(f"Saving output script to {self.outputScriptPath}...")
                with open(self.outputScriptPath, 'w') as f:
                    json.dump(self.outputScript, f, indent=2)
                logging.info("Script saved successfully.")


def main():
    parser = argparse.ArgumentParser(description="Vertex Velocity Scripted Game")
    parser.add_argument("-l", "--level", type=str, help="Level file name")
    parser.add_argument("-i", "--input-script", type=str, help="Input script file name")
    parser.add_argument("-o", "--output-script", type=str, help="Output script file name")
    args = parser.parse_args()

    if not args.level:
        print("Error: \"-l/--level\" is required.")
        sys.exit(1)
    elif not args.input_script and not args.output_script:
        print("Error: At least one of \"-i/--input-script\" or \"-o/--output-script\" must be provided.")
        sys.exit(1)

    ScriptedGame(args.level, args.input_script, args.output_script).run()


if __name__ == "__main__":
    main()
