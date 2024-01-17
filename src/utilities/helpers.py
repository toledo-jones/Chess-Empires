# To convert the Game Window to the Logical Screen DIVIDE. Game_Window / Scale Factor
# To convert the Logical Screen to the Game Window MULTIPLY: Logical Screen * Scale Factor

def convert_to_world_position(screen_position, scale_factor, game_window_offset):
    """ Take Screen Position -> return World Position """

    # Unpack Screen Position
    x, y = screen_position[0], screen_position[1]

    # Adjust for game window offset
    adjusted_x = x - game_window_offset[0]
    adjusted_y = y - game_window_offset[1]

    # Calculate world coordinates using the logical window ratio and scale factors
    world_x = adjusted_x / scale_factor[0]
    world_y = adjusted_y / scale_factor[1]

    return world_x, world_y


def convert_from_world_position(world_position, scale_factor, game_window_offset):
    """ Take World Position -> return Screen Position """

    # Unpack World Position
    x, y = world_position[0], world_position[1]

    adjusted_x = x * scale_factor[0]
    adjusted_y = y * scale_factor[1]

    # Scale the position based on the current scale factors
    screen_x = adjusted_x #- game_window_offset[0]
    screen_y = adjusted_y #- game_window_offset[1]

    # Return converted values
    return screen_x, screen_y


def convert_sprite_alphas(loaded_images):
    for key in loaded_images.keys():
        loaded_images[key] = loaded_images[key].convert_alpha()
    return loaded_images
