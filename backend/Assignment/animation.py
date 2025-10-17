import json
from manim import *
import os
import time
import pkg_resources

# import helper functions and solver function
from helper_funcs import AnimationHelpers
from line_finder import solve_lines

# --- START: MODIFICATIONS FOR API INTEGRATION ---


class MyScene(Scene):
    def construct(self):
        # self.next_section(skip_animations=True)
        # Load the data from the file path provided via arguments
        try:
            script_dir = os.path.dirname(__file__)
            json_path = os.path.join(script_dir, "assignment_problem.json")
            with open(json_path, "r") as f:
                saved_data = json.load(f)
                table_data = saved_data["matrix"]
                question_data = saved_data["matrix"]
                problem_type = saved_data.get("type", "minimization")
        except (FileNotFoundError, KeyError) as e:
            # This default data is now just a fallback for direct execution
            print(f"Could not load : {e}. Using default matrix.")
            table_data = [[85, 75, 65, 125, 75], [90, 78, 66, 132, 78], [75, 66, 57, 114, 69], [80, 72, 60, 120, 72], [76, 64, 56, 112, 68]]
            question_data = [[85, 75, 65, 125, 75], [90, 78, 66, 132, 78], [75, 66, 57, 114, 69], [80, 72, 60, 120, 72], [76, 64, 56, 112, 68]]
            problem_type = "minimization"
            restrictions = []

        square_or_not = len(table_data) == len(table_data[0])
        total_steps = 5  # Base steps: header, square check, row reduction, column reduction, final assignment
        if problem_type == "maximization":
            total_steps += 1  # Add step for maximization transform
        if not square_or_not:
            total_steps += 1  # Add step for adding dummies

        # Animation Starts
        Header = Tex("Assignment Problem Visualization", font_size=54)
        self.play(Write(Header))
        self.wait(0.75)
        self.play(Header.animate.to_edge(UP).scale(0.75))
        table = AnimationHelpers.create_and_show_table(self, table_data, restrictions)
        question_table = table.copy()
        self.wait(1)


        # Step 1 A: If maximization, convert to minimization
        if problem_type == "maximization":
            step_one_a = Tex(r"Step 1.A: Convert Maximization to Minimization", font_size=36).next_to(Header, DOWN)
            self.play(Write(step_one_a))
            self.wait(1)
            self.play(step_one_a.animate.scale(0.75))
             
            new_data, new_table = AnimationHelpers.animate_maximization_transform(self, table, table_data)
            table_data = new_data  # Update the table data to the new minimization data
            table = new_table      # Update the table reference to the new Manim table
            self.play(FadeOut(step_one_a))
            self.wait(1)

        # Step 1: Check if the table is square
        step_one = Tex(r"Step 1: Check if the table is Square or not \\ (i.e. No. of Rows = No. of Columns)", font_size=36).next_to(Header, DOWN)
        self.play(Write(step_one))
        self.wait(1)
        self.play(step_one.animate.scale(0.75))
         
        is_square = AnimationHelpers.animate_square_check(self, table)
        self.wait(1)
        self.play(FadeOut(step_one))

        # Step 1 B: If not square, add dummy rows/columns
        if not is_square:
            step_one_b = Tex(r"Step 1.B: Add Dummy Rows/Columns to make the Table Square", font_size=36).next_to(Header, DOWN)
            self.play(Write(step_one_b))
            self.wait(1)
            self.play(step_one_b.animate.scale(0.75))
             
            new_data, new_table = AnimationHelpers.animate_add_dummies(self, table, table_data)
            table_data = new_data  # Update the table data to the new balanced data
            table = new_table      # Update the table reference to the new Manim table
            self.play(FadeOut(step_one_b))
            self.wait(1)
        # self.next_section(skip_animations=True)
        # --- Step 2: Row Reduction ---
        step_two = Tex(r"Step 2: Row Reduction", font_size=36).next_to(Header, DOWN)
        self.play(Write(step_two))
        self.wait(1)
        explain_row_reduction = Tex("Subtract the minimum value in each row from all entries in that row.").scale(0.6).next_to(step_two, DOWN)
        self.play(Write(explain_row_reduction))
        self.wait(0.5)
        self.play(explain_row_reduction.animate.scale(0.75))

        # Call the new row reduction function
        new_data, new_table = AnimationHelpers.animate_row_reduction(self, table, table_data, restrictions)
        
        # Update the main variables to the new state
        table_data = new_data
        table = new_table

        self.play(FadeOut(step_two, explain_row_reduction))
        self.wait(1)

        # self.next_section(skip_animations=True)
        # --- Step 3: Column Reduction ---
        step_three = Tex(r"Step 3: Column Reduction", font_size=36).next_to(Header, DOWN)
        self.play(Write(step_three))
        self.wait(1)
        explain_column_reduction = Tex(r"Check if each column has atleast one zero \\", r"if Found a zero :- check next column \\", r"If not Found :- Subtract the minimum entry of column with each cell of the same column").scale(0.6).next_to(step_three, DOWN)
        explain_column_reduction[1].set_color(GREEN)
        explain_column_reduction[2].set_color(RED)

        self.play(Write(explain_column_reduction[0]))
        self.wait(0.5)
        self.play(Write(explain_column_reduction[1]))
        self.wait(0.5)
        self.play(Write(explain_column_reduction[2]))
        self.wait(0.5)

        # Call the new column reduction function
        new_data, new_table = AnimationHelpers.animate_column_reduction(self, table, table_data, restrictions)
        
        # Update the main variables to the new state
        table_data = new_data
        table = new_table

        self.play(FadeOut(explain_column_reduction))
        self.wait(0.5)
        self.play(FadeOut(step_three))
        self.wait(1)


        # --- Step 4: Cover all zeros with minimum lines ---
        step_four = Tex(r"Step 4: Cover all zeros with minimum lines \\ (Horizontal or Vertical Lines)", font_size=36).next_to(Header, DOWN)
        self.play(Write(step_four))
        self.wait(1)
        #dimension of the table
        dimension = len(table_data)
        # This loop repeats until an optimal solution is found
        while True :
            print("DEBUG: Matrix being sent to solve_lines:")
            for row in table_data:
                print(row)
            # 1. Find the lines for the current matrix using your solver
            rows_to_cover, cols_to_cover = solve_lines(table_data)
            num_lines = len(rows_to_cover) + len(cols_to_cover)
            print(f"DEBUG: Found {num_lines} lines to cover all zeros.")

            # 2. Animate drawing the lines
            lines_mobject = AnimationHelpers.animate_line_drawing(
                self, table, rows_to_cover, cols_to_cover
            )
            print(cols_to_cover, rows_to_cover)
            # 3. Check if the number of lines is optimal
            # self.next_section()
            if num_lines == dimension:
                # If optimal, show success message and exit the loop
                optimal_text = Tex(f"Lines ({num_lines}) = Dimension ({dimension}). Optimal!", color=GREEN).scale(0.7)
                optimal_text.to_edge(DOWN, buff=1.25)
                self.play(Write(optimal_text))
                self.wait(1)
                self.play(FadeOut(lines_mobject), FadeOut(optimal_text), FadeOut(step_four))
                break # Exit the while loop
            else:
                # If not optimal, show message, then adjust the matrix
                self.play(FadeOut(Header))
                not_optimal_text = Tex(fr"Lines ({num_lines}) $<$ Dimension ({dimension}). Not optimal.", color=RED).scale(0.7)
                not_optimal_text.to_edge(DOWN, buff=1.25)
                self.play(Write(not_optimal_text))
                self.wait(1)
                
                # Fade out the old lines and text before adjusting
                self.play(FadeOut(not_optimal_text), FadeOut(step_four))
                
                print("DEBUG: Adjusted the matrix for the next iteration. ", table_data)
                 
                # Call the adjustment function to get the new data and table
                new_data, new_table = AnimationHelpers.animate_matrix_adjustment(
                self, table, table_data, rows_to_cover, cols_to_cover, lines_mobject)

                print("DEBUG: Adjusted the matrix for the next iteration. ", new_data)
                # Update the main variables for the next loop iteration
                table_data = new_data
                table = new_table

        # --- Proceed to Final Assignment ---
        # self.next_section()
        step_five = Tex("Step 5: Select Optimal Assignment").scale(0.7).to_edge(UP, buff=0.5)
        self.play(Write(step_five))
        self.wait(1)
        
        final_assignments, final_circles= AnimationHelpers.animate_final_assignment(self, table, table_data, step_five, restrictions)
        
        self.wait(2)
        AnimationHelpers.animate_assignment_summary(
            self, question_table, question_data, final_assignments, final_circles
        )
