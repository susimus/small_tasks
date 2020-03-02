from re import sub as re_sub
from typing import List, Tuple, Optional
from sys import exit as sys_exit


if __name__ == '__main__':
    with open("in.txt") as input_file:
        parts_sizes: List[str] = input_file.readline().split(' ')
        K: int = int(parts_sizes[0])
        L: int = int(parts_sizes[1])

        if K != L:
            with open('out.txt', 'w') as output_handle:
                output_handle.write('N\n1')

            sys_exit()

        graph: List[List[int]] = (
            [[0 for _ in range(L)] for _ in range(K)])

        for i in range(K):
            adjacency_list: List[str] = (
                re_sub(' +', ' ', input_file.readline()).split())

            if len(adjacency_list) == 1:
                with open('out.txt', 'w') as output_handle:
                    output_handle.write(f'N\n{i + 1}')

                sys_exit()

            for j in range(len(adjacency_list) - 1):
                # Вершины на входе начинаются с 1 (?), поэтому '- 1'
                graph[i][int(adjacency_list[j]) - 1] = 1

    # Форд-Фалкенсон, f-доп цепи через поиск в глубину
    #
    # Поток в сети, полученной из двудольного графа, подчиняется нескольким
    # правилам:
    # * Поток либо 1, либо 0
    # * Если поток течет через ребро (x, y), то через ребра (s, x) и (y, t)
    #   поток тоже обязательно течет
    # * f-доп цепи не смогут из насыщенной вершины из X сделать не
    #   насыщенную. Если при поиске f-доп цепи был сделан шаг назад в
    #   сторону множества X, то все равно для построения (s, t)-цепи
    #   придется сделать ещё один шаг вперед, чтобы достичь вершины t. Таким
    #   образом, поток будет просто перенаправлен, а не ликвидирован,
    #   для вершины из X (в общем-то, поток в принципе не может быть
    #   ликвидирован где-то в смысле "уменьшен". При построении f-доп цепи
    #   поток всегда увеличивается. Тонкое место в том, что поток в сети из
    #   двудольного графа не может быть перенаправлен так, чтобы насыщенная
    #   вершина из X стала не насыщенной)
    # * Если f-доп цепь не может быть построена для вершины из X, то это
    #   сразу же означает, что вершина не может быть насыщена вообще.
    #
    # Таким образом, имеет смысл строить f-доп цепи только через вершины
    # долей, подразумевая, что мы каждый раз проходим через вершины s и t
    #
    # (Действительно, при таком построении, очередная f-доп цепь ничем не
    # отличается от M-черед цепи)

    # Поток может быть либо 0, либо 1
    #
    # flow[i][j] => поток на (i, j) ребре. i из X, j из Y
    flow: List[List[int]] = (
            [[0 for _ in range(L)] for _ in range(K)])

    for i in range(K):
        # В тапле:
        # 1) Принадлежность вершины к доле: 1 (X) или 2 (Y)
        # 2) Сама вершина
        # 3) Вершина, откуда поиск пришел. [None] для начальной вершины поиска
        dfs_stack: List[Tuple[int, int, Optional[int]]] = [(1, i, None)]

        used_x: List[int] = []
        used_y: List[int] = []

        # f-доп (s, t)-путь, полученный в результате поиска в глубину
        #
        # ОБЯЗАТЕЛЬНО нужно проверять поток на всей протяженности получившегося
        # пути! Поток на ребрах (s, x) и (y, t) ВКЛЮЧИТЕЛЬНО:
        # * Чтобы проверить (s, x) ребро, достаточно начать поиск в глубину из
        #   ещё не насыщенной вершины x из Х
        # * Чтобы проверить (y, t) ребро, достаточно посмотреть наличие потока
        #   для вершины y
        #
        # 0, 2, 4, ... -> индексы вершин из X
        # 1, 3, 5, ... -> индексы вершин из Y
        s_t_path: List[int] = []

        s_t_path_was_created: bool = False

        while len(dfs_stack) != 0:
            # Взять верхнюю вершину из стека в строящийся (s, t) путь,
            # если она смежна с последней вершиной в этом пути
            if len(s_t_path) == 0:
                s_t_path.append(dfs_stack.pop()[1])

            elif (dfs_stack[-1][0] == 1 and len(s_t_path) % 2 == 0
                    and dfs_stack[-1][2] == s_t_path[-1]):
                s_t_path.append(dfs_stack.pop()[1])

            elif (dfs_stack[-1][0] == 2 and len(s_t_path) % 2 == 1
                    and dfs_stack[-1][2] == s_t_path[-1]):
                s_t_path.append(dfs_stack.pop()[1])

            else:
                s_t_path.pop()
                continue

            # Проверка, является ли текущий путь f-дополняющим
            #
            # Путь заканчивается в Y
            # И
            # Поток в последнюю вершину пути НЕ втекает
            if (len(s_t_path) % 2 == 0
                    and not any(
                        [flow[v][s_t_path[-1]] == 1 for v in range(K)])):
                s_t_path_was_created = True
                break

            current_vertex: int = s_t_path[-1]

            # Последняя вершина пути из X
            if len(s_t_path) % 2 == 1:
                # Ранее мы добавили эту вершину из стэка в строящийся путь.
                # Здесь мы точно знаем, что она из Х
                used_x.append(current_vertex)

                # Перебираем все ребра из последней в Y, чтобы добавить
                # подходящие в стек
                for j in range(L):
                    if (graph[s_t_path[-1]][j] == 1
                            and flow[s_t_path[-1]][j] == 0
                            and j not in used_y):
                        dfs_stack.append((2, j, s_t_path[-1]))

            # Последняя вершина пути из Y
            else:
                # Ранее мы добавили эту вершину из стэка в строящийся путь.
                # Здесь мы точно знаем, что она из Y
                used_y.append(current_vertex)

                # Перебираем все ребра из последней в X, чтобы добавить
                # подходящие в стек
                for j in range(K):
                    if (graph[j][s_t_path[-1]] == 1
                            and flow[j][s_t_path[-1]] == 1
                            and j not in used_x):
                        dfs_stack.append((1, j, s_t_path[-1]))

        if not s_t_path_was_created:
            with open('out.txt', 'w') as output_handle:
                output_handle.write('N\n' + str(i + 1))

            sys_exit()
        else:
            # Увеличиваем поток на прямых ребрах
            for j in range(0, len(s_t_path), 2):
                flow[s_t_path[j]][s_t_path[j + 1]] += 1

            # Уменьшаем поток на обратных ребрах
            for j in range(1, len(s_t_path) - 1, 2):
                flow[s_t_path[j + 1]][s_t_path[j]] -= 1

    with open('out.txt', 'w') as output_handle:
        output_handle.write('Y\n')

        for i in range(K):
            for j in range(L):
                if flow[i][j] == 1:
                    output_handle.write(str(j + 1) + ' ')

                    break
