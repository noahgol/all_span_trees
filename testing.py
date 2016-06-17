import find_all_sts as fsts
import networkx as nx

# Test minor capability:
graph = fsts.MinorGraph()
graph.add_edge(1,2)
graph.add_edge(2,3)
graph.add_edge(1,3)
print graph.to_string()
graph2 = fsts.get_minor(graph,1,2)
print graph2.to_string()
