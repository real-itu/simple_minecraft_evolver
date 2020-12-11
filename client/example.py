import grpc

import client.minecraft_pb2_grpc as mcraft_grpc
from client.minecraft_pb2 import *

import time


def average_block_coordinate(start_cord, end_coord):
    min_x, max_x = (start_cord[0], end_coord[0]) if start_cord[0] < end_coord[0] else (end_coord[0], start_cord[0])
    min_y, max_y = (start_cord[1], end_coord[1]) if start_cord[1] < end_coord[1] else (end_coord[1], start_cord[1])
    min_z, max_z = (start_cord[2], end_coord[2]) if start_cord[2] < end_coord[2] else (end_coord[2], start_cord[2])
    blocks = client.readCube(Cube(min=Point(x=int(min_x), y=int(min_y), z=int(min_z)),
                                  max=Point(x=int(max_x), y=int(max_y), z=int(max_z)))).blocks

    non_air_blocks = [b for b in blocks if b.type != AIR]
    avg_x = sum([b.position.x for b in non_air_blocks]) / float(len(non_air_blocks))
    avg_y = sum([b.position.y for b in non_air_blocks]) / float(len(non_air_blocks))
    avg_z = sum([b.position.z for b in non_air_blocks]) / float(len(non_air_blocks))

    return avg_x, avg_y, avg_z

spawn_at = (-193, 6, 15)
end_coords = (-192, 60, -40)

channel = grpc.insecure_channel('localhost:5001')
client = mcraft_grpc.MinecraftServiceStub(channel)

client.fillCube(FillCubeRequest(
    cube=Cube(
        min=Point(x=spawn_at[0]-10, y=spawn_at[1]+4, z=spawn_at[2]-10),
        max=Point(x=spawn_at[0]+10, y=spawn_at[1]+14, z=spawn_at[2]+10)
    ),
    type=AIR
))

client.spawnBlocks(Blocks(blocks=[
    # Lower layer
    Block(position=Point(x=spawn_at[0]+1, y=spawn_at[1]+5, z=spawn_at[2]+1), type=PISTON, orientation=NORTH),
    Block(position=Point(x=spawn_at[0]+1, y=spawn_at[1]+5, z=spawn_at[2]+0), type=SLIME, orientation=NORTH),
    Block(position=Point(x=spawn_at[0]+1, y=spawn_at[1]+5, z=spawn_at[2]-1), type=STICKY_PISTON, orientation=SOUTH),
    Block(position=Point(x=spawn_at[0]+1, y=spawn_at[1]+5, z=spawn_at[2]-2), type=PISTON, orientation=NORTH),
    Block(position=Point(x=spawn_at[0]+1, y=spawn_at[1]+5, z=spawn_at[2]-4), type=SLIME, orientation=NORTH),
    # Upper layer
    Block(position=Point(x=spawn_at[0]+1, y=spawn_at[1]+6, z=spawn_at[2]+0), type=REDSTONE_BLOCK, orientation=NORTH),
    Block(position=Point(x=spawn_at[0]+1, y=spawn_at[1]+6, z=spawn_at[2]-4), type=REDSTONE_BLOCK, orientation=NORTH),
    # Activate
    Block(position=Point(x=spawn_at[0]+1, y=spawn_at[1]+6, z=spawn_at[2]-1), type=QUARTZ_BLOCK, orientation=NORTH),
]))

avg_start = average_block_coordinate(spawn_at, end_coords)
time.sleep(10)
avg_end = average_block_coordinate(spawn_at, end_coords)

print(avg_start)
print(avg_end)








from sims_representation import random_init, set_nodes_as_blocks, crossover, mutation, clone_individual, Node
from utils.block_utils import BlockBuffer
from evaluation import evaluate, evaluate_to_sun

from operator import itemgetter
from numpy.random import uniform, randint
from delete import delete_patch
import sys
import time
sys.setrecursionlimit(10000)

start_coord = (-193, 6, 15)


def scratch():
    # n = Node(0, 1, start_coord)
    bb = BlockBuffer()
    # set_nodes_as_blocks(n, start_coord, bb)
    # bb.send_to_server()
    end_coord = (start_coord[0], start_coord[1] + 100, start_coord[2] - 100)
    blocks = bb.get_cube_info(start_coord, end_coord)


def generate_individual(coordinate):
    node_list = []
    root = random_init(coordinate, node_list, 0.5, 0.05)
    return root, node_list


def show_population(population, coordinates, block_buffer: BlockBuffer):
    root_nodes_pop = list(zip(*population))
    roots_and_coordinates = zip(root_nodes_pop[0], coordinates)
    buffer_blocks_fn = lambda r: set_nodes_as_blocks(r[0], r[1], block_buffer)
    list(map(buffer_blocks_fn, roots_and_coordinates))
    block_buffer.send_to_server()


def evolution(gens=1000, pop_num=200, mutation_p=0.1, parent_cut_r=0.1):
    population_coordinates = [(start_coord[0],
                               start_coord[1],
                               start_coord[2] + (i * 20))
                              for i in range(pop_num)]
    population = [generate_individual(c) for c in population_coordinates]
    block_buffer = BlockBuffer()
    for generation in range(gens):
        if generation == 0 or generation == 1:
            time.sleep(50)

        # Clear the area
        client.fillCube(FillCubeRequest(
            cube=Cube(
            min=Point(x=slots_start[0], y=slots_start[1], z=slots_start[2]),
            max=Point(x=slots_end[0], y=slots_end[1], z=slots_end[2])
            ),
            type=AIR
        ))
        # Show population
        client.spawnBlocks(Blocks([ind.get_blocks()
                                   for ind in population]))
        print(f"Generation --> {generation}")
        get_ind_blocks = lambda i: client.readCube(min=i.get_slot_min(),
                                                   max=i.get_slot_max())
        population_blocks = list(map(evaluate, population))
        evaluations = map(evaluate, population_blocks)
        pop_eval_zipped = zip(population, evaluations)
        pop_eval_zipped = \
            sorted(pop_eval_zipped, key=itemgetter(1), reverse=False)
        sorted_population, _ = map(list, zip(*pop_eval_zipped))
        parent_cuttoff_idx = int(parent_cut_r * pop_num)
        parents = sorted_population[:parent_cuttoff_idx]

        next_generation = [clone_individual(parents[0])]
        for _ in range(pop_num - 1):
            p1 = parents[randint(0, len(parents))]
            p2 = parents[randint(0, len(parents))]
            c = crossover(p1, p2)

            if uniform(0, 1) < mutation_p:
                c = mutation(c[0])
            next_generation.append(c)
        population = next_generation






