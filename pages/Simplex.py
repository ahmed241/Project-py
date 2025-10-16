import streamlit as st
import json
import numpy as np

st.set_page_config(
    page_title="Simplex Method - OR Solver",
    page_icon="📈",
    layout="wide"
)

# Custom CSS matching the home page and other problem pages
st.markdown("""
    <style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .section-header {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    .constraint-card {
        background: white;
        padding: 1.2rem;
        border-radius: 8px;
        margin-bottom: 0.8rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 3px solid #764ba2;
    }
    .stButton>button {
        border-radius: 5px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 8px;
        color: white;
    }
    div[data-testid="metric-container"] label {
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

# Main header
st.markdown("""
    <div class="main-header">
        <h1>📈 Simplex Method Solver</h1>
        <p style="font-size: 1.2rem; margin-top: 1rem;">
            Linear Programming Problem Input
        </p>
    </div>
""", unsafe_allow_html=True)

st.write("Define your linear programming problem to find the optimal solution using the Simplex Algorithm.")
st.markdown("---")

# Sample data definition
SAMPLE_SIMPLEX_DATA = {
    "num_vars": 3,
    "num_constraints": 3,
    "optimization": "Maximize",
    "objective": [3.0, 2.0, 5.0],
    "constraints": [
        {"coeffs": [1.0, 2.0, 1.0], "type": "<=", "rhs": 430.0},
        {"coeffs": [3.0, 0.0, 2.0], "type": "<=", "rhs": 460.0},
        {"coeffs": [1.0, 4.0, 0.0], "type": "<=", "rhs": 420.0}
    ]
}

# Initialize session state
if 'num_vars' not in st.session_state:
    st.session_state.num_vars = 2
if 'num_constraints' not in st.session_state:
    st.session_state.num_constraints = 2
if 'sample_loaded' not in st.session_state:
    st.session_state.sample_loaded = False

# Callback function to load sample data
def load_simplex_sample():
    st.session_state.num_vars = SAMPLE_SIMPLEX_DATA["num_vars"]
    st.session_state.num_constraints = SAMPLE_SIMPLEX_DATA["num_constraints"]
    st.session_state.sample_loaded = True
    st.session_state.opt_type_index = 0 if SAMPLE_SIMPLEX_DATA["optimization"] == "Maximize" else 1
    
    # Store sample data for objective function
    for i, val in enumerate(SAMPLE_SIMPLEX_DATA["objective"]):
        st.session_state[f"obj_{i}"] = val
    
    # Store sample data for constraints
    for j, constraint in enumerate(SAMPLE_SIMPLEX_DATA["constraints"]):
        for i, coeff in enumerate(constraint["coeffs"]):
            st.session_state[f"const_{j}_{i}"] = coeff
        st.session_state[f"type_{j}"] = ["<=", ">=", "="].index(constraint["type"])
        st.session_state[f"rhs_{j}"] = constraint["rhs"]

# Step 1: Define Problem Dimensions
st.markdown('<div class="section-header"><h3>1. Define Problem Dimensions</h3></div>', unsafe_allow_html=True)

# Load sample button at the top
st.button("📋 Load Sample Data", on_click=load_simplex_sample, 
          help="Click to load a pre-defined 3-variable, 3-constraint problem.", 
          type="secondary")

col1, col2 = st.columns(2)
with col1:
    num_vars = st.number_input("Number of Variables:", min_value=2, max_value=10, 
                                value=st.session_state.num_vars, step=1, key="num_vars_input")
    st.session_state.num_vars = num_vars

with col2:
    num_constraints = st.number_input("Number of Constraints:", min_value=1, max_value=10, 
                                       value=st.session_state.num_constraints, step=1, key="num_constraints_input")
    st.session_state.num_constraints = num_constraints

st.markdown("---")

# Step 2: Optimization Type
st.markdown('<div class="section-header"><h3>2. Select Optimization Type</h3></div>', unsafe_allow_html=True)

opt_type_index = st.session_state.get('opt_type_index', 0)
opt_type = st.radio(
    "Is this a minimization or maximization problem?",
    ("Maximize (e.g., Profit, Production)", "Minimize (e.g., Cost, Time)"),
    horizontal=True,
    index=opt_type_index
)
optimization = "Maximize" if "Maximize" in opt_type else "Minimize"

st.markdown("---")

# Step 3: Objective Function
st.markdown('<div class="section-header"><h3>3. Define Objective Function</h3></div>', unsafe_allow_html=True)

st.write(f"Enter the coefficients for the objective function to **{optimization.lower()}**:")

obj_cols = st.columns(num_vars)
obj_coeffs = []

for i in range(num_vars):
    with obj_cols[i]:
        default_val = st.session_state.get(f"obj_{i}", 0.0)
        coeff = st.number_input(
            f"x{i+1} coefficient", 
            value=float(default_val), 
            step=1.0, 
            key=f"obj_{i}",
            help=f"Coefficient for variable x{i+1}"
        )
        obj_coeffs.append(coeff)

# Display the objective function
obj_formula = f"**{optimization} Z =** " + " + ".join([f"{obj_coeffs[i]}x{i+1}" for i in range(num_vars)])
st.markdown(f"<div style='background: #e8f4f8; padding: 1rem; border-radius: 5px; margin-top: 1rem;'>{obj_formula}</div>", 
            unsafe_allow_html=True)

st.markdown("---")

# Step 4: Constraints
st.markdown('<div class="section-header"><h3>4. Define Constraints</h3></div>', unsafe_allow_html=True)
st.write("Enter the coefficients, inequality type, and RHS value for each constraint:")

constraints = []
for j in range(num_constraints):
    st.markdown(f'<div class="constraint-card">', unsafe_allow_html=True)
    st.write(f"**Constraint {j+1}:**")
    
    # Coefficient inputs
    coeff_cols = st.columns(num_vars)
    constraint = {"coefficients": [], "type": "<=", "rhs": 0}
    
    for i in range(num_vars):
        with coeff_cols[i]:
            default_coeff = st.session_state.get(f"const_{j}_{i}", 0.0)
            coeff = st.number_input(
                f"C{j+1} x{i+1}", 
                value=float(default_coeff), 
                step=1.0,
                key=f"const_{j}_{i}", 
                label_visibility="collapsed",
                placeholder=f"x{i+1}"
            )
            constraint["coefficients"].append(coeff)
    
    # Constraint type and RHS
    control_cols = st.columns([1, 1])
    with control_cols[0]:
        default_type_idx = st.session_state.get(f"type_{j}", 0)
        constraint_type = st.selectbox(
            "Inequality Type", 
            ["<=", ">=", "="], 
            key=f"type_{j}", 
            label_visibility="collapsed"
        )
        constraint["type"] = constraint_type
    
    with control_cols[1]:
        default_rhs = st.session_state.get(f"rhs_{j}", 0.0)
        rhs = st.number_input(
            "RHS", 
            value=float(default_rhs), 
            step=1.0,
            key=f"rhs_{j}", 
            label_visibility="collapsed",
            placeholder="RHS"
        )
        constraint["rhs"] = rhs
    
    # Display constraint formula
    constraint_formula = " + ".join([f"{constraint['coefficients'][i]}x{i+1}" for i in range(num_vars)])
    st.caption(f"➜ {constraint_formula} {constraint['type']} {constraint['rhs']}")
    
    constraints.append(constraint)
    st.markdown('</div>', unsafe_allow_html=True)

# Non-negativity constraints
st.info(f"ℹ️ **Non-negativity Constraints:** " + ", ".join([f"x{i+1} ≥ 0" for i in range(num_vars)]))

st.markdown("---")

# Step 5: Choose Output Format
st.markdown('<div class="section-header"><h3>5. Choose Output Format</h3></div>', unsafe_allow_html=True)
output_type = st.radio(
    "How would you like to see the solution?",
    ("Final Answer Only", "Step-by-step Video Solution"),
    horizontal=True,
    label_visibility="collapsed"
)

st.markdown("---")

# Step 6: Generate Solution
st.markdown('<div class="section-header"><h3>6. Generate Solution</h3></div>', unsafe_allow_html=True)

if output_type == "Step-by-step Video Solution":
    if st.button("🎥 Render Video", type="primary", use_container_width=True):
        # Prepare problem data
        problem_data = {
            "problem_type": "simplex",
            "optimization": optimization.lower(),
            "num_variables": num_vars,
            "num_constraints": num_constraints,
            "objective_function": {
                "coefficients": obj_coeffs,
                "type": optimization.lower()
            },
            "constraints": constraints,
            "variable_names": [f"x{i+1}" for i in range(num_vars)]
        }
        
        # Save to JSON file
        with open("simplex_problem.json", "w") as f:
            json.dump(problem_data, f, indent=4)
        
        st.success("✅ Problem saved to 'simplex_problem.json'")
        st.info("🔄 Video rendering will be implemented with Manim!")
        
        # Display the JSON
        with st.expander("📄 View Problem Data"):
            st.json(problem_data)

else:  # Final Answer Only
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🧮 Calculate Final Answer", type="primary", use_container_width=True):
            # Prepare problem data
            problem_data = {
                "problem_type": "simplex",
                "optimization": optimization.lower(),
                "num_variables": num_vars,
                "num_constraints": num_constraints,
                "objective_function": {
                    "coefficients": obj_coeffs,
                    "type": optimization.lower()
                },
                "constraints": constraints,
                "variable_names": [f"x{i+1}" for i in range(num_vars)]
            }
            
            # Save to JSON file
            with open("simplex_problem.json", "w") as f:
                json.dump(problem_data, f, indent=4)
            
            st.success("✅ Problem saved to 'simplex_problem.json'")
            st.info("🔄 Simplex solver implementation coming soon!")
            
            # Display the JSON
            with st.expander("📄 View Problem Data"):
                st.json(problem_data)
    
    with col2:
        if st.button("🏠 Back to Home", use_container_width=True):
            st.switch_page("Home.py")

# Problem Summary
with st.expander("📋 Problem Summary", expanded=False):
    st.markdown("### Current Problem Formulation")
    st.write(f"**Objective:** {optimization} Z = " + 
             " + ".join([f"{obj_coeffs[i]}x{i+1}" for i in range(num_vars)]))
    st.write("**Subject to:**")
    for j, c in enumerate(constraints):
        constraint_str = " + ".join([f"{c['coefficients'][i]}x{i+1}" 
                                    for i in range(num_vars)])
        st.write(f"  {j+1}. {constraint_str} {c['type']} {c['rhs']}")
    st.write(f"**Where:** {', '.join([f'x{i+1} ≥ 0' for i in range(num_vars)])}")