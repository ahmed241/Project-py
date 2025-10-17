import streamlit as st
import json
import pprint
from backend.EOT_Crane import EOT_solver
import requests
import time

BACKEND_URL = "https://project-py-3q8o.onrender.com"

# Page configuration
st.set_page_config(page_title="EOT Crane Design", page_icon="🏗️")

# Page Title
if st.button("⬅️ Back", use_container_width=False):
    st.switch_page("pages/DMS.py")
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
    ("Final Answer Only", "Step-by-Step Video Solution"),
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
if output_type == "Step-by-Step Video Solution":
    if st.button("🎬 Render Video Solution", type="primary"):
        # Prepare the data payload with keys matching the backend model ('load', 'speed', 'height')
        request_data = {
            "load": load_in_tonnes,
            "speed": speed_in_mps,
            "height": lift_height
        }

        job_id = None
        try:
            # --- Step 1: Start the Job ---
            # Call the new 'start' endpoint. This request is fast and returns immediately.
            st.info("🚀 Sending request to the server...")
            response = requests.post(
                f"{BACKEND_URL}/api/start-eot-crane-animation",
                json=request_data
            )
            response.raise_for_status() # Check for HTTP errors like 404 or 500

            job_id = response.json().get("job_id")
            if not job_id:
                st.error("Backend did not return a job ID. Cannot proceed.")
                st.stop()

        except Exception as e:
            st.error(f"❌ Failed to start the animation job: {e}")
            st.stop()

        # --- Step 2: Poll for Status ---
        st.success(f"✅ Job started successfully! Rendering video in the background...")

        # Initialize a progress bar to give the user feedback
        progress_bar = st.progress(0, text="Waiting for render to begin...")

        while True:
            try:
                # Poll the status endpoint with the job_id
                status_response = requests.get(f"{BACKEND_URL}/api/status/{job_id}")
                status_data = status_response.json()
                status = status_data.get("status")

                if status == "completed":
                    progress_bar.progress(100, text="Render Complete!")
                    st.success("✅ Animation generated successfully!")

                    # Build the full URL to the video file and display it
                    video_url = f"{BACKEND_URL}{status_data['video_url']}"
                    st.video(video_url)
                    st.markdown(f"[📥 Download Video]({video_url})")
                    break # Exit the polling loop

                elif status == "failed":
                    st.error("❌ Animation generation failed on the server.")
                    # Display the detailed error log from Manim for easy debugging
                    error_details = status_data.get('error', 'No error details available.')
                    st.text_area("Server Error Log:", error_details, height=250)
                    progress_bar.empty() # Remove the progress bar on failure
                    break # Exit the loop

                elif status == "running":
                    # Animate the progress bar to show that the app is still working
                    current_progress = progress_bar.value
                    if current_progress < 95:
                        progress_bar.progress(current_progress + 3, text="Rendering in progress... please wait.")

                else: # Handle any unexpected status from the backend
                    st.error(f"Received an unknown status from the server: '{status}'")
                    break

                # Wait for a few seconds before the next poll
                time.sleep(3)

            except Exception as e:
                st.error(f"An error occurred while checking the job status: {e}")
                break
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
            
if output_type == "Final Answer Only":
    if st.button("Calculate Final Answer", type="primary"):
        with st.spinner("⚙️ Performing design calculations..."):
            # This function call will now return either the results dictionary or None if it fails
            final_design_report = EOT_solver.design_eot_crane(load_in_tonnes, lift_height, speed_in_mps)

            # Check if the calculation was successful
            if final_design_report:
                st.success("✅ Design calculations completed successfully!")
                st.header("Detailed Component Design Results")
                st.info("Click on each component below to expand its detailed design specifications.")
                st.divider()

                # --- Expander for each design step ---

                with st.expander("Step 1: ⛓️ Rope Design", expanded=True):
                    rope_data = final_design_report['Rope']
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Selected Rope Diameter", f"{rope_data['Diameter_mm']:.1f} mm")
                    col2.metric("Calculated Rope Life", f"{rope_data['Life_Months']:.1f} months")
                    if rope_data['Status'] == 'Safe':
                        col3.success(f"Status: {rope_data['Status']}")
                    else:
                        col3.error(f"Status: {rope_data['Status']}")
                    st.write(f"Based on a required breaking load of **{rope_data['BreakingLoad_Tonnes']:.2f} Tonnes**.")

                with st.expander("Step 2: ⚙️ Pulley & Axle Design"):
                    pulley_data = final_design_report['Pulley']
                    axle_data = final_design_report['AxleAndBearing']
                    col1, col2 = st.columns(2)
                    col1.metric("Pulley Diameter (D)", f"{pulley_data['PulleyDiameter_mm']:.0f} mm")
                    col2.metric("Final Axle Diameter (d)", f"{axle_data['FinalAxleDiameter_mm']:.0f} mm")

                with st.expander("Step 3: 🔵 Bearing Selection (for Pulley Axle)"):
                    bearing_data = final_design_report['AxleAndBearing']
                    col1, col2 = st.columns(2)
                    col1.metric("Required Dynamic Load", f"{bearing_data['DynamicLoad_kgf']:.2f} kgf")
                    st.success(f"Selected Bearing: **No. {bearing_data['SelectedBearing']['BearingNo']}**")

                with st.expander("Step 4: ⚓️ Hook Design"):
                    hook_data = final_design_report['Hook']
                    col1, col2 = st.columns(2)
                    col1.metric("Resultant Stress", f"{hook_data['ResultantStress_N_mm2']:.2f} N/mm²")
                    if hook_data['Status'] == 'Safe':
                        col2.success(f"Status: {hook_data['Status']}")
                    else:
                        col2.error(f"Status: {hook_data['Status']}")
                    st.write(f"Selected Hook Type: Based on PSG 9.1 for a safe load of **{hook_data['ChosenHook']['SafeLoad']} Tonnes**.")

                with st.expander("Step 5: 🔩 Nut & Thrust Bearing Design (for Hook)"):
                    nut_data = final_design_report['Nut']
                    thrust_bearing_data = final_design_report['ThrustBearing']
                    col1, col2 = st.columns(2)
                    col1.metric("Nut Height", f"{nut_data['NutHeight_mm']:.0f} mm")
                    col2.metric("Number of Threads", nut_data['NumberOfThreads'])
                    st.success(f"Selected Thrust Bearing: **No. {thrust_bearing_data['ChosenBearing']['BearingNo']}**")

                with st.expander("Step 6: ➕ Cross Piece & Shackle Plate Design"):
                    cross_piece_data = final_design_report['CrossPiece']
                    shackle_data = final_design_report['ShacklePlate']
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Cross Piece Height", f"{cross_piece_data['FinalHeight_mm']:.0f} mm")
                    col2.metric("Bearing Pressure", f"{shackle_data['BearingPressure_N_mm2']:.2f} N/mm²")
                    if shackle_data['Status'] == 'Safe':
                        col3.success(f"Shackle Status: {shackle_data['Status']}")
                    else:
                        col3.error(f"Shackle Status: {shackle_data['Status']}")

                with st.expander("Step 7: 🥁 Rope Drum Design"):
                    drum_data = final_design_report['RopeDrum']
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Drum Length", f"{drum_data['Length_mm']:.1f} mm")
                    col2.metric("Bending Stress", f"{drum_data['BendingStress_N_mm2']:.2f} N/mm²")
                    if drum_data['Status'] == 'Safe':
                        col3.success(f"Status: {drum_data['Status']}")
                    else:
                        col3.error(f"Status: {drum_data['Status']}")

                with st.expander("Step 8: shaft: Drum Shaft Design"):
                    shaft_data = final_design_report['DrumShaft']
                    col1, col2 = st.columns(2)
                    col1.metric("Final Shaft Diameter", f"{shaft_data['Diameter_mm']:.0f} mm")
                    col2.metric("Equivalent Torque", f"{shaft_data['EquivalentTorque_N_mm']:,.0f} N-mm")

                st.divider()
                # Display the full JSON report for debugging or detailed view
                with st.expander("Show Full Design Data (JSON)"):
                    st.json(final_design_report)

            else:
                # This block runs if design_eot_crane returned None
                st.error("❌ Design Calculation Failed. The input parameters may be outside the valid design range of the PSG data book. Please check the console for specific errors.")