import networkx as nx

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
# TODO: figure out what G.copy() does, to figure out where the bug was!!
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
    duplicates = dict()

    # Here G is an instance of an nx.MultiGraph
    def __init__(self,G=None):
        super(self.__class__,self).__init__()
        if not G is None:
            self.add_nodes_from(G.nodes(data=True))
            self.add_edges_from(G.edges(keys=True, data=True))
            self.duplicates = dict((sortedtup(*e),[sortedtup(*e)]) for e in G.edges())

    def add_edge(self,u,v,key=None,attr_dict=None,**attr):
        if key is None:
            super(self.__class__,self).add_edge(u,v,sortedtup(u,v),attr_dict,**attr)
        else:
            super(self.__class__,self).add_edge(u,v,key,attr_dict,**attr)
        self.duplicates[(sortedtup(u,v))] = [sortedtup(u,v)]

    def get_duplicates(self,dup=None):
        if dup is None:
            return self.duplicates
        elif dup in self.duplicates:
            return self.duplicates[dup]
        else:
            return None

    def set_duplicates(self, dups):
        self.duplicates = dups

    def get_hidden(self):
        return self.hidden_edges

    def set_hidden(self, hiddens):
        self.hidden_edges = hiddens

    # Here dup is a tuple containing the (i,neighb) pair (in sorted order)
    # third is a list of tuples representing edges
    def add_duplicates(self, dup, third):
        if dup in self.duplicates:
            self.duplicates[dup] += third
        else:
            self.duplicates[dup] = third

    def append_hidden(self, hidden):
        self.hidden_edges.append(hidden)

    def to_string(self):
        s = "{Edges : "
        s += str(self.edges(keys=True))
        s += ", Hidden edges: "
        s += str(self.hidden_edges)
        s += ", Duplicates: "
        s += str(self.duplicates) + "}"
        return s

# Here graph is a MinorGraph
# Precondition: i < j and (i,j) is an edge of G
def get_minor(graph,i,j):
    contracted_graph = contracted_edge_multi(graph,(i,j),False)
    G = MinorGraph(contracted_graph)
    G.set_hidden(graph.get_hidden())
    G.append_hidden((i,j))
    G.set_duplicates(graph.get_duplicates())

    # i_neighbs = set(graph.neighbors(i)) - {j}
    j_neighbs = set(graph.neighbors(j)) - {i}
    # for neighb in i_neighbs:
    #     G.add_duplicates(sortedtup(i,neighb),G.get_duplicates(sortedtup(i,neighb)))
    for neighb in j_neighbs:
        G.add_duplicates(sortedtup(i,neighb),G.get_duplicates(sortedtup(j,neighb)))
    return G
