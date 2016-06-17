import find_all_sts as fsts
import networkx as nx

# Test minor capability:
graph = fsts.MinorGraph()
graph.add_edge(1,2)
graph.add_edge(2,3)
graph.add_edge(1,3)

# Test graph minor
# print graph.to_string()
# graph2 = fsts.get_minor(graph,1,2)
# print graph2.to_string()

# Test all bridges:
graph.add_edge(1,4)
# print graph.to_string()
# bridges = fsts.get_bridges(graph)
# for b in bridges:
#     print b
# print graph.to_string()

# Test spanning trees:
graph.add_edge(2,4)
graph.add_edge(3,4)

K5 = nx.complete_graph(8)
G = fsts.MinorGraph(K5)
print G.to_string()
timedict, trees = fsts.get_spanningtrees(G)
print trees, len(trees)
print timedict
