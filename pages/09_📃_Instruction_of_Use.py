import streamlit as st
import time
import numpy as np

import subprocess
import sys

subprocess.run([f"{sys.executable}", "script.py"])

st.set_page_config(page_title="Instruction of Use", page_icon="📃", 
    layout="centered")

st.markdown("# Instruction of Use")
st.sidebar.header("Instruction of Use")
st.write(
    """This analysis is a branch of PubMed Analysis where we analysed publications related to EEG. 
    The program utilises the list of authors within the publication extracted from the main process
    and created a network to see the relationship between authors.
    """
)

st.write("""
    To use this dashboard, you need to first upload the files in 🏠 Home page (first page opened), which you can access from the sidebar on the left:

        - Network Edges file: containing the relationships of authors
        - Node Information file: containing information snippet of authors that can be used for filtering

    _**Please reach out to Business Development team to get the latest version of these files**_

    We recommend to use both Network analysis window and the Author Publication Journey to get a full context of your analysis. The Author Publication Journey is only accessible if you open this dashboard from Zoho Analytics.
""")

st.divider()

st.write("""
    This dashboard uses Network Analysis terminologies. Please refer to [this article](https://cambridge-intelligence.com/keylines-faqs-social-network-analysis/) for the definitions and how to use the metrics.
""")
