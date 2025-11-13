from manim import *
import copy
import os
from MODI_solver import find_loop, adjust_allocations

# --- Manim Scene Configuration ---
config.background_color = WHITE
Tex.set_default(color=BLACK)
MathTex.set_default(color=BLACK)
Line.set_default(color=BLACK)
Table.set_default(color=BLACK)

IMG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")
os.makedirs(IMG_DIR, exist_ok=True)

class StaticHelpers:
    """
    Static helper functions for PDF generation.
    No animations - just add objects and save frames.
    """
    
    def create_table_with_allocations(self, scene, costs, supply, demand, initial_alloc, main_header, img_num):
        """
        Creates table with allocations - STATIC VERSION
        """
        num_sources = len(costs)
        num_destinations = len(costs[0])
        
        # Build table data
        table_data = []
        for i in range(num_sources):
            row = costs[i] + [supply[i]]
            table_data.append(row)
        table_data.append(demand + [sum(supply)])
        
        # Labels
        source_labels = [Tex(chr(65 + i)) for i in range(num_sources)]
        source_labels.append(Tex("Demand"))
        dest_labels = [Tex(str(i+1)) for i in range(num_destinations)]
        dest_labels.append(Tex("Supply"))
        
        # Create table
        table = IntegerTable(
            table_data,
            row_labels=source_labels,
            col_labels=dest_labels,
            h_buff=1.2,
            v_buff=0.8,
            line_config={"stroke_width": 2}
        ).scale(0.5).to_edge(LEFT, buff=0.1)
        
        for item in table.get_entries():
            item.set_color(BLACK)
        
        # Highlight allocated cells
        for r in range(len(initial_alloc)):
            for c in range(len(initial_alloc[0])):
                if initial_alloc[r][c] > 0:
                    table.add_highlighted_cell((r+2, c+2), GREEN, fill_opacity=0.45)
        
        scene.add(table)
        
        # Create allocation mobjects
        alloc_mobject_map = {}
        alloc_mobjects_vgroup = VGroup()
        
        for r in range(len(initial_alloc)):
            for c in range(len(initial_alloc[0])):
                val = initial_alloc[r][c]
                if val > 0:
                    cell = table.get_cell((r+2, c+2))
                    pos = cell.get_corner(UP + LEFT) + DOWN * 0.12 + RIGHT * 0.14
                    
                    if val == 0.001:
                        tex_mob = MathTex(r"\epsilon", color=BLACK).scale(0.5)
                    else:
                        tex_mob = MathTex(str(int(val)), color=PURPLE_E).scale(0.5)
                    
                    tex_mob.move_to(pos).set_z_index(15)
                    alloc_mobject_map[(r, c)] = tex_mob
                    alloc_mobjects_vgroup.add(tex_mob)
        
        scene.add(alloc_mobjects_vgroup)
        table_alloc = VGroup(table, alloc_mobjects_vgroup)
        
        # CRITICAL: Wait to render the frame before saving
        scene.wait(0.01)
        scene.camera.get_image().save(os.path.join(IMG_DIR, f"img{img_num}_table_basic.png"))
        
        return table, alloc_mobject_map, table_alloc
    
    def extend_table(self, scene, table, table_alloc, costs, img_num):
        """
        Extends table with u/v lines - STATIC VERSION
        """
        table_alloc.shift(DOWN * 0.25)
        
        num_data_rows = len(costs)
        num_data_cols = len(costs[0])
        
        # Create u/v lines
        row_lines = VGroup(*[
            Line(
                start=table.get_horizontal_lines()[i].get_right(),
                end=table.get_horizontal_lines()[i].get_right() + RIGHT * 1
            ).set_stroke(BLACK, 2)
            for i in range(num_data_rows + 1)
        ])
        
        col_lines = VGroup(*[
            Line(
                start=table.get_vertical_lines()[i].get_bottom(),
                end=table.get_vertical_lines()[i].get_bottom() + DOWN * 1
            ).set_stroke(BLACK, 2)
            for i in range(num_data_cols + 1)
        ])
        
        outer_h_line = table.get_horizontal_lines()[-1].copy().shift(DOWN * 0.6)
        outer_v_line = table.get_vertical_lines()[-1].copy().shift(RIGHT * 1.29)
        
        scene.add(row_lines, col_lines, outer_h_line, outer_v_line)
        
        # SAVE IMAGE
        scene.camera.get_image().save(os.path.join(IMG_DIR, f"img{img_num}_table_extended.png"))
        
        return row_lines, col_lines
    
    def animate_degeneracy_check(self, scene, table, alloc_mobject_map, costs, main_header, img_num):
        """
        Degeneracy check - STATIC VERSION
        Shows only the final result
        """
        step1_title = Tex("Step 1: Check for Degeneracy").scale(0.65)
        step1_title.next_to(main_header, DOWN, buff=0.1).set_color(LOGO_BLUE)
        scene.add(step1_title)
        
        num_sources = len(costs)
        num_destinations = len(costs[0])
        num_allocations = len(alloc_mobject_map)
        required_allocations = num_sources + num_destinations - 1
        
        # Display count
        counter_text = MathTex(f"Allocations = {num_allocations}").scale(0.7)
        counter_text.to_edge(RIGHT, buff=0.45)
        scene.add(counter_text)
        
        # Formula
        formula_sub = MathTex(f"{num_sources} + {num_destinations} - 1 = {required_allocations}").scale(0.7)
        formula_sub.next_to(counter_text, DOWN, buff=0.2)
        scene.add(formula_sub)
        
        # Result
        is_degenerate = False
        if num_allocations == required_allocations:
            result_grp = VGroup(
                MathTex(f"{num_allocations} = {required_allocations}", color=GREEN),
                Tex("Solution is Non-Degenerate", color=GREEN)
            ).scale(0.7).arrange(DOWN)
        else:
            is_degenerate = True
            result_grp = VGroup(
                MathTex(f"{num_allocations} \\neq {required_allocations}", color=RED),
                Tex("Solution is Degenerate", color=RED)
            ).scale(0.7).arrange(DOWN)
        
        result_grp.next_to(formula_sub, DOWN, buff=0.2).shift(LEFT * 2)
        scene.add(result_grp)
        
        # SAVE IMAGE
        scene.camera.get_image().save(os.path.join(IMG_DIR, f"img{img_num}_degeneracy_check.png"))
        
        # Cleanup for next step
        scene.remove(step1_title, counter_text, formula_sub, result_grp)
        
        return is_degenerate
    
    def handle_degeneracy(self, scene, table, costs, initial_alloc, alloc_mobject_map, main_header, img_num):
        """
        Handle degeneracy - STATIC VERSION
        Shows only the final result with epsilon placed
        """
        step1a_title = Tex("Step 1a: Resolving Degeneracy").scale(0.65)
        step1a_title.next_to(main_header, DOWN, buff=0.1).set_color(RED)
        
        problem_text = Tex("Solution is Degenerate.", color=RED).scale(0.6)
        problem_text.to_edge(RIGHT, buff=0.45).shift(UP * 1.5)
        
        fix_text = Tex(
            r"Add $\epsilon$ to min-cost unallocated cell."
        ).scale(0.6)
        fix_text.next_to(problem_text, DOWN, buff=0.2)
        
        scene.add(step1a_title, problem_text, fix_text)
        
        # Find min-cost cell
        min_cost = float('inf')
        min_cost_cell = (-1, -1)
        num_sources = len(costs)
        num_destinations = len(costs[0])
        
        for r in range(num_sources):
            for c in range(num_destinations):
                if (r, c) not in alloc_mobject_map:
                    if costs[r][c] < min_cost:
                        min_cost = costs[r][c]
                        min_cost_cell = (r, c)
        
        r, c = min_cost_cell
        
        # Highlight cell
        table.add_highlighted_cell((r+2, c+2), ORANGE, fill_opacity=0.45)
        
        # Create epsilon mobject
        cell = table.get_cell((r+2, c+2))
        pos = cell.get_corner(UP + LEFT) + DOWN * 0.12 + RIGHT * 0.14
        epsilon_mobject = MathTex(r"\epsilon", color=BLACK).scale(0.5)
        epsilon_mobject.move_to(pos).set_z_index(15)
        scene.add(epsilon_mobject)
        
        # SAVE IMAGE
        scene.camera.get_image().save(os.path.join(IMG_DIR, f"img{img_num}_degeneracy_resolved.png"))
        
        # Update state
        new_alloc_logic = copy.deepcopy(initial_alloc)
        new_alloc_logic[r][c] = 0.001
        new_alloc_map = alloc_mobject_map.copy()
        new_alloc_map[(r, c)] = epsilon_mobject
        
        # Cleanup
        scene.remove(step1a_title, problem_text, fix_text)
        
        return new_alloc_logic, new_alloc_map, epsilon_mobject
    
    def animate_uv_calculation(self, scene, table, costs, initial_alloc, alloc_mobject_map, row_lines, col_lines, main_header, img_num):
        """
        U/V calculation - STATIC VERSION
        Shows only the final u/v values
        """
        step2_title = Tex("Step 2: Calculate $u_i$ and $v_j$").scale(0.65)
        step2_title.next_to(main_header, DOWN, buff=0.1).set_color(LOGO_BLUE)
        scene.add(step2_title)
        
        formula_text = Tex(r"Use $C_{ij} = u_i + v_j$ for all allocated cells.", color=PURPLE).scale(0.6)
        formula_text.to_edge(RIGHT, buff=0.45).shift(UP * 1.5)
        scene.add(formula_text)
        
        num_sources = len(costs)
        num_destinations = len(costs[0])
        
        u_vals = [None] * num_sources
        v_vals = [None] * num_destinations
        uv_mobjects = VGroup()
        
        allocated_cells = list(alloc_mobject_map.keys())
        
        # Calculate u/v (logic only, no animation)
        u_vals[0] = 0
        loops_done = 0
        while (any(v is None for v in u_vals) or any(v is None for v in v_vals)) and loops_done < 20:
            made_progress = False
            for (r, c) in allocated_cells:
                if u_vals[r] is not None and v_vals[c] is None:
                    v_vals[c] = costs[r][c] - u_vals[r]
                    made_progress = True
                elif v_vals[c] is not None and u_vals[r] is None:
                    u_vals[r] = costs[r][c] - v_vals[c]
                    made_progress = True
            if not made_progress:
                break
            loops_done += 1
        
        # Create all u mobjects
        for r in range(num_sources):
            if u_vals[r] is not None:
                row_label = chr(65 + r)
                u_text = MathTex(f"u_{row_label} = {u_vals[r]}").scale(0.6)
                u_text.move_to(row_lines[r].get_center() + DOWN * 0.25)
                scene.add(u_text)
                uv_mobjects.add(u_text)
        
        # Create all v mobjects
        for c in range(num_destinations):
            if v_vals[c] is not None:
                col_label = str(c + 1)
                v_text = VGroup(
                    MathTex(f"v_{col_label}"),
                    MathTex("="),
                    MathTex(f"{v_vals[c]}")
                ).arrange(DOWN).scale(0.6)
                v_text[1].rotate(PI/2)
                v_text.move_to(col_lines[c].get_center() + RIGHT * 0.27 + UP * 0.08)
                scene.add(v_text)
                uv_mobjects.add(v_text)
        
        # SAVE IMAGE
        scene.camera.get_image().save(os.path.join(IMG_DIR, f"img{img_num}_uv_calculated.png"))
        
        # Cleanup
        scene.remove(step2_title, formula_text)
        
        return u_vals, v_vals, uv_mobjects
    
    def calculate_opportunity_costs(self, scene, table, costs, initial_alloc, u_vals, v_vals, title_text, img_num):
        """
        Opportunity costs - STATIC VERSION
        Shows only the final list of opportunity costs
        """
        num_sources = len(costs)
        num_destinations = len(costs[0])
        
        step3_title = Tex("Step 3: Calculate Opportunity Costs $(d_{ij})$").scale(0.65)
        step3_title.next_to(title_text, DOWN, buff=0.1).set_color(LOGO_BLUE)
        scene.add(step3_title)
        
        formula = MathTex(r"d_{ij} = u_i + v_j - C_{ij}").scale(0.7)
        formula.to_edge(RIGHT, buff=0.5).shift(UP * 2)
        scene.add(formula)
        
        # Calculate all opportunity costs (no animation)
        opportunity_costs = [[None] * num_destinations for _ in range(num_sources)]
        cost_mobjects = VGroup(Tex("Opportunity Costs:", color=LOGO_BLUE).scale(0.7))
        
        most_positive_cost = 0
        entering_cell_coords = None
        entering_cell_mobject = None
        
        for r in range(num_sources):
            for c in range(num_destinations):
                if initial_alloc[r][c] == 0:
                    row_label = chr(65 + r)
                    col_label = str(c + 1)
                    
                    cost_val = u_vals[r] + v_vals[c] - costs[r][c]
                    opportunity_costs[r][c] = cost_val
                    
                    # Create cost text
                    cost_text = MathTex(f"d_{{{row_label}{col_label}}} = {cost_val}").scale(0.65)
                    
                    if cost_val > 0:
                        cost_text.set_color(RED)
                    else:
                        cost_text.set_color(GREEN_E)
                    
                    cost_mobjects.add(cost_text)
                    
                    if cost_val > most_positive_cost:
                        most_positive_cost = cost_val
                        entering_cell_coords = (r, c)
                        entering_cell_mobject = cost_text
        
        # Arrange all costs
        cost_mobjects.arrange(DOWN, buff=0.15, aligned_edge=LEFT).to_edge(RIGHT, buff=0.5).shift(DOWN * 0.5)
        scene.add(cost_mobjects)
        
        # SAVE IMAGE
        scene.camera.get_image().save(os.path.join(IMG_DIR, f"img{img_num}_opportunity_costs.png"))
        
        # Cleanup
        scene.remove(step3_title, formula)
        
        return (
            opportunity_costs,
            cost_mobjects,
            most_positive_cost,
            entering_cell_coords,
            entering_cell_mobject
        )
    
    def animate_check_optimality(self, scene, table, main_header, cost_mobjects, most_positive_cost, entering_cell_coords, entering_cell_mobject, img_num):
        """
        Optimality check - STATIC VERSION
        Shows only the final decision
        """
        step4_title = Tex("Step 4: Check for Optimality").scale(0.65)
        step4_title.next_to(main_header, DOWN, buff=0.1).set_color(LOGO_BLUE)
        scene.add(step4_title)
        
        rule_text = MathTex(r"\text{Optimality: All } d_{ij} \le 0").scale(0.7)
        rule_text.next_to(cost_mobjects, UP, buff=0.3).align_to(cost_mobjects, LEFT)
        scene.add(rule_text)
        
        if most_positive_cost <= 0:
            # Optimal
            result_text = Tex("All costs $\le 0$", color=GREEN_E).scale(0.7)
            result_text.next_to(cost_mobjects, DOWN, buff=0.2).align_to(rule_text, LEFT)
            
            final_text = Tex("Solution is OPTIMAL", color=GREEN).scale(0.8)
            final_text.next_to(result_text, DOWN, buff=0.2).align_to(rule_text, LEFT)
            
            scene.add(result_text, final_text)
            
            # SAVE IMAGE
            scene.camera.get_image().save(os.path.join(IMG_DIR, f"img{img_num}_optimal.png"))
            
            scene.remove(step4_title, rule_text, result_text, final_text, cost_mobjects)
            return True
        
        else:
            # Not optimal
            result_text = Tex("At least one cost $> 0$", color=RED).scale(0.7)
            result_text.next_to(cost_mobjects, DOWN, buff=0.2).align_to(rule_text, LEFT)
            
            final_text = Tex("NOT optimal", color=RED).scale(0.8)
            final_text.next_to(result_text, DOWN, buff=0.2).align_to(rule_text, LEFT)
            
            select_text = Tex("Select most positive as entering cell", color=PURPLE).scale(0.6)
            select_text.next_to(final_text, DOWN, buff=0.2).shift(LEFT * 1.5)
            
            scene.add(result_text, final_text, select_text)
            
            # Draw arrow to entering cell
            r, c = entering_cell_coords
            cell_to_highlight = table.get_cell((r+2, c+2))
            arrow = Arrow(
                entering_cell_mobject.get_right(),
                cell_to_highlight.get_center(),
                buff=0.1,
                color=RED,
                stroke_width=4
            )
            scene.add(arrow)
            
            # SAVE IMAGE
            scene.camera.get_image().save(os.path.join(IMG_DIR, f"img{img_num}_not_optimal.png"))
            
            scene.remove(step4_title, rule_text, result_text, final_text, select_text, arrow, cost_mobjects)
            return False
    
    def animate_loop_and_signs(self, scene, table, initial_alloc, entering_cell_coord, main_header, img_num):
        """
        Loop and signs - STATIC VERSION
        Shows the complete loop with signs
        """
        step5_title = Tex("Step 5: Identify Closed Loop").scale(0.65)
        step5_title.next_to(main_header, DOWN, buff=0.1).set_color(LOGO_BLUE)
        scene.add(step5_title)
        
        # Find loop
        loop_path = find_loop(initial_alloc, entering_cell_coord)
        
        if loop_path is None:
            error_text = Tex("ERROR: No loop found!", color=RED)
            scene.add(error_text)
            scene.camera.get_image().save(os.path.join(IMG_DIR, f"img{img_num}_loop_error.png"))
            return None, VGroup(step5_title, error_text)
        
        # Draw complete loop
        points = []
        for (r, c) in loop_path:
            cell = table.get_cell((r+2, c+2))
            points.append(cell.get_center())
        points.append(points[0])
        
        drawn_path = VGroup()
        for i in range(len(loop_path)):
            line = Line(points[i], points[i+1], color=LOGO_BLUE, stroke_width=5, z_index=10)
            drawn_path.add(line)
        scene.add(drawn_path)
        
        # Add all signs
        sign_mobjects = VGroup()
        for i in range(len(loop_path)):
            (r, c) = loop_path[i]
            cell_to_sign = table.get_cell((r+2, c+2))
            pos = cell_to_sign.get_corner(UP + LEFT) + DR * 0.1 + RIGHT * 0.15
            
            if i % 2 == 0:
                sign = MathTex("+", color=BLACK).scale(0.5)
            else:
                sign = MathTex("-", color=BLACK).scale(0.5)
            
            sign.move_to(pos).set_z_index(20)
            sign_mobjects.add(sign)
        
        scene.add(sign_mobjects)
        
        # SAVE IMAGE
        scene.camera.get_image().save(os.path.join(IMG_DIR, f"img{img_num}_loop_with_signs.png"))
        
        cleanup_mobjects = VGroup(step5_title, drawn_path, sign_mobjects)
        scene.remove(step5_title)
        
        return loop_path, cleanup_mobjects
    
    def animate_table_update(self, scene, old_table_alloc_vgroup, costs, supply, demand, new_allocations, img_num):
        """
        Table update - STATIC VERSION
        Shows the final updated table
        """
        num_sources = len(costs)
        num_destinations = len(costs[0])
        
        # Create new table
        table_data = []
        for i in range(num_sources):
            row = costs[i] + [supply[i]]
            table_data.append(row)
        table_data.append(demand + [sum(supply)])
        
        source_labels = [Tex(chr(65 + i)) for i in range(num_sources)]
        source_labels.append(Tex("Demand"))
        dest_labels = [Tex(str(i+1)) for i in range(num_destinations)]
        dest_labels.append(Tex("Supply"))
        
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
        
        # Add highlights
        for r in range(len(new_allocations)):
            for c in range(len(new_allocations[0])):
                if new_allocations[r][c] > 0:
                    color = ORANGE if new_allocations[r][c] == 0.001 else GREEN
                    new_table.add_highlighted_cell((r+2, c+2), color, fill_opacity=0.45)
        
        # Create allocation mobjects
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
        
        new_table_alloc_vgroup = VGroup(new_table, new_alloc_vgroup)
        new_table_alloc_vgroup.move_to(old_table_alloc_vgroup)
        
        # Remove old, add new
        scene.remove(old_table_alloc_vgroup)
        scene.add(new_table_alloc_vgroup)
        
        # SAVE IMAGE
        scene.camera.get_image().save(os.path.join(IMG_DIR, f"img{img_num}_table_updated.png"))
        
        return new_table, new_alloc_map, new_table_alloc_vgroup