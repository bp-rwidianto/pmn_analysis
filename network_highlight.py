from supporting_functions import *
import networkx as nx
from pyvis.network import Network
import streamlit as st

def highlight_community_pyvis(community_id, graph, aggregated_graph, df_data_items, competitors, topics):
    
    graph_highlight, highlight_communities, node_information = highlight_community(graph, aggregated_graph, community_id, df_data_items)

    # Create graph
    with st.spinner(text="Generating graph object...", show_time=True):
        nt = Network(height="700px", width="700px", bgcolor="#ffffff", font_color="black", select_menu=True, filter_menu=True, cdn_resources='remote')
        nt.from_nx(graph_highlight)
        nt.repulsion()
        st.success("Graph creation complete ✅", width="stretch")

    progress_bar = st.progress(0, text="Adding node information...")

    for node in list(graph_highlight.nodes()):
        progress_bar.progress(float(list(graph_highlight.nodes()).index(node) / len(list(graph_highlight.nodes()))), text="Adding node information...")
        nt.get_node(node)["sub-cluster"] = str(node_information[str(node)]["sub-cluster"])
        nt.get_node(node)["cluster"] = str(node_information[str(node)]["cluster"])
        nt.get_node(node)["label"] = str(f'{node_information[str(node)]["name"]}\n({nt.get_node(node)["id"]})')
        nt.get_node(node)["color"] = str(node_information[str(node)]["color"])
        nt.get_node(node)["publications"] = str(node_information[str(node)]["publications"])
        nt.get_node(node)["countries"] = str(node_information[str(node)]["countries"])
        nt.get_node(node)["active_author"] = str(node_information[str(node)]["active_author"])
        nt.get_node(node)["bp_user"] = str(node_information[str(node)]["bp_user"])
        nt.get_node(node)["mention_bp"] = str(node_information[str(node)]["mention_bp"])
        
        for competitor in competitors:
            nt.get_node(node)[f"Competitor_{competitor}"] = str(node_information[str(node)][f"Competitor_{competitor}"])
        for topic in topics:
            nt.get_node(node)[f"Topic_{topic}"] = str(node_information[str(node)][f"Topic_{topic}"])
    
    # Export graph visual
    nt.save_graph("assets/network.html")

    return nt

def highlight_author_pyvis(author_id, graph, aggregated_graph, df_data_items, competitors, topics):
    
    graph_highlight, node_information = highlight_author(graph, aggregated_graph, author_id, df_data_items)

    # Create graph
    with st.spinner(text="Generating graph object...", show_time=True):
        nt = Network(height="800px", width="1200", bgcolor="#ffffff", font_color="black", select_menu=True, filter_menu=True, cdn_resources='remote')
        nt.from_nx(graph_highlight)
        nt.repulsion()
        st.success("Graph creation complete ✅", width="stretch")

    progress_bar = st.progress(0, text="Adding node information...")

    for node in list(graph_highlight.nodes()):
        progress_bar.progress(float(list(graph_highlight.nodes()).index(node) / len(list(graph_highlight.nodes()))), text="Adding node information...")
        nt.get_node(node)["sub-cluster"] = str(node_information[str(node)]["sub-cluster"])
        nt.get_node(node)["cluster"] = str(node_information[str(node)]["cluster"])
        nt.get_node(node)["label"] = str(f'{node_information[str(node)]["name"]}\n({nt.get_node(node)["id"]})')
        nt.get_node(node)["color"] = str(node_information[str(node)]["color"])
        nt.get_node(node)["publications"] = str(node_information[str(node)]["publications"])
        nt.get_node(node)["countries"] = str(node_information[str(node)]["countries"])
        nt.get_node(node)["active_author"] = str(node_information[str(node)]["active_author"])
        nt.get_node(node)["bp_user"] = str(node_information[str(node)]["bp_user"])
        nt.get_node(node)["mention_bp"] = str(node_information[str(node)]["mention_bp"])

        for competitor in competitors:
            nt.get_node(node)[f"Competitor_{competitor}"] = str(node_information[str(node)][f"Competitor_{competitor}"])
        for topic in topics:
            nt.get_node(node)[f"Topic_{topic}"] = str(node_information[str(node)][f"Topic_{topic}"])
    progress_bar.empty()

    # Export graph visual
    nt.save_graph("assets/network.html")

    return nt
