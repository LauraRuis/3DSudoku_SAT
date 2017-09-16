import json


def convert_sudoku(sudoku):

    output = {i: "" for i in range(9)}
    string_output = {i: "" for i in range(9)}
    sudoku_row = [str(-1) for i in range(9)]
    sudoku_mat = [sudoku_row.copy() for i in range(9)]
    grid = 0
    for item in sudoku["puzzle"]:
        if int(item[0]) == grid:
            grid = int(item[0])
            given_row = item[2]
            given_col = item[4]
            given = item[6]
            sudoku_mat[int(given_row)][int(given_col)] = str(int(given) - 1)
        else:
            output[int(item[0]) - 1] = sudoku_mat
            sudoku_row = [str(-1) for i in range(9)]
            sudoku_mat = [sudoku_row.copy() for i in range(9)]
            grid = int(item[0])
            given_row = item[2]
            given_col = item[4]
            given = item[6]
            sudoku_mat[int(given_row)][int(given_col)] = str(int(given) - 1)
    output[8] = sudoku_mat

    for grid, puzzle in output.items():
        for row in puzzle:
            string_output[int(grid)] += ' '.join(row) + '\n'

    return string_output


def read_sudoku(n, puzzle_dir, save_dir=""):
    data = {}
    puzzles = []
    data_path = puzzle_dir
    for i in range(n):
        data[i] = {}
        try:
            with open(data_path + str(i + 1) + ".txt", "r") as infile:
                puzzle = infile.readlines()
        except FileNotFoundError:
            puzzle = []
            print(str(i + 1) + ".txt" + " Not found")
        puzzles.append({"number": i + 1, "puzzle": puzzle})

    for p in puzzles:
        sudoku = convert_sudoku(p)
        print("Reading puzzle ", p['number'])
        data[p['number'] - 1] = sudoku

    if save_dir:
        outfile = "\\3d_sudoku_strings.json"
        with open(save_dir + "\\" + outfile, 'w') as outfile:
            json.dump(data, outfile, indent=4, separators=(',', ':'))

    return data
