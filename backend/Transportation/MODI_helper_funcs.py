from manim import *
import copy
from MODI_solver import find_loop, adjust_allocations # We will need these later

# --- Manim Scene Configuration ---
config.background_color = WHITE
Tex.set_default(color=BLACK)
MathTex.set_default(color=BLACK)
Line.set_default(color=BLACK)
Table.set_default(color=BLACK)
# ---

class AnimationHelpers:
    """
    A class to hold all the animation helper functions for the MODI method.
    """
    
    def create_table_with_allocations(self, scene, costs, supply, demand, initial_alloc, main_header):
        """
        Step 1: Creates the main table, highlights, u/v lines,
        and persistent allocation number mobjects.
        
        Args:
            scene (Scene): The manim scene object (e.g., 'self').
            costs (list): The 2D cost matrix.
            supply (list): The supply values.
            demand (list): The demand values.
            initial_alloc (list): The 2D allocation matrix from VAM.
            main_header (Mobject): The main scene title, for positioning.

        Returns:
            - table (Table): The Manim Table mobject.
            - alloc_mobject_map (dict): A map of (r,c) -> MathTex mobject.
                                        This is the "state" we will pass to
                                        other functions to update the numbers.
            - table_alloc(VGroup): A Vgroup of the table and allocation
        """
        
        # --- 1. Create the Table Structure ---
        num_sources = len(costs)
        num_destinations = len(costs[0])
        
        # Build the data list for the Manim table
        table_data = []
        for i in range(num_sources):
            row = costs[i] + [supply[i]]
            table_data.append(row)
        # Add the demand row at the bottom
        table_data.append(demand + [sum(supply)])
        
        # Create row and column labels
        source_labels = [Tex(chr(65 + i)) for i in range(num_sources)] # A, B, C...
        source_labels.append(Tex("Demand"))
        dest_labels = [Tex(str(i+1)) for i in range(num_destinations)] # 1, 2, 3...
        dest_labels.append(Tex("Supply"))
        
        # Create the table mobject
        table = IntegerTable(
            table_data,
            row_labels=source_labels,
            col_labels=dest_labels,
            h_buff=1.2,
            v_buff=0.8,
            line_config={"stroke_width": 2}
        ).scale(0.5).to_edge(LEFT, buff=0.1)
        
        # Set all table text to black
        for item in table.get_entries():
            item.set_color(BLACK)
        
        # --- 2. Add Highlights for Allocated Cells ---
        # We just call the table's internal method.
        # Manim will track these highlights for us.
        for r in range(len(initial_alloc)):
            for c in range(len(initial_alloc[0])):
                if initial_alloc[r][c] > 0:
                    table.add_highlighted_cell((r+2, c+2), GREEN, fill_opacity=0.45)
        
        # Animate the table (and its highlights) fading in
        scene.play(FadeIn(table))
        
        # --- 3. Create Persistent Allocation Mobjects ---
        # These are the purple numbers in the corners.
        # We store them in a dictionary so we can find and
        # update them easily in later functions.
        
        # (r, c) -> Mobject
        alloc_mobject_map = {} 
        # A VGroup just to animate them all at once
        alloc_mobjects_vgroup = VGroup() 
        
        for r in range(len(initial_alloc)):
            for c in range(len(initial_alloc[0])):
                val = initial_alloc[r][c]
                if val > 0: # If there is an allocation
                    # Get the cell to position relative to
                    cell = table.get_cell((r+2, c+2))
                    # Calculate position: top-left corner
                    pos = cell.get_corner(UP + LEFT) + DOWN *0.12 + RIGHT * 0.14
                    
                    if val == 0.001:
                        tex_mob = MathTex(r"\epsilon", color=BLACK).scale(0.5)
                    else:
                        tex_mob = MathTex(str(int(val)), color=PURPLE_E).scale(0.5)
                    
                    # Set the mobject's position directly
                    tex_mob.move_to(pos).set_z_index(15)
                    
                    # Store the mobject in our map and vgroup
                    alloc_mobject_map[(r, c)] = tex_mob
                    alloc_mobjects_vgroup.add(tex_mob)
        
        # Animate all allocation numbers writing at once
        scene.play(Write(alloc_mobjects_vgroup))
        table_alloc = VGroup(table, alloc_mobjects_vgroup)
        scene.wait(1)
        
        # Return the essential "state" objects for the next steps
        return table, alloc_mobject_map, table_alloc
    
    def animate_degeneracy_check(self, scene, table, alloc_mobject_map, costs, main_header):
        """
        Step 2: Animates the degeneracy check (m + n - 1) by counting
        the allocation mobjects.

        Args:
            scene (Scene): The manim scene object ('self').
            table (Table): The Manim Table mobject.
            alloc_mobject_map (dict): The map of (r,c) -> Mobject.
            costs (list): The 2D cost matrix (to get m and n).
            main_header (Mobject): The main scene title, for positioning.

        Returns:
            - bool: True if the solution is degenerate, False otherwise.
        """
        
        # --- 1. Title and Setup ---
        step1_title = Tex("Step 1: Check for Degeneracy").scale(0.65)
        step1_title.next_to(main_header, DOWN, buff=0.1).set_color(LOGO_BLUE)
        scene.play(Write(step1_title))

        # --- 2. Get Allocation Counts ---
        num_sources = len(costs)
        num_destinations = len(costs[0])
        
        # Get count directly from the map of mobjects we passed in
        num_allocations = len(alloc_mobject_map) 
        required_allocations = num_sources + num_destinations - 1

        # --- 3. Animate Counting ---
        
        # Position the counter text directly on the right edge
        counter_text = MathTex("Allocations = 0").scale(0.7)
        counter_text.to_edge(RIGHT, buff=0.45) # Position it
        scene.play(Write(counter_text))
        scene.wait(0.5)

        # Iterate through the (r, c) coordinates from the map's keys
        for i, (r, c) in enumerate(alloc_mobject_map.keys()):
            
            # --- MODIFIED ---
            # Get the cell corresponding to the (r, c) coordinate
            cell_to_indicate = table.get_cell((r+2, c+2)) # +2 for headers
            
            # Animate indication of the TABLE CELL
            scene.play(ShowPassingFlashWithThinningStrokeWidth(cell_to_indicate, color=YELLOW, scale_factor=1.1, time_width=1.5), run_time=1)
            
            # Update counter text
            new_counter_text = MathTex(f"Allocations = {i+1}").scale(0.7)
            new_counter_text.to_edge(RIGHT, buff=0.45) # Position it in the same place
            scene.play(ReplacementTransform(counter_text, new_counter_text), run_time=0.2)
            counter_text = new_counter_text # Update reference
        
        scene.wait(1)

        # --- 4. Animate Formula Check ---
        formula = MathTex(r"m + n - 1").scale(0.7)
        formula.next_to(counter_text, DOWN, buff=0.2)
        scene.play(Write(formula))
        scene.wait(1)

        formula_sub = MathTex(f"{num_sources} + {num_destinations} - 1 = {required_allocations}").scale(0.7)
        formula_sub.move_to(formula)
        scene.play(ReplacementTransform(formula, formula_sub))
        scene.wait(1)

        # --- 5. Show Result ---
        is_degenerate = False # Assume non-degenerate
        if num_allocations == required_allocations:
            result_grp = VGroup(
                MathTex(f"{num_allocations} = {required_allocations}", color=GREEN),
                Tex("Solution is Non-Degenerate", color=GREEN)).scale(0.7).arrange(DOWN)
        else:
            is_degenerate = True # Mark as degenerate
            result_grp = VGroup(
                MathTex(f"{num_allocations} \\neq {required_allocations}", color=RED),
                Tex("Solution is Degenerate", color=RED)).scale(0.7).arrange(DOWN)

        result_grp.next_to(formula_sub, DOWN, buff=0.2).shift(LEFT*2)
        scene.play(Write(result_grp))
        scene.wait(2)

        # --- 6. Cleanup and Return ---
        # Group all temporary text
        text_to_fade = VGroup(step1_title, counter_text, formula_sub, result_grp)
        scene.play(FadeOut(text_to_fade))
        
        # Return the *result* of the check for the next step
        return is_degenerate

    
    def handle_degeneracy(self, scene, table, costs, initial_alloc, alloc_mobject_map, main_header):
        """
        Step 2a: Handles degeneracy by adding an epsilon allocation to the
        lowest-cost unallocated cell.

        Args:
            scene (Scene): The manim scene object ('self').
            table (Table): The Manim Table mobject.
            costs (list): The 2D cost matrix.
            initial_alloc (list): The 2D allocation logic matrix.
            alloc_mobject_map (dict): The map of (r,c) -> Mobject.
            main_header (Mobject): The main scene title, for positioning.

        Returns:
            - new_alloc_logic (list): The updated 2D allocation matrix with 0.001 added.
            - new_alloc_map (dict): The updated map including the new epsilon mobject.
            - epsilon_mobject (Tex):
        """
        
        # --- 1. Create Titles and Explanation ---
        step1a_title = Tex("Step 1a: Resolving Degeneracy").scale(0.65)
        step1a_title.next_to(main_header, DOWN, buff=0.1).set_color(RED)
        
        problem_text = Tex("Solution is Degenerate.", color=RED).scale(0.6)
        problem_text.to_edge(RIGHT, buff=0.45).shift(UP*1.5)
        
        fix_text = Tex(r"We must add a small allocation $\epsilon$ to the \\", " unallocated cell", " with the minimum cost.").scale(0.6).shift(LEFT*1.4)
        fix_text.next_to(problem_text, DOWN, buff=0.2)
        fix_text[1].set_color(BLUE) # Highlight "unallocated"
        fix_text[2].set_color(GREEN_E) # Highlight "minimum cost"
        
        scene.play(Write(step1a_title))
        scene.play(Write(problem_text))
        scene.play(Write(fix_text))
        scene.wait(2.5)

        # --- 2. Find the min-cost unallocated cell ---
        min_cost = float('inf')
        min_cost_cell = (-1, -1) # (r, c)
        
        num_sources = len(costs)
        num_destinations = len(costs[0])

        for r in range(num_sources):
            for c in range(num_destinations):
                # Check if cell is UNALLOCATED (i.e., not in our map)
                if (r, c) not in alloc_mobject_map:
                    # Check if this cost is the new minimum
                    if costs[r][c] < min_cost:
                        min_cost = costs[r][c]
                        min_cost_cell = (r, c)
        
        r, c = min_cost_cell
        cell_to_animate = table.get_cell((r+2, c+2)) # +2 for headers

        # --- 3. Animate Finding and Allocating ---
        scene.play(Flash(cell_to_animate, color=RED, scale_factor=1.2))
        scene.wait(1)
        
        # Add a new ORANGE highlight for this cell
        table.add_highlighted_cell((r+2, c+2), ORANGE, fill_opacity=0.45)

        # --- 4. Create the new epsilon mobject ---
        # Get position from user's specified function
        cell = table.get_cell((r+2, c+2))
        pos = cell.get_corner(UP + LEFT) + DOWN * 0.12 + RIGHT * 0.14
        
        epsilon_mobject = MathTex(r"\epsilon", color=BLACK).scale(0.5)
        epsilon_mobject.move_to(pos).set_z_index(15)
        
        scene.play(Write(epsilon_mobject))
        scene.wait(1.5)

        # --- 5. Update State for Next Steps ---
        # Create a new logic matrix with the 0.001 value
        new_alloc_logic = copy.deepcopy(initial_alloc)
        new_alloc_logic[r][c] = 0.001 # Symbolic epsilon for logic
        
        # Create a new map that includes the new mobject
        new_alloc_map = alloc_mobject_map.copy()
        new_alloc_map[(r, c)] = epsilon_mobject
        
        # --- 6. Cleanup and Return ---
        text_to_fade = VGroup(step1a_title, problem_text, fix_text)
        scene.play(FadeOut(text_to_fade))
        
        # Return the updated state
        return new_alloc_logic, new_alloc_map, epsilon_mobject

    def extend_table(self, scene, table, table_alloc, costs):

        # --- Add u/v Extension Lines ---
        # This title is temporary and will be faded out
        # Shift table down slightly to make room
        scene.play(table_alloc.animate.shift(DOWN*0.25))
        
        num_data_rows = len(costs)
        num_data_cols = len(costs[0])
        
        # Create the horizontal lines for u_i
        row_lines = VGroup(*[
            Line(
                start=table.get_horizontal_lines()[i].get_right(),
                end=table.get_horizontal_lines()[i].get_right() + RIGHT * 1
            ).set_stroke(BLACK, 2)
            for i in range(num_data_rows+1) 
        ])
        
        # Create the vertical lines for v_j
        col_lines = VGroup(*[
            Line(
                start=table.get_vertical_lines()[i].get_bottom(),
                end=table.get_vertical_lines()[i].get_bottom() + DOWN * 1
            ).set_stroke(BLACK, 2)
            for i in range(num_data_cols+1)
        ])
        
        outer_h_line = table.get_horizontal_lines()[-1].copy().shift(DOWN * 0.6)
        outer_v_line = table.get_vertical_lines()[-1].copy().shift(RIGHT * 1.29)
        scene.play(Create(row_lines), Create(col_lines), Create(outer_h_line), Create(outer_v_line))
        scene.wait(1)

        return row_lines, col_lines
    
    def animate_uv_calculation(self, scene, table, costs, initial_alloc, alloc_mobject_map, 
                               row_lines, col_lines, main_header):
        """
        Step 3: Animates the calculation of u_i and v_j values.

        Args:
            scene (Scene): The manim scene object ('self').
            table (Table): The Manim Table mobject.
            costs (list): The 2D cost matrix.
            initial_alloc (list): The 2D allocation logic matrix (with epsilon).
            alloc_mobject_map (dict): The map of (r,c) -> Mobject (for finding allocs).
            row_lines (VGroup): Mobjects for u_i placement.
            col_lines (VGroup): Mobjects for v_j placement.
            main_header (Mobject): The main scene title, for positioning.

        Returns:
            - u_vals (list): The calculated u_i values.
            - v_vals (list): The calculated v_j values.
        """
        
        # --- 1. Title and Setup ---
        step2_title = Tex("Step 2: Calculate $u_i$ and $v_j$").scale(0.65)
        step2_title.next_to(main_header, DOWN, buff=0.1).set_color(LOGO_BLUE)
        scene.play(Write(step2_title))
        
        num_sources = len(costs)
        num_destinations = len(costs[0])

        # --- 2. Explain the Formula ---
        formula_text = Tex(r"Use $C_{ij} = u_i + v_j$ for all allocated cells.", color=PURPLE).scale(0.6)
        formula_text.to_edge(RIGHT, buff=0.45).shift(UP*1.5)
        
        start_rule = Tex(r"Start by setting $u_A = 0$").scale(0.6)
        start_rule.next_to(formula_text, DOWN, buff=0.2)
        
        scene.play(Write(formula_text))
        scene.play(Write(start_rule))

        # --- 3. Initialize Calculation Variables ---
        u_vals = [None] * num_sources
        v_vals = [None] * num_destinations
        
        # This VGroup will hold the u/v mobjects we create
        uv_mobjects = VGroup() 
        
        # Get the list of (r, c) tuples of allocated cells
        allocated_cells = list(alloc_mobject_map.keys())

        # --- 4. Start Calculation: Set u_A = 0 ---
        u_vals[0] = 0
        u_text = MathTex("u_A = 0").scale(0.6)
        # Position it next to the first row line
        u_text.move_to(row_lines[0].get_center() + LEFT * 0.08 + DOWN * 0.25)
        
        scene.play(Write(u_text))
        uv_mobjects.add(u_text)
        scene.wait(1)
        
        # This mobject will show the live calculation on the right
        live_calc_text = VGroup().to_edge(RIGHT, buff=0.45) # Placeholder

        # --- 5. Iterative Calculation Loop ---
        loops_done = 0
        while any(v is None for v in u_vals) or any(v is None for v in v_vals):
            made_progress = False
            
            for (r, c) in allocated_cells:
                row_label = chr(65 + r) # 'A', 'B', etc.
                col_label = str(c + 1)  # '1', '2', etc.
                
                # Case 1: u_i is known, v_j is unknown
                if u_vals[r] is not None and v_vals[c] is None:
                    v_vals[c] = costs[r][c] - u_vals[r]
                    made_progress = True
                    
                    # Animate this finding
                    cell_to_flash = table.get_cell((r+2, c+2))
                    scene.play(Flash(cell_to_flash, color=YELLOW, time_width=0.5))
                    
                    # Show formula
                    f1 = MathTex(f"C_{{{row_label}{col_label}}} = u_{row_label} + v_{col_label}").scale(0.7)
                    f1.to_edge(RIGHT, buff=0.45)
                    scene.play(ReplacementTransform(live_calc_text, f1))
                    
                    # Substitute known values
                    f2 = MathTex(f"{costs[r][c]} = {u_vals[r]} + v_{col_label}").scale(0.7)
                    f2.move_to(f1)
                    scene.play(ReplacementTransform(f1, f2))
                    
                    # Show result
                    f3 = MathTex(f"v_{col_label} = {costs[r][c]} - {u_vals[r]} = {v_vals[c]}").scale(0.7)
                    f3.move_to(f1)
                    scene.play(ReplacementTransform(f2, f3))
                    
                    # Create the final text mobject
                    v_text = VGroup(MathTex(f"v_{col_label}"), MathTex("="), MathTex(f"{v_vals[c]}")).arrange(DOWN).scale(0.6)
                    v_text[1].rotate(PI/2)
                    v_text.move_to(col_lines[c].get_center() + RIGHT * 0.27 + UP * 0.08)
                    
                    # Move result to its place
                    scene.play(ReplacementTransform(f3, v_text))
                    live_calc_text = VGroup() # Reset placeholder
                    uv_mobjects.add(v_text)
                    
                # Case 2: v_j is known, u_i is unknown
                elif v_vals[c] is not None and u_vals[r] is None:
                    u_vals[r] = costs[r][c] - v_vals[c]
                    made_progress = True
                    
                    # Animate this finding
                    cell_to_flash = table.get_cell((r+2, c+2))
                    scene.play(Flash(cell_to_flash, color=YELLOW, time_width=0.5))
                    
                    # Show formula
                    f1 = MathTex(f"C_{{{row_label}{col_label}}} = u_{row_label} + v_{col_label}").scale(0.7)
                    f1.to_edge(RIGHT, buff=0.45)
                    scene.play(ReplacementTransform(live_calc_text, f1))
                    
                    # Substitute known values
                    f2 = MathTex(f"{costs[r][c]} = u_{row_label} + {v_vals[c]}").scale(0.7)
                    f2.move_to(f1)
                    scene.play(ReplacementTransform(f1, f2))
                    
                    # Show result
                    f3 = MathTex(f"u_{row_label} = {costs[r][c]} - {v_vals[c]} = {u_vals[r]}").scale(0.7)
                    f3.move_to(f1)
                    scene.play(ReplacementTransform(f2, f3))
                    
                    # Create the final text mobject
                    u_text = MathTex(f"u_{row_label} = {u_vals[r]}").scale(0.6)
                    u_text.move_to(row_lines[r].get_center() + DOWN * 0.25)
                    
                    # Move result to its place
                    scene.play(ReplacementTransform(f3, u_text))
                    live_calc_text = VGroup() # Reset placeholder
                    uv_mobjects.add(u_text)

            loops_done += 1
            if not made_progress or loops_done > (num_sources + num_destinations):
                # Safeguard to prevent infinite loop
                break
        
        # Cleanup the explanation text
        scene.play(FadeOut(formula_text), FadeOut(start_rule))
        
        # --- 6. Cleanup and Return ---
        scene.wait(2)
        scene.play(
            FadeOut(step2_title),
            FadeOut(live_calc_text) # Fade out any remaining calculation
        )
        
        return u_vals, v_vals, uv_mobjects
    
    def calculate_opportunity_costs(self, scene, table, costs, initial_alloc, u_vals, v_vals, title_text):
        """
        Calculates and animates the opportunity costs (d_ij) for all
        unallocated cells using the formula d_ij = u_i + v_j - C_ij.
        Displays the costs in a list on the right.
        Returns the cell with the MOST POSITIVE cost (entering cell).
        """
        
        num_sources = len(costs)
        num_destinations = len(costs[0])

        # --- 1. Set up titles and tracking variables ---
        step3_title = Tex("Step 3: Calculate Opportunity Costs $(d_{ij})$").scale(0.65)
        step3_title.next_to(title_text, DOWN, buff=0.1).set_color(LOGO_BLUE)
        
        formula_text = Tex("For all unallocated (white) cells, use:", color=PURPLE).scale(0.6)
        formula_text.next_to(step3_title, DOWN, buff=0.15)
        
        formula = MathTex(r"d_{ij} = u_i + v_j - C_{ij}").scale(0.7)
        formula.to_edge(RIGHT, buff=0.5).shift(UP*2)
        
        # This VGroup will show the step-by-step calculation "live"
        temp_calc_group = VGroup().scale(0.7).next_to(formula, DOWN, buff=0.25)

        scene.play(
            Write(step3_title),
            Write(formula_text),
            Write(formula)
        )
        scene.wait(2)

        # Tracking variables
        opportunity_costs = [[None] * num_destinations for _ in range(num_sources)]
        cost_mobjects = VGroup(Tex("Opportunity Costs for unallocated cells.")).scale(0.7).to_edge(RIGHT, buff=0.45)
        scene.play(Write(cost_mobjects[0]))
        
        # We look for the MOST POSITIVE cost, as this breaks optimality (d_ij <= 0)
        most_positive_cost = 0 # We are looking for a value > 0
        entering_cell_coords = None     # Will store (r, c)
        entering_cell_mobject = None # Will store the MathTex object
        
        calc_animation = VGroup().to_edge(RIGHT, buff=0.5) 

        # --- 2. Iterate through all cells ---
        for r in range(num_sources):
            for c in range(num_destinations):
                
                if initial_alloc[r][c] == 0:
                    
                    # --- A. Animate the calculation ---
                    cell_to_indicate = table.get_cell((r+2, c+2))
                    row_label = chr(65 + r)
                    col_label = str(c + 1)

                    scene.play(Flash(cell_to_indicate, color=RED))

                    f1 = MathTex(f"d_{{{row_label}{col_label}}} = u_{row_label} + v_{col_label} - C_{{{row_label}{col_label}}}").to_edge(RIGHT, buff=0.5).shift(DOWN*1.3).scale(0.65)
                    scene.play(ReplacementTransform(calc_animation, f1))
                    
                    f2 = MathTex(f"d_{{{row_label}{col_label}}} = ({u_vals[r]}) + ({v_vals[c]}) - ({costs[r][c]})").to_edge(RIGHT, buff=0.5).shift(DOWN*1.3).scale(0.65)
                    scene.play(ReplacementTransform(f1, f2))

                    # --- B. Calculate the value ---
                    cost_val = u_vals[r] + v_vals[c] - costs[r][c]
                    opportunity_costs[r][c] = cost_val

                    f3 = MathTex(f"d_{{{row_label}{col_label}}} = {cost_val}").to_edge(RIGHT, buff=0.5).shift(DOWN*1.3).scale(0.65)
                    scene.play(ReplacementTransform(f2, f3))
                    
                    # --- C. Add text to the list ---
                    final_cost_text = f3.copy()
                    
                    # --- CRITICAL CHANGE ---
                    # Color it: Red for positive (BAD), Green for negative (GOOD)
                    if cost_val > 0:
                        final_cost_text.set_color(RED)
                    else:
                        final_cost_text.set_color(GREEN_E)
                    
                    cost_mobjects.add(final_cost_text)
                    
                    scene.play(
                        cost_mobjects.animate.arrange(DOWN, buff=0.15, aligned_edge=LEFT).to_edge(RIGHT, buff=0.5),
                        FadeOut(f3)
                    )
                    calc_animation = VGroup()

                    # --- D. Check if this is the new "most positive" ---
                    if cost_val > most_positive_cost:
                        most_positive_cost = cost_val
                        entering_cell_coords = (r, c)
                        entering_cell_mobject = final_cost_text # Store the mobject
                        
        # --- 3. Clean up and return ---
        text_to_fade = VGroup(step3_title, formula_text, formula, temp_calc_group)
        scene.play(FadeOut(text_to_fade))
        scene.wait(1)

        # Return the critical values for the next step
        return (
            opportunity_costs, 
            cost_mobjects, 
            most_positive_cost, 
            entering_cell_coords, 
            entering_cell_mobject
        )
    
    def animate_check_optimality(self, scene, table, main_header, 
                                cost_mobjects, 
                                most_positive_cost, 
                                entering_cell_coords, 
                                entering_cell_mobject):
        """
        Step 5: Animates the optimality check.
        Checks if all d_ij <= 0.
        
        Args:
            scene (Scene): The manim scene object ('self').
            table (Table): The Manim Table mobject.
            main_header (Mobject): The main scene title, for positioning.
            cost_mobjects (VGroup): The list of opp costs on the right.
            most_positive_cost (float): The largest d_ij value.
            entering_cell_coords (tuple): (r, c) of the entering cell.
            entering_cell_mobject (MathTex): The mobject in the list to highlight.

        Returns:
            - bool: True if the solution is optimal, False otherwise.
        """
        
        # --- 1. Title and Rule ---
        step4_title = Tex("Step 4: Check for Optimality").scale(0.65)
        step4_title.next_to(main_header, DOWN, buff=0.1).set_color(LOGO_BLUE)
        
        rule_text = MathTex(r"\text{Optimality Condition: }\text{All } d_{ij} \le 0").scale(0.7)
        # Position this relative to the list of costs on the right
        rule_text.next_to(cost_mobjects, UP, buff=0.3).align_to(cost_mobjects, LEFT)
        
        scene.play(Write(step4_title), Write(rule_text))
        scene.wait(2)

        # --- 2. Check the condition ---
        
        # Case 1: Solution IS Optimal
        if most_positive_cost <= 0:
            result_text = Tex("All opportunity costs are $\le 0$.", color=GREEN_E).scale(0.7)
            result_text.next_to(cost_mobjects, DOWN, buff=0.2).align_to(rule_text, LEFT)
            
            final_text = Tex("The solution is OPTIMAL.", color=GREEN).scale(0.8)
            final_text.next_to(result_text, DOWN, buff=0.2).align_to(rule_text, LEFT)
            
            scene.play(Write(result_text))
            scene.play(Write(final_text))
            scene.wait(3)
            
            # Cleanup all text on the right
            scene.play(
                FadeOut(step4_title),
                FadeOut(rule_text),
                FadeOut(result_text),
                FadeOut(final_text),
                FadeOut(cost_mobjects) # Also fade out the list
            )
            return True # Return True (is_optimal)

        # Case 2: Solution is NOT Optimal
        else:
            result_text = Tex("At least one opportunity cost is $> 0$.", color=RED).scale(0.7)
            result_text.next_to(cost_mobjects, DOWN, buff=0.2).align_to(rule_text, LEFT)
            
            final_text = Tex("The solution is NOT optimal.", color=RED).scale(0.8)
            final_text.next_to(result_text, DOWN, buff=0.2).align_to(rule_text, LEFT)
            
            scene.play(Write(result_text))
            scene.play(Write(final_text))
            scene.wait(1.5)
            
            # Highlight the entering cell
            select_text = Tex("Select cell with most positive $d_{ij}$ as entering cell.").scale(0.7)
            select_text.next_to(final_text, DOWN, buff=0.2).shift(LEFT*1.5)
            scene.play(Write(select_text))
            
            # Animate indication of the text mobject in the list
            scene.play(Indicate(entering_cell_mobject, color=YELLOW, scale_factor=1.2))
            
            # Get the (r,c) coordinates
            r, c = entering_cell_coords
            # Get the table cell mobject
            cell_to_highlight = table.get_cell((r+2, c+2))
            
            # Draw an arrow from the text to the cell
            arrow = Arrow(
                entering_cell_mobject.get_right(), 
                cell_to_highlight.get_center(), 
                buff=0.1, 
                color=RED,
                stroke_width=4
            )
            
            scene.play(
                Create(arrow),
                Flash(cell_to_highlight, color=RED, time_width=1.0)
            )
            scene.wait(2)
            
            # Cleanup all text on the right
            scene.play(
                FadeOut(step4_title),
                FadeOut(rule_text),
                FadeOut(result_text),
                FadeOut(final_text),
                FadeOut(select_text),
                FadeOut(arrow),
                FadeOut(cost_mobjects) # Also fade out the list
            )
            return False # Return False (is_optimal)
        
    def animate_loop_and_signs(self, scene, table, initial_alloc, entering_cell_coord, main_header):
        """
        Step 6: Animates finding the closed loop and assigning +/- signs.
        Uses the imported 'find_loop' logic.
        
        Args:
            scene (Scene): The manim scene object ('self').
            table (Table): The Manim Table mobject.
            initial_alloc (list): The 2D allocation logic matrix (with epsilon).
            entering_cell_coord (tuple): (r, c) of the entering cell.
            main_header (Mobject): The main scene title, for positioning.

        Returns:
            - loop_path (list): The list of (r, c) tuples in the loop.
            - cleanup_mobjects (VGroup): All mobjects created in this function.
        """
        
        # --- 1. Title and Rules ---
        step5_title = Tex("Step 5: Identify Closed Loop").scale(0.65)
        step5_title.next_to(main_header, DOWN, buff=0.1).set_color(LOGO_BLUE)
        scene.play(Write(step5_title))

        # Create the rules text on the right
        rules_group = VGroup(
            Tex("Loop Rules:", color=PURPLE),
            Tex(r"1. Start at the entering cell."),
            Tex(r"2. Move horizontally or vertically."),
            Tex(r"3. Turn \textbf{only} at \underline{allocated cells.}"),
            Tex(r"4. End at the starting cell.")
        ).scale(0.6).shift(UP*1.0).arrange(DOWN, buff=0.2, aligned_edge=LEFT)
        
        scene.play(Write(rules_group))
        scene.play(rules_group.animate.to_edge(RIGHT, buff=0.25))
        scene.wait(2) # Give time to read rules

        # --- 2. Find Loop (Using Imported Logic) ---
        # This is the logic call. It happens instantly.
        loop_path = find_loop(initial_alloc, entering_cell_coord)

        if loop_path is None:
            print("--- FATAL ERROR: No loop was found! ---")
            error_text = Tex("ERROR: No loop found!").set_color(RED)
            scene.play(Write(error_text))
            return None, VGroup(step5_title, rules_group, error_text)

        # --- 3. Animate Drawing the Loop ---
        # Get the center-points of all cells in the loop
        points = []
        for (r, c) in loop_path:
            cell = table.get_cell((r+2, c+2)) # +2 for headers
            points.append(cell.get_center())
        # Add the first point to the end to close the loop
        points.append(points[0])

        # Animate drawing the lines one by one
        drawn_path = VGroup()
        for i in range(len(loop_path)):
            line = Line(
                points[i], 
                points[i+1], 
                color=LOGO_BLUE, 
                stroke_width=5, 
                z_index=10 # Draw on top
            )
            scene.play(Create(line), run_time=0.4)
            drawn_path.add(line)
        
        scene.wait(1)

        # --- 4. Animate Adding Signs ---
        sign_text = Tex(r"Assign alternating $+/-$ signs, \\ starting with $+$ at the entering cell.").scale(0.6)
        sign_text.next_to(rules_group, DOWN, buff=0.3).shift(LEFT * 0.75)
        scene.play(Write(sign_text))
        scene.wait(1)

        sign_mobjects = VGroup()
        for i in range(len(loop_path)):
            (r, c) = loop_path[i]
            cell_to_sign = table.get_cell((r+2, c+2))
            pos = cell_to_sign.get_corner(UP + LEFT) + DR * 0.1 + RIGHT * 0.15
            
            if i % 2 == 0:
                # Even index (0, 2, 4...) = +
                sign = MathTex("+", color=BLACK).scale(0.5)
            else:
                # Odd index (1, 3, 5...) = -
                sign = MathTex("-", color=BLACK).scale(0.5)
            
            # Place sign in the corner
            sign.move_to(pos).set_z_index(20)
            sign_mobjects.add(sign)
            
            scene.play(FadeIn(sign, scale=0.5), run_time=0.25)

        scene.wait(2)
        scene.play(FadeOut(
            step5_title, 
            rules_group, 
            sign_text))

        # --- 5. Return mobjects and data for next step ---
        # Group all mobjects created in this function for cleanup
        cleanup_mobjects = VGroup( 
            drawn_path,
            sign_mobjects
        )

        return loop_path, cleanup_mobjects
    
    def animate_allocation_adjustment(self, scene, table, initial_alloc, alloc_mobject_map, 
                                      loop_path, main_header, loop_cleanup_mobjects):
        """
        Step 7: Animates the adjustment of allocations based on the loop.
        Updates the persistent allocation mobjects and highlights.

        Args:
            scene (Scene): The manim scene object ('self').
            table (Table): The Manim Table mobject.
            initial_alloc (list): The 2D allocation logic matrix (with epsilon).
            alloc_mobject_map (dict): The map of (r,c) -> Mobject (the state).
            loop_path (list): The list of (r, c) tuples in the loop.
            main_header (Mobject): The main scene title, for positioning.
            loop_cleanup_mobjects (VGroup): Mobjects from the previous step to fade.

        Returns:
            - new_allocations (list): The new 2D allocation logic matrix.
            - new_alloc_map (dict): The updated map of (r,c) -> Mobject.
        """

        # --- 1. Title ---
        step6_title = Tex("Step 6: Adjust Allocations").scale(0.65)
        step6_title.next_to(main_header, DOWN, buff=0.1).set_color(LOGO_BLUE)
        scene.play(Write(step6_title))
        
        # --- 2. Logic Call (Using Imported Function) ---
        (
            new_allocations, 
            theta, 
            plus_cells, 
            minus_cells
        ) = adjust_allocations(initial_alloc, loop_path)

        # --- 3. Animate Finding Theta ---
        # Create text on the right
        theta_text_group = VGroup()
        theta_text_1 = Tex(r"Find min '$-$' allocation ($\theta$):", color=RED).scale(0.6)
        
        # Format theta value (check for epsilon)
        if theta == 0.001: 
            theta_str = r"\epsilon"
        else: 
            theta_str = str(int(theta))
            
        theta_text_2 = MathTex(f"\\theta = {theta_str}").scale(0.7)
        theta_text_group.add(theta_text_1, theta_text_2).arrange(DOWN, buff=0.2, aligned_edge=LEFT)
        theta_text_group.to_edge(RIGHT, buff=0.45).shift(UP*1.0)

        scene.play(Write(theta_text_1))
        
        # Flash the minus cells' allocation mobjects
        flash_anims = []
        for (r, c) in minus_cells:
            if (r, c) in alloc_mobject_map: # Find the mobject
                flash_anims.append(Flash(alloc_mobject_map[(r, c)], color=RED, time_width=0.5))
        if flash_anims:
            scene.play(*flash_anims)
        
        scene.play(Write(theta_text_2))
        scene.wait(1.5)

        # --- 4. Animate Allocation Mobject Changes ---
        adj_text = Tex(r"Add $\theta$ to '$+$' cells, subtract $\theta$ from '$-$' cells.").scale(0.6)
        adj_text.next_to(theta_text_group, DOWN, buff=0.3)
        scene.play(Write(adj_text))
        
        animation_list = []
        new_alloc_map = alloc_mobject_map.copy() # Copy the old map

        for (r, c) in loop_path:
            old_mob = alloc_mobject_map.get((r, c)) # Get old mobject, or None
            new_val = new_allocations[r][c]
            
            # Get position from your create_table function
            cell = table.get_cell((r+2, c+2))
            pos = cell.get_corner(UP + LEFT) + DOWN * 0.12 + RIGHT * 0.14
            
            # Create new mobject (even if it's empty)
            new_mob = None
            if new_val == 0.001:
                new_mob = MathTex(r"\epsilon", color=BLACK).scale(0.5)
            elif new_val > 0:
                new_mob = MathTex(str(int(new_val)), color=PURPLE_E).scale(0.5)
            else:
                new_mob = MathTex("").scale(0.5) # Empty mobject for 0
            
            new_mob.move_to(pos).set_z_index(15)

            # Create the animation
            if old_mob:
                # This cell was allocated (e.g., 5 -> 0 or 10 -> 15)
                animation_list.append(ReplacementTransform(old_mob, new_mob))
                del new_alloc_map[(r, c)] # Remove old key
            else:
                # This was the unallocated entering cell (e.g., None -> 5)
                animation_list.append(FadeIn(new_mob))
            
            # Add the new mobject to the map if it's not zero
            if new_val > 0:
                new_alloc_map[(r, c)] = new_mob
        
        # Run all allocation change animations
        scene.play(*animation_list)
        scene.wait(1)

        # --- 6. Cleanup ---
        scene.play(
            FadeOut(step6_title),
            FadeOut(theta_text_group),
            FadeOut(adj_text),
            FadeOut(loop_cleanup_mobjects) # Fade out the loop/signs
        )
        
        # --- 7. Return New State ---
        return new_allocations, new_alloc_map
    
    def animate_table_update(self, scene, old_table_alloc_vgroup,
                             costs, supply, demand, new_allocations):
        """
        Step 8: "Refreshes" the table.
        Creates a new table with updated highlights and allocations
        off-screen, then transforms the old table into the new one.

        Args:
            scene (Scene): The manim scene object ('self').
            old_table_alloc_vgroup (VGroup): The VGroup holding the old table + allocs.
            costs (list): The 2D cost matrix.
            supply (list): The supply values.
            demand (list): The demand values.
            new_allocations (list): The new 2D allocation logic matrix.

        Returns:
            - new_table (Table): The new Manim Table mobject.
            - new_alloc_map (dict): The new map of (r,c) -> Mobject.
            - new_table_alloc_vgroup (VGroup): The new VGroup holding the table + allocs.
        """

        # --- 1. Silently Create New Table ---
        # We re-run the logic from 'create_table_with_allocations'
        # but without any 'scene.play()' calls.
        
        num_sources = len(costs)
        num_destinations = len(costs[0])
        
        table_data = []
        for i in range(num_sources):
            row = costs[i] + [supply[i]]
            table_data.append(row)
        table_data.append(demand + [sum(supply)])
        
        source_labels = [Tex(chr(65 + i)) for i in range(num_sources)]
        source_labels.append(Tex("Demand"))
        dest_labels = [Tex(str(i+1)) for i in range(num_destinations)]
        dest_labels.append(Tex("Supply"))
        
        # Create the new table mobject
        new_table = IntegerTable(
            table_data,
            row_labels=source_labels,
            col_labels=dest_labels,
            h_buff=1.2,
            v_buff=0.8,
            line_config={"stroke_width": 2}
        ).scale(0.5)
        
        for item in new_table.get_entries():
            item.set_color(BLACK)
        
        # Add new highlights based on the new allocation logic
        for r in range(len(new_allocations)):
            for c in range(len(new_allocations[0])):
                if new_allocations[r][c] > 0:
                    color = ORANGE if new_allocations[r][c] == 0.001 else GREEN
                    new_table.add_highlighted_cell((r+2, c+2), color, fill_opacity=0.45)
        
        # --- 2. Silently Create New Allocation Mobjects ---
        new_alloc_map = {} 
        new_alloc_vgroup = VGroup() 
        
        for r in range(len(new_allocations)):
            for c in range(len(new_allocations[0])):
                val = new_allocations[r][c]
                if val > 0:
                    cell = new_table.get_cell((r+2, c+2))
                    pos = cell.get_corner(UP + LEFT) + DOWN * 0.12 + RIGHT * 0.14
                    
                    if val == 0.001:
                        tex_mob = MathTex(r"\epsilon", color=BLACK).scale(0.5)
                    else:
                        tex_mob = MathTex(str(int(val)), color=PURPLE_E).scale(0.5)
                    
                    tex_mob.move_to(pos).set_z_index(15)
                    new_alloc_map[(r, c)] = tex_mob
                    new_alloc_vgroup.add(tex_mob)
        
        # --- 3. Group and Position the New Table ---
        # Create the new VGroup
        new_table_alloc_vgroup = VGroup(new_table, new_alloc_vgroup)
        
        # Move the new, invisible group to the *exact* position
        # of the old, visible group for a smooth transform.
        new_table_alloc_vgroup.move_to(old_table_alloc_vgroup)
        # Also move the u/v lines to match (if they exist)
        
        # --- 4. Animate the Transform ---
        scene.play(
            ReplacementTransform(old_table_alloc_vgroup, new_table_alloc_vgroup)
        )
        scene.wait(1)

        # --- 5. Return the New State ---
        return new_table, new_alloc_map, new_table_alloc_vgroup