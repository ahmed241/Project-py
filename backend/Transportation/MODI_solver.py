import copy

def find_loop(allocation, start_row, start_col):
    """
    Finds a closed-loop path starting from an entering cell (start_row, start_col).
    This is a helper function for the MODI method.
    The path must alternate between horizontal and vertical moves, with turns only at allocated cells.
    
    Returns:
    A list of tuples representing the loop path, or None if no loop is found.
    """
    path = [(start_row, start_col)]
    
    # Try to find a loop by first moving horizontally
    # A path-finding function (like DFS) is needed to find the loop
    
    # We create a list of all allocated cells to serve as possible path nodes
    allocated_cells = []
    for r in range(len(allocation)):
        for c in range(len(allocation[0])):
            if allocation[r][c] > 0:
                allocated_cells.append((r,c))

    # Add the starting cell to the list of potential corners
    # This allows it to be found by the path search to close the loop
    if (start_row, start_col) not in allocated_cells:
        allocated_cells.append((start_row, start_col))
    
    # A recursive function to find the path
    def find_path(curr_pos, visited, vertical_move):
        # Base case: if we can return to the start column (if moving vertically) 
        # or start row (if moving horizontally) and form a loop of at least 4 cells.
        if len(visited) > 2:
            if vertical_move: # trying to find a cell in the same column
                if curr_pos[1] == start_col:
                    return visited + [curr_pos]
            else: # trying to find a cell in the same row
                if curr_pos[0] == start_row:
                    return visited + [curr_pos]

        # Explore next moves
        for next_r, next_c in allocated_cells:
            next_pos = (next_r, next_c)
            if next_pos not in visited:
                # If last move was horizontal, next must be vertical
                if not vertical_move and next_c == curr_pos[1]:
                    new_path = find_path(next_pos, visited + [curr_pos], True)
                    if new_path:
                        return new_path
                # If last move was vertical, next must be horizontal
                elif vertical_move and next_r == curr_pos[0]:
                    new_path = find_path(next_pos, visited + [curr_pos], False)
                    if new_path:
                        return new_path
        return None

    # Start search from the entering cell
    # First turn can be horizontal or vertical
    for r, c in allocated_cells:
        if r == start_row and (r,c) != (start_row, start_col): # Horizontal start
            path = find_path((r,c), [(start_row, start_col)], True)
            if path:
                return path
    
    return None # No loop found


def solve_modi(costs, initial_allocation):
    """
    Solve transportation problem using the Modified Distribution (MODI) method.
    This method takes an initial feasible solution and improves it to optimality.
    
    Parameters:
    costs: 2D list of transportation costs.
    initial_allocation: 2D list of allocated quantities from an initial method (e.g., VAM).
    
    Returns:
    optimal_allocation: 2D list of the final, optimal allocated quantities.
    total_cost: The optimal total transportation cost.
    """
    allocation = copy.deepcopy(initial_allocation)
    num_supply = len(costs)
    num_demand = len(costs[0])

    while True:
        # Step 1: Find occupied cells and initialize u and v
        u = [None] * num_supply
        v = [None] * num_demand
        occupied_cells = []
        for r in range(num_supply):
            for c in range(num_demand):
                if allocation[r][c] > 0:
                    occupied_cells.append((r, c))

        # Assume u[0] = 0 to start solving for u and v
        u[0] = 0
        
        # Iteratively solve for u and v using the relation: c[i][j] = u[i] + v[j] for occupied cells
        for _ in range(num_supply + num_demand):
            for r, c in occupied_cells:
                if u[r] is not None and v[c] is None:
                    v[c] = costs[r][c] - u[r]
                elif u[r] is None and v[c] is not None:
                    u[r] = costs[r][c] - v[c]

        # Step 2: Calculate opportunity costs (deltas) for all unoccupied cells
        deltas = [[0 for _ in range(num_demand)] for _ in range(num_supply)]
        most_negative_cell = None
        min_delta = 0

        for r in range(num_supply):
            for c in range(num_demand):
                if allocation[r][c] == 0:
                    delta = costs[r][c] - (u[r] + v[c])
                    deltas[r][c] = delta
                    if delta < min_delta:
                        min_delta = delta
                        most_negative_cell = (r, c)
        
        # Step 3: Check for optimality. If all deltas are non-negative, the solution is optimal.
        if min_delta >= 0:
            break # Optimal solution found

        # Step 4: Find the closed loop to improve the solution
        start_row, start_col = most_negative_cell
        loop = find_loop(allocation, start_row, start_col)
        
        if not loop:
            # This can happen in degenerate cases. For this solver, we stop.
            print("Warning: Could not find a loop. The problem might be degenerate.")
            break

        # Step 5: Adjust allocations along the loop
        plus_cells = []
        minus_cells = []
        for i in range(len(loop)):
            if i % 2 == 0:
                plus_cells.append(loop[i])
            else:
                minus_cells.append(loop[i])
        
        # Find the minimum allocation in the 'minus' cells
        min_allocation = min(allocation[r][c] for r, c in minus_cells)

        # Add to plus_cells and subtract from minus_cells
        for r, c in plus_cells:
            allocation[r][c] += min_allocation
        for r, c in minus_cells:
            allocation[r][c] -= min_allocation

    # Calculate final total cost
    total_cost = sum(
        allocation[r][c] * costs[r][c]
        for r in range(num_supply)
        for c in range(num_demand)
    )

    return allocation, total_cost


# Example usage:
if __name__ == "__main__":
    # Import the VAM solver from the file you provided to get an initial solution
    from VAM_solver import solve_vam

    # Example problem (same as in your VAM file)
    costs = [
                    [20, 18, 18, 21, 19],
                    [21, 22, 23, 20, 24],
                    [18, 19, 21, 18, 19]
                ]
    demand = [60, 80, 85, 105, 70]
    supply = [100, 125, 175]

    # 1. Get the initial feasible solution using VAM
    initial_allocation, initial_cost = solve_vam(supply, demand, costs)
    print("--- Initial Solution (from VAM) ---")
    print("Allocation matrix:")
    for row in initial_allocation:
        print(row)
    print(f"Initial total transportation cost: {initial_cost}\n")

    # 2. Use MODI to find the optimal solution
    optimal_allocation, optimal_cost = solve_modi(costs, initial_allocation)
    print("--- Optimal Solution (from MODI) ---")
    print("Optimal allocation matrix:")
    for row in optimal_allocation:
        print(row)
    print(f"Optimal total transportation cost: {optimal_cost}")