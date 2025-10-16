require 'json'
def draw_lines grid
    #copies the array   
    marking_grid = grid.map { |a| a.dup }

    marked_rows = Array.new
    marked_cols = Array.new

    while there_is_zero(marking_grid) do 
        marking_grid = grid.map { |a| a.dup }

        marked_cols.each do |col|
            cross_out(marking_grid,nil, col)
        end

        marked = assignment(grid, marking_grid) 
        marked_rows = marked[0]
        marked_cols.concat(marked[1]).uniq!

        marking_grid = grid.map { |a| a.dup }

        marking_grid.length.times do |row|
            if !(marked_rows.include? row) then
                cross_out(marking_grid,row, nil)
            end
        end

        marked_cols.each do |col|
            cross_out(marking_grid,nil, col)
        end
    end


    lines = Array.new

    marked_cols.each do |index|
        lines.push(["column", index])
    end
    grid.each_index do |index|
        if !(marked_rows.include? index) then
            lines.push(["row", index])
        end
    end
    return lines
end


def there_is_zero grid
    grid.each_with_index do |row|
        row.each_with_index do |value|
            if value == 0 then
                return true
            end
        end
    end
    return false
end

def assignment grid, marking_grid 
    marking_grid.each_index do |row_index|
        first_zero = marking_grid[row_index].index(0)
        #if there is no zero go to next row
        if first_zero.nil? then
            next        
        else
            cross_out(marking_grid, row_index, first_zero)
            marking_grid[row_index][first_zero] = "*"
        end
    end

    return mark(grid, marking_grid)
end


def mark grid, marking_grid, marked_rows = Array.new, marked_cols = Array.new
    marking_grid.each_with_index do |row, row_index|
        selected_assignment = row.index("*")
        if selected_assignment.nil? then
            marked_rows.push(row_index)
        end
    end

    marked_rows.each do |index|
        grid[index].each_with_index do |cost, col_index|
            if cost == 0 then
                marked_cols.push(col_index) 
            end
        end
    end
    marked_cols = marked_cols.uniq

    marked_cols.each do |col_index|
        marking_grid.each_with_index do |row, row_index|
            if row[col_index] == "*" then
                marked_rows.push(row_index) 
            end
        end
    end

    return [marked_rows, marked_cols]
end


def cross_out(marking_grid, row, col)
    if col != nil then
        marking_grid.each_index do |i|
            marking_grid[i][col] = "X"  
        end
    end
    if row != nil then
        marking_grid[row].map! {|i| "X"} 
    end
end

# --- MAIN SCRIPT LOGIC ---
# 1. Read the matrix from the file saved by Python
input_file = File.read('E:/manimations/Project/Assignment/data_for_ruby.json')
grid = JSON.parse(input_file)

# 2. Run your solver
lines_to_draw = draw_lines(grid)

# 3. THIS MUST BE THE ONLY THING THE SCRIPT PRINTS
puts lines_to_draw.to_json

# grid =  Example grid for testing
#     [0, 0, 0, 2, 0],
#     [4, 2, 0, 8, 2],
#     [0, 1, 2, 1, 4],
#     [0, 2, 0, 2, 2],
#     [2, 0, 2, 0, 4]
# ]
# [
#     [8, 10, 17, 9],
#     [3, 8, 5, 6],
#     [10, 12, 11, 9],
#     [6, 13, 9, 7]
# ]