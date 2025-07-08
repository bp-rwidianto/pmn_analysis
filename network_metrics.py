import networkx as nx

# Degree centrality
def metrics_degree_centrality(graph):
    return nx.degree_centrality(graph)
# Betwenness centrality
def metrics_betweenness_centrality(graph):
    return nx.betweenness_centrality(graph)

# Closeness centrality
def metrics_closeness_centrality(graph):
    return nx.closeness_centrality(graph)

# EigenCentrality
def metrics_eigenvector_centrality(graph):
    return nx.eigenvector_centrality(graph)

# PageRank
def metrics_pagerank(graph):
    return nx.pagerank(graph)
