import grpc

import client.minecraft_pb2_grpc as mcraft_grpc
from client.minecraft_pb2 import *

BLOCKS = BlockType.values()
ORIENTATIONS = Orientation.values()

block_directions = {"north": NORTH,
                    "west": WEST,
                    "south": SOUTH,
                    "east": EAST,
                    "up": UP,
                    "down": DOWN}

block_direction_codes = lambda direction: block_directions[direction]


def move_coordinate(coord: (int, int, int), side_idx, delta=1):
    """A quick way to increment a coordinate in the desired direction"""
    switcher = [
        lambda c: (c[0], c[1], c[2] - delta),  # Go North
        lambda c: (c[0] - delta, c[1], c[2]),  # Go West
        lambda c: (c[0], c[1], c[2] + delta),  # Go South
        lambda c: (c[0] + delta, c[1], c[2]),  # Go East
        lambda c: (c[0], c[1] + delta, c[2]),  # Go Up
        lambda c: (c[0], c[1] - delta, c[2]),  # Go Down
    ]
    return switcher[side_idx](coord)


class BlockBuffer:
    def __init__(self):
        self._blocks = []
        self._channel = grpc.insecure_channel('localhost:5001')
        self._client = mcraft_grpc.MinecraftServiceStub(self._channel)

    def add_block(self, coordinate: (int, int, int), orientation: Orientation, block_type: BlockType):
        assert block_type in BlockType.values(), "Unknown block type"
        assert orientation in Orientation.values(), "Unknown orientation"

        self._blocks.append(Block(
            position=Point(x=coordinate[0], y=coordinate[1], z=coordinate[2]),
            type=block_type,
            orientation=orientation))

    def send_to_server(self):
        response = self._client.spawnBlocks(Blocks(blocks=self._blocks))
        self._blocks = []
        return response

    def fill_cube(self, start_cord: (int, int, int), end_coord: (int, int, int), block_type: BlockType):
        assert block_type in BlockType.values(), "Unknown block type"

        min_x, max_x = (start_cord[0], end_coord[0]) if start_cord[0] < end_coord[0] else (end_coord[0], start_cord[0])
        min_y, max_y = (start_cord[1], end_coord[1]) if start_cord[1] < end_coord[1] else (end_coord[1], start_cord[1])
        min_z, max_z = (start_cord[2], end_coord[2]) if start_cord[2] < end_coord[2] else (end_coord[2], start_cord[2])

        self._client.fillCube(FillCubeRequest(
            cube=Cube(min=Point(x=min_x, y=min_y, z=min_z),
                      max=Point(x=max_x, y=max_y, z=max_z)),
            type=block_type
        ))

    def get_cube_info(self, start_cord: (int, int, int), end_coord: (int, int, int)):
        min_x, max_x = (start_cord[0], end_coord[0]) if start_cord[0] < end_coord[0] else (end_coord[0], start_cord[0])
        min_y, max_y = (start_cord[1], end_coord[1]) if start_cord[1] < end_coord[1] else (end_coord[1], start_cord[1])
        min_z, max_z = (start_cord[2], end_coord[2]) if start_cord[2] < end_coord[2] else (end_coord[2], start_cord[2])

        response = self._client.readCube(Cube(min=Point(x=min_x, y=min_y, z=min_z),
                                              max=Point(x=max_x, y=max_y, z=max_z)))

        return response.blocks

