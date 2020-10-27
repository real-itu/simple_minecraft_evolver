from utils.block_utils import BlockBuffer, AIR


def delete_patch(block_buffer):
    start1_coords = (0, 6, -40)
    end_coords = (-400, 200, 400)
    block_buffer.fill_cube(start1_coords, end_coords, AIR)


if __name__ == "__main__":
    buffer = BlockBuffer()
    delete_patch(buffer)
