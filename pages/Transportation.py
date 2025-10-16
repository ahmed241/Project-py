import streamlit as st
import pandas as pd
import json
import copy
import subprocess
import os
import time
import numpy as np
from scipy.optimize import linprog
from Transportation.VAM_solver import solve_vam

# --- Sample Data Definition ---
SAMPLE_TRANSPORTATION_DATA = {
    "sources": 3,
    "destinations": 4,
    "supply": [300, 400, 500],
    "demand": [250, 350, 400, 200],
    "costs": [
        [3, 1, 7, 4],
        [2, 6, 5, 9],
        [8, 3, 3, 2]
    ]
}

# --- Callback Function ---
# This function is called when the "Load Sample Data" button is clicked
def load_transportation_sample():
    # Update the dimension inputs
    st.session_state.num_sources_input = SAMPLE_TRANSPORTATION_DATA["sources"]
    st.session_state.num_destinations_input = SAMPLE_TRANSPORTATION_DATA["destinations"]

    # Update supply and demand number inputs by targeting their keys
    for i, val in enumerate(SAMPLE_TRANSPORTATION_DATA["supply"]):
        st.session_state[f"supply_{i}"] = val
    for i, val in enumerate(SAMPLE_TRANSPORTATION_DATA["demand"]):
        st.session_state[f"demand_{i}"] = val

    # Update our "source of truth" DataFrame for the data editor
    st.session_state.editable_tp_df = pd.DataFrame(
        SAMPLE_TRANSPORTATION_DATA["costs"],
        columns=[f"Destination {j+1}" for j in range(SAMPLE_TRANSPORTATION_DATA["destinations"])],
        index=[f"Source {chr(65 + i)}" for i in range(SAMPLE_TRANSPORTATION_DATA["sources"])]
    )

def balance_problem(supply, demand, costs):
    """
    Checks if the problem is balanced. If not, adds a dummy source or
    destination with zero costs to balance it.
    """
    supply_copy = copy.deepcopy(supply)
    demand_copy = copy.deepcopy(demand)
    costs_copy = copy.deepcopy(costs)
    
    total_supply = sum(supply_copy)
    total_demand = sum(demand_copy)

    if total_supply == total_demand:
        return supply_copy, demand_copy, costs_copy, False

    is_dummy_added = True
    st.info(f"Problem is unbalanced! Supply={total_supply}, Demand={total_demand}. A dummy will be added.")
    
    if total_supply > total_demand:
        diff = total_supply - total_demand
        demand_copy.append(diff)
        for row in costs_copy:
            row.append(0)
    else:
        diff = total_demand - total_supply
        supply_copy.append(diff)
        num_destinations = len(demand_copy)
        costs_copy.append([0] * num_destinations)
        
    return supply_copy, demand_copy, costs_copy, is_dummy_added

# --- Streamlit App Layout ---
st.set_page_config(layout="wide")
# Back to main button
if st.button("⬅️ Back to Main Menu", use_container_width=False):
    st.switch_page("pages/Home.py")
st.title("🚚 Transportation Problem Solver")
st.write("Define costs, supply, and demand to find the optimal solution.")

# --- Step 1: Define Dimensions ---
st.subheader("1. Define Problem Dimensions")
st.button("Load Sample Data", on_click=load_transportation_sample, help="Click to load a pre-defined 3x4 problem.")

col1, col2 = st.columns(2)
with col1:
    num_sources = st.number_input("Number of Sources (Factories)", min_value=1, value=3, key="num_sources_input")
with col2:
    num_destinations = st.number_input("Number of Destinations (Warehouses)", min_value=1, value=3, key="num_destinations_input")

# --- Step 2: Define Supply and Demand ---
st.subheader("2. Define Supply and Demand")
supply = []
demand = []

col1, col2 = st.columns(2)
with col1:
    st.write("**Supply from Sources**")
    for i in range(num_sources):
        supply_val = st.number_input(f"Source {chr(65 + i)} Supply", min_value=1, value=50, key=f"supply_{i}")
        supply.append(supply_val)

with col2:
    st.write("**Demand at Destinations**")
    for i in range(num_destinations):
        demand_val = st.number_input(f"Destination {i + 1} Demand", min_value=1, value=20, key=f"demand_{i}")
        demand.append(demand_val)

# --- Step 3: Define Cost Matrix ---
st.subheader("3. Define Cost Matrix")

# Initialize or update our "source of truth" DataFrame in session state
if 'editable_tp_df' not in st.session_state or st.session_state.editable_tp_df.shape != (num_sources, num_destinations):
    st.session_state.editable_tp_df = pd.DataFrame(
        [[10 for _ in range(num_destinations)] for _ in range(num_sources)],
        columns=[f"Destination {j + 1}" for j in range(num_destinations)],
        index=[f"Source {chr(65 + i)}" for i in range(num_sources)]
    )

st.write("Enter the transportation cost for each route.")
edited_df = st.data_editor(st.session_state.editable_tp_df)

# Update our state variable with the user's edits
st.session_state.editable_tp_df = edited_df

# --- Step 4: Choose Output Format ---
st.subheader("4. Choose Output Format")
output_type = st.radio(
    "How would you like to see the solution?",
    ("Final Answer Only", "Step-by-step Video Solution (VAM)"),
    horizontal=True,
    label_visibility="collapsed"
)

# --- Step 5: Generate Solution ---
st.subheader("5. Generate Solution")

# Get cost data from our controlled state variable
costs = st.session_state.editable_tp_df.astype(float).values.tolist()

if output_type == "Step-by-step Video Solution (VAM)":
    if st.button("🎥 Render Video", type="primary"):
        st.info("Video rendering logic would be here.")

else: # "Final Answer Only" was selected
    if st.button("🧮 Calculate Final Answer", type="primary"):
        with st.spinner("Calculating solutions..."):
            final_supply, final_demand, final_costs, _ = balance_problem(supply, demand, costs)

            num_sources_final = len(final_supply)
            num_dests_final = len(final_demand)
            
            source_labels = [f"Source {chr(65 + i)}" for i in range(num_sources)]
            if num_sources_final > num_sources: source_labels.append("Dummy Source")
            
            dest_labels = [f"Destination {j + 1}" for j in range(num_destinations)]
            if num_dests_final > num_destinations: dest_labels.append("Dummy Destination")

            st.markdown("---")
            st.subheader("1. Initial Feasible Solution (Vogel's Approximation Method)")
            try:
                vam_allocation, vam_total_cost = solve_vam(final_supply, final_demand, final_costs)
                st.metric(label="**Initial Cost (VAM)**", value=f"{vam_total_cost:,.2f}")
                
                st.write("**VAM Allocation Matrix (Units to Ship):**")
                vam_df = pd.DataFrame(vam_allocation, index=source_labels, columns=dest_labels)
                st.dataframe(vam_df)
            except Exception as e:
                st.error(f"An error occurred during VAM calculation: {e}")

            st.markdown("---")
            st.subheader("2. Final Optimal Solution (using Linear Programming)")
            
            costs_flat = np.array(final_costs).flatten()
            A_eq = []
            for i in range(num_sources_final):
                row = np.zeros(num_sources_final * num_dests_final)
                row[i*num_dests_final : (i+1)*num_dests_final] = 1
                A_eq.append(row)
            for j in range(num_dests_final):
                row = np.zeros(num_sources_final * num_dests_final)
                row[j::num_dests_final] = 1
                A_eq.append(row)
            A_eq = np.array(A_eq)
            b_eq = np.array(final_supply + final_demand)

            res = linprog(c=costs_flat, A_eq=A_eq, b_eq=b_eq, method='highs')

            if res.success:
                st.success("✅ Optimal solution found!")
                
                total_cost = res.fun
                st.metric(label="**Final Minimum Transportation Cost**", value=f"{total_cost:,.2f}")

                st.write("**Optimal Allocation Matrix (Units to Ship):**")
                allocation_matrix = res.x.reshape((num_sources_final, num_dests_final))
                
                alloc_df = pd.DataFrame(allocation_matrix, index=source_labels, columns=dest_labels).round(2)
                st.dataframe(alloc_df)
            else:
                st.error("❌ Solver failed to find an optimal solution.")
                st.write(res.message)