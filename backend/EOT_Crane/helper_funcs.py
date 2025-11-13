from manim import *
from MF_Tools import TransformByGlyphMap

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
        return breaking_load_value_ton, F_value_kgf
    
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

    def animate_axle_design(self, selected_pulley, load_per_fall, title_ref):
        """
        Animates the free-body diagram and length calculation for the pulley axle.

        :Args:
            self (self): The Manim self object.
            selected_pulley (Series): The pandas Series for the selected pulley.
            title_ref (Mobject): The title mobject for positioning.
        :Return:
            VGroup: A VGroup containing all the Mobjects from this animation.
        """
        self.play(Write(title_ref))
        self.wait(0.5)

        # 1. Create the Beam Diagram
        diagram_group = VGroup()
        
        # Draw the beam
        beam = Line(LEFT * 5, RIGHT * 5, color=BLUE, stroke_width=6)
        self.next_section(skip_animations=True)
        # Supports (Reactions)
        support_L = Arrow(LEFT * 5 + DOWN, LEFT * 5, buff=0, color=WHITE)
        support_R = Arrow(RIGHT * 5 + DOWN, RIGHT * 5, buff=0, color=WHITE)
        support_L_tex = MathTex(r"R_1", r"(=2F)").scale(0.7).next_to(support_L, DOWN, buff=0.15)
        support_R_tex = MathTex(r"R_2", r"(=2F)").scale(0.7).next_to(support_R, DOWN, buff=0.15)
        
        # Point Loads
        load_L = Arrow(LEFT * 2.5 + UP, LEFT * 2.5, buff=0, color=YELLOW)
        load_R = Arrow(RIGHT * 2.5 + UP, RIGHT * 2.5, buff=0, color=YELLOW)
        load_L_tex = MathTex(r"2F").scale(0.7).next_to(load_L, UP, buff=0.15)
        load_R_tex = MathTex(r"2F").scale(0.7).next_to(load_R, UP, buff=0.15)
        
        diagram_group.add(
            beam, support_L, support_R, support_L_tex, support_R_tex,
            load_L, load_R, load_L_tex, load_R_tex
        )
        
        # 2. Create Dimensions
        dim_L1 = DoubleArrow(LEFT * 2.5, RIGHT * 2.5, tip_length=0.15, buff=0).set_stroke(WHITE, 1.75).shift(DOWN * 0.75)
        dim_L1_tex = MathTex(r"L_1").scale(0.8).next_to(dim_L1, DOWN)
        
        dim_L2_left = DoubleArrow(LEFT * 5, LEFT * 2.5, tip_length=0.2, buff=0).set_stroke(WHITE, 1.75).shift(DOWN * 0.75)
        dim_L2_left_tex = MathTex(r"L_2").scale(0.8).next_to(dim_L2_left, DOWN)
        
        dim_L2_right = DoubleArrow(RIGHT * 2.5, RIGHT * 5, tip_length=0.2, buff=0).set_stroke(WHITE, 1.75).shift(DOWN * 0.75)
        dim_L2_right_tex = MathTex(r"L_2").scale(0.8).next_to(dim_L2_right, DOWN)
        
        diagram_group.add(
            dim_L1, dim_L1_tex, dim_L2_left, dim_L2_left_tex, dim_L2_right, dim_L2_right_tex
        )
        
        # Animate drawing the diagram
        self.play(LaggedStart(
            Create(beam),
            GrowArrow(support_L), GrowArrow(support_R), Write(support_L_tex), Write(support_R_tex),
            GrowArrow(load_L), GrowArrow(load_R), Write(load_L_tex), Write(load_R_tex),
            lag_ratio=0.25
        ))
        self.wait(0.5)
        self.play(LaggedStart(
            GrowArrow(dim_L1), Write(dim_L1_tex),
            GrowArrow(dim_L2_left), Write(dim_L2_left_tex),
            GrowArrow(dim_L2_right), Write(dim_L2_right_tex),
            lag_ratio=0.25
        ))
        self.wait(1)
        self.play(diagram_group.animate.scale(0.5).next_to(title_ref, DOWN, buff=0.2))
        # 3. Show Formulas for L1 and L2
        pulley_a_val = selected_pulley['a']
        
        # Get 'a' value from the selected pulley
        formula_title = Tex("From PSG 9.10:").scale(0.7).next_to(diagram_group, DOWN, buff=0.1).shift(LEFT*2)
        pulley_a_tex = MathTex(r"\text{Pulley width } a", f" = {pulley_a_val} \\text{{ mm}}").scale(0.7)
        pulley_a_tex[1].set_color(GREEN)
        pulley_a_tex.next_to(formula_title, RIGHT, buff=0.2)
        
        # Formulas
        formula_L1 = MathTex(r"L_1", r"\text{ (dist. b/w pulleys)}", r" = 35 \text{ mm (assumed)}").scale(0.7)
        formula_L1.next_to(pulley_a_tex, DOWN, buff=0.2, aligned_edge=LEFT)
        
        formula_L2 = MathTex(r"L_2", r"\text{ (dist. shackle-pulley)}", r" = 30 \text{ mm (assumed)}").scale(0.7)
        formula_L2.next_to(formula_L1, DOWN, buff=0.2, aligned_edge=LEFT)

        formula_group = VGroup(formula_title, pulley_a_tex, formula_L1, formula_L2)

        self.play(Write(formula_title))
        self.play(Write(pulley_a_tex))
        self.wait(0.5)
        self.play(Write(formula_L1))
        self.play(Write(formula_L2))
        self.wait(1)
        
        # Link formulas to diagram
        self.play(
            Indicate(VGroup(dim_L1, formula_L1[0]), 1.05, LIGHT_PINK),
            Indicate(VGroup(dim_L2_left, dim_L2_right, formula_L2[0]), 1.05, BLUE)
        )
        self.wait(0.5)
        
        # --- Axle Length Calculation ---
        
        # Define values
        t1_val = int(30)
        l1_val = int(35)
        l2_val = int(30)
        a_val = int(pulley_a_val)
        
        # Calculate final length
        l_final_val = (2 * (t1_val / 2)) + l2_val + a_val + l1_val + a_val + l2_val

        # Create MathTex
        t1_tex = MathTex(r"t_1", r"\text{ (shackle thickness)}", r" = 30 \text{ mm (assumed)}").scale(0.7)
        t1_tex.next_to(formula_L2, DOWN, buff=0.2, aligned_edge=LEFT)
        
        l_formula_tex = MathTex(
            r"L", r" = 2 \times \frac{t_1}{2} + L_2 + a + L_1 + a + L_2"
        ).scale(0.7)
        l_formula_tex.next_to(t1_tex, DOWN, buff=0.5, aligned_edge=LEFT)
        
        l_sub_tex = MathTex(
            r"L", r" = 2 \cdot", f"({t1_val / 2}) + {l2_val} + {a_val} + {l1_val} + {a_val} + {l2_val}"
        ).scale(0.7)
        l_sub_tex.next_to(l_formula_tex, DOWN, buff=0.2, aligned_edge=LEFT)
        
        l_final_tex = MathTex(r"L", f" = {l_final_val} \\text{{ mm}}").scale(0.8)
        l_final_tex[1].set_color(GREEN)
        l_final_tex.move_to(l_sub_tex, aligned_edge=LEFT)

        length_calc_group = VGroup(t1_tex, l_formula_tex, l_sub_tex, l_final_tex)
        
        # Animate the calculation
        self.play(Write(t1_tex))
        self.wait(0.5)
        self.play(Write(l_formula_tex))
        self.wait(0.5)
        self.play(TransformMatchingTex(l_formula_tex.copy(), l_sub_tex))
        self.wait(0.5)
        self.play(ReplacementTransform(l_sub_tex, l_final_tex))
        self.wait(1)
        
        self.play(FadeOut(VGroup(formula_title, pulley_a_tex, formula_L1, t1_tex, formula_L2, l_formula_tex)), l_final_tex.animate.next_to(diagram_group, DOWN, buff=0.25))
        F_newtons = load_per_fall * 10
        two_F_newtons = 2 * load_per_fall * 10
        two_F_tex = MathTex("2 ", r"\times", " F", "=").scale(0.75).next_to(l_final_tex, DOWN, buff=0.5)
        two_f_tex_right = MathTex("2 ", r"\times", " F").scale(0.75).next_to(two_F_tex, RIGHT)
        two_F_tex_2 = MathTex("2 ", r"\times", f" {F_newtons}").scale(0.75).move_to(two_f_tex_right, aligned_edge=LEFT)
        final_F_tex = MathTex(f"{two_F_newtons}", r"\text{ N}").scale(0.75).move_to(two_F_tex_2, aligned_edge=LEFT)

        self.play(Write(two_F_tex))
        self.play(Write(two_f_tex_right))
        self.wait(0.5)
        self.play(TransformMatchingTex(two_f_tex_right, two_F_tex_2, transform_mismatches=True))
        self.wait(0.5)
        self.play(ReplacementTransform(two_F_tex_2, final_F_tex))
        self.wait(0.5)
        self.play(l_final_tex.animate.to_edge(LEFT, buff=0.75))
        self.play(VGroup(final_F_tex, two_F_tex).animate.next_to(l_final_tex, RIGHT, buff=0.5))

        bend_tex = Tex("Maximum Bending Moment, ", r"$\text{[BM]}_{max}$").next_to(final_F_tex, DOWN, buff=0.5).shift(RIGHT*2)
        bend_formula = MathTex(r"\text{$[BM]_{max}$ } ", " = ", "2 ", r"\times", " F", r"\times [ \frac{t_1}{2} + \frac{a}{2} + L_2 ]").next_to(bend_tex, DOWN, buff=0.5)
        bend_formula_sub = MathTex(r"\text{$[BM]_{max}$ } ", " = ", "2 ", r"\times", f" {F_newtons} \\times", f" [ \\frac{{{t1_val}}}{{2}} + \\frac{{{a_val}}}{{2}} + {l1_val} ]").next_to(bend_tex, DOWN, buff=0.5)
        bend_val = two_F_newtons * (50 + a_val)
        bend_formula_final = MathTex(r"\text{$[BM]_{max}$} ", " = ", f"{bend_val}", r"\text{ $N\cdot mm $}").next_to(bend_tex, DOWN, buff=0.5)

        self.play(Write(bend_tex))
        self.wait()
        self.play(ReplacementTransform(bend_tex[1], bend_formula[0]))
        self.wait(0.5)
        self.play(Write(bend_formula[1:]))
        self.wait()
        self.play(ReplacementTransform(bend_formula, bend_formula_sub))
        self.wait(0.5)
        self.next_section()
        self.play(ReplacementTransform(bend_formula_sub, bend_formula_final))
        self.wait(0.5)
        self.play(l_final_tex.animate.to_corner(UL, buff=0.15))
        self.play(VGroup(final_F_tex, two_F_tex).animate.next_to(l_final_tex, DOWN, buff=0.25, aligned_edge=LEFT))
        self.play(FadeOut(bend_tex[0]))
        self.play(bend_formula_final.animate.scale(0.5).next_to(two_F_tex, DOWN, buff=0.25, aligned_edge=LEFT))

        # 1. Define Material and Stresses
        material_title = Tex("Material Selection:", " C40 Steel (PSG 1.9)").scale(0.7)
        material_title.next_to(bend_tex[0], DOWN, buff=0.4).to_edge(LEFT)
        
        sigma_y_tex = MathTex(r"\sigma_y = 330 \text{ N/mm}^2").scale(0.7)
        sigma_y_tex.next_to(material_title, DOWN, buff=0.2, aligned_edge=LEFT)
        
        sigma_t_formula = MathTex(r"\sigma_t = \frac{\sigma_y}{\text{FOS}}").scale(0.7)
        sigma_t_formula.next_to(sigma_y_tex, DOWN, buff=0.2, aligned_edge=LEFT)
        
        # Position substitution and final value on top of each other
        sigma_t_sub = MathTex(r"\sigma_t = \frac{330}{3}").scale(0.7)
        sigma_t_sub.align_to(sigma_t_formula, LEFT)
        
        fos_assume = Tex("Assume FOS = 3").scale(0.6).next_to(sigma_t_sub, RIGHT, buff=0.5)
        
        sigma_t_final = MathTex(r"\sigma_t = 110 \text{ N/mm}^2").scale(0.7)
        sigma_t_final.align_to(sigma_t_sub, LEFT)

        # Animate material selection
        self.play(Write(material_title))
        self.play(Write(sigma_y_tex))
        self.play(Write(sigma_t_formula))
        self.wait(0.5)
        self.play(
            TransformMatchingTex(sigma_t_formula.copy(), sigma_t_sub), 
            Write(fos_assume)
        )
        self.wait(0.5)
        self.play(
            FadeOut(fos_assume),
            ReplacementTransform(sigma_t_sub, sigma_t_final), 
        )
        self.wait(1)
        self.play(
            FadeOut(sigma_t_formula),
            FadeOut(sigma_y_tex),
            FadeOut(material_title)
        )

        # 2. Bending Equation and Z derivation
        bending_eq_title = Tex("Bending Equation:").scale(0.7)
        bending_eq_title.next_to(sigma_t_final, DOWN, buff=0.4, aligned_edge=LEFT)
        
        bending_eq = VGroup(MathTex(r"\sigma_b = \frac{M}{Z}"), MathTex(r"\quad \Rightarrow \quad"), MathTex(r"M = \sigma_b \times Z")).scale(0.7).arrange(RIGHT)
        bending_eq.next_to(bending_eq_title, DOWN, buff=0.2, aligned_edge=LEFT)
        
        bending_eq_note = MathTex(r"(\text{Allowable } \sigma_b = \sigma_t = 110 \text{ N/mm}^2)").scale(0.6)
        bending_eq_note.next_to(bending_eq, DOWN, buff=0.2, aligned_edge=LEFT)

        # Z-derivation on the right side
        z_title = Tex("For solid circular shaft:").scale(0.7).to_edge(RIGHT, buff=0.5).shift(UP*1.0)
        z_deriv_1 = MathTex(r"Z = \frac{I}{y}").scale(0.7)
        z_deriv_2 = MathTex(r"Z = \frac{\frac{\pi}{64} \cdot d^4}{\frac{d}{2}}").scale(0.7)
        z_deriv_3 = MathTex(r"Z = \frac{\pi}{32} d^3").scale(0.7)
        z_group = VGroup(z_deriv_1, z_deriv_2, z_deriv_3).arrange(DOWN, aligned_edge=LEFT)
        z_group.next_to(z_title, DOWN, buff=0.2)
        z_brace = Brace(z_group, direction=LEFT)

        self.play(Write(bending_eq_title))
        self.play(Write(bending_eq))
        self.play(Write(bending_eq_note))
        self.wait(0.5)

        self.play(Write(z_title))
        self.play(Write(z_deriv_1), DrawBorderThenFill(z_brace))
        self.wait(0.5)
        self.play(TransformMatchingTex(z_deriv_1.copy(), z_deriv_2))
        self.wait(0.5)
        self.play(TransformFromCopy(z_deriv_2, z_deriv_3))
        self.wait(1)

        # 3. Substitute Z into the formula
        m_formula_z = MathTex(r"M", "=", r"\sigma_b", r"\times", r"\frac{\pi}{32}", r"d^3").scale(0.7)
        m_formula_z.move_to(bending_eq[2], LEFT)
        
        self.play(Indicate(z_deriv_3, scale_factor=1.2, color=YELLOW))
        self.play(TransformMatchingTex(bending_eq[2], m_formula_z, key_map={"M": "M", "=": "=", r"\sigma_b": r"\sigma_b"}))
        self.wait(1)

        # 4. Substitute values and solve for d
        # This uses the 'bend_val' from your previous code block.
        # It assumes bend_val is the number 3138750 from the image.
        M_val = int(bend_val) 
        sigma_b_val = 110
        
        final_sub = MathTex(f"{M_val}", rf" = {sigma_b_val} \times \frac{{\pi}}{{32}} d^3").scale(0.7)
        final_sub.move_to(bending_eq[2], LEFT)

        d_cubed_formula = MathTex(r"d^3 = \frac{" + f"{M_val}" + r" \times 32}{" + f"{sigma_b_val}" + r" \times \pi}").scale(0.7)
        d_cubed_formula.move_to(bending_eq[2], LEFT)
        
        d_cubed_val = (M_val * 32) / (sigma_b_val * PI)
        d_cubed_result = MathTex(f"d^3 = {d_cubed_val:.1f}").scale(0.7)
        d_cubed_result.move_to(bending_eq[2], LEFT)
        d_formula = MathTex(r"d = \sqrt[3]{" + f"{d_cubed_val:.1f}" + r"}").scale(0.7)
        d_formula.move_to(bending_eq[2], LEFT)
        
        d_final_val = d_cubed_val**(1/3)
        d_final = MathTex(f"d = {d_final_val:.2f} \\text{{ mm}}").scale(0.8)
        d_final[0][0].set_color(GREEN) # d
        d_final[0][2:].set_color(GREEN) # 66.24 mm
        d_final.move_to(bending_eq[2], LEFT)

        self.play(
            Indicate(bend_formula_final, scale_factor=1.2, color=BLUE),
            Indicate(sigma_t_final, scale_factor=1.2, color=YELLOW)
        )
        self.play(TransformMatchingTex(m_formula_z, final_sub))
        self.wait(1)
        self.play(TransformMatchingShapes(final_sub, d_cubed_formula))
        self.wait(0.5)
        self.play(ReplacementTransform(d_cubed_formula, d_cubed_result))
        self.wait(0.5)
        self.play(ReplacementTransform(d_cubed_result, d_formula))
        self.wait(0.5)
        self.play(ReplacementTransform(d_formula, d_final))
        
        self.play(Create(SurroundingRectangle(d_final, color=GREEN, buff=0.1)))
        self.wait(3)

        # Group all mobjects created in this step
        calc_group = VGroup(
            material_title, sigma_y_tex, sigma_t_formula, sigma_t_final,
            bending_eq_title, bending_eq, bending_eq_note,
            z_title, z_group, z_brace,
            m_formula_z, final_sub, d_final
        )
        
        # Fade out everything from this step and the previous Bending Moment step
        self.wait(1)

        # Return the final calculated diameter
        return length_calc_group, d_final_val