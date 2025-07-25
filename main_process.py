from supporting_functions import *
from network_metrics import *

import pandas as pd
import numpy as np
import re

import networkx as nx
import matplotlib.pyplot as plt
import random
from tqdm import tqdm

def handle_data_input(network_data, node_data):

    try:
    
        # Handling Network Data
        ## Store network information in dataframe
        df_network = pd.DataFrame(network_data)

        ## Aggregate link informations
        df_edges = pd.DataFrame(network_data)
        df_edges["edge"] = df_edges.apply(lambda x: tuple(x["edge"]), axis = 1)
        df_edges = df_edges.groupby("edge")[["partial_strength", "full_strength"]].agg("sum").reset_index()
        df_edges["node_1"] = df_edges.apply(lambda x: x["edge"][0], axis = 1)
        df_edges["node_2"] = df_edges.apply(lambda x: x["edge"][1], axis = 1)

        ## Convert links into dataframe
        df_data_links = df_edges[["node_1", "node_2", "full_strength"]]

        # Handling Node Data
        ## Store node information in dataframe
        df_data_items = pd.DataFrame(node_data)

        ## Retrieve competitors and topics data for later flagging
        competitors = [re.sub("Competitor_", "", x) for x in df_data_items.columns if "Competitor_" in x]
        topics = [re.sub("Topic_", "", x) for x in df_data_items.columns if "Topic_" in x]

        return df_network, df_data_links, df_data_items, competitors, topics

    except: return None, None, None, None, None

def main_analysis(df_network, df_data_links, df_data_items, competitors, topics):

    # Check input variables
    if df_network is None:
        return None, None, None, None, None
    else:

        # Create network edges
        edges = []

        progress_bar = tqdm(range(0, len(df_data_links)), desc="Generating network edges...")
        for i in range(0, len(df_data_links)):
            progress_bar.update(1)
            link = df_data_links.iloc[i]
            edges.append([int(link["node_1"]), int(link["node_2"])])

        progress_bar.close()

        # Create the graph and add the edges
        graph = nx.Graph()
        graph.add_edges_from(edges)

        # Perform node clustering based on network graph
        # 1. Run Louvain
        partition = community_louvain.best_partition(graph)

        # 2. Post-process to enforce min size and max size
        partition = merge_small_communities(graph, partition, min_size=3)
        partition = split_large_communities(graph, partition, max_size=50)

        # 3. Visualization (coloring)
        unique_communities = list(set(partition.values()))
        color_map = {comm: i for i, comm in enumerate(unique_communities)}
        node_colors = [color_map[partition[node]] for node in graph.nodes()]
        communities = partition

        # Create a new graph where each community is represented as a single node
        aggregated_graph = nx.Graph()
        community_map = {}

        # Create a mapping from community to a unique node in the aggregated graph
        for node, community in communities.items():
            if community not in community_map:
                community_map[community] = len(community_map)
                aggregated_graph.add_node(community_map[community])

        # Add edges between communities if they are connected in the original graph
        for edge in graph.edges():
            node1, node2 = edge
            community1 = community_map[communities[node1]]
            community2 = community_map[communities[node2]]
            if community1 != community2:
                aggregated_graph.add_edge(community1, community2)

        # Visualize the aggregated graph
        fig_total_network, ax_0 = plt.subplots(figsize=(12, 12))
        pos = nx.spring_layout(aggregated_graph, seed=42)
        nx.draw(
            aggregated_graph, pos, with_labels=True, node_color='lightgreen',
            node_size=500, font_size=8, font_color='black', edge_color='gray'
        )

        # ax_0.title("Aggregated Graph by Community", fontsize=14)

        # Add cluster information to data items
        df_data_items["sub-cluster"] = df_data_items.apply(lambda x: communities[int(x["author_id"])] if int(x["author_id"]) in communities.keys() else None, axis = 1)
        df_data_items["cluster"] = df_data_items.apply(lambda x: community_map[communities[int(x["author_id"])]]  if int(x["author_id"]) in communities.keys() else None, axis = 1)
        df_data_items["active_author"] = df_data_items.apply(lambda x: True  if int(x["active_author"]) > 0 else False, axis = 1)
        df_data_items = df_data_items.dropna()
        df_data_items.head()
        print(f"{len(list(aggregated_graph.nodes()))} communities for analysis\n{len(list(graph.nodes()))} author in clusters")

        # # Perform network analysis
        # degree_centrality = metrics_degree_centrality(graph)
        # betweenness_centrality = metrics_betweenness_centrality(graph)
        # closeness_centrality = metrics_closeness_centrality(graph)
        # eigenvector_centrality = metrics_eigenvector_centrality(graph)
        # pagerank = metrics_pagerank(graph)

        # df_data_items["author_id_str"] = df_data_items["author_id"].astype(int)

        # df_data_items["degree_centrality"] = df_data_items["author_id_str"].map(degree_centrality).astype(float).round(7)
        # df_data_items["betweenness_centrality"] = df_data_items["author_id_str"].map(betweenness_centrality).astype(float).round(7)
        # df_data_items["closeness_centrality"] = df_data_items["author_id_str"].map(closeness_centrality).astype(float).round(7)
        # df_data_items["eigenvector_centrality"] = df_data_items["author_id_str"].map(eigenvector_centrality).astype(float).round(7)
        # df_data_items["pagerank"] = df_data_items["author_id_str"].map(pagerank).astype(float).round(7)
        # df_data_items = df_data_items.drop(columns=["author_id_str"])

        # Top-down clean up from node with more than 3 edges
        major_nodes = []
        neighbors = []

        progress_bar = tqdm(range(0, len(list(aggregated_graph.nodes()))), desc="Identifying major clusters...")
        for node in list(aggregated_graph.nodes()):
            progress_bar.update(1)
            if len(list(aggregated_graph.neighbors(node))) >= 3:
                neighbors.extend(list(aggregated_graph.neighbors(node)))
                major_nodes.append(node)
        progress_bar.close()

        neighbors = list(set(neighbors))
        major_nodes = list(set(major_nodes))
        sub_nodes = []
        mini_nodes = []

        for neighbor in neighbors:
            if neighbor not in major_nodes:
                sub_nodes.append(neighbor)

        for node in sub_nodes:
            mini_nodes.extend(list(aggregated_graph.neighbors(node)))

        sub_nodes = list(set(sub_nodes))
        mini_nodes = list(set(mini_nodes))

        print(f'Number of Major Nodes: {len(major_nodes)}')
        print(f'Number of Sub Nodes: {len(sub_nodes)}')

        main_nodes = list(set(major_nodes + sub_nodes + mini_nodes))
        print(f'Number of Main Nodes: {len(main_nodes)}')

        # Clean local clusters without neighbor
        removed_nodes = []

        progress_bar = tqdm(range(0, len(list(aggregated_graph.nodes()))), desc="Removing isolated clusters...")
        for node in list(aggregated_graph.nodes()):
            progress_bar.update(1)
            if node not in main_nodes:
                aggregated_graph.remove_node(node)
                removed_nodes.append(node)
        progress_bar.close()

        # Visualize the aggregated graph
        fig_main_network, ax_1 = plt.subplots(figsize=(12, 12))
        pos = nx.spring_layout(aggregated_graph, seed=42)
        nx.draw(
            aggregated_graph, pos, with_labels=True, node_color='lightgreen',
            node_size=500, font_size=8, font_color='black', edge_color='gray'
        )

        # ax_1.title("Aggregated Graph by Community", fontsize=14)

        return graph, aggregated_graph, df_data_items, fig_total_network, fig_main_network
