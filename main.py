import streamlit as st
import os
import subprocess
import logging
from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from datetime import datetime
from groq import Groq
import multimodal_diagnosis.diagnosis
import personalized_treatment.app
import research_copilot.together
import webbrowser
import requests

# Apply a global style template with the requested customizations
def template1_page_style():
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

            /* ── Base ── */
            .stApp {
                background-color: #1c1f26;
                color: #e2e8f0;
                font-family: 'Inter', sans-serif;
            }

            /* ── Headings ── */
            h1, h2, h3, h4, h5, h6 {
                font-family: 'Inter', sans-serif;
                color: #f8fafc !important;
            }
            h1 { font-size: 2rem; font-weight: 600; letter-spacing: -0.02em; }
            h2 { font-size: 1.4rem; font-weight: 500; }
            h3 { font-size: 1.1rem; font-weight: 500; }

            /* ── Paragraph & label text ── */
            p, label, .stMarkdown {
                color: #94a3b8;
                font-size: 15px;
                line-height: 1.6;
            }

            /* ── Sidebar ── */
            [data-testid="stSidebar"] {
                background-color: #13161c;
                border-right: 1px solid #2a2f3a;
            }
            [data-testid="stSidebar"] * {
                color: #cbd5e1 !important;
                font-family: 'Inter', sans-serif !important;
            }
            [data-testid="stSidebar"] hr {
                border-color: #2a2f3a;
            }

            /* ── Topbar ── */
            header[data-testid="stHeader"] {
                background-color: rgba(28, 31, 38, 0.85);
                backdrop-filter: blur(8px);
                border-bottom: 1px solid #2a2f3a;
            }
            footer { visibility: hidden; }

            /* ── Buttons ── */
            .stButton > button {
                background-color: #f59e0b;
                color: #1c1f26 !important;
                font-family: 'Inter', sans-serif !important;
                font-size: 14px !important;
                font-weight: 600 !important;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                width: 100%;
                transition: background-color 0.2s ease, transform 0.1s ease;
            }
            .stButton > button:hover {
                background-color: #fbbf24;
                transform: translateY(-1px);
            }
            .stButton > button:active {
                background-color: #d97706;
                transform: translateY(0);
            }

            /* ── Download buttons ── */
            .stDownloadButton > button {
                background-color: transparent;
                color: #f59e0b !important;
                font-family: 'Inter', sans-serif !important;
                font-size: 14px !important;
                font-weight: 500 !important;
                border: 1px solid #f59e0b;
                border-radius: 8px;
                padding: 10px 20px;
                width: 100%;
                transition: background-color 0.2s ease;
            }
            .stDownloadButton > button:hover {
                background-color: rgba(245, 158, 11, 0.1);
            }

            /* ── Text inputs & textareas ── */
            .stTextInput > div > div > input,
            .stTextArea > div > div > textarea {
                background-color: #252830;
                color: #e2e8f0 !important;
                border: 1px solid #2a2f3a;
                border-radius: 8px;
                padding: 10px 14px;
                font-family: 'Inter', sans-serif;
                font-size: 14px;
                transition: border-color 0.2s ease, box-shadow 0.2s ease;
            }
            .stTextInput > div > div > input:focus,
            .stTextArea > div > div > textarea:focus {
                border-color: #f59e0b;
                box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.15);
                outline: none;
            }
            .stTextInput > div > div > input::placeholder,
            .stTextArea > div > div > textarea::placeholder {
                color: #475569;
            }

            /* ── Select boxes ── */
            .stSelectbox > div > div {
                background-color: #252830;
                color: #e2e8f0;
                border: 1px solid #2a2f3a;
                border-radius: 8px;
                font-family: 'Inter', sans-serif;
                font-size: 14px;
            }
            .stSelectbox > div > div:focus-within {
                border-color: #f59e0b;
                box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.15);
            }

            /* ── Sliders ── */
            .stSlider > div > div > div > div {
                background-color: #f59e0b !important;
            }
            .stSlider > div > div > div {
                background-color: #2a2f3a;
            }

            /* ── Checkboxes & radios ── */
            .stCheckbox > label > span,
            .stRadio > div > label > span {
                color: #cbd5e1 !important;
                font-size: 14px;
            }

            /* ── Metric cards ── */
            [data-testid="stMetric"] {
                background-color: #252830;
                border: 1px solid #2a2f3a;
                border-radius: 10px;
                padding: 16px 20px;
            }
            [data-testid="stMetricLabel"] {
                color: #64748b !important;
                font-size: 12px !important;
                text-transform: uppercase;
                letter-spacing: 0.05em;
            }
            [data-testid="stMetricValue"] {
                color: #f8fafc !important;
                font-size: 28px !important;
                font-weight: 600 !important;
            }
            [data-testid="stMetricDelta"] svg { display: none; }
            [data-testid="stMetricDelta"] > div {
                color: #f59e0b !important;
                font-size: 13px !important;
            }

            /* ── Dataframes & tables ── */
            [data-testid="stDataFrame"] {
                border: 1px solid #2a2f3a;
                border-radius: 10px;
                overflow: hidden;
            }
            [data-testid="stDataFrame"] th {
                background-color: #252830 !important;
                color: #94a3b8 !important;
                font-size: 12px;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                border-bottom: 1px solid #2a2f3a !important;
            }
            [data-testid="stDataFrame"] td {
                background-color: #1c1f26 !important;
                color: #e2e8f0 !important;
                border-bottom: 1px solid #252830 !important;
            }

            /* ── Expanders ── */
            .streamlit-expanderHeader {
                background-color: #252830 !important;
                color: #e2e8f0 !important;
                border: 1px solid #2a2f3a !important;
                border-radius: 8px;
                font-size: 14px;
            }
            .streamlit-expanderContent {
                background-color: #1e2128 !important;
                border: 1px solid #2a2f3a;
                border-top: none;
                border-radius: 0 0 8px 8px;
            }

            /* ── Dividers ── */
            hr {
                border-color: #2a2f3a;
            }

            /* ── Scrollbar ── */
            ::-webkit-scrollbar { width: 6px; height: 6px; }
            ::-webkit-scrollbar-track { background: #1c1f26; }
            ::-webkit-scrollbar-thumb { background: #2a2f3a; border-radius: 3px; }
            ::-webkit-scrollbar-thumb:hover { background: #f59e0b; }
        </style>
    """, unsafe_allow_html=True)

def sidebar_navigation():
    # Use session state to remember the current page
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Home"
    
    # Sidebar navigation buttons - Kept only the 4 essential ones
    if st.sidebar.button("HOME \u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0"):
        st.session_state.current_page = 'Home'
    if st.sidebar.button("MULTIMODAL DIAGNOSIS \u00A0\u00A0\u00A0\u00A0\u00A0"):
        st.session_state.current_page = 'Diagnosis'
    if st.sidebar.button("PERSONALIZED TREATMENT \u00A0\u00A0\u00A0\u00A0"):
        st.session_state.current_page = 'Personalized Treatment'
    if st.sidebar.button("RESEARCH COPILOT \u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0"):
        st.session_state.current_page = 'Research Copilot'

# Main Home page content
def show_home():
    st.markdown("""
        <div style="text-align: center; margin-top: 10px;">
            <h1>
                MED-ASSIST
            </h1>
            <p style="font-size: 24px; color: white; margin-top: 10px; font-family: 'Kode Mono', sans-serif; text-align:left;">
                Your intelligent copilot for rapid medical image analysis, hyper-personalized recovery plans.
            </p>
        </div>
    """, unsafe_allow_html=True)

# Remaining page functions
def show_personalized_treatment():
    personalized_treatment.app.app()

def show_research_copilot():
    research_copilot.together.app()

def show_diagnosis():
    multimodal_diagnosis.diagnosis.app()

# Main function
def main():
    # Apply page styles
    template1_page_style()
    
    # Sidebar navigation
    sidebar_navigation()
    
    # Display the page according to the session state
    if st.session_state.current_page == 'Home':
        show_home()
    elif st.session_state.current_page == 'Personalized Treatment':
        show_personalized_treatment()
    elif st.session_state.current_page == 'Research Copilot':
        show_research_copilot()
    elif st.session_state.current_page == 'Diagnosis':
        show_diagnosis()

if __name__ == "__main__":  
    main()
