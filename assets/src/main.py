import pygame
from network.client import GameClient
from utilities.input_handler import get_player_input
from game.engine import GameEngine
from game.scenes.game_scene import GameScene
from game.state_manager import StateManager
from utilities.input_handler import InputHandler


# Initialize Pygame
pygame.init()

# Set up window size and other configurations
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Set up the game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Your Game Title")
clock = pygame.time.Clock()

# Create the game engine
game_engine = GameEngine(SCREEN_WIDTH, SCREEN_HEIGHT)

# Initialize the state manager
state_manager = StateManager()

# Initialize the input handler with the state manager
input_handler = InputHandler(state_manager)

# Initialize the game scene with the state manager
game_scene = GameScene(state_manager)

# Create the game client
game_client = GameClient("localhost", 5000)
game_client.connect()

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Handle player input
    player_input = get_player_input()
    game_client.send_string(player_input)

    # Update game logic
    game_engine.update()

    # Clear the screen
    screen.fill((0, 0, 0))

    # Render game elements
    game_engine.render(screen)

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(FPS)

# Close the game client
game_client.close()

# Quit Pygame
pygame.quit()