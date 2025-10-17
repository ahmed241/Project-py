import streamlit as st
import pandas as pd
import requests
import numpy as np
from scipy.optimize import linear_sum_assignment

BACKEND_URL = "http://localhost:7000"
# --- Sample Data Definition ---
SAMPLE_ASSIGNMENT_DATA = {
    "rows": 4,
    "cols": 4,
    "matrix": [
        [90, 75, 75, 80],
        [35, 85, 55, 65],
        [125, 95, 90, 105],
        [45, 110, 95, 115],
    ]
}

# --- Callback Function ---
# This function is called when the "Load Sample Data" button is clicked
def load_assignment_sample():
    # Update the dimension inputs in the UI
    if st.session_state.matrix_type_radio == "Square":
        st.session_state.n_dim_input = SAMPLE_ASSIGNMENT_DATA["rows"]
    else: # Rectangular
        st.session_state.num_rows_input = SAMPLE_ASSIGNMENT_DATA["rows"]
        st.session_state.num_cols_input = SAMPLE_ASSIGNMENT_DATA["cols"]

    # Create a DataFrame from the sample data and store it in our own state variable.
    # This is the correct way, as we are not touching a widget's key.
    st.session_state.editable_df = pd.DataFrame(
        SAMPLE_ASSIGNMENT_DATA["matrix"],
        columns=[f"Col {j+1}" for j in range(SAMPLE_ASSIGNMENT_DATA["cols"])],
        index=[f"Row {i+1}" for i in range(SAMPLE_ASSIGNMENT_DATA["rows"])]
    )

# --- App UI ---
# Back to main button
if st.button("⬅️ Back", use_container_width=False):
    st.switch_page("pages/OR.py")
st.title("Hungarian Algorithm Visualizer")

# --- Step 1: Define Matrix Dimensions ---
st.header("1. Define Your Matrix")

matrix_type = st.radio(
    "Select Matrix Type:",
    ("Square", "Rectangular"),
    horizontal=True,
    key="matrix_type_radio" # Add key for the callback
)

if matrix_type == "Square":
    n = st.number_input("Dimension (n x n):", min_value=2, max_value=5, step=1, key="n_dim_input")
    rows, cols = n, n
else: # Rectangular
    col1, col2 = st.columns(2)
    with col1:
        rows = st.number_input("Number of Rows:", min_value=2, max_value=6, step=1, key="num_rows_input")
    with col2:
        cols = st.number_input("Number of Columns:", min_value=2, max_value=6, step=1, key="num_cols_input")

# --- Step 2: Problem Type Selection ---
st.header("2. Select Problem Type")
problem_type = st.radio(
    "Is this a minimization or maximization problem?",
    ("Minimization (e.g., Cost or Time)", "Maximization (e.g., Profit)"),
    horizontal=True
)

# --- Step 3: Enter Matrix Values ---
st.header("3. Enter Matrix Values")

st.button("Load Sample Data", on_click=load_assignment_sample, help="Click to load a pre-defined 4x4 problem.")

# Initialize or update our DataFrame in session state.
# This is our "source of truth" for the data editor.
if 'editable_df' not in st.session_state or st.session_state.editable_df.shape != (rows, cols):
    st.session_state.editable_df = pd.DataFrame(
        [[10 for _ in range(cols)] for _ in range(rows)],
        columns=[f"Col {j+1}" for j in range(cols)],
        index=[f"Row {i+1}" for i in range(rows)]
    )

st.write("Enter costs matrix in the table below:")
# Display the data editor with the data from our state variable.
# The user's edits are returned by the widget.
edited_df = st.data_editor(st.session_state.editable_df)

# After the user interacts, update our state variable with the edited data.
st.session_state.editable_df = edited_df

# For now, we assume no restricted cells.
st.session_state.restricted_cells = [[False for _ in range(cols)] for _ in range(rows)]

# --- Step 4: Your Current Matrix (Optional Display) ---
with st.expander("Confirm Your Current Matrix"):
    st.table(st.session_state.editable_df)

# --- Step 5: Choose Output Format ---
st.header("4. Choose Output Format")
output_type = st.radio(
    "How would you like to see the solution?",
    ("Final Answer Only", "Step-by-step Video Solution"),
    horizontal=True,
    label_visibility="collapsed"
)

# --- Step 6: Generate the chosen output ---
st.header("5. Generate Solution")

# Get the matrix from our "source of truth" state variable
matrix_values = st.session_state.editable_df.astype(float).values.tolist()

if output_type == "Step-by-step Video Solution":
    if st.button("Render Video", type="primary"):
        with st.spinner("🎥 Generating animation... This may take time."):
                try:
                    # Call backend API
                    response = requests.post(
                        f"{BACKEND_URL}/api/assignment",
                        json={
                            "matrix": matrix_values,
                            "problem_type": problem_type
                        }
                    )
                    
                    result = response.json()
                    
                    if "error" in result:
                        st.error(f"Error: {result['error']}")
                    else:
                        st.success("✅ Animation generated successfully!")
                        
                        # Display video
                        video_url = f"{BACKEND_URL}{result['video_url']}"
                        st.success(f"Video at {video_url}")
                        st.video(video_url)
                        # Download link
                        st.markdown(f"[📥 Download Video]({video_url})")
                
                except requests.exceptions.Timeout:
                    st.error("⏰ Request timed out. The animation is taking too long.")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

else: # The "Final Answer Only" option was selected
    if st.button("Calculate Final Answer", type="primary"):
        try:
            original_matrix = np.array(matrix_values, dtype=float)
            cost_matrix = original_matrix.copy()

            is_maximization = "Maximization" in problem_type
            if is_maximization:
                max_val = np.max(cost_matrix[np.isfinite(cost_matrix)]) if np.any(np.isfinite(cost_matrix)) else 0
                cost_matrix = max_val - cost_matrix

            row_ind, col_ind = linear_sum_assignment(cost_matrix)
            
            st.success("Optimal solution found!")
            
            optimal_value = original_matrix[row_ind, col_ind].sum()
            metric_label = "Total Profit" if is_maximization else "Total Cost"
            st.metric(label=f"**Optimal Value ({metric_label})**", value=f"{optimal_value:,.2f}")

            st.write("**Assignments:**")
            assignment_data = []
            for r, c in zip(row_ind, col_ind):
                assignment_data.append({
                    "Assign": f"Row {r+1}",
                    "To": f"Column {c+1}",
                    "Value": original_matrix[r, c]
                })
            st.table(pd.DataFrame(assignment_data))

        except Exception as e:
            st.error(f"An error occurred during calculation: {e}")