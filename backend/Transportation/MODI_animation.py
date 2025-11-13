from manim import *
from manim_narration import NarrationScene
from manim_narration.speech import KokoroService
from MODI_helper_funcs import AnimationHelpers
from VAM_solver import solve_vam
from MODI_solver import adjust_allocations # <-- Import the logic function
import json
import os

class MODI_Transportation(NarrationScene):
    def construct(self):
        self.set_speech_services(
            en=KokoroService(voice="af_jessica", lang_code="en-us")
        )
        # --- 0. Setup ---
        # Load data from JSON
        script_dir = os.path.dirname(__file__)
        json_path = os.path.join(script_dir, "transportation_problem.json")
        with open(json_path, "r") as f:
            data = json.load(f)
            supply = data["supply"]
            demand = data["demand"]
            costs = data["costs"]
            
        # --- 1. Get Initial VAM Solution ---
        # This is the pure logic step
        initial_allocation, initial_cost, update_costs, costs_to_solve, update_demand, update_supply = solve_vam(supply, demand, costs)

        # --- 2. Animate Scene Titles ---
        Header = Tex("Transportation Problem\\\\Modified Distribution Method (MODI)", font_size=48)
        self.play(Write(Header))
        self.wait(0.75)
        vam_title = Tex("Initial Solution using Vogel's Approximation Method")
        self.play(Header.animate.scale(0.75).to_edge(UP, buff=0.25))
        
        self.play(Write(vam_title))
        self.wait(0.25)
        self.play(vam_title.animate.scale(0.75).next_to(Header, DOWN, buff=0.1).set_color(LIGHT_PINK))

        # --- 3. Create Helper and Initial Table (One-Time Setup) ---
        helpers = AnimationHelpers()

        (
            table, 
            alloc_mobject_map, 
            table_alloc # This VGroup holds the table + allocs
        ) = helpers.create_table_with_allocations(
            self,
            costs_to_solve, 
            update_supply, 
            update_demand, 
            initial_allocation,
            Header
        )
        with self.narration(speech_service_id="en", text = "Final Optimal Solution using Modified Distribution Method") as narration:
            self.play(FadeOut(vam_title)) # Fade VAM title
        # --- 4. Extend Table (One-Time Setup) ---
        # This shifts the table to its final position
        (
            row_lines,
            col_lines
        ) = helpers.extend_table(
            self,
            table,
            table_alloc, 
            costs_to_solve
        )

        # --- 5. START MODI ITERATION LOOP ---
        # We use a 'for' loop as a safety break (max 5 iterations)
        # A real solver might use 'while True'
        
        for i in range(5):
            # self.next_section(f"Iteration {i+1}")
            
            # --- 5a. Degeneracy Check ---
            is_degenerate = helpers.animate_degeneracy_check(
                self,
                table,
                alloc_mobject_map,
                costs_to_solve,
                Header
            ) 
            epsilon_mob = None # Clear epsilon tracker each loop
            
            # --- 5b. Handle Degeneracy ---
            if is_degenerate:
                (
                    initial_allocation, # Overwrite logic
                    alloc_mobject_map,  # Overwrite map
                    epsilon_mob         # Get the epsilon mobject
                ) = helpers.handle_degeneracy(
                    self,
                    table,
                    costs_to_solve,
                    initial_allocation,
                    alloc_mobject_map,
                    Header
                )
                table_alloc.add(epsilon_mob) # Add epsilon to the main VGroup

            # --- 5c. Calculate u_i and v_j ---
            (
                u_vals, 
                v_vals,
                uv_mobs
            ) = helpers.animate_uv_calculation(
                self,
                table,
                costs_to_solve,
                initial_allocation,
                alloc_mobject_map,
                row_lines,
                col_lines,
                Header
            )

            # --- 5d. Calculate Opportunity Costs ---
            (
                opportunity_costs, 
                cost_mobjects, 
                most_positive_cost, 
                entering_cell_coords, 
                entering_cell_mobject
            ) = helpers.calculate_opportunity_costs( # This is your function
                self,
                table,
                costs_to_solve,
                initial_allocation, # This is the logic matrix
                u_vals,
                v_vals,
                Header
            )

            # --- 5e. Check for Optimality ---
            is_optimal = helpers.animate_check_optimality(
                self,
                table,
                Header,
                cost_mobjects,
                most_positive_cost,
                entering_cell_coords,
                entering_cell_mobject
            )

            self.wait(1)

            # --- 5f. Decide Next Step ---
            if is_optimal:
                if epsilon_mob: # Clean up any leftover epsilon
                    self.play(FadeOut(epsilon_mob))
                self.wait(3)
                break # <-- EXIT THE FOR LOOP
            
            else:
                # --- 5g. Find and Animate Loop ---
                (
                    loop_path,
                    loop_cleanup_mobjects # Mobjects to fade out
                ) = helpers.animate_loop_and_signs(
                    self,
                    table,
                    initial_allocation,  # The logic matrix (with epsilon)
                    entering_cell_coords, # The (r, c) tuple
                    Header
                )

                # --- 5h. Get New Logic (No animation) ---
                # We need the *results* of the adjustment
                # to feed into the table_update function.
                (
                    new_allocations_logic, 
                    theta, 
                    plus_cells, 
                    minus_cells
                ) = adjust_allocations(initial_allocation, loop_path)

                # --- 5i. Update Table Visuals ---
                (
                    new_table,
                    new_alloc_map_updated,
                    new_table_alloc
                ) = helpers.animate_table_update(
                    self,
                    table_alloc, # The old VGroup
                    update_costs,
                    update_supply,
                    update_demand,
                    new_allocations_logic # The new logic
                )

                # --- 5j. Update State for Next Iteration ---
                initial_allocation = new_allocations_logic
                alloc_mobject_map = new_alloc_map_updated
                table = new_table
                table_alloc = new_table_alloc
                
                # --- 5k. Cleanup ---
                self.play(
                    FadeOut(loop_cleanup_mobjects),
                    FadeOut(epsilon_mob), # Fade out old epsilon if it exists
                    FadeOut(uv_mobs)
                )
                
                # --- LOOP CONTINUES ---
        
        # --- 6. End of Animation ---
        self.wait(3)