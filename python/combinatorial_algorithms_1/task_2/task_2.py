from sys import exit as sys_exit
from re import sub as re_sub


with open("in.txt") as input_file:
    rows_count = int(input_file.readline())
    columns_count = int(input_file.readline())

    if rows_count < 3 or columns_count < 3:
        with open("out.txt", "w") as output_file:
            output_file.write("N")

        print("Rows count < 3 or columns count < 3")
        sys_exit(0)

    labyrinth_matrix = []

    for i in range(rows_count):
        matrix_line = re_sub(' +', ' ', input_file.readline()).split(" ")
        labyrinth_matrix.append([])

        for j in range(columns_count):
            labyrinth_matrix[i].append(matrix_line[j])

    start_vertex = tuple(int(coordinate) - 1
                         for coordinate in re_sub(' +', ' ', input_file.readline()).split(" "))
    finish_vertex = tuple(int(coordinate) - 1
                          for coordinate in re_sub(' +', ' ', input_file.readline()).split(" "))

    assert len(start_vertex) == len(finish_vertex) == 2, \
        "Start or/and finish coordinates in wrong format"

    assert (0 <= start_vertex[0] < len(labyrinth_matrix)
            and 0 <= start_vertex[1] < len(labyrinth_matrix[0])), "Start vertex out of bounds"
    assert (0 <= finish_vertex[0] < len(labyrinth_matrix)
            and 0 <= finish_vertex[1] < len(labyrinth_matrix[0])), "Finish vertex out of bounds"

    if labyrinth_matrix[finish_vertex[0]][finish_vertex[1]] == "1":
        with open("out.txt", "w") as output_file:
            output_file.write("N")

        print("Finish vertex is '1', not accessible")
        sys_exit(0)

previous_vertex = dict()
visited_vertices = set(start_vertex)  # {(0, 1), (0, 2), ...}
deep_search_stack = [start_vertex]

while len(deep_search_stack) != 0:
    current_vertex = deep_search_stack.pop()

    for position_shift in [(0, -1), (0, 1), (-1, 0), (1, 0)][::-1]:
        shifted_vertex = (
            current_vertex[0] + position_shift[0],
            current_vertex[1] + position_shift[1])

        if shifted_vertex == finish_vertex:
            previous_vertex[finish_vertex] = current_vertex
            visited_vertices.add(finish_vertex)
            deep_search_stack.clear()
            break

        # checking element accessibility
        if (shifted_vertex not in visited_vertices
                and 0 <= shifted_vertex[0] < len(labyrinth_matrix)
                and 0 <= shifted_vertex[1] < len(labyrinth_matrix[0])
                and labyrinth_matrix[shifted_vertex[0]][shifted_vertex[1]] == "0"):
            previous_vertex[shifted_vertex] = current_vertex
            deep_search_stack.append(shifted_vertex)
            visited_vertices.add(shifted_vertex)

if finish_vertex not in visited_vertices:
    with open("out.txt", "w") as output_file:
        output_file.write("N")

    sys_exit(0)

output_vertices = [f'{finish_vertex[0] + 1} {finish_vertex[1] + 1}\n']
current_vertex = previous_vertex[finish_vertex]
while current_vertex != start_vertex:
    output_vertices.append(f'{current_vertex[0] + 1} {current_vertex[1] + 1}\n')
    current_vertex = previous_vertex[current_vertex]

output_vertices.append(f'{start_vertex[0] + 1} {start_vertex[1] + 1}\n')
output_vertices.reverse()

with open("out.txt", "w") as output_file:
    output_file.write("Y\n")
    output_file.writelines(output_vertices)
