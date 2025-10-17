import pandas as pd
import numpy as np
import math
import pprint

# Import the data tables from your converted psg_data.py file
# This file should contain all the pandas DataFrames with PSG data.
import backend.EOT_Crane.PSG_data_EOT as psg

def design_eot_crane(load_tonnes, lift_height, hoist_speed):
    """
    Performs the complete design calculations for an EOT crane's hoisting mechanism.
    It checks for valid components at each step and returns a dictionary with the
    results, or None if a suitable component cannot be found.
    """
    # Create an empty dictionary to store the results of each step.
    results = {}
    print("-" * 50)
    
    # Apply a factor of safety (10%) to the input load to get the design load.
    design_load = 1.1 * load_tonnes
    print(f'Design Load = {design_load:.2f} Tonnes')

    # --- Step 1: Rope Design ---
    print('\n## Step 1: Design of Rope (6x37 Cross Laid)')
    # Calculate the load on each fall of the rope and the required breaking strength.
    load_per_fall = design_load / 3.8024
    breaking_load = load_per_fall * 12.54545455
    print(f'Load per Fall = {load_per_fall:.4f} Tonnes')
    print(f'Breaking Load Calculated = {breaking_load:.2f} Tonnes')
    
    # --- ROBUST SELECTION ---
    # Find all ropes from the PSG data table that can handle the required breaking load.
    suitable_ropes = psg.psg_data_ropedia[psg.psg_data_ropedia['Load_Tonnes'] >= breaking_load]
    # EXCEPTION CHECK: If the DataFrame is empty, no rope was found. Stop the design.
    if suitable_ropes.empty:
        print(f'❌ Error: No suitable rope found in PSG data for a breaking load of {breaking_load:.2f} Tonnes.')
        return None
        
    # Select the first (smallest) suitable rope from the filtered list.
    selected_rope_d = suitable_ropes['Rope_Dia_mm'].iloc[0]
    selected_bl = suitable_ropes['Load_Tonnes'].iloc[0]
    print(f'Selected rope diameter: {selected_rope_d:.2f} mm with Breaking Load: {selected_bl:.2f} Tonnes')
    
    # Calculate the tensile stress in the selected rope.
    tensile_stress = (3183.098862 * load_per_fall) / (selected_rope_d) ** 2
    
    # --- ROBUST SELECTION (for range-based data) ---
    # Find the correct C1 value from the table based on the selected rope diameter.
    # This logic finds the last row where the start of the range is less than our value.
    c1_row = psg.c1_table[psg.c1_table['Range_Start'] <= selected_rope_d].iloc[-1:]
    # EXCEPTION CHECK: If no C1 range is found, stop.
    if c1_row.empty:
        print(f"❌ Error: Could not find a C1 value for rope diameter {selected_rope_d:.2f} mm. Design cannot proceed.")
        return None

    # Get the C1 value from the selected row.
    c1 = c1_row['C1_Value'].iloc[0]
    
    # Calculate the expected life of the rope in months.
    m = 1500 / (tensile_stress * c1 * 1.02)
    z = np.interp(m, psg.mz_table['m'], psg.mz_table['Z']) # Interpolate to find Z value
    N = (z * 1000) / 10200 # N is the life in months
    rope_status = 'Safe' if N > 10 else 'Fails in Life'
    print(f'Rope Life in Months, N = {N:.1f} ({rope_status})')
    # Store the results of this step.
    results['Rope'] = {'Diameter_mm': selected_rope_d, 'BreakingLoad_Tonnes': selected_bl, 'Life_Months': N, 'Status': rope_status}

    # --- Step 2: Design of Pulley ---
    print('\n## Step 2: Selection of Pulley from PSG 9.10')
    # --- ROBUST SELECTION ---
    # Find all pulleys suitable for the selected rope diameter.
    suitable_pulleys = psg.pulley_data[psg.pulley_data['RopeDiameter'] >= selected_rope_d]
    # EXCEPTION CHECK: If no pulley is found, stop.
    if suitable_pulleys.empty:
        print(f"❌ Error: No suitable pulley found for rope diameter {selected_rope_d:.2f} mm.")
        return None
        
    # Select the first suitable pulley.
    chosen_pulley = suitable_pulleys.iloc[0]
    pulley_dia = (23 * selected_rope_d) + selected_rope_d # Pulley diameter calculation
    print(f'Selected pulley with diameter D = {pulley_dia:.0f} mm')
    results['Pulley'] = {'SelectedPulley': chosen_pulley.to_dict(), 'PulleyDiameter_mm': pulley_dia}

    # --- Step 3 & 4: Design of Axle & Bearing Selection ---
    print('\n## Step 3 & 4: Design of Axle and Bearing Selection')
    a_pulley = chosen_pulley['a']
    bending_moment = 2 * load_per_fall * (45 + a_pulley / 2) * 10000
    axle_dia_cal = np.cbrt(bending_moment / 10.79922475) # Calculate theoretical axle diameter
    
    # --- ROBUST SELECTION ---
    # Find a standard bearing with an inner diameter 'd' greater than what we calculated.
    suitable_axles = psg.bearing_data[psg.bearing_data['d'] >= axle_dia_cal]
    if suitable_axles.empty:
        print(f"❌ Error: No standard bearing found for a required axle diameter of {axle_dia_cal:.2f} mm.")
        return None
    axle_dia = suitable_axles['d'].iloc[0] # Select the smallest standard diameter
    print(f'Calculated Axle Diameter = {axle_dia_cal:.2f} mm. Selected Standard Diameter = {axle_dia:.0f} mm')

    # Calculate the dynamic load on the bearing.
    equi_load = 1.44 * load_per_fall * 1000
    pulley_rpm = (hoist_speed * 2 * 1000) / (math.pi * pulley_dia)
    lmr = (600000 * pulley_rpm) / 1000000
    dynamic_load = equi_load * lmr ** 0.3
    
    # --- ROBUST SELECTION ---
    # Find a bearing that has the correct inner diameter AND can handle the dynamic load.
    valid_bearings = psg.bearing_data[(psg.bearing_data['dynamicCapacity'] >= dynamic_load) & (psg.bearing_data['d'] == axle_dia)]
    if valid_bearings.empty:
        print(f"❌ Error: No bearing found with diameter {axle_dia:.0f} mm that can support a dynamic load of {dynamic_load:.2f} kgf.")
        return None
    chosen_bearing = valid_bearings.iloc[0]
    print(f'Selected Bearing No. {chosen_bearing["BearingNo"]} for dynamic load {dynamic_load:.2f} kgf')
    results['AxleAndBearing'] = {'FinalAxleDiameter_mm': axle_dia, 'SelectedBearing': chosen_bearing.to_dict(), 'DynamicLoad_kgf': dynamic_load}

    # --- Step 5: Hook Design ---
    print(f'\n## Step 5: Hook Design (C type Hook for {load_tonnes:.0f} Tonnes)')
    # --- ROBUST SELECTION ---
    # Select a standard hook that can handle the initial safe load.
    selected_hook = psg.hook_data[psg.hook_data['SafeLoad'] >= load_tonnes]
    if selected_hook.empty:
        print(f"❌ Error: No standard hook found for a safe load of {load_tonnes:.2f} Tonnes.")
        return None
    chosen_hook = selected_hook.iloc[0]
    
    # Calculate stresses in the hook using trapezoidal formulas.
    C = chosen_hook['C']
    H = 0.93 * C
    bi = 1.2 * (0.6 * C)
    bo = 1.6 * (0.12 * C)
    Ac = ((H / 2) * (bi + bo)) # Area of cross-section
    direct_stress = load_tonnes * 10000 / Ac
    R_trapezoid = (C / 2) + (H * (bi + (2 * bo))) / (3 * (bo + bi))
    Mb = load_tonnes * R_trapezoid * 10000
    ro = (0.5 * C) + H
    rn = (0.5 * H * (bi + bo)) / ((((bi * ro) - (bo * 0.5 * C)) / H) * math.log(ro / (0.5 * C)) - (bi - bo))
    hi = rn - (0.5 * C)
    bending_stress = (Mb * hi) / (Ac * (R_trapezoid - rn) * 0.5 * C)
    resultant_stress = direct_stress + bending_stress
    hook_status = 'Safe' if resultant_stress < 150 else 'Fails'
    print(f'Resultant Stress in Hook = {resultant_stress:.2f} N/mm² ({hook_status})')
    results['Hook'] = {'ChosenHook': chosen_hook.to_dict(), 'ResultantStress_N_mm2': resultant_stress, 'Status': hook_status}

    # --- Step 6: Design of Nut for Hook ---
    print(f'\n## Step 6: Design of Nut for Hook (Thread: {chosen_hook["G1"]})')
    # --- ROBUST SELECTION ---
    # Find the thread data for the nut based on the selected hook's shank diameter.
    chosen_nut = psg.thread_data[psg.thread_data['NominalDiameter'] == chosen_hook['G1_value']]
    if chosen_nut.empty:
        print(f"❌ Error: No thread data found for nut nominal diameter {chosen_hook['G1_value']} mm.")
        return None
        
    # Calculate the required number of threads and height of the nut.
    t_thread = chosen_nut['p'].iloc[0] - chosen_nut['e'].iloc[0]
    n_thread = math.ceil((load_tonnes * 10000) / (math.pi * chosen_nut['dc'].iloc[0] * t_thread * 75))
    h_nut = chosen_nut['p'].iloc[0] * n_thread
    print(f'No. of Threads = {n_thread}, Height of Nut = {h_nut:.0f} mm')
    results['Nut'] = {'ChosenNut': chosen_nut.to_dict(orient='records')[0], 'NumberOfThreads': n_thread, 'NutHeight_mm': h_nut}

    # --- Step 7: Thrust Bearing Selection for Hook ---
    print('\n## Step 7: Thrust Bearing Selection for Hook')
    static_load_kgf = load_tonnes * 1000
    # --- ROBUST SELECTION ---
    # Find a thrust bearing that fits the hook and can handle the static load.
    valid_thrust_bearings = psg.thrust_bearing_data[(psg.thrust_bearing_data['Co_kgf'] >= static_load_kgf) & (psg.thrust_bearing_data['d'] >= chosen_hook['Gmin'])]
    if valid_thrust_bearings.empty:
        print(f"❌ Error: No thrust bearing found for static load {static_load_kgf:.0f} kgf and min diameter {chosen_hook['Gmin']} mm.")
        return None
    chosen_thrust_bearing = valid_thrust_bearings.iloc[0]
    print(f"Selected Thrust Bearing No. {chosen_thrust_bearing['BearingNo']} for static load {static_load_kgf:.0f} kgf")
    results['ThrustBearing'] = {'ChosenBearing': chosen_thrust_bearing.to_dict()}

    # --- Step 8: Design of Cross Piece ---
    print('\n## Step 8: Design of Cross Piece')
    # These are direct calculations based on previously selected components.
    B_cross = chosen_thrust_bearing['D'] + 28
    L_axle = 130 + (chosen_pulley['a'] * 2)
    bending_2 = (load_tonnes * 5000) * ((0.5 * L_axle) - (chosen_thrust_bearing['D'] * 0.25))
    h_cross_calc = math.sqrt((bending_2 * 6) / ((B_cross - chosen_thrust_bearing['d']) * 100)) + (chosen_thrust_bearing['H'] / 3)
    h_cross = math.ceil(h_cross_calc)
    print(f'Calculated height h = {h_cross_calc:.2f} mm. Final height = {h_cross} mm')
    results['CrossPiece'] = {'FinalHeight_mm': h_cross, 'TrunionDiameter_mm': chosen_thrust_bearing['d']}

    # --- Step 9: Design of Shackle Plate ---
    print('\n## Step 9: Design of Shackle Plate and Side Plate')
    t_shackle_side = 35 # Assumed thickness
    p_ind = (load_tonnes * 5000) / (t_shackle_side * chosen_thrust_bearing['d'])
    shackle_status = 'Safe' if p_ind <= 60 else 'Fails (Increase side plate thickness)'
    print(f'Induced Bearing Pressure = {p_ind:.2f} N/mm² ({shackle_status})')
    results['ShacklePlate'] = {'BearingPressure_N_mm2': p_ind, 'Status': shackle_status}

    # --- Step 10: Design of Rope Drum ---
    print('\n## Step 10: Design of Rope Drum')
    # --- ROBUST SELECTION ---
    # Select the groove dimensions for the drum based on rope diameter.
    selected_drum_groove = psg.groove_data[psg.groove_data['RopeDia'] >= selected_rope_d]
    if selected_drum_groove.empty:
        print(f"❌ Error: No drum groove data found for rope diameter {selected_rope_d:.2f} mm.")
        return None
    chosen_drum_groove = selected_drum_groove.iloc[0]
    
    # Calculate drum dimensions and stresses.
    l1 = chosen_pulley['a'] + 25
    Df = (29 * selected_rope_d)
    Wd = (0.002 * 23 * selected_rope_d) + 1 # Thickness in cm
    Di = (23 * selected_rope_d) - (2 * Wd * 10) # Inner diameter in mm
    Ld_cm = (((lift_height * 400) / (math.pi * 2.3 * selected_rope_d)) + 12) * (chosen_drum_groove['S1'] * 0.1) + (l1 * 0.1)
    Ld_mm = round(Ld_cm * 10)
    
    sigma_b_ind = (1600000 * load_per_fall * Ld_cm * selected_rope_d * 23) / (((selected_rope_d * 23) ** 4 - Di ** 4) * math.pi)
    drum_status = 'Safe' if sigma_b_ind < 50 else 'Fails in Bending'
    print(f'Length of Drum, L = {Ld_mm:.2f} mm')
    print(f'Induced Bending Stress = {sigma_b_ind:.2f} N/mm² ({drum_status})')
    results['RopeDrum'] = {'Length_mm': Ld_mm, 'InnerDiameter_mm': Di, 'BendingStress_N_mm2': sigma_b_ind, 'Status': drum_status}

    # --- Step 11: Design of Drum Shaft ---
    print('\n## Step 11: Design of Drum Shaft')
    D_drum = 23 * selected_rope_d
    drum_volume_m3 = ((math.pi / 4) * (D_drum**2 - Di**2) * Ld_mm) / 1000**3
    drum_wt_N = drum_volume_m3 * 9.81 * 7200
    udl = drum_wt_N / (Ld_mm / 1000) # Uniformly Distributed Load in N/m
    
    # Calculate moment and torque on the shaft.
    Mb_shaft = (load_per_fall * 50000 * (Ld_cm/100)) - (udl * (Ld_cm/100)**2 * 0.125) # Moment in N-m
    torque = 1000 * ((18.5 * 60000) / (2 * math.pi * pulley_rpm)) # Torque in N-mm
    
    equi_torque = math.sqrt((Mb_shaft*1000)**2 + torque**2) # Convert moment to N-mm for calculation
    # Calculate required shaft diameter using ASME code for shafts.
    d_shaft = math.ceil(np.cbrt(equi_torque / (0.196 * 114))) # Using allowable shear stress tau = 114 N/mm2
    print(f'Calculated Shaft Diameter, ds = {d_shaft:.0f} mm')
    results['DrumShaft'] = {'EquivalentTorque_N_mm': equi_torque, 'Diameter_mm': d_shaft}

    # If all steps complete successfully, return the full results dictionary.
    return results

# This block allows you to run the script directly from the command line for testing.
if __name__ == "__main__":
    print("--- EOT Crane Hoisting Mechanism Design (Test Runner) ---")
    
    try:
        load_input = float(input('Enter the load in tonnes: '))
        lift_input = float(input('Enter the lifting height in meters: '))
        speed_input = float(input('Enter the lifting speed in m/min: '))
        
        # Run the main design function with user inputs.
        final_design_report = design_eot_crane(load_input, lift_input, speed_input)
        
        # If the function returns a report (not None), print it nicely.
        if final_design_report:
            print("\n--- ✅ Final Hoisting Mechanism Design Report ---")
            pprint.pprint(final_design_report)
    except ValueError:
        print("\n❌ Invalid input. Please enter numbers only.")
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")