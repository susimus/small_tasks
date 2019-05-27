from re import sub as re_sub
from sys import (
    maxsize as sys_maxsize,
    exit as sys_exit)
from typing import List, Dict, Set


with open("in.txt") as input_file:
    vertices_count: int = int(input_file.readline())

    next_vertices: List[Dict[int, int]] = []
    for i in range(vertices_count):
        raw_input = [
            int(str_input) for str_input in
            re_sub(' +', ' ', input_file.readline()).split(" ")[:-1]]
        next_vertices.append({
            key_: value_ for key_, value_ in
            list(zip(
                [vertex - 1 for vertex in raw_input[::2]],
                raw_input[1::2]))})

    start_vertex: int = int(input_file.readline()) - 1
    end_vertex: int = int(input_file.readline()) - 1

shortest_distance: List[int] = [sys_maxsize for i in range(vertices_count)]
shortest_distance[start_vertex] = 0
previous_vertex: Dict[int, int] = dict()
marked_vertices: Set[int] = set()
for i in range(vertices_count):
    current_vertex: int = -1
    for j in range(vertices_count):
        if (j not in marked_vertices
                and (current_vertex == -1
                     or shortest_distance[j] < shortest_distance[current_vertex])):
            current_vertex = j
    if shortest_distance[current_vertex] == sys_maxsize:
        break

    marked_vertices.add(current_vertex)

    for j in next_vertices[current_vertex]:
        vertex_to: int = j
        edge_length: int = next_vertices[current_vertex][j]
        if shortest_distance[current_vertex] + edge_length < shortest_distance[vertex_to]:
            shortest_distance[vertex_to] = shortest_distance[current_vertex] + edge_length
            previous_vertex[vertex_to] = current_vertex

if end_vertex not in previous_vertex:
    with open("out.txt", "w") as output_file:
        output_file.write("N")
        sys_exit(0)

path_to_vertex: List[int] = []
current_vertex = end_vertex
while current_vertex != start_vertex:
    path_to_vertex.append(current_vertex + 1)
    current_vertex = previous_vertex[current_vertex]
path_to_vertex.append(start_vertex + 1)
path_to_vertex.reverse()

with open("out.txt", "w") as output_file:
    output_file.write("Y\n")
    output_file.write(' '.join(str(path_to_vertex)[1:-1].split(', ')) + '\n')

    accumulator = 0
    for i in range(len(path_to_vertex) - 1):
        accumulator += next_vertices[path_to_vertex[i] - 1][path_to_vertex[i + 1] - 1]
    output_file.write(f"{accumulator}\n")
