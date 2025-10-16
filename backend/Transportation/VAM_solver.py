import copy

def solve_vam(supply, demand, costs):
    """
    Solve transportation problem using Vogel's Approximation Method (VAM)
    
    Parameters:
    supply: list of supply quantities
    demand: list of demand quantities
    costs: 2D list of transportation costs
    
    Returns:
    allocation: 2D list of allocated quantities
    total_cost: total transportation cost
    """
    
    # Create working copies
    supply_left = copy.deepcopy(supply)
    demand_left = copy.deepcopy(demand)
    costs_matrix = copy.deepcopy(costs)
    allocation = [[0 for _ in range(len(demand))] for _ in range(len(supply))]
    
    while sum(supply_left) > 0 and sum(demand_left) > 0:
        # Calculate penalties
        row_penalties = []
        col_penalties = []
        
        # Row penalties
        for i in range(len(supply_left)):
            if supply_left[i] == 0:
                row_penalties.append(-1)
                continue
            row_costs = [c for j, c in enumerate(costs_matrix[i]) if demand_left[j] > 0]
            if len(row_costs) >= 2:
                row_penalties.append(sorted(row_costs)[1] - sorted(row_costs)[0])
            elif len(row_costs) == 1:
                row_penalties.append(row_costs[0])
            else:
                row_penalties.append(-1)
        
        # Column penalties
        for j in range(len(demand_left)):
            if demand_left[j] == 0:
                col_penalties.append(-1)
                continue
            col_costs = [costs_matrix[i][j] for i in range(len(supply_left)) if supply_left[i] > 0]
            if len(col_costs) >= 2:
                col_penalties.append(sorted(col_costs)[1] - sorted(col_costs)[0])
            elif len(col_costs) == 1:
                col_penalties.append(col_costs[0])
            else:
                col_penalties.append(-1)
        
        # Find highest penalty
        max_row_penalty = max(row_penalties)
        max_col_penalty = max(col_penalties)
        
        if max_row_penalty >= max_col_penalty:
            i = row_penalties.index(max_row_penalty)
            valid_costs = [
                (costs_matrix[i][j], j)
                for j in range(len(demand_left))
                if demand_left[j] > 0
            ]
            j = min(valid_costs, key=lambda x: x[0])[1]
        else:
            j = col_penalties.index(max_col_penalty)
            valid_costs = [
                (costs_matrix[i][j], i)
                for i in range(len(supply_left))
                if supply_left[i] > 0
            ]
            i = min(valid_costs, key=lambda x: x[0])[1]
        
        # Allocate
        quantity = min(supply_left[i], demand_left[j])
        allocation[i][j] = quantity
        supply_left[i] -= quantity
        demand_left[j] -= quantity
    
    # Calculate total cost
    total_cost = sum(
        allocation[i][j] * costs[i][j]
        for i in range(len(supply))
        for j in range(len(demand))
    )
    
    return allocation, total_cost

# Example usage:
if __name__ == "__main__":
    # Example problem
    costs = [
                    [20, 18, 18, 21, 19],
                    [21, 22, 23, 20, 24],
                    [18, 19, 21, 18, 19]
                ]
    demand = [60, 80, 85, 105, 70]
    supply = [100, 125, 175]
            
    allocation, total_cost = solve_vam(supply, demand, costs)
    print("Allocation matrix:")
    for row in allocation:
        print(row)
    print(f"Total transportation cost: {total_cost}")