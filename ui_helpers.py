# ===============================
# File: ui_helpers.py
# ===============================
import os
import streamlit as st

def load_css(file_name):
    css_path = os.path.join(os.path.dirname(__file__), 'static', file_name)
    with open(css_path) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def tooltip_html(text, tooltip_text):
    return f"""
    <div class="textbox-container">
      <div class="tooltip">
        <div class="icon">i</div>
        <span class="tooltiptext">{tooltip_text}</span>
      </div>
    </div>
    """

