from main_process import *
import streamlit as st
import json
import time

st.set_page_config(
    page_title="Network Analysis",
    page_icon="🏠",
    layout="centered"
)

# Content
st.title("Welcome to PubMed's Network Analysis Dashboard 📊")
st.sidebar.info("👋 Welcome!")

st.markdown(
    """
    In this dashboard, you can perform network analysis from the output of PubMed Publication Analysis main branch. To begin, please upload your files below:
"""
)
st.write("\n")

# Input form for file upload
col1, col2 = st.columns(2)

is_ready = False
is_analysis = False

network_edges_file = col1.file_uploader("Upload Network Edges File")
if network_edges_file is not None:
    json_string = network_edges_file.read()
    network_data = json.loads(json_string)

node_information_file = col2.file_uploader("Upload Node Information File")
if node_information_file is not None:
    json_string = node_information_file.read()
    node_data = json.loads(json_string)
st.write("\n")

# Action on submit
if st.button("Submit", type="primary", use_container_width=True):
    with st.spinner(text="Processing files...", show_time=True):
        time.sleep(1)
        if (network_edges_file is not None) and (node_information_file is not None):
            st.success("Files found! ✅", width="stretch")
            is_ready = True
        else:
            st.error("Some of the files are missing. Please upload the file before continue.", width="stretch")

    if is_ready:  
        with st.spinner(text="Now checking if the files are correct...", show_time=True, width="stretch"):
            df_network, df_data_links, df_data_items, competitors = handle_data_input(network_data, node_data)
            if df_network is None:
                st.error("You have uploaded a wrong file. Please upload the correct one, or contact administrator for more information.", width="stretch")
            else:
                st.success("Uploaded files are correct! ✅", width="stretch")
                is_analysis = True
    else:
        pass

    if is_analysis:
        with st.spinner(text="Performing analysis...This might take a while", show_time=True, width="stretch"):
            graph, aggregated_graph, df_data_items, fig_total_network, fig_main_network = main_analysis(df_network, df_data_links, df_data_items, competitors)
            if graph is None:
                st.error("Analysis has failed. Please try again", width="stretch")
            else:
                st.success("Analysis complete! ✅ You now can go to 📊 Network Analysis page to see the analysis result", width="stretch")
                st.write("\n")
                st.page_link("pages/01_📊_Network_Analysis.py", label="Network Analysis", icon="📊")
                
                # Handle states on run success
                st.session_state.graph = graph
                st.session_state.aggregated_graph = aggregated_graph
                st.session_state.df_data_items = df_data_items
                st.session_state.df_network = df_network
                st.session_state.df_data_links = df_data_links
                st.session_state.df_data_items = df_data_items
                st.session_state.df_data_items_filtered = df_data_items
                st.session_state.competitors = competitors
                st.session_state.fig_total_network = fig_total_network
                st.session_state.fig_main_network = fig_main_network


# State handler
if 'graph' not in st.session_state:
    st.session_state.graph = None
    st.session_state.aggregated_graph = None
    st.session_state.df_data_items = None
    st.session_state.df_network = None
    st.session_state.df_data_links = None
    st.session_state.df_data_items = None
    st.session_state.competitors = None
    st.session_state.fig_total_network = None
    st.session_state.fig_main_network = None

    st.session_state.df_data_items_filtered = None
    st.session_state.author_names = (None)
    st.session_state.community_ids = (None)
    st.session_state.community_id = None
