def main():
    import sys
    import pygame

    # Initialize Pygame and load all necessary game resources
    pygame.init()

    # Initialize the window (fullscreen mode)
    window = pygame.display.set_mode((0, 0), pygame.NOFRAME)
    pygame.display.toggle_fullscreen()  # Toggle fullscreen twice to force it on

    import Constant

    from Engine import Engine

    # Set the volume for the background music (0.0 is mute, 1.0 is full volume)
    pygame.mixer.music.set_volume(0.1)

    # Define a custom event to signal when the music ends
    MUSIC_END = pygame.USEREVENT + 1
    pygame.mixer.music.set_endevent(
        MUSIC_END
    )  # Set the event that triggers when music finishes

    # Initialize the game clock to manage frame rate
    clock = pygame.time.Clock()

    # Create and initialize the game engine
    engine = Engine(window)

    # Create and display the splash screen
    from Splash import SplashScreen

    splash_screen = SplashScreen(engine.display_surface)
    splash_screen.display()

    Constant.load_settings()

    # Load images required for the game (pieces, board, etc.)\
    Constant.load_images()

    # Load background music
    Constant.load_music(Constant.MUSIC_ON)

    # Load sound effects (clicks, moves, etc.)
    Constant.load_sounds()

    from State import MainMenu
    import time

    # Set the initial game state to the Main Menu
    state = MainMenu(engine.display_surface, engine, splash_screen)
    engine.set_state(state)  # Set the initial state in the engine

    # Set the game window's title and icon
    pygame.display.set_caption("Chess Empires")
    pygame.display.set_icon(
        Constant.IMAGES["icon"]
    )  # Set the window icon from loaded images

    # Main game loop
    while engine.running:
        # Current state handling input
        current_state = engine.state[-1]

        # Initialize a dictionary to track last input times for each event type
        last_input_time = {"mouse_click": 0, "key_press": 0}

        # Define the cooldown period (in seconds) between repeated inputs
        input_cooldown = 0.05  # 200 milliseconds for mouse clicks and key presses

        # Event loop: Process all events for the current frame
        for event in pygame.event.get():
            current_time = time.time()  # Get the current time for input tracking

            # Handle mouse click
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Check if the button is left or right mouse button
                if event.button == 1 or event.button == 3:
                    # Check if enough time has passed since the last click
                    if current_time - last_input_time["mouse_click"] >= input_cooldown:
                        # Handle the mouse click event
                        current_state.handle_input(event)
                        # Update last input time for mouse click
                        last_input_time["mouse_click"] = current_time

            # Handle mouse release
            elif event.type == pygame.MOUSEBUTTONUP:
                # Check for left mouse button release
                if event.button == 1:
                    # Handle the mouse release event
                    current_state.handle_input(event)

            # Handle key press (KEYDOWN)
            elif event.type == pygame.KEYDOWN:
                # Check if enough time has passed since the last key press
                if current_time - last_input_time["key_press"] >= input_cooldown:
                    # Handle the key press event
                    current_state.handle_input(event)

                    # Update last input time for key press
                    last_input_time["key_press"] = current_time

            # Handle Mouse Motion
            elif event.type == pygame.MOUSEMOTION:
                # Handle mouse movement events
                current_state.handle_input(event)

            # Handle other events (music end, etc.)
            elif event.type == MUSIC_END:
                Constant.load_music(Constant.MUSIC_ON)  # Reload music when it ends

            # Exit game
            elif event.type == pygame.QUIT:
                Constant.save_settings()
                pygame.quit()
                sys.exit()

        # Reset frame counter if needed (depending on how your game loop is structured)
        # For example, you could reset the counter after a certain number of frames or just let it loop.

        # Update game state (e.g., check for actions, etc.)
        engine.update()

        # Draw the current game state (rendering the game scene)
        current_state.draw()

        engine.draw_display_surface()

        # Update the game display (rendering everything to the window)
        pygame.display.update()

        # Control the frame rate (to limit FPS)
        clock.tick(Constant.MAX_FPS)

    if not engine.running:
        main()


if __name__ == "__main__":
    main()
