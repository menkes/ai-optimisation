import streamlit as st
import pandas as pd
import numpy as np
from anthropic import Anthropic
from bs4 import BeautifulSoup
import os
import json
import yaml

from generic.graph import graph
from utils.prompts import OPTIMIZATION_DATA_ANALYSER_SYSTEM_PROMPT, OPTIMIZATION_DATA_ANALYSER_USER_PROMPT, CREATE_APPLICATION_SYSTEM_PROMPT, CREATE_APPLICATION_USER_PROMPT

# Initialize session state variables if they don't exist
def initialize_session_state():
    st.session_state.setdefault("application_code", "")
    st.session_state.setdefault("dfs_string", "")
    st.session_state.setdefault("problem_statement", "")
    st.session_state.setdefault("uploaded_files", None)
    st.session_state.setdefault("result_message", "")
    st.session_state.setdefault("results_placeholder", None)

initialize_session_state()

# Initialize Anthropic client
client = Anthropic()


# Helper function to collect optimization data

def clear_session():
    session_dir = os.path.join("session")
    for file in os.listdir(session_dir):
        if file.startswith("data-"):
            os.remove(os.path.join(session_dir, file))

def collect_optimization_data(state):
    # data = {}
    # for k, v in st.session_state.items():
    #     # if k not in ["application_code", "result_message","results_placeholder", "uploaded_files", "run_optimization", "load_application"] and not k.startswith("_"):
    #     data[k] = str(st.session_state[k])
    # print(data)
    data = {}
    for k, v in state.items():
        if k not in ["application_code", "result_message","results_placeholder", "uploaded_files", "run_optimization", "load_application"] and not k.startswith("_"):
            data[k] = str(state[k])
    with open(os.path.join("session","optimization_data.json"), "w") as f:
        json.dump(data, f)
    return yaml.dump(data)

# Run optimization function
def run_optimization(state):
    clear_session()
    st.session_state.result_message = ""
    st.session_state.results_placeholder.empty()
    user_input = collect_optimization_data(state)
    print("user_input", user_input)
    config = {"configurable": {"thread_id": "1"}}
    for event in graph.stream({"messages": ("user", user_input)}, config=config):
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)
            if type(value["messages"][-1].content) == str:
                st.session_state.result_message += value["messages"][-1].content
            st.session_state.results_placeholder.markdown(st.session_state.result_message)
            # results_placeholder.markdown(st.session_state.results)
            # print("Assistant:", value["messages"][-1].content)



# Load application code from file
def load_application():
    with open(os.path.join("session","current_application.py"), "r") as f:
        st.session_state.application_code = f.read()

# Extract output content from Anthropic response
def get_output(input_string):
    soup = BeautifulSoup(input_string, 'html.parser')
    return soup.find('output').text

# Generate optimization data analysis using Anthropic API
def generate_optimization_data_analysis(dataset, message_placeholder):
    st.session_state.problem_statement = ""
    message_placeholder.empty()

    with client.messages.stream(
        max_tokens=1024,
        system=OPTIMIZATION_DATA_ANALYSER_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": OPTIMIZATION_DATA_ANALYSER_USER_PROMPT.format(DATASET=dataset)}],
        model="claude-3-5-sonnet-20240620"
    ) as stream:
        for text in stream.text_stream:
            st.session_state.problem_statement += text
            message_placeholder.markdown(st.session_state.problem_statement)

# Create application using Anthropic API
def create_application(example_data, problem_statement):
    st.session_state.application_code = None
    response = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=2048,
        system=CREATE_APPLICATION_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": CREATE_APPLICATION_USER_PROMPT.format(dataset=example_data, problem_statement=problem_statement)}]
    )
    application_code = response.content[0].text
    print(response.content)
    st.session_state.application_code = get_output(application_code)
    
    with open(os.path.join("session","current_application.py"), "w") as f:
        f.write(st.session_state.application_code)

# Page 1: Application Generator
def page_one():
    st.title("Application Generator")

    # File uploader for CSV files
    uploaded_files = st.file_uploader("Choose a CSV file", type="csv", accept_multiple_files=True)
    if uploaded_files:
        st.session_state.uploaded_files = uploaded_files

    # Process uploaded files and generate problem statement
    if st.session_state.uploaded_files and not st.session_state.problem_statement:
        dfs = [pd.read_csv(file) for file in st.session_state.uploaded_files]
        st.session_state.dfs_string = "\n".join([df.to_string() for df in dfs])

        # Display data preview
        st.write("Here are the first 5 rows of your files:")
        for df in dfs:
            st.dataframe(df.head())

        analysis_message_placeholder = st.empty()

        # Generate problem statement using the Anthropic API
        with st.chat_message("user"):
            generate_optimization_data_analysis(st.session_state.dfs_string, message_placeholder=analysis_message_placeholder)

        # Button to generate application after problem statement is ready
        if st.session_state.problem_statement and not st.session_state.application_code:
            st.button("Generate Application", key="generate_application", on_click=create_application,
                      args=(st.session_state.dfs_string, st.session_state.problem_statement))

    elif st.session_state.problem_statement:
        st.write(st.session_state.problem_statement)
        st.button("Generate Application", key="generate_application", on_click=create_application,
                  args=(st.session_state.dfs_string, st.session_state.problem_statement))
    else:
        st.write("Please upload a CSV file.")

# Page 2: Display current application
def page_two():
    st.button("Load Application", key="load_application", on_click=load_application)

    if not st.session_state.application_code:
        st.write("Please generate an application first.")
    else:
        try:
            exec(st.session_state.application_code)
            if not st.session_state.results_placeholder:
                st.session_state.results_placeholder = st.empty()
                
        except Exception as e:
            st.error(f"An error occurred: {e}")

# Sidebar navigation
st.sidebar.title("DAISY Decision AI System")
page = st.sidebar.radio("Go to", ["Application Generator", "Current Application"])

# Page routing
if page == "Application Generator":
    page_one()
else:
    page_two()
