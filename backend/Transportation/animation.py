import argparse
import json
import os
import time

parser = argparse.ArgumentParser()
parser.add_argument("--data_file", type=str, required=True)
parser.add_argument("--output_name", type=str, required=True)
args = parser.parse_args()

class TransportationScene(Scene):
    def construct(self):
        with open(args.data_file, "r") as f:
            data = json.load(f)
            supply = data["supply"]
            demand = data["demand"]
            cost = data["cost"]
        
        Header = Tex("Transportation Problem\\\\Vogel's Approximation Method", font_size=48).to_edge(UP, buff=0.1)
        self.play(Write(Header))
        self.wait(0.75)
        self.play(Header.animate.scale(0.75))
        
        full_table = AnimationHelpers.create_transportation_table(
            self, costs, supply, demand
        )
        table = full_table
        
        # This will return a new table and balanced data if changes were made
        balanced_table, balanced_costs, balanced_supply, balanced_demand = AnimationHelpers.animate_balance_problem(self, table, costs, supply, demand)

        # From this point on, use the BALANCED variables for everything
        row_penalty_lines, col_penalty_lines = AnimationHelpers.animate_extend_for_penalties(
            self, balanced_table) # Use the balanced_table
        self.wait(1)
        
        
        # --- Main VAM Loop ---
        current_supply = copy.deepcopy(supply)
        current_demand = copy.deepcopy(demand)
        satisfied_rows = set() # Use set for efficiency
        satisfied_cols = set() # Use set for efficiency
        allocations = {}  # Dictionary to store {(row, col): quantity}
        allocation_mobs = VGroup() # Group to hold allocation mobjects
        iteration = 0
        
        while sum(current_demand) > 0 and sum(current_supply) > 0:
            iteration += 1
            iteration_text = Tex(f"Iteration {iteration}", color=BLUE).scale(0.8).to_corner(UR, buff=0.2)
            self.play(Write(iteration_text))
            
            # Step 1: Calculate row penalties
            row_penalties, row_penalty_texts = AnimationHelpers.calculate_row_penalties(
                self, balanced_table, balanced_costs, row_penalty_lines, Header, satisfied_rows, satisfied_cols, iteration
            )
            # Step 2: Calculate column penalties
            col_penalties, col_penalty_texts = AnimationHelpers.calculate_column_penalties(
                self, balanced_table, balanced_costs, col_penalty_lines, Header, satisfied_rows, satisfied_cols, iteration
            )
            
            # Combine penalties
            all_penalties = row_penalties + col_penalties
            
            # --- THIS IS THE NEWLY ADDED PART ---
            # Step 3: Perform allocation based on penalties
            alloc_i, alloc_j, quantity, new_alloc_mob = AnimationHelpers.animate_allocation_step(
                self, balanced_table, all_penalties, row_penalty_texts, col_penalty_texts,
                current_supply, current_demand, satisfied_rows, satisfied_cols, balanced_costs
            )
            
            # Store the result
            allocations[(alloc_i, alloc_j)] = quantity
            allocation_mobs.add(new_alloc_mob)
            
            self.play(FadeOut(iteration_text))
            self.wait(0.5)
        
        # --- FINAL STEP ---
        # Step 4: Calculate the total cost from allocations
        AnimationHelpers.animate_total_cost_calculation(
            self, table, costs, allocations
        )
        self.wait(5)