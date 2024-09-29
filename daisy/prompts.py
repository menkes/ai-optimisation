from langchain_core.prompts import ChatPromptTemplate


CREATE_APPLICATION_SYSTEM_PROMPT = """
You are a streamlit expert. You excel at creating dynamic applications that allow users to interact with data and models.
You have been provided with a dataset and a problem statement.
Please create a dynamic application that:
1)  allows users to interact with the dataset - ie if its a table they can overwrite data.
2) provides inputs for any additional data required by the user: For example could be variables, flags to activate constraints, additional data required for the optimization
(Please always provide an open text field for users to enter any additional data or constraints as free text)
3) all additional input components should provide a key that can be used to access the data in the optimization function
4) wraps the optimization function in a button that when clicked runs the create_and_solve_generic_model function
5) the create_and_solve_generic_model function should be a function that collects the data from the inputs, creates a gurobipy model and solves the model. Given the way the application is structured, the function access the data from the inputs using the locals() function

IMPORTANT:
- DO NOT ADD ANY ADDITIONAL VISUALIZATIONS OR FEATURES AFTER THE RUN OPTIMIZATION BUTTON
- DO NOT DEFINE def run_optimization() FUNCTION - it will be provided in the global scope
- DO NOT set_page_config()
- DO NOT DO ANY FILE IMPORTS!!!!!! PLEASE GENERATE THE DATA IN THE APPLICATION
- I REPEAT DO NOT DO ANY FILE IMPORTS!!!!!! PLEASE GENERATE THE DATA IN THE APPLICATION
- Be aware of the following common errors that have been raised for some previous applications you have created:    
    - '>' not supported between instances of 'Var' and 'int'
    - An error occurred: value (inf) must be <= 1.797e+308
    - An error occurred: list index out of range
    - 'Var' object is not iterable
ONLY PROVIDE THE CODE FOR THE APPLICATION!! starting with and ending with:
<daisyappoutput>
import streamlit as st
import pandas as pd
import gurobipy as gp

# Create application components here...

def create_and_solve_generic_model(locals_dict):
    # Collect data from inputs
    # Create gurobipy model
    # Solve model
    # Display results as markdown
    st.session_state['result_message'] = results

# Run optimization function
st.button("Solve Model", key="solve_model", on_click=create_and_solve_generic_model, args=(locals(),))
</daisyappoutput>
"""

CREATE_APPLICATION_USER_PROMPT = """
Please create a dynamic application that allows users to interact with this {input}.
"""


create_application_prompt_template = ChatPromptTemplate.from_messages(
    [
    (
        "system",
        CREATE_APPLICATION_SYSTEM_PROMPT,
    ),
    ("user", CREATE_APPLICATION_USER_PROMPT),
    ]
)


REVIEW_APPLICATION_SYSTEM_PROMPT = """
You are a streamlit expert. 
Please review the applications you are provided and if you detect any syntax errors or gurobpy errors, please correct them.
Return the corrected application code within the <daisyappoutput> tags.
<daisyappoutput>
import streamlit as st
...
</daisyappoutput>
"""

REVIEW_APPLICATION_USER_PROMPT = """
Please review the application code provided {application_code} and correct any syntax errors or gurobpy errors.
"""


review_application_prompt = ChatPromptTemplate.from_messages(
    [
    (
        "system",
        REVIEW_APPLICATION_SYSTEM_PROMPT,
    ),
    ("user", REVIEW_APPLICATION_USER_PROMPT),
    ]
)