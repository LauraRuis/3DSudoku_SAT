import os
import json

json_data = open ('sudoku_data.json').read()
sudokus = json.loads(json_data)
currfol = os.getcwd()


for j in range(10): # write first 10 sudokus
    fn = "sudokus/sud%d.txt" %j
    filename = os.path.join(currfol,fn)
    with open(filename, "w") as f:
        f.write('order 9 3 \n')
        for i in range(9):
            f.write(sudokus[str(j)][str(i)])


