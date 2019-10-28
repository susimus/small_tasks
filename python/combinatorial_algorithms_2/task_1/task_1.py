from typing import List, Tuple, Optional
from re import sub as re_sub


with open("in.txt") as input_file:
    n: int = int(input_file.readline())

    # In form of adjacency matrix
    graph: List[List[Optional[int]]] = [
        [None for _ in range(n)] for _ in range(n)]

    for i in range(n):
        matrix_line: List[str] = (
            re_sub(' +', ' ', input_file.readline()).split(" "))

        for j in range(n):
            graph[i][j] = int(matrix_line[j])
                                               
infinity: int = 32767
vertex_is_used: List[bool] = [False for _ in range(n)]

# Хранит вес ребра: это ребро является наименьшим по весу среди тех, которые
#   инцидентны вершине i и вершине из растущего дерева одновременно.
# Если вершина уже в остове, то вес = 0
min_edge_weight: List[int] = [infinity for _ in range(n)]
min_edge_weight[0] = 0
# Аналогично, но хранит вершину-конец такого ребра
min_edge_vertex: List[int] = [-1 for i in range(n)]

spanning_tree_edges: List[Tuple[int, int]] = []
spanning_tree_weight: int = 0

for i in range(n):
    v: int = -1

    # Подбираем вершину: она ещё не в остове И в [min_edge_weight] у такой
    #   вершины лежит минимальный вес
    for j in range(n):
        if (
                not vertex_is_used[j]
                and (v == -1 or min_edge_weight[j] < min_edge_weight[v])):
            v = j

    # Выше не нашли подходящую вершину => входящий граф не связен
    assert min_edge_weight[v] != infinity, "No MST"

    # Помечаем вершину как использованную
    vertex_is_used[v] = True

    # Проверка, что для выбранной вершины был отработан подбор нужного мин
    #   ребра
    if min_edge_vertex[v] != -1:
        spanning_tree_edges.append((v, min_edge_vertex[v]))

        spanning_tree_weight += min_edge_weight[v]

    # Подбираем нужные ребра для массивов [min_edge_weight] и [min_edge_vertex]
    for to in range(n):
        if graph[v][to] < min_edge_weight[to]:
            min_edge_weight[to] = graph[v][to]

            min_edge_vertex[to] = v

# In form of adjacency lists
result_tree: List[List[int]] = [list() for i in range(n)]

for edge in spanning_tree_edges:
    result_tree[edge[0]].append(edge[1])
    result_tree[edge[1]].append(edge[0])

with open('out.txt', 'w') as output:
    for adjacent_vertices in result_tree:
        for adjacent_vertex in sorted(adjacent_vertices):
            output.write(f'{adjacent_vertex + 1} ')

        output.write('0\n')

    output.write(str(spanning_tree_weight))
