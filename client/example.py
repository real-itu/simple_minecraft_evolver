import grpc

import client.minecraft_pb2_grpc as mcraft_grpc
from client.minecraft_pb2 import *


channel = grpc.insecure_channel('localhost:5001')
client: mcraft_grpc.MinecraftServiceStub = mcraft_grpc.MinecraftServiceStub(channel)

spawn_at = (-193, 6, 15)
end_coords = (-194, 7, 20)


response = client.spawnBlocks(Blocks(blocks=[
    Block(position=Point(x=spawn_at[0], y=spawn_at[1], z=spawn_at[2]), type=PISTON, orientation=NORTH),
    Block(position=Point(x=spawn_at[0], y=spawn_at[1], z=spawn_at[2]-3), type=PISTON, orientation=UP),
    Block(position=Point(x=spawn_at[0], y=spawn_at[1], z=spawn_at[2]-6), type=SPONGE, orientation=UP)
]))
print(response)

response = client.readCube(Cube(min=Point(x=1, y=1, z=1), max=Point(x=2, y=3, z=3)))
print(response)


response = client.fillCube(FillCubeRequest(
   cube=Cube(min=Point(x=end_coords[0], y=spawn_at[1], z=spawn_at[2]),
             max=Point(x=spawn_at[0], y=end_coords[1], z=end_coords[2])),
   type=OBSIDIAN
))
print(response)
