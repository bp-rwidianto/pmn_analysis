from supporting_functions import *
from network_highlight import *
import streamlit as st
import streamlit.components.v1 as components

import time
import pandas as pd
import numpy as np
import re
from stvis import pv_static

st.set_page_config(
    page_title="Network Analysis",
    page_icon="📊",
    layout="wide"
)

# Read session's statefull
if ('df_data_items' in st.session_state) and (st.session_state.df_data_items is not None):
    st.session_state.author_names = tuple(sorted(st.session_state.df_data_items_filtered["FullName"].unique()))
    st.session_state.community_ids = tuple(sorted(st.session_state.df_data_items_filtered["cluster"].unique()))
    is_expanded = True
    st.session_state.community_id = None
    graph_dict = {
        'graph': st.session_state.graph,
        'aggregated_graph': st.session_state.aggregated_graph,
        'df_data_items': st.session_state.df_data_items,
        'competitors': st.session_state.competitors
    }

# Functions and components
def set_community_id(new_value):
    st.session_state.community_id = new_value

## Community members
@st.fragment
def community_members():
    st.subheader("Community members")
    col1, col2 = st.columns([6, 2])
    community_id = col2.selectbox(
        "Select community",
        st.session_state.community_ids, width="stretch",
        index=None
    )
    if community_id is not None:
        table_view = st.session_state.df_data_items_filtered[st.session_state.df_data_items_filtered['cluster'] == community_id][['author_id', 'FullName', 'publications', 'countries', 'bp_user', 'active_author', 'degree_centrality', 'betweenness_centrality', 'closeness_centrality', 'eigenvector_centrality', 'pagerank']]
        table_view.columns = ['Author ID', 'Name', 'Publications', 'Country', 'BP user', 'Active author', 'Degee cent.', 'Betweeness cent.', 'Closeness cent.', 'Eigen cent.', 'PageRank']
        st.dataframe(
            # st.session_state.df_data_items_filtered[st.session_state.df_data_items_filtered['cluster'] == community_id][['author_id', 'FullName', 'publications', 'countries', 'bp_user', 'active_author', 'degree_centrality', 'betweenness_centrality', 'closeness_centrality', 'eigenvector_centrality', 'pagerank']]
            table_view
            )
    else:
        st.write("Please select a community on the selection box")
    

## Community map
# Fragment for isolated updates
@st.fragment
def static_community_map_fragment():
    tab1, tab2 = st.tabs(["Full Network", "Main Network Clusters"])

    with tab1:
        st.header("Full Network")
        st.pyplot(st.session_state.fig_total_network)

    with tab2:
        st.header("Main Network Clusters")
        st.pyplot(st.session_state.fig_main_network)

## Author details
# Fragment for isolated updates
@st.fragment
def author_detail_fragment():
    with st.container(border=True, height=1550):
        st.subheader("Author details")
        author_name = st.selectbox(
            "Select author",
            st.session_state.author_names, width="stretch",
            index=None
        )

        if author_name is not None:
            author_details = get_item(st.session_state.df_data_items, author_name)
            
            st.write(f'### **{author_details["FullName"]} ({author_details["author_id"]})**\n\n')
            colA, colB = st.columns([1, 13])
            colA.write(f'**Affiliations**')
            with colB.container(height=120, border=False):
                affiliations = re.split("\\n", author_details['CurrentAffiliation'])
                for affiliation in affiliations:
                    affiliation_text = re.sub("\\n", "", affiliation)
                    st.write(f'- {affiliation_text}')
            col1, col2, col3 = st.columns(3)
            col1.write_stream(stream_author_data(author_details))
            col2.write_stream(stream_author_competitors(author_details))
            
            with col3.container(border=True):
                st.write_stream(stream_author_network(author_details))
            
        
            author_id = get_item(st.session_state.df_data_items, author_name)["author_id"]
            with st.spinner(text="Creating network map, this process might take a while. Please wait...", show_time=True):
                # col1, col2, col3 = st.columns([1, 6, 1])
                html_text = highlight_author_pyvis(author_id, st.session_state.graph, st.session_state.aggregated_graph, st.session_state.df_data_items, st.session_state.competitors, st.session_state.topics)
                # with col2:
                # st.success("Graph creation complete ✅")
                pv_static(html_text)
                    


# Handle data stream
def stream_author_competitors(author_details):
    competitors = re.split(": [0-9]+[\\n]", author_details['manufacturerCount'])
    competitors_count = re.findall(": ([0-9]+)", author_details['manufacturerCount'])
    competitors_text = []

    true_competitor_name = {
        "atus": "Natus",
        "euroelectrics": "Neuroelectrics",
        "exstim": "Nexstim",
        "euracle": "Neuracle",
        "euroconcise": "Neuroconcise",
        "euroSky": "NeuroSky",
        "RSign": "NRSign"
    }

    for i in range(0, len(competitors)):
        if int(competitors_count[i]) > 0:
            competitors_text.append(f" -  {true_competitor_name[competitors[i]] if competitors[i] in true_competitor_name.keys() else competitors[i]}: {competitors_count[i]}")

    full_competitors_text = '\n'.join(competitors_text)
    full_text = f"**Manufacturers:**\n\n{full_competitors_text}"

    for word in full_text.split(" "):
        yield word + " "
        time.sleep(0.02)

def stream_author_data(author_details):

    full_text = f"Number of Publications:\n{author_details['publications']}\n\nCountry:\n{author_details['countries']}\n\nBP User:\n{author_details['bp_user']}\n\nActive author:\n{True if author_details['active_author'] > 0 else False}\n\nBP Mention:\n{author_details['mention_bp']}\n\nCommunity ID:\n{int(author_details['cluster'])}"
        
    for word in full_text.split(" "):
        yield word + " "
        time.sleep(0.02)

def stream_author_network(author_details):
    full_text = f"**Network metrics:**\n\n- Degree centrality:\n{round(author_details['degree_centrality'], 5)}\n- Betweenness centrality:\n{round(author_details['betweenness_centrality'], 5)}\n- Closeness centrality:\n{round(author_details['closeness_centrality'], 5)}\n- Eigen centrality:\n{round(author_details['eigenvector_centrality'], 5)}\n- PageRank:\n{round(author_details['pagerank'], 5)}"
        
    for word in full_text.split(" "):
        yield word + " "
        time.sleep(0.02)

# Main content
col1, col2, col3 = st.columns([1, 6, 1])
with col2:
    st.title("PubMed Network Analysis 📊")
    author_details = None

    if ('df_data_items' not in st.session_state) or (st.session_state.df_data_items is None):
        st.write('### No processed data found!')
        st.write('Please upload the network and information files in "Home" page to view the network analysis contents.')

    else:
        ## Sidebar and widgets
        st.sidebar.write("## __Analysis Filters__")
        is_bp_user = st.sidebar.toggle("BP user")
        is_active_author = st.sidebar.toggle("Active author")
        country_filter = st.sidebar.multiselect("Author country", tuple(sorted(st.session_state.df_data_items["countries"].unique())))
        is_expanded = False

        ## Widget filter handler
        if (is_bp_user == True) or (is_active_author == True) or (len(country_filter)):
            temp = st.session_state.df_data_items
            if (is_bp_user):
                temp = temp[temp["bp_user"]]
            if (is_active_author):
                temp = temp[temp["active_author"] > 0]
            if (len(country_filter)):
                temp = temp[temp["countries"].isin(country_filter)]

            st.session_state.df_data_items_filtered = temp
            st.session_state.author_names = tuple(sorted(st.session_state.df_data_items_filtered["FullName"].unique()))
            st.session_state.community_ids = tuple(sorted(st.session_state.df_data_items_filtered["cluster"].unique()))


            
        with st.expander("Community network map (static)", expanded=is_expanded):
            static_community_map_fragment()
            community_members()

        st.divider()

        author_detail_fragment()



