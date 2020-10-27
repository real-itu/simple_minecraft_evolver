from sims_representation import random_init, set_nodes_as_blocks, crossover, mutation, clone_individual
from utils.block_utils import BlockBuffer
from evaluation import evaluate

from operator import itemgetter
from numpy.random import uniform, randint
from delete import delete_patch
import sys
sys.setrecursionlimit(10000)

# TODO Change the start_coord close to wherever you spawn on your server
start_coord = (-193, 6, 15)


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


def evolution(generations=1000, pop_number=200, mutation_prob=0.1, parent_cuttoff_ratio=0.1):
    population_coordinates = [(start_coord[0], start_coord[1], start_coord[2] + (i * 20)) for i in range(pop_number)]
    population = [generate_individual(c) for c in population_coordinates]
    block_buffer = BlockBuffer()
    for generation in range(generations):
        delete_patch(block_buffer)
        show_population(population, population_coordinates, block_buffer)
        print(f"Generation --> {generation}")

        evaluations = list(map(evaluate, population))
        print(max(evaluations))
        pop_eval_zipped = zip(population, evaluations)
        pop_eval_zipped = sorted(pop_eval_zipped, key=itemgetter(1), reverse=True)
        sorted_population, _ = map(list, zip(*pop_eval_zipped))
        parent_cuttoff_idx = int(parent_cuttoff_ratio * pop_number)
        parents = sorted_population[:parent_cuttoff_idx]

        next_generation = [clone_individual(parents[0])]
        for _ in range(pop_number - 1):
            p1 = parents[randint(0, len(parents))]
            p2 = parents[randint(0, len(parents))]
            c = crossover(p1, p2)

            if uniform(0, 1) < mutation_prob:
                c = mutation(c[0])
            next_generation.append(c)
        population = next_generation


if __name__ == "__main__":
    evolution(generations=200, pop_number=20, mutation_prob=0.05)

