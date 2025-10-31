import sys # Used for float('inf')

def max_to_min(costs):
    """
    Converts Maximization Problem to minimization by calculating
    the 'regret' or 'opportunity loss' matrix.
    The formula is max_cost - cell_cost.
    """
    # Find the single largest cost in the entire matrix
    max_entry = -float('inf')
    for row in costs:
        for entry in row:
            if entry > max_entry:
                max_entry = entry
    
    minimised_cost = []
    for row in costs:
        minimised_row = []
        for c in row:
            # The conversion is max_entry - c
            minimised_row.append(max_entry - c)
        minimised_cost.append(minimised_row)
    
    return minimised_cost

def balance_problem(supply, demand, costs):
    """
    Ensures the problem is balanced (total supply == total demand).
    If not, adds a dummy row or column with 0 costs.
    """
    # Make copies to avoid modifying the original lists
    supply = list(supply)
    demand = list(demand)
    costs = [list(row) for row in costs]
    
    total_supply = sum(supply)
    total_demand = sum(demand)
    
    if total_supply == total_demand:
        return supply, demand, costs, False # False means no dummy added

    is_dummy_added = True
    if total_supply < total_demand:
        # Add a dummy supply row
        diff = total_demand - total_supply
        supply.append(diff)
        # Add a new row of 0 costs
        costs.append([0] * len(demand))
        
    elif total_demand < total_supply:
        # Add a dummy demand column
        diff = total_supply - total_demand
        demand.append(diff)
        # Add a new column of 0 costs
        for row in costs:
            row.append(0)
        
    return supply, demand, costs, is_dummy_added


def _calculate_penalties(costs, available_rows, available_cols):
    """
    Calculates the penalties for all available rows and columns.
    Penalty = difference between the two smallest costs in a line.
    """
    num_rows = len(costs)
    num_cols = len(costs[0])
    
    # Initialize penalties with -1 (or any value < 0)
    # This marks them as "not calculated" or "not available"
    row_penalties = [-1] * num_rows
    col_penalties = [-1] * num_cols

    # --- Calculate Row Penalties ---
    for r in range(num_rows):
        # Only calculate for available rows
        if available_rows[r]:
            # Find all costs in this row from available columns
            row_costs = []
            for c in range(num_cols):
                if available_cols[c]:
                    row_costs.append(costs[r][c])
            
            if len(row_costs) > 0:
                row_costs.sort() # Sort costs from smallest to largest
                
            if len(row_costs) >= 2:
                row_penalties[r] = row_costs[1] - row_costs[0]
            elif len(row_costs) == 1:
                row_penalties[r] = row_costs[0] # Only one cell left
            else:
                row_penalties[r] = -1 # No cells available in this row

    # --- Calculate Column Penalties ---
    for c in range(num_cols):
        # Only calculate for available columns
        if available_cols[c]:
            # Find all costs in this col from available rows
            col_costs = []
            for r in range(num_rows):
                if available_rows[r]:
                    col_costs.append(costs[r][c])

            if len(col_costs) > 0:
                col_costs.sort() # Sort costs
            
            if len(col_costs) >= 2:
                col_penalties[c] = col_costs[1] - col_costs[0]
            elif len(col_costs) == 1:
                col_penalties[c] = col_costs[0] # Only one cell left
            else:
                col_penalties[c] = -1 # No cells available in this col
                
    return row_penalties, col_penalties

def _find_best_allocation_candidate(costs, supply, demand, 
                                    row_penalties, col_penalties, 
                                    available_rows, available_cols):
    """
    Finds the best cell to allocate to based on VAM's advanced
    tie-breaking rules.
    
    1. Finds all rows/cols with the maximum penalty.
    2. For each, finds the potential allocation (Rule 1: max allocation).
    3. If tied, finds the one with the minimum cost (Rule 2: min cost).
    
    Returns:
        A tuple: ( (r, c), allocation_amount )
        Returns (None, 0) if no candidate is found.
    """
    
    # Find the absolute highest penalty value
    max_row_pen = max(row_penalties)
    max_col_pen = max(col_penalties)
    max_penalty_value = max(max_row_pen, max_col_pen)
    
    # This can happen at the end
    if max_penalty_value < 0:
        return None, 0

    candidates = []
    
    # --- 1. Gather all candidate cells from qualifying ROWS ---
    for r, pen in enumerate(row_penalties):
        if pen == max_penalty_value:
            # This row has the max penalty. Find its min cost cell.
            (cell_r, cell_c) = _find_min_cost_cell(costs, 'row', r, 
                                                   available_rows, available_cols)
            
            # This can happen if a row is available but has no
            # available columns left
            if (cell_r, cell_c) == (-1, -1):
                continue 
            
            cost = costs[cell_r][cell_c]
            # Rule 1: Find potential max allocation
            potential_alloc = min(supply[cell_r], demand[cell_c])
            
            # Store: (potential_alloc, cost, (row, col))
            candidates.append((potential_alloc, cost, (cell_r, cell_c)))

    # --- 2. Gather all candidate cells from qualifying COLS ---
    for c, pen in enumerate(col_penalties):
        if pen == max_penalty_value:
            # This col has the max penalty. Find its min cost cell.
            (cell_r, cell_c) = _find_min_cost_cell(costs, 'col', c, 
                                                   available_rows, available_cols)

            if (cell_r, cell_c) == (-1, -1):
                continue 
            
            cost = costs[cell_r][cell_c]
            potential_alloc = min(supply[cell_r], demand[cell_c])
            
            # We must check if this cell was already added by a 
            # row. This avoids duplicates if (0,1) is the min
            # for both Row 0 and Col 1.
            if (potential_alloc, cost, (cell_r, cell_c)) not in candidates:
                candidates.append((potential_alloc, cost, (cell_r, cell_c)))
    
    if not candidates:
        return None, 0

    # --- 3. Find the best candidate ---
    # We sort by:
    #   1. potential_alloc (item[0]), descending (hence the 'reverse=True')
    #   2. cost (item[1]), ascending (which is the default)
    #
    # We can also use a key with a trick: (item[0], -item[1])
    # sorting by -item[1] (negative cost) in descending order
    # is the same as sorting by cost ascending.
    
    candidates.sort(key=lambda item: (item[0], -item[1]), reverse=True)
    
    # The best candidate is now the first one in the list
    best = candidates[0]
    best_cell = best[2]       # (r, c)
    best_alloc_amt = best[0]  # The potential allocation
    
    return best_cell, best_alloc_amt

def _find_min_cost_cell(costs, line_type, index, available_rows, available_cols):
    """
    Finds the cell (r, c) with the minimum cost within the specified
    row or column.
    """
    min_cost = float('inf')
    best_cell = (-1, -1) # (row, col)

    if line_type == 'row':
        r = index
        # Search all available columns in this row
        for c in range(len(costs[0])):
            if available_cols[c] and costs[r][c] < min_cost:
                min_cost = costs[r][c]
                best_cell = (r, c)
                
    elif line_type == 'col':
        c = index
        # Search all available rows in this column
        for r in range(len(costs)):
            if available_rows[r] and costs[r][c] < min_cost:
                min_cost = costs[r][c]
                best_cell = (r, c)
                
    return best_cell

def solve_vam(supply, demand, costs, problem_type="minimisation"):
    """
    Solves the Transportation Problem using Vogel's Approximation Method (VAM)
    with advanced tie-breaking.
    
    Handles both 'minimisation' and 'maximisation' problem types.
    """
    
    # We MUST store the original costs to calculate the final
    # cost/profit correctly.
    original_costs = [list(row) for row in costs]
    
    if problem_type == "maximisation":
        print("Maximisation problem detected. Converting to minimisation...")
        # We use the converted 'costs' matrix for all VAM logic
        costs = max_to_min(costs)
        print("Converted costs (regret matrix):")
        for row in costs:
            print(f"  {row}")
    
    # --- Integration End ---

    # 1. Balance the problem
    # This uses the (potentially converted) 'costs' matrix
    current_supply, current_demand, costs, _ = balance_problem(supply, demand, costs)
    updated_supply = current_supply.copy()
    updated_demand = current_demand.copy()
    
    # If a dummy row/col was added, we must add it to original_costs
    # as well so the indices match up later when calculating total_cost
    if len(current_supply) > len(original_costs): # Dummy row added
        original_costs.append([0] * len(original_costs[0]))

    if len(current_demand) > len(original_costs[0]): # Dummy col added
        for row in original_costs:
            row.append(0)

    num_rows = len(current_supply)
    num_cols = len(current_demand)

    # 2. Set up tracking variables
    allocations = [[0] * num_cols for _ in range(num_rows)]
    available_rows = [True] * num_rows
    available_cols = [True] * num_cols
    
    total_cost = 0 # This will store the final cost/profit
    total_supply_left = sum(current_supply)

    # 3. Main VAM Loop
    print("\nStarting VAM iterations...")
    step = 1
    while total_supply_left > 0:
        
        # 3a. Calculate penalties (using converted costs)
        row_pen, col_pen = _calculate_penalties(costs, available_rows, available_cols)
        
        # 3b. Find best cell (using converted costs)
        (r, c), allocation_amount = _find_best_allocation_candidate(
            costs, current_supply, current_demand, 
            row_pen, col_pen, 
            available_rows, available_cols
        )
        
        # 3c. Check if we're done
        if (r, c) == None:
            try:
                r = available_rows.index(True)
                c = available_cols.index(True)
            except ValueError:
                break 

        # 3d. Make allocation
        allocation_amount = min(current_supply[r], current_demand[c])

        # 3e. Update matrices
        allocations[r][c] = allocation_amount
        current_supply[r] -= allocation_amount
        current_demand[c] -= allocation_amount
        total_supply_left -= allocation_amount
        
        # --- CRITICAL CHANGE ---
        # We calculate the final sum using the ORIGINAL costs
        # (This calculates cost for minimisation, profit for maximisation)
        total_cost += allocation_amount * original_costs[r][c]

        # 3f. Cross out rows/cols
        if current_supply[r] == 0:
            available_rows[r] = False
        if current_demand[c] == 0:
            available_cols[c] = False
            
        step += 1
    return allocations, total_cost, original_costs, updated_demand, updated_supply

# --- How to Use It ---

# Your input data from the file
costs = [
                [40, 25, 22, 33],
                [44, 35, 30, 30],
                [38, 38, 28, 30]
            ]
demand = [40, 20, 60, 30]
supply = [100, 30, 70]

# costs = [
#         [8, 7, 3],
#         [3, 8, 9],
#         [11, 3, 5]
#     ]
# demand = [50, 80, 80]
# supply = [60, 70, 80]

# # 1. Get the initial solution using VAM
initial_allocation, initial_cost, update_costs, update_demad, update_supply = solve_vam(supply, demand, costs)
print(initial_allocation)
print(update_costs)
print(update_demad)
print(update_supply)