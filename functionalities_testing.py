import utils.block_utils as bu
import sys
import time
sys.setrecursionlimit(10000)


start_coord = (157, 4, -102)
#entities_2_spawn = [
#    (bu.ENTITY_AREA_EFFECT_CLOUD, start_coord[0] + 2, start_coord[1], start_coord[2]),
#    (bu.ENTITY_ZOMBIE, start_coord[0] + 2, start_coord[1], start_coord[2] + 4)
#    ]


# 28 throws an error
start_idx = 91
entities_2_spawn = [(start_idx + i, start_coord[0] + ((start_idx+i)*3), start_coord[1], start_coord[2]) for i in range(89)]


def main():
    client_handler = bu.ClientHandler()

    for i, e in enumerate(entities_2_spawn, start=start_idx):
        print("==============")
        print(f"Trying to spawn entity no. {i}")
        uuids = client_handler.spawn_entities([e]).uuids
        spawned_entities = client_handler.read_entities(uuids)
        if len(spawned_entities.entities) > 0 and hasattr(spawned_entities.entities[0], 'position'):
            e_name = [n for n in str(spawned_entities.entities._values[0]).split("\n") if n.startswith("type")]
            print(f"spawned entity -> {e_name}")
        else:
            print(f"failed to spawn entity {i}")


if __name__ == '__main__':
    main()
