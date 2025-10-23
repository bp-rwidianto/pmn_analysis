import streamlit as st

import time
import pandas as pd
import numpy as np
import re

import subprocess
import sys

subprocess.run([f"{sys.executable}", "script.py"])

st.set_page_config(
    page_title="Communities",
    page_icon="👥",
    layout="wide"
)

# Read session's statefull
if ('df_data_items' in st.session_state) and (st.session_state.df_data_items is not None):
    st.session_state.author_names = tuple(sorted(st.session_state.df_data_items_filtered["FullName"].unique()))
    st.session_state.community_ids = tuple(sorted(st.session_state.df_data_items_filtered["cluster"].unique()))
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

def summarise_topics_overall(df_data_items):
    df_simplified = df_data_items[["cluster", "topicCount"]]
    df_long = []

    for i in range(len(df_simplified)):
        data = df_simplified.iloc[i]["topicCount"]
        cluster = df_simplified.iloc[i]["cluster"]
        items = re.findall("(.+)\\n", data)
        for item in items:
            clean_topic = re.sub("Topic_", "", item)
            topic_name = re.split(": ", clean_topic)[0]
            topic_number = re.split(": ", clean_topic)[1]
                               
            df_long.append({
                "Cluster": int(cluster),
                "Topic": topic_name,
                "Publications": int(topic_number)
            })
    
    df_long = pd.DataFrame(df_long).groupby(["Cluster", "Topic"]).sum()
    return df_long

def summarise_topics(dict_series):
    topic_dict_count = {}
    full = []

    for i in range(len(dict_series)):
        row = dict_series.iloc[i]["topicCount"]
        name = dict_series.iloc[i]["FullName"]
        items = re.findall("(.+)\\n", row)
        for item in items:
            clean_topic = re.sub("Topic_", "", item)
            topic_name = re.split(": ", clean_topic)[0]
            topic_number = re.split(": ", clean_topic)[1]
            if int(topic_number) > 0:
                if topic_name in list(topic_dict_count.keys()):
                    topic_dict_count[topic_name] = int(topic_dict_count[topic_name]) + int(topic_number)
                else:
                    topic_dict_count[topic_name] = int(topic_number)
                    
                full.append({
                    "Name": name,
                    "Topic": topic_name,
                    "Publications": int(topic_number)
                })

    for key in list(topic_dict_count.keys()):
        full.append({
            "Name": "## Community ##",
            "Topic": key,
            "Publications": int(topic_dict_count[key])
        })

    return full

def summarise_manufacturer(dict_series):
    manufacturer_dict_count = {}
    full = []

    for i in range(len(dict_series)):
        row = dict_series.iloc[i]["manufacturerCount"]
        name = dict_series.iloc[i]["FullName"]
        items = re.findall("(.+)\\n", row)
        for item in items:
            clean_manufacturer = re.sub("Competitor_", "", item)
            manufacturer_name = re.split(": ", clean_manufacturer)[0]
            manufacturer_number = re.split(": ", clean_manufacturer)[1]
            if int(manufacturer_number) > 0:
                if manufacturer_name in list(manufacturer_dict_count.keys()):
                    manufacturer_dict_count[manufacturer_name] = int(manufacturer_dict_count[manufacturer_name]) + int(manufacturer_number)
                else:
                    manufacturer_dict_count[manufacturer_name] = int(manufacturer_number)
                    
                full.append({
                    "Name": name,
                    "Manufacturer": manufacturer_name,
                    "Publications": int(manufacturer_number)
                })

    for key in list(manufacturer_dict_count.keys()):
        full.append({
            "Name": "## Community ##",
            "Manufacturer": key,
            "Publications": int(manufacturer_dict_count[key])
        })

    return full

## Community members
@st.fragment
def community_members(community_id):
    st.subheader("Community members")
    if community_id is not None:
        table_view = st.session_state.df_data_items_filtered[st.session_state.df_data_items_filtered['cluster'] == community_id][['author_id', 'FullName', 'CurrentAffiliation', 'publications', 'countries', 'bp_user', 'active_author']]
        table_view.columns = ['Author ID', 'Name', 'Affiliations', 'Publications', 'Country', 'BP user', 'Active author']
        st.dataframe(
            # st.session_state.df_data_items_filtered[st.session_state.df_data_items_filtered['cluster'] == community_id][['author_id', 'FullName', 'publications', 'countries', 'bp_user', 'active_author', 'degree_centrality', 'betweenness_centrality', 'closeness_centrality', 'eigenvector_centrality', 'pagerank']]
            table_view
            )
    else:
        st.write("Please select a community on the selection box")

## Community topics
@st.fragment
def community_topics(community_id):
    st.subheader("Community topics of interest")
    if community_id is not None:
        topic_view = st.session_state.df_data_items_filtered[st.session_state.df_data_items_filtered['cluster'] == community_id][['FullName', 'topicCount']]
        topic_summary = summarise_topics(topic_view)
        df_topic_summary = pd.DataFrame(topic_summary)
        df_topic_summary = df_topic_summary[df_topic_summary["Name"] == "## Community ##"][["Topic", "Publications"]]
        st.bar_chart(topic_summary, color="Topic", x="Name", y="Publications",  horizontal=True, stack="normalize", height=1000)
        st.subheader("Community summary")
        st.dataframe(df_topic_summary)
    else:
        st.write("Please select a community on the selection box")

## Community manufacturers
@st.fragment
def community_manufacturers(community_id):
    st.subheader("Community's product manufacturer")
    if community_id is not None:
        manufacturer_view = st.session_state.df_data_items_filtered[st.session_state.df_data_items_filtered['cluster'] == community_id][['FullName', 'manufacturerCount']]
        manufacturer_summary = summarise_manufacturer(manufacturer_view)
        df_manufacturer_summary = pd.DataFrame(manufacturer_summary)
        df_manufacturer_summary = df_manufacturer_summary[df_manufacturer_summary["Name"] == "## Community ##"][["Manufacturer", "Publications"]]
        st.bar_chart(manufacturer_summary, color="Manufacturer", x="Name", y="Publications",  horizontal=True, stack="normalize", height=1000)
        st.subheader("Community summary")
        st.dataframe(df_manufacturer_summary)
        # st.write(
        #     # st.session_state.df_data_items_filtered[st.session_state.df_data_items_filtered['cluster'] == community_id][['author_id', 'FullName', 'publications', 'countries', 'bp_user', 'active_author', 'degree_centrality', 'betweenness_centrality', 'closeness_centrality', 'eigenvector_centrality', 'pagerank']]
        #     summarise_manufacturer(manufacturer_view)
        #     )
    else:
        st.write("Please select a community on the selection box")

## Community map
# Fragment for isolated updates
@st.fragment
def static_community_map_fragment():
    tab1, tab2, tab3 = st.tabs(["Full Network", "Main Network Clusters", "Community Interests"])

    with tab1:
        st.header("Full Network")
        st.pyplot(st.session_state.fig_total_network)

    with tab2:
        st.header("Main Network Clusters")
        st.pyplot(st.session_state.fig_main_network)
    
    with tab3:
        st.header("Community Topic of Interests")
        st.download_button(
            label="Download CSV",
            data=summarise_topics_overall(st.session_state.df_data_items_filtered).to_csv().encode("utf-8"),
            file_name="data.csv",
            mime="text/csv",
            icon=":material/download:",
        )
        with st.container(height=500):
            st.dataframe(summarise_topics_overall(st.session_state.df_data_items_filtered))

# Main content
col1, col2, col3 = st.columns([1, 6, 1])
with col2:
    st.title("Community view 👥")
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

        ## Community main view
        community_id = st.selectbox(
            "Select community",
            st.session_state.community_ids, width="stretch",
            index=None
        )

        tab1, tab2, tab3 = st.tabs(["Community Members", "Topic of Interests", "Product Manufacturers"])
        with tab1:
            community_members(community_id)
        
        with tab2:
            community_topics(community_id)
        
        with tab3:
            community_manufacturers(community_id)
