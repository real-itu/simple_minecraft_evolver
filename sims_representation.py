from numpy.random import choice, randint, uniform
from utils.block_utils import Blocks, ORIENTATIONS, block_directions, move_coordinate, BlockBuffer, Orientation, \
    BlockType, AIR, OBSIDIAN, REDSTONE_BLOCK, GLASS, BROWN_MUSHROOM_BLOCK, BROWN_GLAZED_TERRACOTTA, NETHER_BRICK, \
    COBBLESTONE, SLIME, ACACIA_DOOR
from typing import List
from copy import deepcopy
from numpy.random import randint

ALLOWED_SIDES = [ORIENTATIONS[0], ORIENTATIONS[1], ORIENTATIONS[4]]
ALLOWED_BLOCKS = [OBSIDIAN,
                  REDSTONE_BLOCK,
                  GLASS,
                  BROWN_MUSHROOM_BLOCK,
                  NETHER_BRICK,
                  COBBLESTONE,
                  SLIME,
                  ACACIA_DOOR
                  ]


class Node:
    """basic node structure for graph representation of a block and its neighbors """

    def __init__(self, block_type_id, orientation, coordinate):
        self.block_type = block_type_id
        self.orientation = orientation
        self.neighbors = [None] * len(ORIENTATIONS)
        self.coordinate = coordinate
        self.parent = None
        self.side = None

    def insert_neighbor(self, node, side):
        # assert node is node, "node has to be type node"
        assert side in ORIENTATIONS, \
            'orientation must be between [0, 5]'
        self.neighbors[side] = node
        node.parent = self
        node.side = side


def set_nodes_as_blocks(node: Node, coordinate: (int, int, int),
                        block_buffer: BlockBuffer, block_type=None):
    block_type = block_type if block_type is not None else node.block_type
    block_orientation = node.orientation
    block_buffer.add_block(coordinate, block_orientation, block_type)

    for side_idx, neigh in enumerate(node.neighbors):
        if neigh is not None:
            set_nodes_as_blocks(neigh, move_coordinate(coordinate, side_idx), block_buffer)


def update_coordinates(root: Node):
    nodes_stack = [root]
    while not len(nodes_stack) == 0:
        node = nodes_stack.pop()
        for i, neigh in enumerate(node.neighbors):
            if neigh is not None:
                nodes_stack.append(neigh)
                neigh.coordinate = move_coordinate(node.coordinate, i)


def delete_from_root_node(coordinate: (int, int, int), node: Node, block_buffer: BlockBuffer):
    set_nodes_as_blocks(node, coordinate, block_buffer, AIR)


def node_to_list_depth_first(root: Node):
    node_lst = [root]
    node_stack = [root]

    while len(node_stack) > 0:
        node = node_stack.pop()
        for neighbor in node.neighbors:
            if neighbor is not None:
                node_stack.append(neighbor)
                node_lst.append(neighbor)
    return node_lst


def mutation(individual_old: Node):
    clone_root = deepcopy(individual_old)
    node_list = node_to_list_depth_first(clone_root)
    if len(node_list) > 1:
        x_point_remove = randint(1, len(node_list))
        x_node_remove = node_list[x_point_remove]
        x_parent = x_node_remove.parent
        add_to_side = x_node_remove.side
        x_root_add = random_init(x_node_remove.coordinate, [], 0.5, 0.05)
        x_root_add.parent = x_parent
        x_root_add.side = add_to_side
        x_parent.neighbors[add_to_side] = x_root_add

    return clone_root, node_to_list_depth_first(clone_root)


def clone_individual(individual: (Node, List[Node])):
    clone_root = deepcopy(individual[0])
    return clone_root, node_to_list_depth_first(clone_root)


def crossover(root_parent: (Node, List[Node]), second_parent: (Node, List[Node])):
    if root_parent[0] is second_parent[0]:
        clone_root = deepcopy(root_parent[0])
        return clone_root, node_to_list_depth_first(clone_root)

    if len(root_parent[1]) == 1:
        # Here is for the case when ind1 is just a single node without neighbours.
        # In that case, add a "virtual" node that will be replaced by the section of the second parent
        rand_side = choice(ALLOWED_SIDES)
        rand_btype = choice(ALLOWED_BLOCKS)
        virtual_neighbour = Node(rand_btype, 0, (0, 0, 0))
        root_parent[0].insert_neighbor(virtual_neighbour, rand_side)
        x_node_remove = virtual_neighbour

    else:
        # pick random two nodes from individuals
        x_point_remove = randint(1, len(root_parent[1]))
        x_node_remove = root_parent[1][x_point_remove]

    x_point_insert = randint(0, len(second_parent[1]))
    x_node_insert = second_parent[1][x_point_insert]
    root = root_parent[0]

    new_root = Node(root.block_type, root.orientation, root.coordinate)
    new_node_list = [new_root]
    node_stack = [root]
    new_nodes_stack = [new_root]

    # make a child
    while not len(node_stack) == 0:
        focus_parent_node = node_stack.pop()
        focus_child_node = new_nodes_stack.pop()
        for neigh in focus_parent_node.neighbors:
            if neigh is x_node_remove:
                side = neigh.side
                neigh = x_node_insert
                neigh.side = side
            if neigh is not None:
                new_node = Node(neigh.block_type, neigh.orientation, neigh.coordinate)
                new_node_list.append(new_node)
                focus_child_node.insert_neighbor(new_node, neigh.side)
                new_nodes_stack.append(new_node)
                node_stack.append(neigh)

    return new_root, new_node_list


def random_init(current_coordinate, node_list, prob, delta_prob):
    rand_block_type = choice(ALLOWED_BLOCKS)
    rand_orientation = randint(0, len(ORIENTATIONS))
    node = Node(rand_block_type, rand_orientation, current_coordinate)
    node_list.append(node)
    if prob <= 0.0:
        return node
    else:
        for side in ALLOWED_SIDES:  # create a one-directional structure
            if uniform() < prob:
                new_coordinate = move_coordinate(current_coordinate, side)
                neighbor_node = random_init(new_coordinate, node_list, prob - delta_prob, delta_prob)
                node.insert_neighbor(neighbor_node, side)
        return node
