import pandas as pd
import numpy as np
import math
import pprint

# Import the data tables from your converted psg_data.py file
import PSG_data_EOT as psg

def design_eot_crane(load_tonnes, lift_height, hoist_speed):
    """
    Performs the complete design calculations for an EOT crane's hoisting mechanism.
    This function translates the entire EOT1.m MATLAB script.
    """
    results = {}
    print("-" * 50)
    
    design_load = 1.1 * load_tonnes
    print(f'Design Load = {design_load:.2f} Tonnes')

    # --- Step 1: Rope Design ---
    print('\n## Step 1: Design of Rope (6x37 Cross Laid)')
    load_per_fall = design_load / 3.8024
    breaking_load = load_per_fall * 12.54545455
    print(f'Load per Fall = {load_per_fall:.4f} Tonnes')
    print(f'Breaking Load Calculated = {breaking_load:.2f} Tonnes')
    
    suitable_ropes = psg.psg_data_ropedia[psg.psg_data_ropedia['Load_Tonnes'] >= breaking_load]
    if suitable_ropes.empty:
        print('Error: No suitable rope found for the calculated breaking load.')
        return None
        
    selected_rope_d = suitable_ropes['Rope_Dia_mm'].iloc[0]
    selected_bl = suitable_ropes['Load_Tonnes'].iloc[0]
    print(f'Selected rope diameter: {selected_rope_d:.2f} mm with Breaking Load: {selected_bl:.2f} Tonnes')
    
    tensile_stress = (3183.098862 * load_per_fall) / (selected_rope_d) ** 2
    c1_row = psg.c1_table[(selected_rope_d >= psg.c1_table['Range_Start']) & (selected_rope_d <= psg.c1_table['Range_End'])]
    c1 = c1_row['C1_Value'].iloc[0]
    m = 1500 / (tensile_stress * c1 * 1.02)
    z = np.interp(m, psg.mz_table['m'], psg.mz_table['Z'])
    N = (z * 1000) / 10200
    rope_status = 'Safe' if N > 10 else 'Fails in Life'
    print(f'Rope Life in Months, N = {N:.1f} ({rope_status})')
    results['Rope'] = {'Diameter_mm': selected_rope_d, 'BreakingLoad_Tonnes': selected_bl, 'Life_Months': N, 'Status': rope_status}

    # --- Step 2: Design of Pulley ---
    print('\n## Step 2: Selection of Pulley from PSG 9.10')
    suitable_pulleys = psg.pulley_data[psg.pulley_data['RopeDiameter'] >= selected_rope_d]
    chosen_pulley = suitable_pulleys.iloc[0]
    pulley_dia = (23 * selected_rope_d) + selected_rope_d
    print(f'Selected pulley with diameter D = {pulley_dia:.0f} mm')
    results['Pulley'] = {'SelectedPulley': chosen_pulley.to_dict(), 'PulleyDiameter_mm': pulley_dia}

    # --- Step 3 & 4: Design of Axle & Bearing Selection ---
    print('\n## Step 3 & 4: Design of Axle and Bearing Selection')
    a_pulley = chosen_pulley['a']
    bending_1 = 2 * load_per_fall * (45 + a_pulley / 2) * 10000
    axle_dia_cal = np.cbrt(bending_1 / 10.79922475)
    axle_dia = psg.bearing_data[psg.bearing_data['d'] >= axle_dia_cal]['d'].iloc[0]
    print(f'Calculated Axle Diameter = {axle_dia_cal:.2f} mm. Selected Standard Diameter = {axle_dia:.0f} mm')

    equi_load = 1.44 * load_per_fall * 1000
    pulley_rpm = (hoist_speed * 2 * 1000) / (math.pi * pulley_dia)
    lmr = (600000 * pulley_rpm) / 1000000
    dynamic_load = equi_load * lmr ** 0.3
    
    valid_bearings = psg.bearing_data[(psg.bearing_data['dynamicCapacity'] >= dynamic_load) & (psg.bearing_data['d'] == axle_dia)]
    chosen_bearing = valid_bearings.iloc[0]
    print(f'Selected Bearing No. {chosen_bearing["BearingNo"]} for dynamic load {dynamic_load:.2f} kgf')
    results['AxleAndBearing'] = {'FinalAxleDiameter_mm': axle_dia, 'SelectedBearing': chosen_bearing.to_dict(), 'DynamicLoad_kgf': dynamic_load}

    # --- Step 5: Hook Design ---
    print(f'\n## Step 5: Hook Design (C type Hook for {load_tonnes:.0f} Tonnes)')
    selected_hook = psg.hook_data[psg.hook_data['SafeLoad'] >= load_tonnes]
    chosen_hook = selected_hook.iloc[0]
    
    C = chosen_hook['C']
    H = 0.93 * C
    bi = 1.2 * (0.6 * C)
    bo = 1.6 * (0.12 * C)
    Ac = ((H / 2) * (bi + bo))
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

    # --- Step 6: Design of Nut ---
    print(f'\n## Step 6: Design of Nut for Hook (Thread: {chosen_hook["G1"]})')
    chosen_nut = psg.thread_data[psg.thread_data['NominalDiameter'] == chosen_hook['G1_value']]
    t_thread = chosen_nut['p'].iloc[0] - chosen_nut['e'].iloc[0]
    n_thread = math.ceil((load_tonnes * 10000) / (math.pi * chosen_nut['dc'].iloc[0] * t_thread * 75))
    h_nut = chosen_nut['p'].iloc[0] * n_thread
    print(f'No. of Threads = {n_thread}, Height of Nut = {h_nut:.0f} mm')
    results['Nut'] = {'ChosenNut': chosen_nut.to_dict(orient='records')[0], 'NumberOfThreads': n_thread, 'NutHeight_mm': h_nut}

    # --- Step 7: Thrust Bearing Selection ---
    print('\n## Step 7: Thrust Bearing Selection for Hook')
    static_load_kgf = load_tonnes * 1000
    valid_thrust_bearings = psg.thrust_bearing_data[(psg.thrust_bearing_data['Co_kgf'] >= static_load_kgf) & (psg.thrust_bearing_data['d'] >= chosen_hook['Gmin'])]
    chosen_thrust_bearing = valid_thrust_bearings.iloc[0]
    print(f"Selected Thrust Bearing No. {chosen_thrust_bearing['BearingNo']} for static load {static_load_kgf:.0f} kgf")
    results['ThrustBearing'] = {'ChosenBearing': chosen_thrust_bearing.to_dict()}

    # --- Step 8: Design of Cross Piece ---
    print('\n## Step 8: Design of Cross Piece')
    B_cross = chosen_thrust_bearing['D'] + 28
    L_axle = 130 + (chosen_pulley['a'] * 2)
    bending_2 = (load_tonnes * 5000) * ((0.5 * L_axle) - (chosen_thrust_bearing['D'] * 0.25))
    h_cross_calc = math.sqrt((bending_2 * 6) / ((B_cross - chosen_thrust_bearing['d']) * 100)) + (chosen_thrust_bearing['H'] / 3)
    h_cross = math.ceil(h_cross_calc)
    print(f'Calculated height h = {h_cross_calc:.2f} mm. Final height = {h_cross} mm')
    results['CrossPiece'] = {'FinalHeight_mm': h_cross, 'TrunionDiameter_mm': chosen_thrust_bearing['d']}

    # --- Step 9: Design of Shackle Plate ---
    print('\n## Step 9: Design of Shackle Plate and Side Plate')
    t_shackle_side = 35
    p_ind = (load_tonnes * 5000) / (t_shackle_side * chosen_thrust_bearing['d'])
    shackle_status = 'Safe' if p_ind <= 60 else 'Fails (Increase side plate thickness)'
    print(f'Induced Bearing Pressure = {p_ind:.2f} N/mm² ({shackle_status})')
    results['ShacklePlate'] = {'BearingPressure_N_mm2': p_ind, 'Status': shackle_status}

    # --- Step 10: Design of Rope Drum ---
    print('\n## Step 10: Design of Rope Drum')
    selected_drum_groove = psg.groove_data[psg.groove_data['RopeDia'] >= selected_rope_d]
    chosen_drum_groove = selected_drum_groove.iloc[0]
    l1 = chosen_pulley['a'] + 25
    Df = (29 * selected_rope_d)
    Wd = (0.002 * 23 * selected_rope_d) + 1
    Di = (23 * selected_rope_d) - (2 * Wd * 10) # w is in cm
    Ld_cm = (((lift_height * 400) / (math.pi * 2.3 * selected_rope_d)) + 12) * (chosen_drum_groove['S1'] * 0.1) + (l1 * 0.1)
    Ld_mm = Ld_cm * 10
    
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
    udl = drum_wt_N / (Ld_mm / 1000) # UDL in N/m
    
    Mb_shaft = (load_per_fall * 50000 * (Ld_cm/100)) - (udl * (Ld_cm/100)**2 * 0.125) # Moment in N-m
    torque = 1000 * ((18.5 * 60000) / (2 * math.pi * pulley_rpm)) # Torque in N-mm
    
    equi_torque = math.sqrt((Mb_shaft*1000)**2 + torque**2) # Convert moment to N-mm
    d_shaft = math.ceil(np.cbrt(equi_torque / (0.196 * 114))) # Using ASME tau = 114 N/mm2, pi/16 = 0.196
    print(f'Calculated Shaft Diameter, ds = {d_shaft:.0f} mm')
    results['DrumShaft'] = {'EquivalentTorque_N_mm': equi_torque, 'Diameter_mm': d_shaft}

    return results

# --- Main execution block to run the script from the command line ---
if __name__ == "__main__":
    print("--- EOT Crane Hoisting Mechanism Design ---")
    
    # Get user inputs
    try:
        load_input = float(input('Enter the load in tonnes: '))
        lift_input = float(input('Enter the lifting height in meters: '))
        speed_input = float(input('Enter the lifting speed in m/min: '))
        
        # Run the design function
        final_design_report = design_eot_crane(load_input, lift_input, speed_input)
        
        # Print the final results dictionary in a readable format
        if final_design_report:
            print("\n--- ✅ Final Hoisting Mechanism Design Report ---")
            pprint.pprint(final_design_report)
    except ValueError:
        print("\nInvalid input. Please enter numbers only.")
    except Exception as e:
        print(f"\nAn error occurred during the design process: {e}")






