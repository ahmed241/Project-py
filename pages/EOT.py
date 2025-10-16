import streamlit as st
import json
import pprint
from EOT_Crane import EOT_solver

# Page configuration
st.set_page_config(page_title="EOT Crane Design", page_icon="🏗️")

# Page Title
st.title("🏗️ EOT Crane Hoisting Mechanism Design")
st.write("Enter the required specifications to begin the design process based on PSG Design Data Book standards.")
st.markdown("---")


# --- Input Section ---
st.header("1. Input Parameters")

# --- 1. Load Input with Unit Selection ---
st.subheader("Hoisting Load")
col1, col2 = st.columns([2, 1])
with col1:
    load_value = st.number_input("Enter the load to be lifted", min_value=0.1, value=10.0, step=0.5, key="load_val")
with col2:
    load_unit = st.radio("Select Load Unit", ["tonnes", "kN"], horizontal=True, label_visibility="collapsed", key="load_unit")


# --- 2. Speed Input with Unit Selection ---
st.subheader("Hoisting Speed")
col1, col2 = st.columns([2, 1])
with col1:
    speed_value = st.number_input("Enter the hoisting speed", min_value=0.1, value=5.0, step=0.1, key="speed_val")
with col2:
    speed_unit = st.radio("Select Speed Unit", ["m/min", "m/s"], horizontal=True, label_visibility="collapsed", key="speed_unit")


# --- 3. Lift Input ---
st.subheader("Lift Height")
lift_height = st.number_input("Enter the required lift height (in metres)", min_value=1.0, value=6.0, step=0.5, key="lift_h")

st.markdown("---")

# --- Step 2: Choose Output Format ---
st.header("2. Choose Output Format")
output_type = st.radio(
    "How would you like to see the solution?",
    ("Final Answer Only", "Step-by-step Video Solution"),
    horizontal=True,
    label_visibility="collapsed"
)

# --- Step 3: Generate Solution ---
st.header("3. Generate Solution")


# Normalize the load to Tonnes for calculation
if load_unit == 'kN':
    # 1 kN = 0.1 Tonnes
    load_in_tonnes = load_value * 0.1
else: # 'kN'
    load_in_tonnes = load_value

# Normalize the speed to m/s for calculation
if speed_unit == 'm/min':
    speed_in_mps = speed_value / 60.0
else: # 'm/s'
    speed_in_mps = speed_value

# Create a dictionary of the input data
input_data = {
"load_value": load_in_tonnes,
"speed_value": speed_in_mps,
"lift_height": lift_height
}
if output_type == "Final Answer Only":
    if st.button("Calculate Final Answer", type="primary"):
        # First, save the raw data to a JSON file
        try:
            with open("EOT_Crane/data.json", "w") as f:
                json.dump(input_data, f, indent=4)
            st.toast("Input data saved to `data.json`")
        except Exception as e:
            st.error(f"Failed to save data: {e}")

        # --- Unit Conversion & Calculation Logic ---
        st.subheader("Standardized Design Inputs")
        st.success("The design process will be based on the following standardized parameters:")
        

        # Display the standardized inputs
        col1, col2, col3 = st.columns(3)
        col1.metric(label="Load (Tonnes)", value=f"{load_in_tonnes:,.2f} Tonnes")
        col2.metric(label="Speed (m/s)", value=f"{speed_in_mps:.3f} m/s")
        col3.metric(label="Lift (metres)", value=f"{lift_height:.2f} m")
        
        st.info("These values are now ready for detailed component design.")
        st.markdown("---")
        st.header("Detailed Component Design Results")
        final_design_report = EOT_solver.design_eot_crane(load_in_tonnes,lift_height, speed_in_mps)
        if final_design_report:
            print("\n--- ✅ Final Hoisting Mechanism Design Report ---")
            pprint.pprint(final_design_report)

else: # "Step-by-step Video Solution" was selected
    if st.button("Render Video", type="primary"):
        # First, save the raw data to a JSON file for the backend to use
        try:
            with open("EOT_Crane/data.json", "w") as f:
                json.dump(input_data, f, indent=4)
            st.success("Input data saved to `data.json`")
            
            st.info("🚀 Preparing to send data to the Manim render service...")
            
            with st.expander("Confirm Data Sent"):
                st.json(input_data)
                
            # (Here you would add the code to make an HTTP request to your FastAPI backend)

        except Exception as e:
            st.error(f"Failed to save data: {e}")