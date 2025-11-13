from manim import *
from MODI_IMG_helper import StaticHelpers  # Your new static helpers file
from VAM_solver import solve_vam
from MODI_solver import adjust_allocations
import json
import os
from PIL import Image

class MODI_Static_PDF(Scene):
    """
    Static version of MODI animation for PDF generation.
    Run with: manim -sqh yourfile.py MODI_Static_PDF
    
    Images will be saved to: images/img1_table_basic.png, img2_..., etc.
    """
    def construct(self):
        # --- 0. Setup ---
        script_dir = os.path.dirname(__file__)
        json_path = os.path.join(script_dir, "transportation_problem.json")
        
        with open(json_path, "r") as f:
            data = json.load(f)
            supply = data["supply"]
            demand = data["demand"]
            costs = data["costs"]
        
        # Get initial VAM solution
        initial_allocation, initial_costs, update_costs, update_demand, update_supply = solve_vam(supply, demand, costs)
        
        # --- 1. Title Frame ---
        img_counter = 1
        
        Header = Tex("Transportation Problem\\\\Modified Distribution Method (MODI)", font_size=48)
        Header.scale(0.75).to_edge(UP, buff=0.25)
        self.add(Header)
        
        vam_title = Tex("Initial Solution using Vogel's Approximation Method")
        vam_title.scale(0.75).next_to(Header, DOWN, buff=0.1).set_color(LIGHT_PINK)
        self.add(vam_title)
        self.wait()
        self.camera.get_image().save(os.path.join(script_dir, "images", f"img{img_counter}_title.png"))
        img_counter += 1
        
        self.remove(vam_title)
        
        # --- 2. Create Helper ---
        helpers = StaticHelpers()
        
        # --- 3. Create Initial Table ---
        (
            table,
            alloc_mobject_map,
            table_alloc
        ) = helpers.create_table_with_allocations(
            self,
            update_costs,
            update_supply,
            update_demand,
            initial_allocation,
            Header,
            img_counter
        )
        img_counter += 1
        
        # --- 4. Extend Table ---
        (
            row_lines,
            col_lines
        ) = helpers.extend_table(
            self,
            table,
            table_alloc,
            update_costs,
            img_counter
        )
        img_counter += 1
        
        # --- 5. MODI ITERATION LOOP ---
        for iteration in range(5):  # Max 5 iterations
            
            print(f"\n--- ITERATION {iteration + 1} ---")
            
            # --- 5a. Degeneracy Check ---
            is_degenerate = helpers.animate_degeneracy_check(
                self,
                table,
                alloc_mobject_map,
                update_costs,
                Header,
                img_counter
            )
            img_counter += 1
            
            epsilon_mob = None
            
            # --- 5b. Handle Degeneracy ---
            if is_degenerate:
                (
                    initial_allocation,
                    alloc_mobject_map,
                    epsilon_mob
                ) = helpers.handle_degeneracy(
                    self,
                    table,
                    update_costs,
                    initial_allocation,
                    alloc_mobject_map,
                    Header,
                    img_counter
                )
                img_counter += 1
                table_alloc.add(epsilon_mob)
            
            # --- 5c. Calculate u_i and v_j ---
            (
                u_vals,
                v_vals,
                uv_mobs
            ) = helpers.animate_uv_calculation(
                self,
                table,
                update_costs,
                initial_allocation,
                alloc_mobject_map,
                row_lines,
                col_lines,
                Header,
                img_counter
            )
            img_counter += 1
            
            # --- 5d. Calculate Opportunity Costs ---
            (
                opportunity_costs,
                cost_mobjects,
                most_positive_cost,
                entering_cell_coords,
                entering_cell_mobject
            ) = helpers.calculate_opportunity_costs(
                self,
                table,
                update_costs,
                initial_allocation,
                u_vals,
                v_vals,
                Header,
                img_counter
            )
            img_counter += 1
            
            # --- 5e. Check for Optimality ---
            is_optimal = helpers.animate_check_optimality(
                self,
                table,
                Header,
                cost_mobjects,
                most_positive_cost,
                entering_cell_coords,
                entering_cell_mobject,
                img_counter
            )
            img_counter += 1
            
            # --- 5f. Decision ---
            if is_optimal:
                print("Solution is OPTIMAL!")
                
                # Create final optimal frame
                final_text = Tex("Solution is OPTIMAL!", color=GREEN).scale(1.2)
                final_text.to_edge(DOWN, buff=1)
                self.add(final_text)
                self.wait()
                self.camera.get_image().save(os.path.join(script_dir, "images", f"img{img_counter}_final_optimal.png"))
                
                if epsilon_mob:
                    self.remove(epsilon_mob)
                self.remove(uv_mobs)
                break  # EXIT LOOP
            
            else:
                print("Solution is NOT optimal. Finding loop...")
                
                # --- 5g. Find and Show Loop ---
                (
                    loop_path,
                    loop_cleanup_mobjects
                ) = helpers.animate_loop_and_signs(
                    self,
                    table,
                    initial_allocation,
                    entering_cell_coords,
                    Header,
                    img_counter
                )
                img_counter += 1
                
                if loop_path is None:
                    print("ERROR: No loop found!")
                    break
                
                # --- 5h. Get New Allocations (Logic) ---
                (
                    new_allocations_logic,
                    theta,
                    plus_cells,
                    minus_cells
                ) = adjust_allocations(initial_allocation, loop_path)
                
                print(f"Theta = {theta}")
                print(f"Plus cells: {plus_cells}")
                print(f"Minus cells: {minus_cells}")
                
                # --- 5i. Update Table Visuals ---
                (
                    new_table,
                    new_alloc_map_updated,
                    new_table_alloc
                ) = helpers.animate_table_update(
                    self,
                    table_alloc,
                    update_costs,
                    update_supply,
                    update_demand,
                    new_allocations_logic,
                    img_counter
                )
                img_counter += 1
                
                # --- 5j. Update State ---
                initial_allocation = new_allocations_logic
                alloc_mobject_map = new_alloc_map_updated
                table = new_table
                table_alloc = new_table_alloc
                
                # --- 5k. Cleanup ---
                self.remove(loop_cleanup_mobjects)
                if epsilon_mob:
                    self.remove(epsilon_mob)
                self.remove(uv_mobs)
        
        print(f"\n✓ Generated {img_counter - 1} images in 'images/' folder")
        print("Use the PDF generation script to combine them into a PDF.")

def create_pdf_from_images():
    img_dir = os.path.join(os.path.dirname(__file__), "images")
    output_pdf = "MODI_Method.pdf"
    
    # Get all PNG files sorted by number
    import re
    png_files = [f for f in os.listdir(img_dir) if f.endswith('.png')]
    png_files.sort(key=lambda x: int(re.findall(r'\d+', x)[0]))
    
    print(f"Found {len(png_files)} images")
    
    if not png_files:
        print("No images found!")
        return
    
    # Open images
    images = []
    for png_file in png_files:
        img_path = os.path.join(img_dir, png_file)
        img = Image.open(img_path).convert('RGB')
        images.append(img)
        print(f"  Added: {png_file}")
    
    # Save as PDF
    if images:
        images[0].save(
            output_pdf,
            save_all=True,
            append_images=images[1:],
            resolution=100.0
        )
        print(f"\n✓ PDF created: {output_pdf}")

if __name__ == "__main__":
    create_pdf_from_images()