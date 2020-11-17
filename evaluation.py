from sims_representation import Node, update_coordinates
from typing import List
from utils.block_utils import BlockBuffer, GOLD_BLOCK, AIR


def evaluate(individual: (Node, List[Node])):
    update_coordinates(individual[0])
    max_height = max([c.coordinate[1] for c in individual[1]])
    num_blocks = len(individual[1])
    fitness = max_height - 0.5 * num_blocks
    return fitness


def evaluate_to_sun(individual: (Node, List[Node]), pop_coord, block_buffer: BlockBuffer):
    root = individual[0]

    # Place the sun
    sun_coordinate = (pop_coord[0] - 10, pop_coord[1] + 10, pop_coord[2] - 10)
    block_buffer.add_block(sun_coordinate, 0, GOLD_BLOCK)
    block_buffer.send_to_server()

    blocks = block_buffer.get_cube_info(pop_coord,
                                        (sun_coordinate[0] - 1, sun_coordinate[1] + 1, sun_coordinate[2] -1))

    _sun = [b for b in blocks if b.type == GOLD_BLOCK]
    assert len(_sun) == 1, "no sun found"
    _sun = _sun[0]

    closest_to_sun = float("inf")
    for b in blocks:
        if b.type != AIR and b.type != GOLD_BLOCK:
            dist = (b.position.x - _sun.position.x) ** 2 + \
                   (b.position.y - _sun.position.y) ** 2 + \
                   (b.position.z - _sun.position.z) ** 2
            dist = dist ** 0.5
            if dist < closest_to_sun:
                closest_to_sun = dist

    return closest_to_sun

