from __future__ import annotations

import typing
import timeit

if typing.TYPE_CHECKING:
    pass

# Define the dimensions of the board
rows, cols = 100, 100


# Approach 1: Generate the range every time
def generate_every_time():
    for r in range(rows):
        for c in range(cols):
            pass


# Approach 2: Store the range in a variable and loop over it
board_positions = [(r, c) for r in range(rows) for c in range(cols)]


def use_stored_positions():
    for r, c in board_positions:
        pass


# Measure the execution time of both approaches
time_generate_every_time = timeit.timeit(generate_every_time, number=1000)
time_use_stored_positions = timeit.timeit(use_stored_positions, number=1000)

print(f"Time to generate every time: {time_generate_every_time:.6f} seconds")
print(f"Time to use stored positions: {time_use_stored_positions:.6f} seconds")
