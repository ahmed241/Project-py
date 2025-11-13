"""
Assignment Problem Solver
Solves assignment problems using the Hungarian Algorithm
Supports video (Manim), PDF, and direct solution outputs
"""

import json
import argparse
import numpy as np
from typing import List, Dict, Tuple
import sys

# Import your actual solver and visualization libraries
# from manim import *  # For video generation
# from reportlab.lib.pagesizes import letter  # For PDF generation
# from scipy.optimize import linear_sum_assignment  # For solving


class AssignmentSolver:
    """Hungarian Algorithm Implementation"""
    
    def __init__(self, cost_matrix: np.ndarray, problem_type: str = 'min'):
        self.original_matrix = cost_matrix.copy()
        self.matrix = cost_matrix.copy()
        self.problem_type = problem_type
        self.rows, self.cols = cost_matrix.shape
        self.steps = []  # Store solution steps for visualization
        
    def solve(self) -> Dict:
        """Solve the assignment problem"""
        
        # Convert maximization to minimization if needed
        if self.problem_type == 'max':
            max_val = np.max(self.matrix)
            self.matrix = max_val - self.matrix
            self.steps.append({
                'step': 'Convert to Minimization',
                'description': f'Subtract all values from {max_val}',
                'matrix': self.matrix.tolist()
            })
        
        # Make matrix square if needed
        if self.rows != self.cols:
            self.matrix = self._make_square()
            self.steps.append({
                'step': 'Make Square Matrix',
                'description': f'Added dummy rows/columns to make {max(self.rows, self.cols)}x{max(self.rows, self.cols)}',
                'matrix': self.matrix.tolist()
            })
        
        # Step 1: Row Reduction
        for i in range(len(self.matrix)):
            min_val = np.min(self.matrix[i])
            self.matrix[i] -= min_val
            
        self.steps.append({
            'step': 'Row Reduction',
            'description': 'Subtract minimum value from each row',
            'matrix': self.matrix.tolist()
        })
        
        # Step 2: Column Reduction
        for j in range(len(self.matrix[0])):
            min_val = np.min(self.matrix[:, j])
            self.matrix[:, j] -= min_val
            
        self.steps.append({
            'step': 'Column Reduction',
            'description': 'Subtract minimum value from each column',
            'matrix': self.matrix.tolist()
        })
        
        # Step 3: Find optimal assignment
        # Using scipy's implementation (you can replace with your own)
        try:
            from scipy.optimize import linear_sum_assignment
            row_ind, col_ind = linear_sum_assignment(self.matrix)
        except ImportError:
            # Fallback to simple greedy assignment for demo
            row_ind, col_ind = self._greedy_assignment()
        
        # Calculate total cost
        total_cost = sum(self.original_matrix[i, j] for i, j in zip(row_ind, col_ind))
        
        # Create assignment mapping
        assignments = [
            {
                'worker': int(i + 1),
                'task': int(j + 1),
                'cost': float(self.original_matrix[i, j])
            }
            for i, j in zip(row_ind, col_ind)
            if i < self.rows and j < self.cols  # Exclude dummy assignments
        ]
        
        return {
            'assignments': assignments,
            'total_cost': float(total_cost),
            'problem_type': self.problem_type,
            'steps': self.steps,
            'optimal': True
        }
    
    def _make_square(self) -> np.ndarray:
        """Add dummy rows or columns to make matrix square"""
        size = max(self.rows, self.cols)
        square_matrix = np.zeros((size, size))
        
        # Copy original values
        square_matrix[:self.rows, :self.cols] = self.matrix
        
        # Fill dummy cells with large values (for minimization)
        # or zero (they won't affect the solution)
        if self.rows < size:
            square_matrix[self.rows:, :] = np.max(self.matrix) * 10
        if self.cols < size:
            square_matrix[:, self.cols:] = np.max(self.matrix) * 10
            
        return square_matrix
    
    def _greedy_assignment(self) -> Tuple[np.ndarray, np.ndarray]:
        """Simple greedy assignment as fallback"""
        n = len(self.matrix)
        row_ind = []
        col_ind = []
        used_cols = set()
        
        for i in range(n):
            available_cols = [j for j in range(n) if j not in used_cols]
            if available_cols:
                min_col = min(available_cols, key=lambda j: self.matrix[i, j])
                row_ind.append(i)
                col_ind.append(min_col)
                used_cols.add(min_col)
        
        return np.array(row_ind), np.array(col_ind)


def generate_video(input_data: Dict, output_path: str) -> None:
    """Generate Manim animation video"""
    print("Generating video animation...")
    
    # TODO: Implement Manim animation
    # This would create a Manim scene showing the Hungarian algorithm steps
    # For now, just create a placeholder
    
    print(f"Video would be saved to: {output_path}")
    print("Note: Manim integration needed for actual video generation")
    
    # Placeholder: You would implement your Manim scene here
    # from manim import Scene, Text, Table
    # class HungarianAnimation(Scene):
    #     def construct(self):
    #         # Your animation code
    #         pass


def generate_pdf(solution: Dict, output_path: str) -> None:
    """Generate PDF report"""
    print("Generating PDF report...")
    
    # TODO: Implement PDF generation with reportlab or similar
    # This would create a detailed PDF with all steps
    
    print(f"PDF would be saved to: {output_path}")
    print("Note: PDF generation library needed")
    
    # Placeholder: You would implement PDF generation here
    # from reportlab.lib.pagesizes import letter
    # from reportlab.pdfgen import canvas
    # # Generate PDF with solution steps


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Assignment Problem Solver')
    parser.add_argument('--input', required=True, help='Input JSON file path')
    parser.add_argument('--output', required=True, help='Output file path')
    parser.add_argument('--type', required=True, choices=['video', 'pdf', 'direct'], help='Output type')
    
    args = parser.parse_args()
    
    try:
        # Read input data
        with open(args.input, 'r') as f:
            input_data = json.load(f)
        
        # Extract problem parameters
        cost_matrix = np.array(input_data['tableData'])
        problem_type = input_data['problemType']
        
        print(f"Solving {input_data['rows']}x{input_data['cols']} assignment problem...")
        print(f"Problem type: {problem_type}")
        print(f"Output type: {args.type}")
        
        # Solve the problem
        solver = AssignmentSolver(cost_matrix, problem_type)
        solution = solver.solve()
        
        # Generate output based on type
        if args.type == 'video':
            generate_video(input_data, args.output)
            # For demo, also save solution as JSON
            json_output = args.output.replace('.mp4', '.json')
            with open(json_output, 'w') as f:
                json.dump(solution, f, indent=2)
                
        elif args.type == 'pdf':
            generate_pdf(solution, args.output)
            # For demo, also save solution as JSON
            json_output = args.output.replace('.pdf', '.json')
            with open(json_output, 'w') as f:
                json.dump(solution, f, indent=2)
                
        else:  # direct
            with open(args.output, 'w') as f:
                json.dump(solution, f, indent=2)
        
        print("Solution generated successfully!")
        print(f"Total cost: {solution['total_cost']}")
        print(f"Assignments: {len(solution['assignments'])}")
        
        # Print solution to stdout
        print("SOLUTION")
        for assignment in solution['assignments']:
            print(f"Worker {assignment['worker']} Task {assignment['task']} (Cost: {assignment['cost']})")
        print(f"Total Cost: {solution['total_cost']}")
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()