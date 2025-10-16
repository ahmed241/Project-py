# voiceover_generator.py
# Install: pip install gtts pydub

import json
from gtts import gTTS
from pydub import AudioSegment
import os

class VoiceoverGenerator:
    """
    Generates dynamic voiceover scripts based on the problem data
    and creates audio files for each step.
    """
    
    def __init__(self, data_file="data.json"):
        with open(data_file, "r") as f:
            self.data = json.load(f)
        
        self.matrix = self.data["matrix"]
        self.problem_type = self.data.get("type", "minimization")
        self.n = len(self.matrix)
        self.output_dir = "voiceovers"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_all_voiceovers(self):
        """Generate all voiceover segments"""
        segments = []
        
        # Introduction
        segments.append(("intro", self.script_intro()))
        
        # Check square
        segments.append(("square_check", self.script_square_check()))
        
        # Maximization (if applicable)
        if self.problem_type == "maximization":
            segments.append(("max_to_min", self.script_maximization()))
        
        # Row reduction
        segments.append(("row_reduction", self.script_row_reduction()))
        
        # Column reduction
        segments.append(("col_reduction", self.script_column_reduction()))
        
        # Line drawing
        segments.append(("line_drawing", self.script_line_drawing()))
        
        # Final assignment
        segments.append(("final_assignment", self.script_final_assignment()))
        
        # Generate audio for each segment
        audio_files = []
        for name, script in segments:
            audio_file = self.text_to_speech(script, name)
            audio_files.append((name, audio_file))
        
        return audio_files
    
    def script_intro(self):
        return f"""Welcome to the Assignment Problem visualization. 
        We have a {self.n} by {self.n} cost matrix. 
        Our goal is to find the optimal assignment that minimizes the total cost. 
        Let's begin by examining our matrix."""
    
    def script_square_check(self):
        rows = len(self.matrix)
        cols = len(self.matrix[0])
        
        if rows == cols:
            return f"""Step 1: Checking if the matrix is square. 
            We have {rows} rows and {cols} columns. 
            The matrix is square, so we can proceed directly."""
        else:
            return f"""Step 1: Checking if the matrix is square. 
            We have {rows} rows and {cols} columns. 
            The matrix is not square. We need to add dummy rows or columns 
            with zero costs to balance it."""
    
    def script_maximization(self):
        max_val = max(max(row) for row in self.matrix)
        return f"""Since this is a maximization problem, we first convert it 
        to a minimization problem. We find the maximum value in the matrix, 
        which is {max_val}, and subtract each entry from this maximum."""
    
    def script_row_reduction(self):
        return """Step 2: Row Reduction. 
        For each row, we find the minimum value and subtract it from 
        all entries in that row. This ensures each row has at least one zero."""
    
    def script_column_reduction(self):
        return """Step 3: Column Reduction. 
        For each column, we check if it has at least one zero. 
        If not, we subtract the minimum value from all entries in that column."""
    
    def script_line_drawing(self):
        return f"""Step 4: Covering zeros with minimum lines. 
        We draw horizontal and vertical lines to cover all zeros. 
        If the number of lines equals {self.n}, we have an optimal solution. 
        Otherwise, we need to adjust the matrix and repeat."""
    
    def script_final_assignment(self):
        return """Step 5: Making the optimal assignment. 
        We assign each row to a column, ensuring each assignment 
        corresponds to a zero in our reduced matrix. 
        This gives us the minimum total cost."""
    
    def text_to_speech(self, text, filename):
        """Convert text to speech and save as MP3"""
        output_path = os.path.join(self.output_dir, f"{filename}.mp3")
        
        # Use gTTS (Google Text-to-Speech)
        tts = gTTS(text=text, lang='en', slow=False)
        tts.save(output_path)
        
        print(f"Generated: {output_path}")
        return output_path
    
    def get_timing_data(self):
        """
        Returns timing information for syncing with animation.
        This should match your Manim scene's wait times.
        """
        timings = {
            "intro": 8.0,           # Adjust based on actual audio length
            "square_check": 6.0,
            "max_to_min": 7.0,
            "row_reduction": 10.0,
            "col_reduction": 8.0,
            "line_drawing": 10.0,
            "final_assignment": 8.0,
        }
        return timings


if __name__ == "__main__":
    generator = VoiceoverGenerator()
    audio_files = generator.generate_all_voiceovers()
    
    print("\n✅ All voiceover segments generated!")
    print("\nGenerated files:")
    for name, path in audio_files:
        print(f"  - {name}: {path}")
    
    # Print timing data
    timings = generator.get_timing_data()
    print("\n📊 Suggested timing for Manim:")
    for step, duration in timings.items():
        print(f"  {step}: {duration}s")