from sys import exit as sys_exit
from collections import deque
from re import sub as re_sub


with open("in.txt") as input_file:
    vertices_count = int(input_file.readline())

    if vertices_count < 3:
        with open("out.txt", "w") as output_file:
            output_file.write("A")
        sys_exit(0)

    adjacency_matrix = []

    for i in range(vertices_count):
        matrix_line = re_sub(' +', ' ', input_file.readline()).split(" ")
        adjacency_matrix.append([])

        for j in range(vertices_count):
            adjacency_matrix[i].append(int(matrix_line[j]))

previous_vertex = [-1 for i in range(vertices_count)]
visited_vertices = set()
broad_search_queue = deque([0])

while len(visited_vertices) != vertices_count:
    current_vertex = -1
    if len(broad_search_queue) == 0:
        for vertex in range(vertices_count):
            if vertex not in visited_vertices:
                current_vertex = vertex
                break

        assert current_vertex != -1, "Failed when resolving 'current_vertex'"
    else:
        current_vertex = broad_search_queue.popleft()

    for vertex in range(vertices_count):
        if (adjacency_matrix[current_vertex][vertex] == 1 and
                vertex != previous_vertex[current_vertex]):
            if vertex not in visited_vertices:
                broad_search_queue.append(vertex)
                previous_vertex[vertex] = current_vertex
            else:
                path_current_vertex = deque([current_vertex])
                path_vertex = deque([vertex])

                while (previous_vertex[path_vertex[0]] != -1 or
                        previous_vertex[path_current_vertex[0]] != -1):
                    if previous_vertex[path_vertex[0]] != -1:
                        path_vertex.appendleft(previous_vertex[path_vertex[0]])
                    if previous_vertex[path_current_vertex[0]] != -1:
                        path_current_vertex.appendleft(previous_vertex[path_current_vertex[0]])

                intersection_length = len(
                    set.intersection(set(path_vertex), set(path_current_vertex)))
                cycle_vertices = sorted(
                    list(path_vertex)[intersection_length - 1:] +
                    list(path_current_vertex)[intersection_length:])
                cycle_vertices = [element + 1 for element in cycle_vertices]

                with open("out.txt", "w") as output_file:
                    output_file.write("N\n")
                    output_file.write(str(sorted(cycle_vertices))[1:-1])
                sys_exit(0)

    visited_vertices.add(current_vertex)

assert len(broad_search_queue) == 0

with open("out.txt", "w") as output_file:
    output_file.write("A")
sys_exit(0)
