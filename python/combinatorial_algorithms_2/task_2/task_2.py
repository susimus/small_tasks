from sys import exit as sys_exit
from re import sub as re_sub


with open("in.txt") as input_file:
    n = int(input_file.readline())

    adjacency_matrix = []

    for i in range(n):
        matrix_line = re_sub(' +', ' ', input_file.readline()).split(" ")
        adjacency_matrix.append([])

        for j in range(n):
            adjacency_matrix[i].append(int(matrix_line[j]))

# vector < vector<int> > g;  # adjacency_matrix
# const int INF = 32767; // значение "бесконечность"
#
# // алгоритм
# vector<bool> used (n);
# vector<int> min_e (n, INF), sel_e (n, -1);
# min_e[0] = 0;
# for (int i=0; i<n; ++i) {
# 	int v = -1;
# 	for (int j=0; j<n; ++j)
# 		if (!used[j] && (v == -1 || min_e[j] < min_e[v]))
# 			v = j;
# 	if (min_e[v] == INF) {
# 		cout << "No MST!";
# 		exit(0);
# 	}
#
# 	used[v] = true;
# 	if (sel_e[v] != -1)
# 		cout << v << " " << sel_e[v] << endl;
#
# 	for (int to=0; to<n; ++to)
# 		if (g[v][to] < min_e[to]) {
# 			min_e[to] = g[v][to];
# 			sel_e[to] = v;
# 		}
# }
