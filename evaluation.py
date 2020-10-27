from sims_representation import Node, update_coordinates


def evaluate(individual: (Node, list)):
    update_coordinates(individual[0])
    max_height = max([c.coordinate[1] for c in individual[1]])
    num_blocks = len(individual[1])
    fitness = max_height - 0.5 * num_blocks
    return fitness
