from manim import *

class AnimationHelpers:
    """
    A class to store helper functions that create specific animations.
    This helps keep the main animation script clean and organized.
    """

    def animate_rope_design(self, load, title1):
        """
        Animates the entire rope design and selection process.

        :Args:
            self (self): The Manim self object to which animations are added.
            data (dict): The dictionary containing data loaded from the JSON file.

        :Return:
            VGroup: A VGroup containing all the Mobjects created in this function.
        """
        # Information text
        rope_text = MathTex(r"\text{Rope Selected: }", r" 6 \times 37 \text{ Wire Rope}").scale(0.7)
        rope_text[1].set_color(GREEN)
        system_text = MathTex(r"\text{System: }", r" 4 \text{ Falls, } 3 \text{ Bends}").scale(0.7)
        system_text[1].set_color(GREEN_D)
        no_of_falls_text= MathTex(r"(\text{No. of Falls},\: N = 4)").scale(0.5)
        class_text = Tex(r"Crane Class: ", r" II (Medium Duty)").scale(0.7)
        class_text[1].set_color(GREEN_E)

        # Group and position the information text
        info_text = VGroup(rope_text, system_text, no_of_falls_text, class_text).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        info_text.next_to(title1, DOWN, buff=0.5).to_edge(LEFT, buff=0.5)

        self.play(Write(info_text))
        self.wait(1)

        # --- Section 2: Design Load Calculation ---
        
        title2 = Tex("Design Load, Q'").scale(0.8)
        title2.next_to(info_text, DOWN, buff=0.75).to_edge(LEFT, buff=0.5)

        # Get initial load from data
        initial_load = load 
        design_load = initial_load * 1.10

        # Create MathTex for the calculation steps
        calc_line1 = MathTex(
            r"\text{Q'}", "=", r"\text{Q}", "+", r"10\% \text{Q}"
        ).scale(0.7)
        calc_line2 = MathTex(
            r"\text{Q'}", "=", f"{initial_load}", "+", fr"(0.10 \times {initial_load})"
        ).scale(0.7)
        calc_line3 = MathTex(
            r"\text{Q'}",f"= {design_load:.2f}", r"\text{ Tonnes}"
        ).scale(0.7)

        # Group and position the calculation
        calc_group = VGroup(calc_line1, calc_line2, calc_line3).arrange(DOWN, aligned_edge=LEFT)
        calc_group.next_to(title2, DOWN, buff=0.2, aligned_edge=LEFT)
        calc_line3.move_to(calc_line2)

        # Animate the calculation process
        self.play(Write(title2))
        self.play(Write(calc_line1))
        self.wait(0.5)
        self.play(TransformMatchingTex(calc_line1.copy(), calc_line2))
        self.wait(0.5)
        self.play(ReplacementTransform(calc_line2, calc_line3))
        self.wait(1)
        
        title3 = Tex("Calculate Breaking Load").scale(0.8)
        title3.next_to(rope_text, RIGHT, buff=0.75)
        # formula from PSG 9.1
        breaking_load_formula = VGroup(
            MathTex(r"P = \frac{F \times \sigma_{u}}{\frac{\sigma_{u}}{n} - ( \frac{d}{D_{min}}\times 36000 )}"),
            Tex("......(From P.S.G 9.1)")
            ).scale(0.7).arrange(RIGHT)
        breaking_load_formula.next_to(title3, DOWN, buff=0.2, aligned_edge=LEFT)
        # Animate Section 3 & 4
        self.play(Write(title3))
        self.play(Write(breaking_load_formula[0]))
        self.wait(0.25)
        self.play(Write(breaking_load_formula[1]))
        self.wait(2)

        # --- Section 3 & 4: Efficiencies and Breaking Load ---
        F_text = MathTex(r"F, \text{load per fall (Tonnes)}").scale(0.65).next_to(breaking_load_formula, DOWN)
        F_formula = MathTex("F", "=", r"\frac{Q'}{N \times \eta_{p} \times \eta_{tr}}").scale(0.75).next_to(F_text, DOWN, buff=0.2)
        self.play(Write(F_text))
        self.wait(0.25)
        self.play(Write(F_formula))
        self.play(Indicate(F_formula[0]), Indicate(breaking_load_formula[0][0][2]))
        
        title4 = Tex("Assuming Efficiencies").scale(0.8).next_to(F_formula, DOWN, buff=0.25)

        eff_text = Tex(r"Pulley $\eta_{p} = 97\%$", r", Transmission $\eta_{tr} = 98\%$").scale(0.7).next_to(title4, DOWN, buff=0.2)

        self.play(Write(title4))
        self.play(Write(eff_text))
        self.play(Indicate(no_of_falls_text), Indicate(F_formula[2][3]))
        self.wait(1)

        t1 = Tex("Substituting values:").scale(0.7).next_to(F_formula, DOWN, buff=0.25, aligned_edge=LEFT)
        F_formula_1 = MathTex("F", "=", f"\\frac{{{design_load:.2f}}}{{4 \\times 0.97 \\times 0.98}}").scale(0.75).move_to(F_formula)
        F_value_tonnes = design_load * 0.2629917
        F_value_kgf = design_load * 0.2629917 * 1000
        F_formula_2 = MathTex(f"F = {F_value_tonnes:.2f}",  r"\text{ Tonnes}").scale(0.75).next_to(F_formula_1, DOWN, buff=0.2, aligned_edge=LEFT)
        F_formula_3 = MathTex(f"F = {F_value_kgf:.2f}",  r"\text{ Kgf}").scale(0.75).next_to(F_formula_1, DOWN, buff=0.2, aligned_edge=LEFT)
        self.play(FadeOut(VGroup(title4, eff_text)))
        self.play(Write(t1))
        self.wait(0.5)
        self.play(TransformMatchingTex(F_formula, F_formula_1))
        self.wait(0.5)
        self.play(FadeOut(t1))
        self.play(Write(F_formula_2))
        self.wait(0.5)
        self.play(TransformMatchingTex(F_formula_2, F_formula_3))
        self.wait(1)
        self.play(FadeOut(F_text), FadeOut(F_formula_1), F_formula_3.animate.next_to(breaking_load_formula, DOWN))
        t2 = MathTex(r"\text{Take }", r"\sigma_{u}", r"= 18000 \text{ kgf}/cm^2 \text{ ..... P.S.G 9.4}").scale(0.6).next_to(F_formula_3, DOWN, buff=0.25, aligned_edge=LEFT)
        self.play(Write(t2))
        self.wait(1)
        t3 = MathTex(r"\text{Design Factor, } n = n' \times \text{duty factor}").scale(0.6).next_to(t2, DOWN, buff=0.25)
        t3_1 = MathTex(r"n' = 5 \text{ for class II Crane} \text{ .....P.S.G 9.1}").scale(0.6).next_to(t3, DOWN).shift(LEFT*0.5)
        t3_2 = Tex("duty factor = 1.2 for class II Crane .....P.S.G 9.2").scale(0.6).next_to(t3_1, DOWN).shift(LEFT*0.5)
        t3_1_1 = MathTex(r"n", "=", r"n'", r"\times", r"\text{ duty factor}").scale(0.6).next_to(t3_2, DOWN).shift(RIGHT*0.75)
        t3_3 = MathTex(r"n", "=", "5", r"\times", "1.2").scale(0.6).next_to(t3_2, DOWN).shift(RIGHT*0.75)
        t3_4 = MathTex(r"n", "=", "6").scale(0.6).next_to(t3_2, DOWN).shift(RIGHT*0.75)

        self.play(Write(t3))
        self.wait(0.1)
        self.play(Write(t3_1), Write(t3_2))
        self.wait(0.1)
        self.play(Write(t3_1_1))
        self.wait(0.25)
        self.play(Indicate(t3_1_1[2], color=PURPLE), Indicate(t3_1[0][0:2], color=PURPLE), Indicate(t3_2[0][0:11], color=GREEN), Indicate(t3_1_1[4], color=GREEN))
        self.play(TransformMatchingTex(t3_1_1, t3_3))
        self.wait(0.1)
        self.play(TransformMatchingTex(t3_3, t3_4))
        self.wait(1)
        self.play(FadeOut(VGroup(t3, t3_1, t3_2)), t3_4.animate.next_to(t2, DOWN))

        t4 = MathTex(r"\frac{D_{min}}{d}", r"= 23 \text{ for 3 bends} \text{ .....P.S.G 9.1}").scale(0.6).next_to(t3_4, DOWN)
        self.play(Write(t4))
        self.play(Indicate(t2[1], color=RED), Indicate(breaking_load_formula[0][0][4:6], color=RED), Indicate(breaking_load_formula[0][0][7:9], color=RED_E))
        self.play(Indicate(t3_4[0], color=BLUE), Indicate(breaking_load_formula[0][0][10], color=BLUE))
        self.play(Indicate(t4[0], color=YELLOW), Indicate(breaking_load_formula[0][0][13:19], color=YELLOW))

        breaking_load_formula_1 = MathTex("P", "=", f"\\frac{{{F_value_kgf:.2f} \\times 18000}}{{\\frac{{18000}}{{6}} - \\frac{{1}}{{23}} \\times 36000 }}").scale(0.75).move_to(breaking_load_formula[0])
        self.play(TransformMatchingTex(breaking_load_formula[0], breaking_load_formula_1))
        self.wait(0.1)
        breaking_load_value_kgf = F_value_kgf*(138/11)
        breaking_load_value_ton = breaking_load_value_kgf/1000
        breaking_load_formula_2 = MathTex("P", "=", f"{breaking_load_value_kgf}", r"\text{ kgf}").scale(0.75).move_to(breaking_load_formula_1)
        breaking_load_formula_3 = MathTex("P", "=", f"{breaking_load_value_ton}", r"\text{ tonnes}").scale(0.75).move_to(breaking_load_formula_1)
        self.play(TransformMatchingTex(breaking_load_formula_1, breaking_load_formula_2))
        self.play(TransformMatchingTex(breaking_load_formula_2, breaking_load_formula_3))
        
        fade_out_grp = VGroup(rope_text,system_text, no_of_falls_text,class_text, title2, calc_group, title3, F_formula_3, t2, t3_4, t4, breaking_load_formula[1], breaking_load_formula_3)
        self.wait(0.75)
        self.play(FadeOut(fade_out_grp))
        return breaking_load_value_ton
    
    def animate_rope_selection_from_table(self, breaking_load_value_ton, psg_data_ropedia, title1):
        """
        Animates the rope diameter selection process from PSG data table.
        
        :Args:
            self (self): The Manim self object to which animations are added.
            breaking_load_value_ton (float): The calculated breaking load in tonnes.
            psg_data_ropedia (DataFrame): DataFrame containing rope diameter and load data.
            title1 (Mobject): The title mobject for positioning reference.
        
        :Return:
            tuple: (selected_rope_dia, selected_load) - The selected rope diameter and its load capacity.
        """
        
        # Title for this section
        title_selection = Tex("Select Rope Diameter from P.S.G 9.4").scale(0.8)
        title_selection.next_to(title1, DOWN, buff=0.5).to_edge(LEFT, buff=0.5)
        self.play(Write(title_selection))
        self.wait(0.5)
        
        # Display the breaking load requirement
        breaking_load_text = MathTex(
            r"\text{Required Breaking Load: }", 
            f"{breaking_load_value_ton:.2f}", 
            r"\text{ tonnes}"
        ).scale(0.7)
        breaking_load_text[1].set_color(YELLOW)
        breaking_load_text.next_to(title_selection, DOWN, buff=0.3).to_edge(LEFT, buff=0.5)
        self.play(Write(breaking_load_text))
        self.wait(0.5)
        
        # Create explanation text
        selection_criteria = Tex(
            r"Selection Criteria: Load Capacity $\geq$ Required Breaking Load"
        ).scale(0.65)
        selection_criteria.next_to(breaking_load_text, DOWN, buff=0.25).to_edge(LEFT, buff=0.5)
        self.play(Write(selection_criteria))
        self.wait(0.5)
        
        # Prepare table data
        table_data = [["Rope Dia (mm)", "Load (Tonnes)"]]  # Header
        for _, row in psg_data_ropedia.iterrows():
            table_data.append([f"{int(row['Rope_Dia_mm'])}", f"{row['Load_Tonnes']:.2f}"])
        
        # Create table with smaller font size to fit screen
        table = Table(
            table_data,
            include_outer_lines=True,
            line_config={"stroke_width": 1},
            element_to_mobject_config={"font_size": 20},
            h_buff=0.5,
            v_buff=0.25
        ).scale(0.65)
        
        # Position table to the right side
        table.next_to(selection_criteria, DOWN, buff=0.5).shift(RIGHT * 2)
        
        # Ensure table doesn't go off screen
        if table.get_bottom()[1] < -3.5:
            table.to_corner(UR, buff=0.25)
        
        self.play(Create(table))
        self.wait(1)
        
        # Highlight header row
        header_rect = SurroundingRectangle(
            VGroup(table.get_rows()[0]), 
            color=BLUE, 
            buff=0.05,
            stroke_width=3
        )
        self.play(Create(header_rect))
        self.wait(0.5)
        
        # Information text for checking process
        checking_text = Tex("Checking each rope...").scale(0.6)
        checking_text.next_to(table.get_bottom(), LEFT, buff=0.3).shift(DOWN*0.5)
        self.play(Write(checking_text))
        self.wait(0.3)
        
        # Iterate through data rows (skip header)
        selected_row_index = None
        selected_rope_dia = None
        selected_load = None
        
        for idx, (df_idx, row) in enumerate(psg_data_ropedia.iterrows(), start=1):
            rope_dia = row['Rope_Dia_mm']
            load_capacity = row['Load_Tonnes']
            
            # Move rectangle to current row
            current_row = table.get_rows()[idx]
            new_rect = SurroundingRectangle(
                current_row, 
                color=BLUE, 
                buff=0.05,
                stroke_width=3
            )
            
            self.play(Transform(header_rect, new_rect), run_time=0.4)
            self.wait(0.3)
            
            # Check condition
            if load_capacity >= breaking_load_value_ton:
                # Condition met - turn green and stop
                green_rect = SurroundingRectangle(
                    current_row, 
                    color=GREEN, 
                    buff=0.05,
                    stroke_width=4
                )
                self.play(
                    Transform(header_rect, green_rect),
                    checking_text.animate.set_color(GREEN)
                )
                
                # Add checkmark
                checkmark = Tex(r"$\checkmark$ Selected!").scale(0.7).set_color(GREEN)
                checkmark.next_to(checking_text, RIGHT, buff=0.3)
                self.play(Write(checkmark))
                
                selected_row_index = idx
                selected_rope_dia = rope_dia
                selected_load = load_capacity
                self.wait(1)
                break
            else:
                # Condition not met - flash red
                red_rect = SurroundingRectangle(
                    current_row, 
                    color=RED, 
                    buff=0.05,
                    stroke_width=3
                )
                self.play(Transform(header_rect, red_rect), run_time=0.3)
                self.wait(0.2)
                
                # Change back to blue before moving to next
                blue_rect = SurroundingRectangle(
                    current_row, 
                    color=BLUE, 
                    buff=0.05,
                    stroke_width=3
                )
                self.play(Transform(header_rect, blue_rect), run_time=0.2)
        
        self.wait(1)
        
        # Fade out everything except the selected row
        rows_to_fade = []
        for i, table_row in enumerate(table.get_rows()):
            if i != selected_row_index:  # Keep header and selected row
                rows_to_fade.append(table_row)
        
        # Also fade out table lines that aren't part of selected/header rows
        fade_group = VGroup(*rows_to_fade, checking_text, checkmark, selection_criteria, table.get_horizontal_lines(), table.get_vertical_lines())
        self.play(FadeOut(fade_group), run_time=0.8)
        self.wait(0.5)
        
        # Create explanation of the selection
        explanation_title = Tex("Selection Summary:").scale(0.75).set_color(BLUE)
        explanation_title.next_to(breaking_load_text, DOWN, buff=0.5).to_edge(LEFT, buff=0.5)
        
        explanation_1 = MathTex(
            r"\text{Selected Rope Diameter: }", 
            r"\; \;", 
            r"\text{ mm}"
        ).scale(0.7)
        
        explanation_2 = MathTex(
            r"\text{Load Capacity: }", 
            f"{selected_load:.2f}", 
            r"\text{ tonnes}"
        ).scale(0.7)
        explanation_2[1].set_color(GREEN)
        
        explanation_3 = MathTex(
            r"\text{Required: }", 
            f"{breaking_load_value_ton:.2f}", 
            r"\text{ tonnes}"
        ).scale(0.7)
        explanation_3[1].set_color(YELLOW)
        
        comparison = MathTex(
            f"{selected_load:.2f}", 
            r"\geq", 
            f"{breaking_load_value_ton:.2f}",
            r"\: \checkmark"
        ).scale(0.7)
        comparison[0].set_color(GREEN)
        comparison[2].set_color(YELLOW)
        comparison[3].set_color(GREEN)
        
        explanation_group = VGroup(
            explanation_1, 
            explanation_2, 
            explanation_3, 
            comparison
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        explanation_group.next_to(explanation_title, DOWN, buff=0.3, aligned_edge=LEFT)
        
        self.play(Write(explanation_title))
        self.play(Write(explanation_1), run_time=0.8)
        self.play(Write(explanation_2), run_time=0.8)
        self.wait(0.5)
        self.play(table.get_rows()[selected_row_index][0].animate.scale(1.3).next_to(explanation_1[0], buff=0.15))
        self.play(Write(explanation_3), run_time=0.8)
        self.wait(0.5)
        self.play(Write(comparison), run_time=0.8)
        self.wait(1)
        
        # Add final note
        safety_note = Tex(
            r"This rope diameter provides adequate safety margin",
            font_size=28
        ).set_color(BLUE_C)
        safety_note.next_to(explanation_group, DOWN, buff=0.4).shift(RIGHT*1.2)
        self.play(FadeIn(safety_note))
        self.wait(2)
        
        # Fade out everything
        final_fade_group = VGroup(
            header_rect,
            breaking_load_text,
            title_selection,
            explanation_title,
            explanation_group,
            safety_note,
            table.get_rows()[selected_row_index]
        )
        self.play(FadeOut(final_fade_group))
        self.wait(0.5)
        
        return selected_rope_dia, selected_load

    def animate_pulley_selection(self, selected_rope_dia, pulley_data, title_ref):
        """
        Animates the selection of a pulley based on the selected rope diameter.

        :Args:
            self (self): The Manim self object.
            selected_rope_dia (float): The diameter of the selected rope.
            pulley_data (DataFrame): DataFrame with pulley dimensions.
            title_ref (Mobject): The title mobject for positioning.

        :Return:
            Series: A pandas Series containing the data of the selected pulley.
        """
        self.play(Write(title_ref))

        # --- 1. Display Input and Criteria ---
        input_dia_text = MathTex(
            r"\text{Selected Rope Diameter: }", f"{selected_rope_dia}", r"\text{ mm}"
        ).scale(0.7)
        input_dia_text[1].set_color(GREEN)
        input_dia_text.next_to(title_ref, DOWN, buff=0.4).to_edge(LEFT, buff=0.5)

        criteria_text = Tex(
            r"Criteria: Select first pulley where Groove Dia. $\geq$ Rope Dia."
        ).scale(0.65)
        criteria_text.next_to(input_dia_text, DOWN, buff=0.25, aligned_edge=LEFT)

        self.play(Write(input_dia_text))
        self.play(Write(criteria_text))
        self.wait(1)

        # --- 2. Find the Correct Pulley Before Animating ---
        selected_pulley_series = pulley_data[pulley_data['RopeDiameter'] >= selected_rope_dia].iloc[0]
        selected_index = selected_pulley_series.name

        # --- 3. Create and Animate the Table ---
        table_data = [pulley_data.columns.to_list()] + pulley_data.astype(str).values.tolist()
        table = Table(
            table_data,
            line_config={"stroke_width": 1, "color": TEAL},
            h_buff=0.3,
        ).scale(0.3) # Scale to fit more columns
        table.next_to(criteria_text, DOWN, buff=0.3).to_edge(RIGHT, buff=0.5)

        self.play(Create(table))
        self.wait(1)

        # --- 4. Animate the Selection Process ---
        scanner = SurroundingRectangle(table.get_rows()[1], color=BLUE, buff=0.1)
        self.play(Create(scanner))

        for i in range(selected_index + 1):
            target_row = table.get_rows()[i + 1] # +1 for header
            self.play(scanner.animate.move_to(target_row), run_time=0.4)
            if i < selected_index:
                self.play(scanner.animate.set_color(RED), run_time=0.2)
                self.wait(0.1)
                self.play(scanner.animate.set_color(BLUE), run_time=0.2)
            else:
                self.play(scanner.animate.set_color(GREEN))
                self.wait(1)

        # --- 5. Display Summary and Visual ---
        rows_to_fade = []
        for i, row in enumerate(table.get_rows()):
            if i != selected_index + 1: # Keep the selected row
                rows_to_fade.append(row)
        
        fade_group = VGroup(*rows_to_fade, criteria_text, table.get_horizontal_lines(), table.get_vertical_lines())
        self.play(FadeOut(fade_group))
        
        # Move selected row and scanner to a better position
        selected_row_group = VGroup(table.get_rows()[selected_index + 1], scanner)
        self.play(selected_row_group.animate.to_edge(RIGHT, buff=1.0).shift(UP*1.5))

        # --- 6. Show Pulley summary ---
        summary_title = Tex("Selected Pulley Dimensions:").scale(0.7)

        summary_text = VGroup(
            MathTex(f"a = {selected_pulley_series['a']} \\text{{ mm}}"),
            MathTex(f"b = {selected_pulley_series['b']} \\text{{ mm}}"),
            MathTex(f"h = {selected_pulley_series['h']} \\text{{ mm}}"),
            MathTex(f"r = {selected_pulley_series['r']} \\text{{ mm}}"),
        ).arrange(DOWN, aligned_edge=LEFT).scale(0.6).next_to(summary_title, DOWN, buff=0.2, aligned_edge=LEFT)

        self.play(Write(summary_title))
        self.play(Write(summary_text))
        self.wait(4)

        # --- 8. Final Fade Out ---
        final_fade_group = VGroup(
            title_ref,
            input_dia_text,
            selected_row_group,
            summary_title,
            summary_text
        )
        self.play(FadeOut(final_fade_group))
        self.wait(0.5)

        return selected_pulley_series

    