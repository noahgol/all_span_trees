import networkx as nx
from copy import deepcopy

def sortedtup(a,b):
    return (min(a,b),max(a,b))

# Modification of nx.contracted_edge to work with keys in MultiGraphs
def contracted_edge_multi(G, edge, self_loops=True):
    if not G.has_edge(*edge):
        raise ValueError('Edge {0} does not exist in graph G; cannot contract'
                         ' it'.format(edge))
    return contracted_nodes_multi(G, *edge, self_loops=self_loops)

# Modification of nx.contracted_nodes to work with keys in MultiGraphs
# Here G must be a nx.MultiGraph
# TODO: figure out what G.copy() does (aka deepcopy(G)), to figure out where the bug was!!
def contracted_nodes_multi(G, u, v, self_loops=True):
    H = G.copy()
    if H.is_directed():
        in_edges = ((w, u, k, d) for w, x, k, d in G.in_edges(v, keys=True, data=True)
                    if self_loops or w != u)
        out_edges = ((u, w, k, d) for x, w, k, d in G.out_edges(v, keys=True, data=True)
                     if self_loops or w != u)
        new_edges = chain(in_edges, out_edges)
    else:
        new_edges = ((u, w, k, d) for x, w, k, d in G.edges(v, keys=True, data=True)
                     if self_loops or w != u)
    v_data = H.node[v]
    H.remove_node(v)
    H.add_edges_from(new_edges)
    if 'contraction' in H.node[u]:
        H.node[u]['contraction'][v] = v_data
    else:
        H.node[u]['contraction'] = {v: v_data}
    return H

class MinorGraph(nx.MultiGraph):
    hidden_edges = []

    # Here G is an instance of an nx.MultiGraph
    def __init__(self,G=None):
        super(self.__class__,self).__init__()
        if not G is None:
            self.add_nodes_from(G.nodes(data=True))
            # See if G is MultiGraph or just graph
            try:
                self.add_edges_from(G.edges(keys=True, data=True))
            except TypeError:
                self.add_edges_from(G.edges(data=True))

    def add_edge(self,u,v,key=None,attr_dict=None,**attr):
        if key is None:
            super(self.__class__,self).add_edge(u,v,sortedtup(u,v),attr_dict,**attr)
        else:
            super(self.__class__,self).add_edge(u,v,key,attr_dict,**attr)

    def remove_edge_hidden(self,u,v,key=None):
        super(self.__class__,self).remove_edge(u,v,key=key)
        self.hidden_edges.append(key)

    def get_hidden(self):
        return self.hidden_edges

    def set_hidden(self, hiddens):
        self.hidden_edges = hiddens

    def append_hidden(self, hidden):
        self.hidden_edges.append(hidden)

    def to_string(self):
        s = "{Edges : "
        s += str(self.edges(keys=True))
        s += ", Hidden edges: "
        s += str(self.hidden_edges)+ "}"
        return s

# Here graph is a MinorGraph
# Precondition: i < j and (i,j) is an edge of G
def get_minor(graph,i,j,key):
    contracted_graph = contracted_edge_multi(graph,(i,j),False)
    G = MinorGraph(contracted_graph)
    G.set_hidden(deepcopy(graph.get_hidden()))
    G.append_hidden(key)
    return G

def get_bridges(graph):
    all_edges = graph.edges(keys=True,data=True)
    for e in all_edges:
        graph.remove_edge(*e[:-1])
        removed_comps = nx.number_connected_components(graph)
        graph.add_edge(*e) # Will maintain the original key associated with this edge
        if nx.number_connected_components(graph) < removed_comps:
            yield e

def remove_bridges(graph):
    all_bridges = get_bridges(graph)
    for bridge in all_bridges:
        graph.remove_edge_hidden(*bridge[:-1])

def get_spanningtrees(graph):
    graph_stack = [graph]
    spanning_trees = []
    while graph_stack:
        # print "***", [H.to_string() for H in graph_stack]
        G = graph_stack.pop()
        remove_bridges(G)
        edges_iter = G.edges_iter(data=True,keys=True)
        e = next(edges_iter,None) # Know that e will not be a branch
        # print "Next edge: ", e
        if e is None:
            spanning_trees.append(G)
        else:
            G1 = get_minor(G,*e[:-1]) # Will automatically make deep copy of G
            G2 = G.copy()
            G2.remove_edge(*e[:-1])
            graph_stack += [G1, G2]
    return [T.get_hidden() for T in spanning_trees]
