import streamlit as st
import pandas as pd
import requests
import numpy as np
import time
from scipy.optimize import linear_sum_assignment

BACKEND_URL = "https://project-py-3q8o.onrender.com"
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
    ("Final Answer Only", "Step-by-Step Video Solution"),
    horizontal=True,
    label_visibility="collapsed"
)

# --- Step 6: Generate the chosen output ---
st.header("5. Generate Solution")

# Get the matrix from our "source of truth" state variable
matrix_values = st.session_state.editable_df.astype(float).values.tolist()

if output_type == "Step-by-Step Video":
    if st.button("🎬 Generate Solution Video", type="primary"):
        # This is the data payload to send to the backend.
        request_data = {
            "matrix": matrix_values,  # 'costs' is the variable from your st.data_editor
            "problem_type": problem_type.lower() # e.g., "minimization"
        }
        
        job_id = None
        try:
            # --- Step 1: Start the Job ---
            # This request uses the new 'start' endpoint and returns instantly.
            st.info("🚀 Sending request to the server...")
            response = requests.post(
                f"{BACKEND_URL}/api/start-assignment-animation",
                json=request_data
            )
            response.raise_for_status() # Raises an error for bad status codes (like 404 or 500)
            
            job_id = response.json().get("job_id")
            if not job_id:
                st.error("Backend did not return a job ID. Cannot check status.")
                st.stop()

        except Exception as e:
            st.error(f"❌ Failed to start the animation job: {e}")
            st.stop()

        # --- Step 2: Poll for Status ---
        st.success(f"✅ Job started successfully (ID: {job_id}). Rendering video in the background...")
        
        # Initialize the progress bar
        progress_bar = st.progress(0, text="Waiting for render to begin...")

        while True:
            try:
                # Check the job status using the job_id
                status_response = requests.get(f"{BACKEND_URL}/api/status/{job_id}")
                status_data = status_response.json()
                status = status_data.get("status")

                if status == "completed":
                    progress_bar.progress(100, text="Render Complete!")
                    st.success("✅ Animation generated successfully!")
                    
                    # Construct the full URL and display the video
                    video_url = f"{BACKEND_URL}{status_data['video_url']}"
                    st.video(video_url)
                    st.markdown(f"[📥 Download Video]({video_url})")
                    break # Exit the polling loop

                elif status == "failed":
                    st.error("❌ Animation generation failed on the server.")
                    # Display the detailed error message from Manim
                    error_details = status_data.get('error', 'No error details available.')
                    st.text_area("Server Error Log:", error_details, height=250)
                    progress_bar.empty() # Remove the progress bar on failure
                    break # Exit the loop

                elif status == "running":
                    # Update the progress bar to show activity
                    current_progress = progress_bar.value
                    if current_progress < 95:
                        progress_bar.progress(current_progress + 3, text="Rendering in progress... please wait.")
                
                else: # Handle unexpected statuses
                    st.error(f"Received an unknown status from the server: '{status}'")
                    break

                # Wait for 3 seconds before polling again to avoid spamming the server
                time.sleep(3)

            except Exception as e:
                st.error(f"An error occurred while checking the job status: {e}")
                break

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