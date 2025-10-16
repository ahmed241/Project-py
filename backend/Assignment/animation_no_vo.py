

from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.gtts import GTTSService
import json
import argparse
import os
import time

from helper_funcs import AnimationHelpers
from line_finder import solve_lines

class MySceneWithVoiceover(VoiceoverScene):
    def construct(self):
        # Set up the voiceover service
        self.set_speech_service(GTTSService(lang="en", tld="com"))
        
        # Load data
        try:
            with open("data.json", "r") as f:
                saved_data = json.load(f)
                table_data = saved_data["matrix"]
                question_data = saved_data["matrix"]
                problem_type = saved_data.get("type", "minimization")
                restrictions = saved_data.get("restrictions", [])
        except (FileNotFoundError, KeyError) as e:
            print(f"Could not load: {e}. Using default matrix.")
            table_data = [[9, 2, 7, 8], [6, 4, 3, 7], [5, 8, 1, 8], [7, 6, 9, 4]]
            question_data = table_data
            problem_type = "minimization"
            restrictions = []
        
        n = len(table_data)
        
        # --- INTRODUCTION WITH VOICEOVER ---
        Header = Text("Assignment Problem Visualization", font_size=48)
        
        with self.voiceover(text=f"""Welcome to the Assignment Problem visualization. 
                            We have a {n} by {n} cost matrix. 
                            Our goal is to find the optimal assignment that minimizes the total cost.""") as tracker:
            self.play(Write(Header))
            self.wait(tracker.duration - 2)  # Sync with audio
        
        self.play(Header.animate.to_edge(UP).scale(0.75))
        
        # --- CREATE TABLE ---
        table = AnimationHelpers.create_and_show_table(self, table_data, restrictions)
        question_table = table.copy()
        
        # --- STEP 1: SQUARE CHECK WITH VOICEOVER ---
        rows = len(table_data)
        cols = len(table_data[0])
        is_square = rows == cols
        
        step_one = Text("Step 1: Check if matrix is square", font_size=32).next_to(Header, DOWN)
        self.play(Write(step_one))
        
        if is_square:
            script = f"We have {rows} rows and {cols} columns. The matrix is square!"
        else:
            script = f"We have {rows} rows and {cols} columns. Not square, we'll add dummies."
        
        with self.voiceover(text=script) as tracker:
            is_square = AnimationHelpers.animate_square_check(self, table)
            self.wait(tracker.duration)
        
        self.play(FadeOut(step_one))
        
        # --- MAXIMIZATION (IF NEEDED) ---
        if problem_type == "maximization":
            step_one_a = Text("Step 1A: Convert to Minimization", font_size=32).next_to(Header, DOWN)
            self.play(Write(step_one_a))
            
            max_val = max(max(row) for row in table_data)
            script = f"""This is a maximization problem. We convert it by finding 
                      the maximum value, which is {max_val}, and subtracting 
                      each entry from it."""
            
            with self.voiceover(text=script) as tracker:
                new_data, new_table = AnimationHelpers.animate_maximization_transform(
                    self, table, table_data
                )
                table_data = new_data
                table = new_table
                self.wait(tracker.duration)
            
            self.play(FadeOut(step_one_a))
        
        # --- ADD DUMMIES (IF NEEDED) ---
        if not is_square:
            step_one_b = Text("Step 1B: Add Dummy Rows/Columns", font_size=32).next_to(Header, DOWN)
            self.play(Write(step_one_b))
            
            with self.voiceover(text="Adding dummy rows or columns with zero costs to balance the matrix.") as tracker:
                new_data, new_table = AnimationHelpers.animate_add_dummies(self, table, table_data)
                table_data = new_data
                table = new_table
                self.wait(tracker.duration)
            
            self.play(FadeOut(step_one_b))
        
        # --- STEP 2: ROW REDUCTION ---
        step_two = Text("Step 2: Row Reduction", font_size=32).next_to(Header, DOWN)
        self.play(Write(step_two))
        
        with self.voiceover(text="""Now we perform row reduction. For each row, 
                            we find the minimum value and subtract it from all 
                            entries in that row.""") as tracker:
            explain = Text("Subtract minimum from each row", font_size=24).next_to(step_two, DOWN)
            self.play(Write(explain))
            self.wait(tracker.duration)
        
        new_data, new_table = AnimationHelpers.animate_row_reduction(self, table, table_data, restrictions)
        table_data = new_data
        table = new_table
        
        self.play(FadeOut(step_two, explain))
        
        # --- STEP 3: COLUMN REDUCTION ---
        step_three = Text("Step 3: Column Reduction", font_size=32).next_to(Header, DOWN)
        self.play(Write(step_three))
        
        with self.voiceover(text="""For column reduction, we check each column. 
                            If it has at least one zero, we're good. 
                            Otherwise, we subtract the minimum value.""") as tracker:
            self.wait(tracker.duration)
        
        new_data, new_table = AnimationHelpers.animate_column_reduction(self, table, table_data, restrictions)
        table_data = new_data
        table = new_table
        
        self.play(FadeOut(step_three))
        
        # --- STEP 4: LINE DRAWING ---
        dimension = len(table_data)
        step_four = Text("Step 4: Cover zeros with lines", font_size=32).next_to(Header, DOWN)
        self.play(Write(step_four))
        
        with self.voiceover(text=f"""Now we draw horizontal and vertical lines 
                            to cover all zeros. If the number of lines equals {dimension}, 
                            we have an optimal solution.""") as tracker:
            self.wait(tracker.duration)
        
        # Line drawing loop (same as before, but with voiceover for each iteration)
        iteration = 0
        while True:
            rows_to_cover, cols_to_cover = solve_lines(table_data)
            num_lines = len(rows_to_cover) + len(cols_to_cover)
            
            lines_mobject = AnimationHelpers.animate_line_drawing(
                self, table, rows_to_cover, cols_to_cover
            )
            
            if num_lines == dimension:
                with self.voiceover(text=f"Perfect! We have {num_lines} lines for a {dimension} by {dimension} matrix. Optimal solution found!") as tracker:
                    optimal_text = Text(f"Lines = {num_lines}. Optimal!", color=GREEN, font_size=28).to_edge(DOWN)
                    self.play(Write(optimal_text))
                    self.wait(tracker.duration)
                
                self.play(FadeOut(lines_mobject, optimal_text, step_four))
                break
            else:
                with self.voiceover(text=f"We only have {num_lines} lines, but need {dimension}. Let's adjust the matrix.") as tracker:
                    not_optimal_text = Text(f"Lines = {num_lines} < {dimension}. Adjusting...", 
                                          color=RED, font_size=28).to_edge(DOWN)
                    self.play(Write(not_optimal_text))
                    self.wait(tracker.duration)
                
                self.play(FadeOut(not_optimal_text, step_four))
                
                new_data, new_table = AnimationHelpers.animate_matrix_adjustment(
                    self, table, table_data, rows_to_cover, cols_to_cover, lines_mobject
                )
                table_data = new_data
                table = new_table
                
                iteration += 1
                if iteration > 10:  # Safety break
                    break
        
        # --- STEP 5: FINAL ASSIGNMENT ---
        step_five = Text("Step 5: Optimal Assignment", font_size=32).to_edge(UP)
        self.play(Write(step_five))
        
        with self.voiceover(text="""Finally, we make the optimal assignment. 
                            Each row is assigned to a column where we have a zero.""") as tracker:
            self.wait(tracker.duration)
        
        final_assignments, final_circles = AnimationHelpers.animate_final_assignment(
            self, table, table_data, step_five, restrictions
        )
        
        # --- SUMMARY ---
        total_cost = sum(question_data[r][c] for r, c in final_assignments)
        
        with self.voiceover(text=f"""And we're done! The optimal total cost is {total_cost}. 
                            Thank you for watching this visualization.""") as tracker:
            AnimationHelpers.animate_assignment_summary(
                self, question_table, question_data, final_assignments, final_circles
            )
            self.wait(tracker.duration)


# if __name__ == "__main__":
#     timestamp = int(time.time())
#     file_name = f"assignment_vo_{timestamp}.mp4"
    
#     project_root = os.getcwd()
#     output_dir = os.path.join(project_root, "public", "videos")
#     os.makedirs(output_dir, exist_ok=True)
    
#     config.media_dir = output_dir
#     config.output_file = file_name
#     config.quality = "medium_quality"
#     config.preview = False
#     config.disable_caching = True
    
#     scene = MySceneWithVoiceover()
#     scene.render()
    
#     print(file_name, flush=True)