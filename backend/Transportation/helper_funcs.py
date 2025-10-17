from manim import *
import copy
import pkg_resources

class AnimationHelpers:
    """
    Helper functions for Transportation Problem (VAM + MODI) visualization.
    """
    
    def create_transportation_table(self, costs, supply, demand):
        """
        Creates a transportation table with supply and demand as part of the table structure.
        """
        num_sources = len(costs)
        num_destinations = len(costs[0])
        
        # Build the complete data including supply column
        table_data = []
        for i in range(num_sources):
            row = costs[i] + [supply[i]]
            table_data.append(row)
        
        # Add demand row at the bottom
        table_data.append(demand + [sum(supply)])  # Total in bottom-right
        
        # Labels
        source_labels = [Tex(chr(65 + i)) for i in range(num_sources)]  # A, B, C...
        source_labels.append(Tex("Demand"))  # Last row label
        
        dest_labels = [Tex(chr(68 + i)) for i in range(num_destinations)]  # D, E, F...
        dest_labels.append(Tex("Supply"))  # Last column label
        
        # Create the complete table
        table = IntegerTable(
            table_data,
            row_labels=source_labels,
            col_labels=dest_labels,
            h_buff=1.2,
            v_buff=0.8
        ).scale(0.5).to_edge(LEFT, buff=0.1)
        
        # Animate creation
        self.play(FadeIn(table))
        self.play(table.animate.shift(DOWN*0.25))
        self.wait(1)
        
        return table

    def animate_balance_problem(self, table, costs, supply, demand):
        """
        Animates the process of balancing an unbalanced transportation problem
        by adding and highlighting a dummy row or column.
        """
        total_supply = sum(supply)
        total_demand = sum(demand)

        # Make copies to work with
        new_costs = copy.deepcopy(costs)
        new_supply = copy.deepcopy(supply)
        new_demand = copy.deepcopy(demand)

        if total_supply == total_demand:
            # --- Problem is already balanced ---
            balanced_text = Tex("Total Supply = Total Demand", "Problem is Balanced", color=GREEN).scale(0.7).to_edge(UP, buff=1)
            self.play(Write(balanced_text))
            self.wait(2)
            self.play(FadeOut(balanced_text))
            return table, new_costs, new_supply, new_demand

        # --- Problem is Unbalanced ---
        unbalanced_text = Tex("Total Supply ≠ Total Demand", "Problem is Unbalanced", color=YELLOW).scale(0.7).to_edge(UP, buff=1)
        self.play(Write(unbalanced_text))
        self.wait(2)

        if total_supply > total_demand:
            # --- Add Dummy Column ---
            balancing_text = Tex("Adding a Dummy Destination to absorb excess supply.", color=BLUE).scale(0.7).next_to(unbalanced_text, DOWN)
            self.play(Write(balancing_text))

            difference = total_supply - total_demand
            new_demand.append(difference)
            for row in new_costs:
                row.append(0)

            # Re-create the table with new dimensions
            new_table = self.create_transportation_table(new_costs, new_supply, new_demand)
            new_table.move_to(table.get_center()) # Position it where the old one was

            self.play(
                FadeOut(table),
                FadeOut(unbalanced_text),
                FadeOut(balancing_text),
                Create(new_table)
            )
            
            # Highlight the new dummy column
            dummy_col_index = len(new_demand) # The index of the supply column
            dummy_column = new_table.get_columns()[dummy_col_index]
            highlight = SurroundingRectangle(dummy_column, color=YELLOW, buff=0.1)
            highlight_text = Tex("Dummy Column", color=YELLOW).scale(0.6).next_to(highlight, UP, buff=0.1)
            self.play(Create(highlight), Write(highlight_text))
            self.wait(3)
            self.play(FadeOut(highlight), FadeOut(highlight_text))
            
            return new_table, new_costs, new_supply, new_demand

        else: # demand > supply
            # --- Add Dummy Row ---
            balancing_text = Tex("Adding a Dummy Source to meet extra demand.", color=BLUE).scale(0.7).next_to(unbalanced_text, DOWN)
            self.play(Write(balancing_text))

            difference = total_demand - total_supply
            new_supply.append(difference)
            new_costs.append([0] * len(new_demand))
            
            # Re-create the table with new dimensions
            new_table = self.create_transportation_table(new_costs, new_supply, new_demand)
            new_table.move_to(table.get_center())

            self.play(
                FadeOut(table),
                FadeOut(unbalanced_text),
                FadeOut(balancing_text),
                Create(new_table)
            )

            # Highlight the new dummy row
            dummy_row_index = len(new_supply) # The index of the demand row
            dummy_row = new_table.get_rows()[dummy_row_index]
            highlight = SurroundingRectangle(dummy_row, color=YELLOW, buff=0.1)
            highlight_text = Tex("Dummy Row", color=YELLOW).scale(0.6).next_to(highlight, LEFT, buff=0.1)
            self.play(Create(highlight), Write(highlight_text))
            self.wait(3)
            self.play(FadeOut(highlight), FadeOut(highlight_text))
            
            return new_table, new_costs, new_supply, new_demand

    def animate_extend_for_penalties(self, table):
        """
        Animates extending table lines for penalties.
        """
        # Get table dimensions
        num_rows = len(table.get_rows())
        num_cols = len(table.get_columns())
        
        # Create horizontal lines for row penalties
        row_lines = VGroup(*[
            Line(
                start=table.get_horizontal_lines()[i].get_right(),
                end=table.get_horizontal_lines()[i].get_right() + RIGHT * 1.5
            ).set_stroke(WHITE, 3)
            for i in range(num_rows - 1)  # Exclude demand row
        ])
        
        # Create vertical lines for column penalties
        col_lines = VGroup(*[
            Line(
                start=table.get_vertical_lines()[i].get_bottom(),
                end=table.get_vertical_lines()[i].get_bottom() + DOWN * 1.5
            ).set_stroke(WHITE, 3)
            for i in range(num_cols - 1)  # Exclude supply column
        ])
        
        # Animate the extensions
        self.play(
            Create(row_lines),
            Create(col_lines)
        )
        self.wait(1)
        outer_horizontal_line = table.get_horizontal_lines()[-1].copy().set_stroke(WHITE, 4).move_to(table.get_bottom())
        outer_vertical_line = table.get_vertical_lines()[-1].copy().set_stroke(WHITE, 4).move_to(table.get_right())
        self.play(
            Create(outer_horizontal_line),
            Create(outer_vertical_line)
        )
        
        return row_lines, col_lines
    
    def calculate_row_penalties(self, table, costs, row_penalty_positions, step_header, satisfied_rows, satisfied_cols, iteration):
        """
        For each row, finds the two smallest costs and calculates the difference.
        """
        explanation = Tex(
            "Row Penalty = Difference between\\\\two smallest costs in the row",
            color=YELLOW
        ).scale(0.6).next_to(step_header, DOWN, buff=0.25).shift(LEFT*4)
        if iteration == 1:
            self.play(Write(explanation))
            self.wait(1)
        
        penalty_values = []  # Store penalty values and their indices
        penalty_texts = []  # Store penalty text objects as a list for indexing
        
        for i, row_costs in enumerate(costs):
            if i in satisfied_rows:
                # Skip satisfied rows
                penalty_text = Tex("-", color=GRAY).scale(0.75)
                penalty_text.next_to(row_penalty_positions[i], DOWN, buff=0.2)
                self.play(Write(penalty_text), run_time=0.2)
                penalty_values.append((-1, i, 'row'))  # -1 indicates satisfied
                penalty_texts.append(penalty_text)
                continue
            
            # Get valid costs (not in satisfied columns)
            valid_costs = [row_costs[j] for j in range(len(row_costs)) if j not in satisfied_cols]
            
            if len(valid_costs) < 2:
                # Only one valid cost - use it as penalty
                penalty = valid_costs[0]
                penalty_text = Integer(penalty, color=YELLOW).scale(0.75)
                penalty_text.next_to(row_penalty_positions[i], DOWN, buff=0.2)
                self.play(Write(penalty_text), run_time=0.2)
                penalty_values.append((penalty, i, 'row'))
                penalty_texts.append(penalty_text)
                continue
            
            # Highlight the current row (exclude supply column)
            row_cells = VGroup(*table.get_rows()[i + 1][1:-1])  # Exclude label and supply
            row_highlight = SurroundingRectangle(row_cells, color=BLUE, buff=0.1)
            self.play(Create(row_highlight), run_time=0.4)
            
            # Find two smallest values
            sorted_costs = sorted(valid_costs)
            min1, min2 = sorted_costs[0], sorted_costs[1]
            penalty = min2 - min1
            
            # Highlight the two smallest cells
            for j, cost in enumerate(row_costs):
                if j not in satisfied_cols and (cost == min1 or cost == min2):
                    cell = table.get_cell((i + 2, j + 2))
                    self.play(Flash(cell, color=GREEN, flash_radius=0.7), run_time=0.3)
            
            # Show the calculation next to row
            if iteration < 2:
                calc_text = Tex(f"{min2} - {min1} = {penalty}", color=YELLOW).scale(0.5)
                calc_text.next_to(row_penalty_positions[i], DOWN, buff=0.2).shift(LEFT*0.1)
                self.play(Write(calc_text), run_time=0.4)
                self.wait(1)
            
                # Place penalty value at the extended line position
                penalty_text = Integer(penalty, color=YELLOW).scale(0.75)
                penalty_text.move_to(calc_text.get_center())
            
                self.play(
                    ReplacementTransform(calc_text, penalty_text),
                    FadeOut(row_highlight),
                    run_time=0.4
                )
            else:
                penalty_text = Integer(penalty, color=YELLOW).scale(0.75)
                penalty_text.next_to(row_penalty_positions[i], DOWN, buff=0.2)
                self.play(
                    Write(penalty_text),
                    FadeOut(row_highlight),
                    run_time=0.4
                )
            penalty_values.append((penalty, i, 'row'))
            penalty_texts.append(penalty_text)
            self.wait(0.2)
        if iteration == 1:
            self.play(FadeOut(explanation))

        # Convert to VGroup for positioning
        penalty_texts_group = VGroup(*penalty_texts)
        if iteration == 1:
            cover_line = table.get_vertical_lines()[-2].copy().set_stroke(WHITE, 3).next_to(penalty_texts_group, RIGHT, buff=0.2)
            self.play(Create(cover_line))
            self.wait(0.5)
        return penalty_values, penalty_texts
    
    def calculate_column_penalties(self, table, costs, col_penalty_positions, step_header, satisfied_rows, satisfied_cols, iteration):
        """
        For each column, finds the two smallest costs and calculates the difference.
        """
        if iteration == 1:
            explanation = Tex(
                "Column Penalty = Difference between\\\\two smallest costs in the column",
                color=YELLOW
            ).scale(0.6).next_to(step_header, DOWN, buff=0.25).shift(LEFT*4)
            
            self.play(Write(explanation))
            self.wait(1)
        
        num_destinations = len(costs[0])
        penalty_values = []  # Store penalty values and their indices
        penalty_texts = []  # Store penalty text objects as a list for indexing
        
        for j in range(num_destinations):
            if j in satisfied_cols:
                # Skip satisfied columns
                penalty_text = Tex("-", color=GRAY).scale(0.75)
                penalty_text.next_to(col_penalty_positions[j], RIGHT, buff=0.25).shift(UP*0.2)
                self.play(Write(penalty_text), run_time=0.2)
                penalty_values.append((-1, j, 'col'))  # -1 indicates satisfied
                penalty_texts.append(penalty_text)
                continue
            
            # Get column costs (excluding satisfied rows)
            col_costs = [costs[i][j] for i in range(len(costs)) if i not in satisfied_rows]
            
            if len(col_costs) < 2:
                # Only one valid cost - use it as penalty
                penalty = col_costs[0]
                penalty_text = Integer(penalty, color=YELLOW).scale(0.75)
                penalty_text.next_to(col_penalty_positions[j], RIGHT, buff=0.25).shift(UP*0.2)
                self.play(Write(penalty_text), run_time=0.2)
                penalty_values.append((penalty, j, 'col'))
                penalty_texts.append(penalty_text)
                continue
            
            # Highlight the current column (exclude demand row)
            col_cells = VGroup(*[table.get_rows()[i + 1][j + 1] for i in range(len(costs)) if i not in satisfied_rows])
            col_highlight = SurroundingRectangle(col_cells, color=BLUE, buff=0.1)
            self.play(Create(col_highlight), run_time=0.4)
            
            # Find two smallest values
            sorted_costs = sorted(col_costs)
            min1, min2 = sorted_costs[0], sorted_costs[1]
            penalty = min2 - min1
            
            # Highlight the two smallest cells
            for i in range(len(costs)):
                if i not in satisfied_rows and costs[i][j] in [min1, min2]:
                    cell = table.get_cell((i + 2, j + 2))
                    self.play(Flash(cell, color=GREEN, flash_radius=0.7), run_time=0.3)
            
            # Show the calculation below column (only for first and second iteration)
            if iteration < 2:
                calc_text = Tex(f"{min2} - {min1} = {penalty}", color=YELLOW).scale(0.5)
                calc_text.next_to(col_penalty_positions[j], RIGHT, buff=0.2).shift(LEFT*0.1 + UP*0.2)
                self.play(Write(calc_text), run_time=0.4)
                self.wait(1)
                
                # Place penalty value at the extended line position
                penalty_text = Integer(penalty, color=YELLOW).scale(0.75)
                penalty_text.move_to(calc_text.get_center()).shift(LEFT*0.25)
            
                self.play(
                    ReplacementTransform(calc_text, penalty_text),
                    FadeOut(col_highlight),
                    run_time=0.4
                )
            else:
                penalty_text = Integer(penalty, color=YELLOW).scale(0.75)
                penalty_text.next_to(col_penalty_positions[j], RIGHT, buff=0.2)
                self.play(
                    Write(penalty_text),
                    FadeOut(col_highlight),
                    run_time=0.4
                )

            penalty_values.append((penalty, j, 'col'))
            penalty_texts.append(penalty_text)
            self.wait(0.2)
        if iteration == 1:
            self.play(FadeOut(explanation))
        
        # Convert to VGroup for positioning
        penalty_texts_group = VGroup(*penalty_texts)
        if iteration == 1:
            cover_line = table.get_horizontal_lines()[-2].copy().set_stroke(WHITE, 3).next_to(penalty_texts_group, DOWN, buff=0.2)
            self.play(Create(cover_line))
            self.wait(0.5)
        return penalty_values, penalty_texts
    
    def animate_allocation_step(self, table, all_penalties, row_penalty_texts, col_penalty_texts, supply_left, demand_left, satisfied_rows, satisfied_cols, costs):
        """
        Finds the max penalty, handles ties by checking max allocation and min cost,
        allocates to the best cell, and updates supply/demand.
        """
        # 1. Find the highest penalty value
        max_penalty_val = -1
        if all_penalties:
            max_penalty_val = max(p[0] for p in all_penalties)

        explanation = Tex(f"The highest penalty is {max_penalty_val}", color=ORANGE).scale(0.7).to_edge(UP, buff=1.0)
        self.play(Write(explanation))

        # 2. Highlight all penalties that match the max value
        highlights = VGroup()
        tied_penalties = [p for p in all_penalties if p[0] == max_penalty_val]
        for penalty_val, index, p_type in tied_penalties:
            if p_type == 'row':
                target_text = row_penalty_texts[index]
            else: # 'col'
                target_text = col_penalty_texts[index]
            highlight_box = SurroundingRectangle(target_text, color=ORANGE, buff=0.15)
            highlights.add(highlight_box)
        self.play(Create(highlights))
        self.wait(1)

        # --- START: TIE-BREAKING LOGIC ---
        
        # 3. If there's a tie, evaluate candidates. Otherwise, just pick the only one.
        if len(tied_penalties) > 1:
            tie_text = Tex("Tie in max penalty!", " Evaluating options...", color=YELLOW).scale(0.7).next_to(explanation, DOWN)
            self.play(Write(tie_text))
            self.wait(1)

            candidates = []
            temp_highlights = VGroup()

            # Create an anchor for the evaluation text list
            eval_title = Tex("Tie-Break Candidates:", color=PURPLE).scale(0.6).to_edge(RIGHT, buff=1).shift(UP)
            self.play(Write(eval_title))
            temp_highlights.add(eval_title)
            last_eval_text = eval_title

            # Gather data for each tied option
            for p_val, p_idx, p_type in tied_penalties:
                temp_min_cost = float('inf')
                temp_i, temp_j = -1, -1

                if p_type == 'row':
                    for col_idx, cost in enumerate(costs[p_idx]):
                        if col_idx not in satisfied_cols and cost < temp_min_cost:
                            temp_min_cost = cost
                            temp_i, temp_j = p_idx, col_idx
                else: # 'col'
                    for row_idx, row in enumerate(costs):
                        if row_idx not in satisfied_rows and row[p_idx] < temp_min_cost:
                            temp_min_cost = row[p_idx]
                            temp_i, temp_j = row_idx, p_idx

                possible_alloc = min(supply_left[temp_i], demand_left[temp_j])
                
                # Animate the evaluation: Highlight cell and write text in the list
                cell = table.get_cell((temp_i + 2, temp_j + 2))
                cell_eval_highlight = SurroundingRectangle(cell, color=PURPLE)
                
                # Add cell coordinates for clarity and position text in the list
                eval_text = Tex(f"Cell ({chr(65+temp_i)}, {chr(68+temp_j)}): Alloc: {possible_alloc}, Cost: {temp_min_cost}", color=PURPLE).scale(0.5)
                eval_text.next_to(last_eval_text, DOWN, buff=0.2).align_to(eval_title, LEFT)
                
                temp_highlights.add(cell_eval_highlight, eval_text)
                self.play(Create(cell_eval_highlight), Write(eval_text))
                
                # Update the last text object for positioning the next one
                last_eval_text = eval_text

                candidates.append({
                    'penalty_info': (p_val, p_idx, p_type),
                    'min_cost': temp_min_cost,
                    'possible_alloc': possible_alloc,
                    'cell_indices': (temp_i, temp_j)
                })
            self.wait(2)
            self.play(FadeOut(temp_highlights))

            # Sort candidates: 1. by largest allocation (desc), 2. by smallest cost (asc)
            sorted_candidates = sorted(candidates, key=lambda c: (-c['possible_alloc'], c['min_cost']))
            winner = sorted_candidates[0]
            
            # Announce the reason for the choice
            reason_text = None
            if sorted_candidates[0]['possible_alloc'] > sorted_candidates[1]['possible_alloc']:
                reason_text = Tex("Choosing the one with the largest possible allocation.", color=BLUE).scale(0.7)
            else:
                reason_text = Tex("Allocation also tied. Choosing the one with the minimum cost.", color=BLUE).scale(0.7)
            reason_text.next_to(tie_text, DOWN)
            self.play(Write(reason_text))
            self.wait(2)
            self.play(FadeOut(tie_text), FadeOut(reason_text))

            best_penalty = winner['penalty_info']
            min_cost = winner['min_cost']
            alloc_i, alloc_j = winner['cell_indices']

        else:
            # No tie, proceed as before
            best_penalty = tied_penalties[0]
            min_cost = float('inf')
            _, index, p_type = best_penalty
            if p_type == 'row':
                for col_idx, cost in enumerate(costs[index]):
                    if col_idx not in satisfied_cols and cost < min_cost:
                        min_cost = cost
                        alloc_i, alloc_j = index, col_idx
            else: # 'col'
                for row_idx, row in enumerate(costs):
                    if row_idx not in satisfied_rows and row[index] < min_cost:
                        min_cost = row[index]
                        alloc_i, alloc_j = row_idx, index
        
        # --- END: TIE-BREAKING LOGIC ---

        # 4. Announce selected row/column and find the minimum cost cell
        _, index, p_type = best_penalty
        if p_type == 'row':
            row_cells = VGroup(*table.get_rows()[index + 1][1:-1])
            self.play(Indicate(row_cells, color=BLUE))
            explanation_2 = Tex(f"Select row {index+1}. Find the minimum cost cell.", color=BLUE).scale(0.7).next_to(explanation, DOWN)
        else: # 'col'
            col_cells = VGroup(*table.get_columns()[index + 1][1:-1])
            self.play(Indicate(col_cells, color=BLUE))
            explanation_2 = Tex(f"Select column {index+1}. Find the minimum cost cell.", color=BLUE).scale(0.7).next_to(explanation, DOWN)
        
        self.play(Write(explanation_2))
        cell_to_allocate = table.get_cell((alloc_i + 2, alloc_j + 2))
        cell_highlight = SurroundingRectangle(cell_to_allocate, color=GREEN)
        self.play(Create(cell_highlight))
        self.wait(1)
        
        # ... The rest of the function (allocation, updating supply/demand, etc.) remains unchanged ...
        # 5. Determine allocation and animate it
        quantity = min(supply_left[alloc_i], demand_left[alloc_j])
        alloc_text = Integer(quantity, color=GREEN).scale(0.5)
        alloc_text.move_to(cell_to_allocate.get_center() + UL*0.1)
        
        explanation_3 = Tex(f"Allocate: min(Supply[{supply_left[alloc_i]}], Demand[{demand_left[alloc_j]}]) = {quantity}", color=GREEN).scale(0.7).next_to(explanation_2, DOWN)
        self.play(Write(explanation_3))
        self.play(Write(alloc_text))
        self.wait(1)

        # 6. Update supply and demand values
        new_supply = supply_left[alloc_i] - quantity
        new_demand = demand_left[alloc_j] - quantity

        supply_mob = table.get_entries((alloc_i + 2, len(demand_left) + 2))
        demand_mob = table.get_entries((len(supply_left) + 2, alloc_j + 2))

        new_supply_mob = Integer(new_supply).move_to(supply_mob)
        new_demand_mob = Integer(new_demand).move_to(demand_mob)

        self.play(Transform(supply_mob, new_supply_mob), Transform(demand_mob, new_demand_mob))
        supply_left[alloc_i] = new_supply
        demand_left[alloc_j] = new_demand
        self.wait(1)

        # 7. Mark satisfied row/column
        if supply_left[alloc_i] == 0:
            satisfied_rows.add(alloc_i)
            row_to_fade = VGroup(*table.get_rows()[alloc_i+1][1:])
            row_line = table.get_horizontal_lines()[alloc_i + 1].copy().set_stroke(RED, 3).move_to(row_to_fade.get_center())
            self.play(Create(row_line))
        if demand_left[alloc_j] == 0:
            satisfied_cols.add(alloc_j)
            col_to_fade = VGroup(*table.get_columns()[alloc_j+1][1:])
            col_line = table.get_vertical_lines()[alloc_j + 1].copy().set_stroke(RED, 3).move_to(col_to_fade.get_center())
            self.play(Create(col_line))
        
        self.wait(1)

        # 8. Cleanup
        self.play(
            FadeOut(highlights),
            FadeOut(cell_highlight),
            FadeOut(explanation),
            FadeOut(explanation_2),
            FadeOut(explanation_3),
            FadeOut(VGroup(*row_penalty_texts)),
            FadeOut(VGroup(*col_penalty_texts))
        )
        return alloc_i, alloc_j, quantity, alloc_text
    
    def animate_removing_extend_for_penalties(self, row_lines, col_lines):
        """
        Animates removing the extended penalty lines.
        """
        self.play(FadeOut(VGroup(row_lines, col_lines)))
        self.wait(0.5)

    # --- NEW FUNCTION TO ADD AT THE END OF THE CLASS ---
    def animate_total_cost_calculation(self, table, costs, allocations):
        """
        Animates the final cost calculation based on the allocations made.
        """
        final_header = Tex("Final Step: Calculate Total Cost", color=GREEN).scale(0.8).to_edge(UP, buff=1)
        self.play(Write(final_header))
        self.wait(1)
        
        total_cost = 0
        calc_lines = VGroup() # To hold text lines of the calculation
        
        # Position for the calculation text
        calc_position = table.get_right() + RIGHT*1 + UP*2

        title = Tex("Initial Feasible Solution:", font_size=28).move_to(calc_position).align_to(calc_position, LEFT)
        calc_lines.add(title)
        self.play(Write(title))

        st = 0
        for (i, j), quantity in allocations.items():
            st += 1
            cost = costs[i][j]
            total_cost += quantity * cost
            
            # Highlight the cell
            cell = table.get_cell((i + 2, j + 2)) # +2 for labels
            highlight = SurroundingRectangle(cell, color=YELLOW, buff=-0.1)
            self.play(Create(highlight))
            
            # Create and display the calculation line
            line_text = Tex("+", f" ({quantity}", r" units \\times ", f"{cost})", font_size=24)
            if st == 1: # First item
                 line_text = Tex(f" ({quantity}", r" units \\times ", f"{cost})", font_size=24)

            line_text.to_edge(RIGHT, buff=0.75)
            
            self.play(Write(line_text))
            calc_lines.add(line_text)
            self.play(FadeOut(highlight))
            self.wait(0.5)

        # Display the final total
        separator = Line(LEFT, RIGHT).set_width(3).next_to(calc_lines, DOWN, buff=0.2)
        final_cost_text = Tex(f"= {total_cost}", font_size=28, color=YELLOW)
        final_cost_text.next_to(separator, DOWN, buff=0.2).align_to(calc_lines, LEFT)

        self.play(Create(separator))
        self.play(Write(final_cost_text))