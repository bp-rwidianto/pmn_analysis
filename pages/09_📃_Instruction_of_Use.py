import streamlit as st
import time
import numpy as np

st.set_page_config(page_title="Instruction of Use", page_icon="📃")

st.markdown("# Instruction of Use")
st.sidebar.header("Instruction of Use")
st.write(
    """This analysis is a branch of PubMed Analysis where we analysed publications related to EEG. 
    The program utilises the list of authors within the publication extracted from the main process
    and created a network to see the relationship between authors.
    """
)