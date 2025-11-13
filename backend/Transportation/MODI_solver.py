from VAM_solver import solve_vam
import argparse
import sys
import json
import numpy as np

def check_degeneracy(initial_allocations, costs):
    """Check if Solution is degenerate or not m+n-1 = no. of allocation
    Returns:
        bool: False if degenerate
        True if non-degenerate
    
    """
    m = len(costs) # no. of rows
    n = len(costs[0]) # no. of columns
    allocated_cells = []
    
    for r in range(len(initial_allocations)):
        for c in range(len(initial_allocations[0])):
            # A cell is "allocated" if its value is > 0
            # This will include our small EPSILON value later
            if initial_allocations[r][c] > 0:
                allocated_cells.append((r,c))

    no_of_allocations = len(allocated_cells)
    
    # Check if the number of allocations is correct
    # m+n-1 should equal the number of allocations
    if m+n-1 != no_of_allocations:
        diff = abs((m+n-1) - no_of_allocations)
        return False, diff
    else:
        return True, None # Solution is non-degenerate


def find_min_cost_unallocated(costs, allocations, diff):
    """
    Finds a specified number of unallocated cells with the minimum costs.

    This is often used to resolve degeneracy in the Transportation Problem
    by finding where to place 'epsilon' allocations.

    Args:
        costs (list[list[int]]): 2D list of costs for each cell.
        allocations (list[list[int]]): 2D list of allocations.
                                       0 indicates an unallocated cell.
        diff (int): The number of minimum-cost cells to find.

    Returns:
        list[tuple]: A list of tuples, where each tuple is
                     (row, col, cost). The list contains the 'diff'
                     cells with the lowest cost, sorted by cost.
    """
    unallocated_cells = []
    
    # Get the number of rows and columns from the costs matrix
    num_rows = len(costs)
    if num_rows == 0:
        return []  # Return empty if costs matrix is empty
    num_cols = len(costs[0])
    
    # Iterate through each cell to find unallocated ones
    for r in range(num_rows):
        for c in range(num_cols):
            # Check if the cell is unallocated
            if allocations[r][c] == 0:
                # Store its position (row, col) and its cost
                cost = costs[r][c]
                unallocated_cells.append((r, c, cost))
                
    # Sort the list of unallocated cells based on their cost (the 3rd item)
    # The key=lambda x: x[2] tells sort() to use the cost for comparison
    unallocated_cells.sort(key=lambda x: x[2])
    
    # Return the first 'diff' elements from the sorted list
    # This gives you the 'diff' cells with the minimum cost
    return unallocated_cells[:diff]

def add_epsilon_allocations(allocations, epsilon_cells):
    """
    Updates the allocation matrix by adding epsilon allocations
    to resolve degeneracy. This function modifies the matrix in-place.

    Args:
        allocations (list[list[int/float]]): The allocation matrix.
        epsilon_cells (list[tuple]): List of (r, c, cost) tuples
                                     where epsilon should be added.
    
    Returns:
        list[list[int/float]]: The modified allocation matrix.
    """
    # Epsilon is a very small positive quantity
    # It's treated as an allocation, but has a value of 0
    EPSILON = 0.0001
    
    # Unpack the tuple (row, col, cost) for each cell
    for (r, c, cost) in epsilon_cells:
        # We check if it's 0, just to be safe
        if allocations[r][c] == 0:
            allocations[r][c] = EPSILON

    return allocations

def u_v_calculation(costs, allocations):
    """
    Calculates the 'u' (row) and 'v' (column) values for the MODI method
    based on the allocated cells.
    
    The calculation is based on the formula: C[i][j] = u[i] + v[j]
    for all *allocated* cells.

    Args:
        costs (list[list[int]]): The 2D cost matrix.
        allocations (list[list[float/int]]): The 2D allocation matrix,
                                             which may include epsilon.

    Returns:
        tuple: A tuple containing two lists: (u_values, v_values)
    """
    num_rows = len(costs)
    num_cols = len(costs[0])
    
    # 1. Find all allocated cells (row, col)
    # A cell is "allocated" if its value is > 0 (this includes epsilon)
    allocated_cells = []
    for r in range(num_rows):
        for c in range(num_cols):
            if allocations[r][c] > 0:
                allocated_cells.append((r, c))
                
    # 2. Initialize u and v lists with 'None'
    # 'None' means the value is not yet calculated
    u = [None] * num_rows
    v = [None] * num_cols
    
    # 3. Set the first u value to 0, as per the MODI rule
    u[0] = 0
    
    # 4. Loop until all u and v values are calculated
    # We use 'calculated_count' to track progress
    calculated_count = 1  # We start with 1 (u[0])
    total_to_calculate = num_rows + num_cols
    
    # This loop will run until all u's and v's are found
    # We add a safeguard to prevent infinite loops if something is wrong
    loop_count = 0
    max_loops = (num_rows + num_cols) * 2
    
    while calculated_count < total_to_calculate:
        
        # This flag tracks if we found any new value in this iteration
        made_progress = False
        
        for (r, c) in allocated_cells:
            cost = costs[r][c]
            
            # Case 1: u[r] is known, v[c] is unknown
            # We can calculate v[c] = cost - u[r]
            if u[r] is not None and v[c] is None:
                v[c] = cost - u[r]
                calculated_count += 1
                made_progress = True
            
            # Case 2: v[c] is known, u[r] is unknown
            # We can calculate u[r] = cost - v[c]
            elif u[r] is None and v[c] is not None:
                u[r] = cost - v[c]
                calculated_count += 1
                made_progress = True
        
        # Safeguard: If we went through all cells and made no progress,
        # it means the allocations are not connected (which resolving
        # degeneracy should prevent, but it's good to have)
        loop_count += 1
        if not made_progress and loop_count > max_loops:
            break
            
    return u, v

def calculate_opportunity_costs(costs, allocations, u, v):
    """
    Calculates the opportunity cost (improvement index) for all
    UNALLOCATED cells.

    Formula: opportunity_cost = u[i] + v[j] - costs[i][j]

    Args:
        costs (list[list[int]]): The 2D cost matrix.
        allocations (list[list[float/int]]): The 2D allocation matrix.
        u (list[int/float]): The calculated 'u' (row) values.
        v (list[int/float]): The calculated 'v' (column) values.

    Returns:
        list[list[float/None]]: A 2D matrix where unallocated cells
        contain their opportunity cost, and allocated cells are None.
    """
    num_rows = len(costs)
    num_cols = len(costs[0])
    
    # Create a new matrix to store the opportunity costs
    # We initialize it with 'None' for all cells
    opp_costs = [[None] * num_cols for _ in range(num_rows)]
    
    # Loop through every cell in the matrix
    for r in range(num_rows):
        for c in range(num_cols):
            if u[r] == None:
                u[r] = 0
            if v[c] == None:
                v[c] = 0
            # We only calculate this for UNALLOCATED cells
            # (Allocated cells have a value > 0, including epsilon)
            if allocations[r][c] == 0:
                
                # Apply the formula: u[i] + v[j] - C[i][j]
                cost = u[r] + v[c] - costs[r][c]
                opp_costs[r][c] = cost
                
    return opp_costs

def check_optimality(opp_costs):
    """
    Checks if the current solution is optimal by examining opportunity costs.
    
    - Optimal: All opportunity costs are <= 0.
    - Not Optimal: At least one opportunity cost is > 0.

    Args:
        opp_costs (list[list[float/None]]): The 2D matrix of opportunity costs.
                                            (None for allocated cells).

    Returns:
        tuple: 
        (True, None) if the solution is optimal.
        (False, pivot_cell) if not optimal. 'pivot_cell' is the (r, c)
        tuple of the cell with the *most positive* opportunity cost.
    """
    
    # We are looking for the *most positive* opportunity cost.
    # We can start our "max" at 0.
    max_positive_cost = 0  
    pivot_cell = None
    
    num_rows = len(opp_costs)
    num_cols = len(opp_costs[0])
    
    for r in range(num_rows):
        for c in range(num_cols):
            cost = opp_costs[r][c]
            
            # We only check unallocated cells (which have a cost number)
            if cost is not None:
                if cost > max_positive_cost:
                    # This is a positive cost, and it's the largest
                    # one we've found so far.
                    max_positive_cost = cost
                    pivot_cell = (r, c) # Save the location (row, col)
    
    # After checking all cells:
    if max_positive_cost > 0:
        # We found at least one positive cost. The solution is NOT optimal.
        return False, pivot_cell
    else:
        # No positive costs were found (max_positive_cost is still 0).
        # The solution IS optimal.
        return True, None

def find_loop(allocations, pivot_cell):
    """
    Finds a closed-loop path (Stepping Stone path) starting and
    ending at the pivot cell.

    The path follows these rules:
    1. Starts at the (unallocated) pivot cell.
    2. Moves horizontally or vertically.
    3. Only "turns" (e.g., from row to col) at allocated cells.
    4. The loop must have at least 4 cells.

    Args:
        allocations (list[list[float/int]]): The 2D allocation matrix.
        pivot_cell (tuple): The (row, col) of the starting unallocated cell.

    Returns:
        list[tuple]: A list of (row, col) tuples representing the loop.
                     Returns None if no loop is found.
    """
    num_rows = len(allocations)
    num_cols = len(allocations[0])
    pivot_r, pivot_c = pivot_cell

    # Get all allocated cells as a set for quick lookup
    allocated_cells = set()
    for r in range(num_rows):
        for c in range(num_cols):
            if allocations[r][c] > 0:
                allocated_cells.add((r, c))

    # We will try to find a path from an allocated cell in the
    # pivot's row to an allocated cell in the pivot's column.
    
    # 1. Get all potential "start" cells (allocated, in pivot's row)
    row_starters = [(pivot_r, c) for c in range(num_cols) if (pivot_r, c) in allocated_cells]
    
    # 2. Get all potential "end" cells (allocated, in pivot's column)
    col_enders = [(r, pivot_c) for r in range(num_rows) if (r, pivot_c) in allocated_cells]

    # --- Define the recursive search function (DFS) ---
    # This search finds a path between 'start' and 'end' by
    # alternating row/column searches.
    def find_path_dfs(r, c, search_direction, end_cell, visited, path_stack):
        """
        Recursive helper to find the path.
        'search_direction' is the direction we MUST search next.
        """
        visited.add((r, c))
        path_stack.append((r, c))

        if (r, c) == end_cell:
            return True # Found the end!

        if search_direction == 'col':
            # We just moved horizontally, so now we search vertically
            for next_r in range(num_rows):
                if next_r == r: continue
                next_cell = (next_r, c)
                
                if next_cell == end_cell:
                    path_stack.append(end_cell)
                    return True
                
                if next_cell in allocated_cells and next_cell not in visited:
                    if find_path_dfs(next_r, c, 'row', end_cell, visited, path_stack):
                        return True
                        
        elif search_direction == 'row':
            # We just moved vertically, so now we search horizontally
            for next_c in range(num_cols):
                if next_c == c: continue
                next_cell = (r, next_c)
                
                if next_cell == end_cell:
                    path_stack.append(end_cell)
                    return True
                
                if next_cell in allocated_cells and next_cell not in visited:
                    if find_path_dfs(r, next_c, 'col', end_cell, visited, path_stack):
                        return True

        # No path found from here, backtrack
        path_stack.pop()
        return False
    # --- End of DFS definition ---

    # Now, try to find a path for every start/end combination
    for start_cell in row_starters:
        for end_cell in col_enders:
            if start_cell == end_cell: continue
            
            path_stack = []
            visited = set()
            
            # Start from 'start_cell', and we "got here" by row,
            # so our first search MUST be by column.
            if find_path_dfs(start_cell[0], start_cell[1], 'col', end_cell, visited, path_stack):
                # Success! Construct the full loop
                # pivot -> start_cell -> ...path... -> end_cell -> pivot
                return [pivot_cell] + path_stack
            

    # If we found no loops, we must also try searching
    # from col_starters to row_enders (the other direction)
    col_starters = [(r, pivot_c) for r in range(num_rows) if (r, pivot_c) in allocated_cells]
    row_enders = [(pivot_r, c) for c in range(num_cols) if (pivot_r, c) in allocated_cells]
    
    for start_cell in col_starters:
        for end_cell in row_enders:
            if start_cell == end_cell: continue
            
            path_stack = []
            visited = set()
            
            # Start from 'start_cell', we "got here" by col,
            # so our first search MUST be by row.
            if find_path_dfs(start_cell[0], start_cell[1], 'row', end_cell, visited, path_stack):
                return [pivot_cell] + path_stack

    # If after all that, nothing is found
    return None

def adjust_allocations(allocations, loop):
    """
    Adjusts the allocations based on the found loop.
    1. Assigns alternate + and - to the loop cells, starting with +
       at the pivot.
    2. Finds the minimum allocation value from all 'minus' cells.
    3. Adds this value to all 'plus' cells.
    4. Subtracts this value from all 'minus' cells.

    Args:
        allocations (list[list[float/int]]): The current allocation matrix.
        loop (list[tuple]): The loop path, e.g., [(r1,c1), (r2,c2), ...]

    Returns:
        list[list[float/int]]: The new, improved allocation matrix.
    """
    plus_cells = []
    minus_cells = []
    
    # 1. Assign + and -
    # The loop starts with the pivot, which is a '+' cell
    for i in range(len(loop)):
        cell = loop[i]
        if i % 2 == 0:
            # Even index (0, 2, 4...) = +
            plus_cells.append(cell)
        else:
            # Odd index (1, 3, 5...) = -
            minus_cells.append(cell)
    

    # 2. Find the minimum allocation in the 'minus' cells
    # This is the amount 'theta' we can shift
    min_allocation = float('inf')
    for (r, c) in minus_cells:
        # We ignore the pivot, which has 0, by checking > 0
        if allocations[r][c] > 0 and allocations[r][c] < min_allocation:
            min_allocation = allocations[r][c]
            
    # Handle the rare case where an epsilon was the min value
    if min_allocation == float('inf'):
         # This can happen if all 'minus' cells were 0 or epsilon
         # We'll just find the smallest value, even if it's epsilon
         min_allocation = min(allocations[r][c] for (r,c) in minus_cells)

    # Create a new allocation matrix (deep copy) to modify
    new_allocations = [row[:] for row in allocations]

    # 3. Add 'min_allocation' to all 'plus' cells
    for (r, c) in plus_cells:
        new_allocations[r][c] += min_allocation

    # 4. Subtract 'min_allocation' from all 'minus' cells
    for (r, c) in minus_cells:
        new_allocations[r][c] -= min_allocation
        
    return new_allocations, min_allocation, plus_cells, minus_cells

def calculate_final_cost(costs, allocations):
    """
    calculates final costs
    Args:
        cost (list[list[float/int]]): 2D cost matrix
        allocation (list[list[float/int]]): final allocation

    Returns:
        int : final total minimum cost of transportation
    """
    total_cost = 0
    for i in range(len(costs)):
        for j in range(len(costs[0])):
            # Multiply cost by allocation for each cell and sum
            total_cost += costs[i][j] * allocations[i][j]
    return total_cost

def solve_MODI(costs_for_modi, original_costs, initial_allocation):
    """
    Solve transportation problem using the Modified Distribution (MODI) method.
    ...
    Parameters:
    costs_for_modi: 2D list of costs for MODI logic (minimization matrix).
    original_costs: 2D list of the original problem costs (for final sum).
    initial_allocation: 2D list of allocated quantities from VAM.
    ...
    """
    
    current_allocation = [row[:] for row in initial_allocation]
    
    while True:
        # 1. Handle Degeneracy (uses minimization matrix)
        is_non_degenerate, diff = check_degeneracy(current_allocation, costs_for_modi)
        print("done degeneracy")

        if not is_non_degenerate:
            epsilon_cells = find_min_cost_unallocated(costs_for_modi, current_allocation, diff)
            current_allocation = add_epsilon_allocations(current_allocation, epsilon_cells)
            print("adjusted degeneracy")

        # 2. Calculate u, v (uses minimization matrix)
        u, v = u_v_calculation(costs_for_modi, current_allocation)
        print("done u & v calculation")

        # 3. Calculate Opportunity Costs (uses minimization matrix)
        opportunity_cost = calculate_opportunity_costs(costs_for_modi, current_allocation, u, v)
        print("done opportunity cost")

        # 4. Check for Optimality
        is_optimal, pivot_cell = check_optimality(opportunity_cost)
        print("done optimality check")

        if is_optimal:
            print("Solution is optimal. Breaking loop.")
            break
        else:
            # 5a. Find Loop
            loop = find_loop(current_allocation, pivot_cell)
            print("found loop")
            
            if loop is None:
                print("Error: Could not find a loop. Returning current solution.", file=sys.stderr)
                break 

            # 5b. Adjust Allocations
            new_allocation_matrix, _, _, _ = adjust_allocations(current_allocation, loop)
            print("adjusted allocation")
            
            current_allocation = new_allocation_matrix
            print("--- RESTARTING LOOP ---")
            
    # 6. After loop breaks, calculate final cost using ORIGINAL costs
    total_cost = calculate_final_cost(original_costs, current_allocation)
    
    return current_allocation, total_cost