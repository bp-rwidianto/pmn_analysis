import networkx as nx
import community as community_louvain
from collections import defaultdict, Counter
import streamlit as st

# Enforce cluster minimum members
def merge_small_communities(graph, partition, min_size=3):
    # Build inverse mapping: community -> list of nodes
    community_to_nodes = defaultdict(list)
    for node, comm in partition.items():
        community_to_nodes[comm].append(node)

    # Identify small communities
    small_communities = {comm for comm, nodes in community_to_nodes.items() if len(nodes) < min_size}

    # Create a fresh copy of the partition
    new_partition = dict(partition)

    for comm in small_communities:
        for node in community_to_nodes[comm]:
            # Find neighboring communities (excluding its own)
            neighbor_comms = Counter(
                new_partition[neighbor]
                for neighbor in graph.neighbors(node)
                if new_partition[neighbor] not in small_communities
            )

            if neighbor_comms:
                # Choose most common neighboring large community
                target_comm = neighbor_comms.most_common(1)[0][0]
            else:
                # If no valid neighbors, assign to the largest community
                large_communities = {
                    c: len(n) for c, n in community_to_nodes.items()
                    if c not in small_communities
                }
                target_comm = max(large_communities, key=large_communities.get)

            new_partition[node] = target_comm

    return new_partition

# Enforce cluster maximum number of members
def split_large_communities(graph, partition, max_size=50):
    # Step 1: Group nodes by communities
    comm_to_nodes = defaultdict(list)
    for node, comm in partition.items():
        comm_to_nodes[comm].append(node)

    new_partition = {}
    next_comm_id = max(partition.values()) + 1  # starting point for new cluster IDs

    for comm, nodes in comm_to_nodes.items():
        if len(nodes) <= max_size:
            # Keep the small or correctly-sized community as is
            for node in nodes:
                new_partition[node] = comm
        else:
            # Too large: split using Louvain on the subgraph
            subgraph = graph.subgraph(nodes)
            sub_partition = community_louvain.best_partition(subgraph)

            # Assign new community IDs
            sub_groups = defaultdict(list)
            for node, sub_comm in sub_partition.items():
                sub_groups[sub_comm].append(node)

            for sub_nodes in sub_groups.values():
                if len(sub_nodes) <= max_size:
                    for node in sub_nodes:
                        new_partition[node] = next_comm_id
                    next_comm_id += 1
                else:
                    # Recursively split again
                    temp_partition = split_large_communities(graph.subgraph(sub_nodes), {n: 0 for n in sub_nodes}, max_size)
                    for node, final_comm in temp_partition.items():
                        new_partition[node] = next_comm_id + final_comm
                    next_comm_id += max(temp_partition.values()) + 1

    return new_partition

# Get data item of a specific person
def get_item(df_data_items, name):
    return_cols = [x for x in df_data_items.columns if ("Competitor_" not in x) and ("Topic_" not in x)]
    return df_data_items.loc[df_data_items[df_data_items.FullName == name].index[0]][return_cols]

# Retrieve members of a cluster
def nodes_member(agg_graph, node):
    edges = list(agg_graph.edges(node))
    members = [node]
    for edge in edges:
        members.append(edge[1])
    return members

# Highlight community by removing non-edges of the highlighted community
def highlight_community(graph, aggregated_graph, highlight_communities, df_data_items):
    
    # Retrieve nodes arround highlighted communities
    # highlight_communities = highlight_communities
    highlight_community = []
    
    # for highlight_community_ in highlight_communities:
    
    highlight_community.extend(nodes_member(aggregated_graph, highlight_communities))
        
    highlight_community = list(set(highlight_community))       

    # Filter out non-highlight community from base graph
    filter_out_communities_progress_bar = st.progress(0, text="Filtering non-highlight community from graph...")
    nodes_to_include = []
    for i in range(0, len(df_data_items)):
        filter_out_communities_progress_bar.progress(i / len(df_data_items), text="Filtering non-highlight community from graph...")
        row = df_data_items.iloc[i]
        if row["cluster"] in highlight_community:
            nodes_to_include.append(row["author_id"])
    
    filter_out_nodes_progress_bar = st.progress(0, text="Filtering non-highlight nodes from graph...")
    graph_highlight = graph.copy()
    for node in list(graph_highlight.nodes):
        filter_out_nodes_progress_bar.progress(list(graph_highlight.nodes).index(node) / len(list(graph_highlight.nodes)), text="Filtering non-highlight nodes from graph...")
        if str(node) not in nodes_to_include:
            graph_highlight.remove_node(int(node))

    # Prepare cmap for color highlight
    cmap_highlights = {}
    cmap = {
        '0': '#fbb4ae',
        '1': '#b3cde3',
        '2': '#ccebc5',
        '3': '#decbe4',
        '4': '#fed9a6',
        '5': '#ffffcc',
        '6': '#e5d8bd',
        '7': '#fddaec'
    }

    for i, community in enumerate(highlight_community):
        cmap_highlights[community] = cmap[str(i%7)]
        
    # Get information of nodes for highlight communities only
    df_highlight = df_data_items[df_data_items["cluster"].isin(highlight_community)]
    competitors = [x for x in df_highlight.columns if x not in ["author_id", "FullName", "publications", "countries", "bp_user", "active_author", "mention_bp", "sub-cluster", "cluster"]]
    node_information = {}
    
    adding_node_info_progress_bar = st.progress(0, text="Creating node information references...")
    for i in range(0, len(df_highlight)):
        adding_node_info_progress_bar.progress(i/len(df_highlight), text="Creating node information references...")
        row = df_highlight.iloc[i]
        core_information = {
            "item_id": row["author_id"],
            "sub-cluster": row["sub-cluster"],
            "cluster": row["cluster"],
            "name": row["FullName"],
            "publications": row["publications"],
            "countries": row["countries"],
            "active_author": row["active_author"],
            "bp_user": row["bp_user"],
            "mention_bp": row["mention_bp"],
            "manufacturers": row["manufacturerCount"],
            "color": cmap_highlights[int(row["cluster"])]
        }
        
        competitor_dict = {}
        for competitor in competitors:
            competitor_dict[competitor] = row[competitor]

        core_information.update(competitor_dict)
        node_information[row["author_id"]] = core_information

    return graph_highlight, highlight_community, node_information

def highlight_author(graph, aggregated_graph, highlight_author, df_data_items):

    # Filter out non-highlight community from base graph
    author_data = df_data_items[df_data_items["author_id"] == str(highlight_author)]
    print("author_data", author_data)
    author_cluster = author_data["cluster"]
    neighbors =  [str(element) for element in list(graph.neighbors(int(highlight_author)))]
    neighbors_data = df_data_items[df_data_items["author_id"].isin(neighbors)]
    
    nodes_to_include = [highlight_author]
    for i in range(0, len(df_data_items)):
        row = df_data_items.iloc[i]
        # print(row["cluster"])
        if str(row["cluster"]) == str(author_cluster):
            nodes_to_include.append(row["author_id"])

    nodes_to_include = nodes_to_include + neighbors
    
    graph_highlight = graph.copy()
    for node in list(graph_highlight.nodes):
        if str(node) not in nodes_to_include:
            graph_highlight.remove_node(int(node))

    # Prepare cmap for color highlight
    cmap_highlights = {}
    cmap = {
        '0': '#fbb4ae',
        '1': '#b3cde3',
        '2': '#ccebc5',
        '3': '#decbe4',
        '4': '#fed9a6',
        '5': '#ffffcc',
        '6': '#e5d8bd',
        '7': '#fddaec'
    }
        
    # Get information of nodes for highlight communities only
    df_highlight = df_data_items[df_data_items["author_id"].isin([str(element) for element in list(graph_highlight.nodes)])]
    competitors = [x for x in df_data_items.columns if "Competitor_" in x]
    topics = [x for x in df_data_items.columns if "Topic_" in x]
    node_information = {}
    
    for i in range(0, len(df_highlight)):
        row = df_highlight.iloc[i]
        
        if str(int(row["cluster"])) == str(int(author_cluster)):
            color_ = cmap['0']
        else:
            color_ = cmap['1']
            
        core_information = {
            "item_id": row["author_id"],
            "sub-cluster": row["sub-cluster"],
            "cluster": row["cluster"],
            "name": row["FullName"],
            "publications": row["publications"],
            "countries": row["countries"],
            "active_author": row["active_author"],
            "bp_user": row["bp_user"],
            "mention_bp": row["mention_bp"],
            "manufacturers": row["manufacturerCount"],
            "color": color_
        }
        
        competitor_dict = {}
        for competitor in competitors:
            competitor_dict[competitor] = row[competitor]

        core_information.update(competitor_dict)

        topic_dict = {}
        for topic in topics:
            topic_dict[topic] = row[topic]

        core_information.update(topic_dict)
        
        node_information[row["author_id"]] = core_information

    # Alignment with available information
    for node_ in list(graph_highlight.nodes()):
        if str(node_) not in list(node_information.keys()):
            graph_highlight.remove_node(node_)

    return graph_highlight, node_information
