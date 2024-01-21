""" This script cuts up a large image into smaller tiles """
import os
from itertools import product
from PIL import Image


def tile(filename, dir_in, dir_out, tile_size):
    name, ext = os.path.splitext(filename)
    img = Image.open(os.path.join(dir_in, filename))
    w, h = img.size

    grid = product(range(0, h - h % tile_size, tile_size), range(0, w - w % tile_size, tile_size))
    for i, j in grid:
        box = (j, i, j + tile_size, i + tile_size)
        out = os.path.join(dir_out, f'{name}_{i}_{j}{ext}')
        img.crop(box).save(out)


# params
filename = "filename.png"
input_directory = "/assets/img_manipulation/split"
output_directory = "/assets/img_manipulation/output"
tile_size = 0


if __name__ == '__main__':
    tile(filename, input_directory, output_directory, tile_size)
