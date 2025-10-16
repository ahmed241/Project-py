from manim import *

class AnimationHelpers:
    """
    This class will contain all the custom animation functions
    for the Hungarian algorithm visualization.
    """

    def create_and_show_table(self, table_data, restrictions=None):
        """
        Creates a Manim IntegerTable from a 2D list, animates its creation,
        and returns the table mobject.
        """
        # 1. Determine the dimensions from the data
        num_rows = len(table_data)
        num_cols = len(table_data[0]) if num_rows > 0 else 0

        # 2. Generate row and column labels automatically
        row_labels = [Tex(str(i + 1)) for i in range(num_rows)]
        col_labels = [Tex(str(chr(65 + i))) for i in range(num_cols)] # A, B, C...

        # 3. Create the IntegerTable mobject
        table = IntegerTable(
            table_data,
            row_labels=row_labels,
            col_labels=col_labels,
            h_buff=1.5 # Add more buffer for readability
        ).scale(0.7).shift(DOWN*0.5) # Shift down to make space for header

        # 4. Animate the table's creation
        self.play(FadeIn(table))
        self.wait(1)
        return table

    def animate_square_check(self, table):
        """
        Animates the process of checking if a table is square.
        Returns True if it is, False otherwise.
        """
        # Get the VGroups for data rows and columns (excluding headers/labels)
        data_rows = VGroup(*table.get_rows()[1:])
        data_cols = VGroup(*table.get_columns()[1:])
        num_rows = len(data_rows)
        num_cols = len(data_cols)

        self.play(table.animate.shift(DOWN*0.75))
        # 1. Highlight and count the rows
        row_box = SurroundingRectangle(data_rows, color=BLUE, buff=0.2)
        row_text = Tex(f"Rows = {num_rows}").next_to(row_box, RIGHT)
        self.play(Create(row_box), Write(row_text))
        self.wait(1)

        # 2. Highlight and count the columns
        col_box = SurroundingRectangle(data_cols, color=YELLOW, buff=0.2)
        col_text = Tex(f"Columns = {num_cols}").next_to(col_box, DOWN)
        self.play(Create(col_box), Write(col_text))
        self.wait(1)

        # 3. Display the final result
        is_square = (num_rows == num_cols)
        if is_square:
            result_text = Tex("Matrix is Square (Rows = Columns)", color=GREEN).scale(0.8)
        else:
            result_text = Tex("Matrix is Not Square", color=RED).scale(0.8)
        
        result_text.next_to(table, UP, buff=0.15)
        self.play(Write(result_text))
        self.wait(1.5)

        # 4. Clean up the animation
        self.play(FadeOut(VGroup(row_box, row_text, col_box, col_text, result_text)))
        
        return is_square
    
    def animate_maximization_transform(self, table, data):
        """
        Animates the conversion of a maximization problem to a minimization problem.
        Returns the new data and the new Manim table object.
        """
        # 1. Explain the goal
        explanation = Tex("Maximization Problem:", " Convert to Minimization").scale(0.8).next_to(table, UP, buff=0.65)
        self.play(Write(explanation), table.animate.shift(DOWN*0.75).scale(0.9))
        self.wait(1)

        # 2. Find the maximum value in the matrix
        max_val = 0
        for row in data:
            for val in row:
                if val > max_val:
                    max_val = val
        
        # Animate finding the max value
        max_val_text = Tex(f"Find maximum value: {max_val}").scale(0.8).next_to(explanation, DOWN)
        max_val_cells = VGroup(*[cell for cell in table.get_entries() if isinstance(cell, Integer) and cell.get_value() == max_val])
        self.play(Write(max_val_text))
        self.play(Indicate(max_val_cells, color=ORANGE, scale_factor=1.2))
        self.wait(1)

        # 3. Explain the transformation rule
        rule_text = Tex("New Value", "=", "Max Value", "-", "Old Value", font_size=36).next_to(max_val_text, DOWN)
        rule_text_1 = Tex("New Value", "=", f"{max_val}", "-", "Old Value", font_size=36).next_to(max_val_text, DOWN)
        self.play(Write(rule_text))
        self.wait(1)
        self.play(ReplacementTransform(rule_text, rule_text_1, path_arc=PI/2), rum_time=1.5)

        # 4. Calculate the new data and create the new table
        new_data = [[max_val - val for val in row] for row in data]
        
        # We need a local helper to create the new table correctly
        def create_new_table_from_data(table_data, position):
            n_rows, n_cols = len(table_data), len(table_data[0])
            col_lbls = [Tex(str(chr(65+i))) for i in range(n_cols)]
            row_lbls = [Tex(str(i+1)) for i in range(n_rows)]
            new_table_obj = IntegerTable(table_data, col_labels=col_lbls, row_labels=row_lbls, h_buff=1.5).scale(0.7)
            new_table_obj.move_to(position)
            return new_table_obj

        new_table = create_new_table_from_data(new_data, table.get_center())

        # 5. Animate the transformation and clean up
        self.play(
            ReplacementTransform(table, new_table),
            FadeOut(VGroup(explanation, max_val_text, rule_text_1))
        )
        self.wait(1)
        
        return new_data, new_table
    
    def animate_add_dummies(self, table, data):
        """
        Animates adding dummy rows or columns to balance a non-square matrix.
        Returns the new data and the new Manim table object.
        """
        num_rows = len(data)
        num_cols = len(data[0])
        
        if num_rows == num_cols:
            return data, table # Do nothing if already square

        # 1. Determine the difference and what to add
        if num_rows > num_cols:
            # Add dummy columns
            diff = num_rows - num_cols
            explanation = Tex(f"Adding {diff} dummy column(s) of zeros.").scale(0.7).next_to(table, DOWN)
            
            new_data = [row + [0] * diff for row in data]
            
            # Generate new labels
            new_dim = num_rows
            row_labels = [Tex(str(i+1)) for i in range(new_dim)]
            col_labels = [Tex(str(chr(65+i))) for i in range(num_cols)] + \
                         [Tex(f"Dummy {i+1}") for i in range(diff)]
        else: # num_cols > num_rows
            # Add dummy rows
            diff = num_cols - num_rows
            explanation = Tex(f"Adding {diff} dummy row(s) of zeros.").scale(0.7).next_to(table, DOWN)
            
            new_data = data + [[0] * num_cols for _ in range(diff)]

            # Generate new labels
            new_dim = num_cols
            row_labels = [Tex(str(i+1)) for i in range(num_rows)] + \
                         [Tex(f"Dummy {i+1}") for i in range(diff)]
            col_labels = [Tex(str(chr(65+i))) for i in range(new_dim)]

        self.play(Write(explanation))
        self.wait(1)

        # 2. Create a new, squared table from the new data and labels
        new_table = IntegerTable(
            new_data,
            col_labels=col_labels,
            row_labels=row_labels,
            h_buff=1
        ).scale(0.7).move_to(table)

        # 3. Animate the transformation and clean up
        self.play(FadeOut(explanation))
        self.wait(0.4)
        self.play(TransformMatchingShapes(table, new_table))
        self.wait(1)
        # Wave animation for newly added elements
        if num_rows > num_cols:
            # Wave through new columns
            for col_idx in range(num_cols, len(new_data[0])):
                col_elements = VGroup(*[new_table.get_entries((i+2, col_idx+2)) for i in range(len(new_data))])
                self.play(ApplyWave(col_elements), run_time=0.5)
        else:
            # Wave through new rows
            for row_idx in range(num_rows, len(new_data)):
                row_elements = VGroup(*[new_table.get_entries((row_idx+2, j+2)) for j in range(len(new_data[0]))])
                self.play(ApplyWave(row_elements), run_time=1.5)
        self.wait(1)
        return new_data, new_table

    def animate_row_reduction(self, table, data, restrictions=None):
        """
        Animates row reduction using a two-table view and returns the new data and table.
        Takes a single table as input and creates the comparison view internally.
        """
        # --- 1. Setup the two-table view ---
        # The table on the left is a static reference copy.
        original_table = table.copy()
        # The table on the right is the one we will animate and change.
        processed_table = table
        if len(data[0]) > 4:
            self.play(original_table.animate.scale(0.5))
            self.play(processed_table.animate.scale(0.5))
        else:
            self.play(
                original_table.animate.scale(0.8),
                processed_table.animate.scale(0.9)
            )
        
        self.play(
            original_table.animate.to_edge(LEFT, buff=0.15),
            processed_table.animate.to_edge(RIGHT, buff=1)
        )
        self.wait(0.5)

        # --- 2. Animate the reduction row by row ---
        rows_to_change = processed_table.get_rows()
        new_data = []

        for i in range(len(data)):
            cells_to_change = VGroup(*rows_to_change[i+1][1:])
            current_row_data = data[i]
            
            # Find minimum excluding restricted cells
            min_entry = float('inf')
            for j, val in enumerate(current_row_data):
                if restrictions and restrictions[i][j]:
                    continue  # Skip restricted cells
                if val < min_entry:
                    min_entry = val
            
            # If all cells in row are restricted, skip reduction
            if min_entry == float('inf'):
                continue
            
            row_highlight = SurroundingRectangle(cells_to_change, buff=0.1, color=BLUE)
            self.play(Create(row_highlight), run_time=0.4)
            
            min_entry = min(current_row_data)
            min_cell_col_index = current_row_data.index(min_entry)
            min_cell = original_table.get_rows()[i+1][min_cell_col_index + 1]
            self.play(Indicate(min_cell, color=YELLOW, scale_factor=1.2), run_time=0.6)

            animations = []
            new_row_data = []
            for j, val in enumerate(current_row_data):
                cell_to_transform = cells_to_change[j]
                new_value = val - min_entry
                new_row_data.append(new_value)
                new_mobject = Integer(new_value).move_to(cell_to_transform)
                animations.append(Transform(cell_to_transform, new_mobject))
                
            new_data.append(new_row_data)
            
            if i == 0:
                sub_labels = VGroup(*[Tex(f"-{min_entry}", color=RED).scale(0.6).next_to(c, RIGHT, buff=0.1) for c in cells_to_change])
                self.play(Write(sub_labels), run_time=0.6)
                self.wait(0.4)
                self.play(AnimationGroup(*animations, lag_ratio=0.15))
                self.play(FadeOut(sub_labels), run_time=0.4)
            else:
                self.play(AnimationGroup(*animations, lag_ratio=0.15))
                self.wait(0.4)

            self.play(FadeOut(row_highlight), run_time=0.4)
                
        # --- 3. Cleanup and Return ---
        self.play(FadeOut(original_table))
        self.play(
            processed_table.animate.move_to(ORIGIN).shift(DOWN*1.5)
        )
        return new_data, processed_table
    
    def animate_column_reduction(self, table, data, restrictions=None):
        """
        Animates the column reduction process and returns the new data and table.
        """
        # Create a copy of the data to modify
        new_data = [row[:] for row in data]
        num_rows = len(new_data)
        num_cols = len(new_data[0])

        # Create a highlight rectangle to move across columns
        highlight_rect = SurroundingRectangle(VGroup(*table.get_columns()[1][1:]), color=BLUE)
        self.play(Create(highlight_rect))
        for i in range(len(data)):
            current_row_data = data[i]
            
            # Find minimum excluding restricted cells
            min_entry = float('inf')
            for j, val in enumerate(current_row_data):
                if restrictions and restrictions[i][j]:
                    continue  # Skip restricted cells
                if val < min_entry:
                    min_entry = val
            
            # If all cells in row are restricted, skip reduction
            if min_entry == float('inf'):
                continue

        for j in range(num_cols):
            # Move highlight to the current column
            col_cells_to_highlight = VGroup(*table.get_columns()[j+1][1:])
            self.play(highlight_rect.animate.move_to(col_cells_to_highlight))
            
            # Get column values from our reliable data list
            column_values = [new_data[i][j] for i in range(num_rows)]
            has_zero = 0 in column_values

            if has_zero:
                # If a zero is present, the column is fine
                self.play(highlight_rect.animate.set_color(GREEN))
                self.wait(0.5)
            else:
                # If no zero, perform reduction
                self.play(highlight_rect.animate.set_color(RED))
                
                # Find the minimum value
                min_entry = min(column_values)
                min_row_index = column_values.index(min_entry)
                min_cell = table.get_rows()[min_row_index + 1][j + 1]
                self.play(Indicate(min_cell, color=ORANGE, scale_factor=1.2))
                
                # Animate the subtraction for each cell in the column
                animations = []
                for i in range(num_rows):
                    cell_to_change = table.get_rows()[i+1][j+1]
                    new_value = new_data[i][j] - min_entry
                    new_data[i][j] = new_value # Update our data list
                    
                    new_mobject = Integer(new_value).move_to(cell_to_change)
                    animations.append(Transform(cell_to_change, new_mobject))
                
                self.play(AnimationGroup(*animations, lag_ratio=0.15))
                self.play(highlight_rect.animate.set_color(GREEN)) # Show the column is now fixed

        # Clean up and return the final results
        self.play(FadeOut(highlight_rect))
        self.wait()
        self.play(table.animate.move_to(ORIGIN).shift(DOWN*0.25))
        return new_data, table
    
    def animate_line_drawing(self, table, rows_to_cover, cols_to_cover):
        """
        Animates drawing horizontal and vertical lines over the specified
        rows and columns of a table.
        
        Returns the VGroup of lines and the total number of lines drawn.
        """
        lines = VGroup()
        line_config = {"color": YELLOW, "stroke_width": 3, "stroke_opacity": 0.75}
        self.wait(0.5)
        
        # Get table dimensions for accurate line drawing
        num_data_rows = len(table.get_rows()) - 1
        num_data_cols = len(table.get_columns()) - 1

        # Create horizontal lines
        for r_idx in rows_to_cover:
            # Get the first and last cells of the data row to define line boundaries
            left_cell = table.get_cell((r_idx + 2, 2))
            right_cell = table.get_cell((r_idx + 2, num_data_cols + 1))
            
            line = Line(
                left_cell.get_left() + 0.3 * LEFT,
                right_cell.get_right() + 0.3 * RIGHT,
                **line_config
            )
            lines.add(line)

        # Create vertical lines
        for c_idx in cols_to_cover:
            # Get the first and last cells of the data column
            top_cell = table.get_cell((2, c_idx + 2))
            bottom_cell = table.get_cell((num_data_rows + 1, c_idx + 2))

            line = Line(
                top_cell.get_top() + 0.3 * UP,
                bottom_cell.get_bottom() + 0.3 * DOWN,
                **line_config
            )
            lines.add(line)
            
        self.play(Create(lines, lag_ratio=0.4))
        self.wait(1)
        
        return lines
    
    def animate_matrix_adjustment(self, table, data, covered_rows, covered_cols, lines):
        """
        Animates the matrix adjustment process by transforming individual cell entries
        in-place, using the user's preferred animation style.
        """
        # --- Step 1: Identify cell categories and find the minimum value ---
        new_data = [row[:] for row in data]
        n = len(data)
        uncovered_values = []
        uncovered_cells = VGroup() # Used for highlighting
        intersection_cells = VGroup()

        for r in range(n):
            for c in range(n):
                is_row_covered = r in covered_rows
                is_col_covered = c in covered_cols
                
                if not is_row_covered and not is_col_covered:
                    uncovered_values.append(data[r][c])
                    uncovered_cells.add(table.get_cell((r + 2, c + 2)))
                
                if is_row_covered and is_col_covered:
                    intersection_cells.add(table.get_cell((r + 2, c + 2)))

        if not uncovered_values:
            return data, table 

        min_val = min(uncovered_values)
        print(f"DEBUG: Minimum uncovered value is {min_val}")
        
        # --- Step 2: Animate the explanation (using your custom layout) ---
        explanation1 = Tex("Find smallest ", f"uncovered value: {min_val}").scale(0.7).next_to(table, UP, buff=1.55)
        explanation1[1].set_color(BLUE)
        highlight_boxes = VGroup(*[SurroundingRectangle(cell, color=BLUE, buff=-0.15) for cell in uncovered_cells])

        
        self.play(Write(explanation1))
        self.play(Create(highlight_boxes))
        min_val_location = None
        for r in range(len(data)):
            for c in range(len(data[0])):
                # Check if the cell is uncovered
                if not (r in covered_rows or c in covered_cols):
                    # Check if this uncovered cell has the minimum value
                    if data[r][c] == min_val:
                        min_val_location = (r, c)
                        break
            if min_val_location:
                break
        
        # Now, get the guaranteed correct position from the table using the indices
        target_position = table.get_cell((min_val_location[0] + 2, min_val_location[1] + 2)).get_center()
        self.play(Flash(target_position, color=ORANGE, flash_radius=0.7))
        self.wait(1)
        explanation2 = Tex(f"Subtract {min_val} from ", "uncovered cells ", rf"\\add {min_val} to ", "intersection cells.").scale(0.7).next_to(explanation1, DOWN)
        explanation2[1].set_color(BLUE)
        explanation2[3].set_color(PURPLE)
        self.play(Write(explanation2))
        self.wait(1.5)

        highlight_intersection = VGroup(*[SurroundingRectangle(cell, color=PURPLE, buff=-0.15) for cell in intersection_cells])
        self.play(Create(highlight_intersection))
        

        # --- Step 3: Animate the in-place transformations targeting the ENTRIES ---
        # Store animations and cells to update
        animations = []
        cells_to_update = []

        # Prepare animations for uncovered cells (subtraction)
        for r in range(n):
            for c in range(n):
                if not (r in covered_rows or c in covered_cols):
                    new_value = data[r][c] - min_val
                    new_data[r][c] = new_value
                    
                    # Get the entry and change its value directly
                    entry = table.get_entries((r + 2, c + 2))
                    entry.set_value(new_value)
                    
        for r, c in [(r, c) for r in covered_rows for c in covered_cols]:
            new_value = data[r][c] + min_val
            new_data[r][c] = new_value
            
            entry = table.get_entries((r + 2, c + 2))
            entry.set_value(new_value)

        # Play all changes at once
        if animations:
            self.play(AnimationGroup(*animations, lag_ratio=0.1))

        # Cleanup
        self.play(FadeOut(VGroup(explanation1, explanation2, highlight_boxes, lines, highlight_intersection)))
        
        return new_data, table
    
    def animate_final_assignment(self, table, data, header, restrictions=None):
        """
        Animates the assignment process using a simple, sequential scan of rows
        and then columns, including cross-out animations.
        """
        # --- Phase 1: Setup ---
        explanation_text = Tex("Starting Assignment Process...").scale(0.7).next_to(header, DOWN, buff=0.1)
        self.play(Write(explanation_text))
        self.wait(0.5)

        available_zeros = {
        (r, c) for r, row in enumerate(data) 
        for c, val in enumerate(row) 
        if val == 0 and not (restrictions and restrictions[r][c])  # Exclude restricted
    }
        assignments = []
        assigned_circles = VGroup()
        crossed_out_marks = VGroup()
        n = len(data)

        # --- Phase 2: Row Scan ---
        new_text = Tex("Scanning rows for unique zeros...").scale(0.7).next_to(header, DOWN, buff=0.1)
        self.play(ReplacementTransform(explanation_text, new_text))
        explanation_text = new_text

        for r in range(n):
            zeros_in_row = {loc for loc in available_zeros if loc[0] == r}
            if len(zeros_in_row) == 1 and len(assignments) < n - 1:
                (r_assign, c_assign) = zeros_in_row.pop()
                
                found_row = Tex(f"Found a unique zero at row {r_assign+1}").scale(0.7).next_to(new_text, DOWN, buff=0.25)
                cell = table.get_cell((r_assign + 2, c_assign + 2))
                circle = Circle(color=GREEN, stroke_width=3).surround(cell, buffer_factor=-0.15)
                self.play(Write(found_row))
                self.wait(0.5)
                self.play(Create(circle))
                
                assignments.append((r_assign, c_assign))
                assigned_circles.add(circle)
                available_zeros.discard((r_assign, c_assign))

                # Cross out other zeros in the assigned column
                zeros_to_cross = {loc for loc in available_zeros if loc[1] == c_assign}
                if zeros_to_cross:
                    cross_text = Tex(f"Crossing out other zeros in the same column and row").scale(0.7).next_to(found_row, DOWN, buff=0.1)
                    crosses = VGroup(*[Cross(table.get_cell((rc[0]+2, rc[1]+2)), stroke_width=3, scale_factor=0.75) for rc in zeros_to_cross])
                    self.play(Write(cross_text))
                    self.wait(0.5)
                    self.play(Create(crosses))
                    self.play(FadeOut(found_row))
                    self.play(FadeOut(cross_text))
                    crossed_out_marks.add(crosses)
                    available_zeros -= zeros_to_cross
                
                else:
                    no_cross_text = Tex(f"No other zeros to cross out in row {r_assign+1} and column {c_assign+1}").scale(0.7).next_to(found_row, DOWN, buff=0.1)
                    self.play(Write(no_cross_text))
                    self.wait(0.75)
                    self.play(FadeOut(found_row))
                    self.play(FadeOut(no_cross_text))
        
        # --- Phase 3: Column Scan ---
        new_text = Tex("Scanning columns for unique zeros...").scale(0.7).next_to(header, DOWN, buff=0.1)
        self.play(ReplacementTransform(explanation_text, new_text))
        explanation_text = new_text
        
        for c in range(n):
            zeros_in_col = {loc for loc in available_zeros if loc[1] == c}
            if len(zeros_in_col) == 1 and len(assignments) < n - 1:
                (r_assign, c_assign) = zeros_in_col.pop()

                found_col = Tex(f"Found a unique zero at column {chr(c_assign+65)}").scale(0.7).next_to(new_text, DOWN, buff=0.25)
                self.play(Write(found_col))
                self.wait(0.5)
                cell = table.get_cell((r_assign + 2, c_assign + 2))
                circle = Circle(color=GREEN, stroke_width=3).surround(cell, buffer_factor=-0.15)
                self.play(Create(circle))
                
                assignments.append((r_assign, c_assign))
                assigned_circles.add(circle)
                available_zeros.discard((r_assign, c_assign))

                # Cross out other zeros in the assigned row
                zeros_to_cross = {loc for loc in available_zeros if loc[0] == r_assign}
                if zeros_to_cross:
                    cross_text = Tex(f"Crossing out other zeros in the same row and column").scale(0.7).next_to(found_col, DOWN, buff=0.1)
                    self.play(Write(cross_text))
                    self.wait(0.5)
                    self.play(FadeOut(found_col))
                    self.play(FadeOut(cross_text))
                    crosses = VGroup(*[Cross(table.get_cell((rc[0]+2, rc[1]+2)), stroke_width=3, scale_factor=0.75) for rc in zeros_to_cross])
                    self.play(Create(crosses))
                    crossed_out_marks.add(crosses)
                    available_zeros -= zeros_to_cross
                else:
                    no_cross_text = Tex(f"No other zeros to cross out in row {r_assign+1} and column {chr(c_assign+65)}").scale(0.7).next_to(found_col, DOWN, buff=0.1)
                    self.play(Write(no_cross_text))
                    self.wait(0.75)
                    self.play(FadeOut(found_col))
                    self.play(FadeOut(no_cross_text))

        # --- Phase 4: Assign any remaining zeros (for cases with multiple solutions) ---
        if len(assignments) < n and available_zeros:
            new_text = Tex(r" As only one zero is left \\ Assigning remaining zero...").scale(0.7).next_to(header, DOWN, buff=0.5)
            self.play(ReplacementTransform(explanation_text, new_text))
            explanation_text = new_text
            
            assigned_rows = {a[0] for a in assignments}
            assigned_cols = {a[1] for a in assignments}

            for r_assign, c_assign in sorted(list(available_zeros)):
                if r_assign not in assigned_rows and c_assign not in assigned_cols:
                    cell = table.get_cell((r_assign + 2, c_assign + 2))
                    circle = Circle(color=GREEN, stroke_width=3).surround(cell, buffer_factor=-0.15)
                    self.play(Create(circle))
                    assignments.append((r_assign, c_assign))
                    assigned_rows.add(r_assign)
                    assigned_cols.add(c_assign)
                    assigned_circles.add(circle)

        # --- Phase 5: Final Result ---
        new_text = Tex("Optimal Assignment Found!").scale(0.7).move_to(explanation_text)
        self.play(ReplacementTransform(explanation_text, new_text))
        if len(crossed_out_marks) > 0:
            self.play(FadeOut(crossed_out_marks))
        self.wait(2)

        return assignments, assigned_circles
    def animate_assignment_summary(self, table, original_data, assignments, circles):
        """
        Animates a final summary, showing the assignments in text form
        and calculating the total cost from the original matrix.
        """
        # 1. Create the text for the final assignment list
        summary_header = Tex("Final Assignment:").scale(0.8)
        summary_lines = VGroup()
        
        # Sort assignments by row for a clean 1, 2, 3... order
        sorted_assignments = sorted(assignments, key=lambda x: x[0])

        num_rows = len(original_data)
        num_cols = len(original_data[0]) if num_rows > 0 else 0
        row_labels_text = [str(i + 1) for i in range(num_rows)]
        col_labels_text = [str(chr(65 + i)) for i in range(num_cols)]

        for r, c in sorted_assignments:
            line_text = Tex(f"{row_labels_text[r]} $\\rightarrow$ {col_labels_text[c]}", font_size=36)
            summary_lines.add(line_text)
        
        summary_lines.arrange(DOWN, buff=0.2, aligned_edge=LEFT)
        summary_vgroup = VGroup(summary_header, summary_lines).arrange(DOWN, buff=0.4).to_edge(RIGHT, buff=0.5).shift(DOWN*0.5)
        
        # 2. Add Summary Group
        self.play(Write(summary_vgroup))
        self.wait(1)

        # 3. Animate the cost calculation
        cost_header = Tex("Optimal Cost:", font_size=40).next_to(table.get_bottom(), DOWN, buff=0.1, aligned_edge=LEFT).to_edge(LEFT, buff=0.5)
        
        # Get the costs from the ORIGINAL data matrix
        costs = [original_data[r][c] for r, c in assignments]
        cost_sum_str = " + ".join(map(str, costs))
        
        cost_sum_tex = Tex(cost_sum_str, font_size=40)
        total_cost_tex = Tex(f"= {sum(costs)}", font_size=48, color=YELLOW)
        
        cost_line = VGroup(cost_sum_tex, total_cost_tex).arrange(RIGHT, buff=0.2)
        cost_line.next_to(cost_header, RIGHT, buff=0.3)

        self.play(Write(cost_header))
        self.wait(0.5)
        self.play(Write(cost_sum_tex))
        self.wait(0.5)
        self.play(Write(total_cost_tex))
        self.wait(2)