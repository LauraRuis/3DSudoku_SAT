import os
import json

json_data = open ('data.json').read()
sudokus = json.loads(json_data)
currfol = os.getcwd()

three_d = True

empty_sud = "-1 -1 -1 -1 -1 -1 -1 -1 -1\n-1 -1 -1 -1 -1 -1 -1 -1 -1\n-1 -1 -1 -1 -1 -1 -1 -1 -1\n-1 -1 -1 -1 -1 -1 -1 -1 -1\n-1 -1 -1 -1 -1 -1 -1 -1 -1\n-1 -1 -1 -1 -1 -1 -1 -1 -1\n-1 -1 -1 -1 -1 -1 -1 -1 -1\n-1 -1 -1 -1 -1 -1 -1 -1 -1\n-1 -1 -1 -1 -1 -1 -1 -1 -1\n"
if three_d:

    for j in range(5354): # write first 10 sudokus
        fn = "sudokus/sud%d.txt" %j
        filename = os.path.join(currfol,fn)
        with open(filename, "w") as f:
            f.write('order 9 3 \n')
            for i in range(9):
		if not sudokus[str(j)][str(i)]:
			f.write(empty_sud)
		else:
			f.write(sudokus[str(j)][str(i)])

else:

    for j in range(5354): # write first 10 sudokus
        for i in range(9):
            fn = "sudokus2d/sud%d-%d.txt" % (j, i)
            filename = os.path.join(currfol, fn)
            with open(filename, "w") as f:
                f.write('order 9 3 \n')
		if not sudokus[str(j)][str(i)]:
			f.write(empty_sud)
		else:

		        f.write(sudokus[str(j)][str(i)])
		        f.close()
