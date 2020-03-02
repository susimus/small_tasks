from typing import List, Set, Tuple, Deque
from collections import deque


with open("in.txt") as input_handle:
    n: int = int(input_handle.readline())
    labyrinth: List[str] = []

    for i in range(n):
        labyrinth.append(input_handle.readline())

used: Set[Tuple[int, int]] = {(0, 0), (n - 1, n - 1)}
bfs_queue: Deque[Tuple[int, int]] = deque()
total_price: int = 0

for cell in [(0, 1), (1, 0), (n - 1, n - 2), (n - 2, n - 1)]:
    if labyrinth[cell[0]][cell[1]] == '.':
        bfs_queue.append(cell)
        used.add(cell)

    elif labyrinth[cell[0]][cell[1]] == '+':
        total_price += 9

while len(bfs_queue) != 0:
    current_cell: Tuple[int, int] = bfs_queue.popleft()

    adjacent_vertices: List[Tuple[int, int]] = (
        [(current_cell[0] + 1, current_cell[1]),
         (current_cell[0] - 1, current_cell[1]),
         (current_cell[0], current_cell[1] + 1),
         (current_cell[0], current_cell[1] - 1)])

    for cell in adjacent_vertices:
        if (cell[0] >= n or cell[0] < 0 or cell[1] >= n or cell[1] < 0
                or labyrinth[cell[0]][cell[1]] == '+'):
            total_price += 9

        elif labyrinth[cell[0]][cell[1]] == '.' and cell not in used:
            bfs_queue.append(cell)
            used.add(cell)

with open('out.txt', 'w') as output_handle:
    output_handle.write(str(total_price))
