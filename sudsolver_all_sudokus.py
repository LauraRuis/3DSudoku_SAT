#!/usr/bin/env python

import argparse
import subprocess
import sys
import signal
import time
import sudoku

conflict_file = open("conflicts_count.txt", "w")

#Definig Parse
parser = argparse.ArgumentParser(description='Sudoku Solver', prog='sudokusolver')

#Add arguments
parser.add_argument('sudokufile', action='store', default="sudoku-5x5.pls", help='Text file with Sudoku problem definition')
parser.add_argument('-o','--output', action='store', default="cnf/output.cnf", help='Output file for cnf formula')
parser.add_argument('-e','--encoding', action='store', default="extended", help='Encoding Method{extended|optimized}')
parser.add_argument('-solve', action='store_true', help='Call SatSolver and pretty print solution (need glucose_1.0 compiled in ./gucose_1.0)')
parser.add_argument('-crypto', action='store_true', help='Call cryptominisolver & pretty print')
parser.add_argument('-test', action='store_true', help='Make test')
parser.add_argument('-t','--timeout', action='store', type=int, default="0", help='Test Timeout in milliseconds (default: nolimit)')
parser.add_argument('--version', action='version', version='%(prog)s 1.0')    

args = parser.parse_args()
AMOUNT = 5354

# Get sudoku file and properties
for h in range(AMOUNT):
	for k in range(9):
		try:
			f = open(args.sudokufile + str(h) + "-" + str(k) + ".txt")
			print(args.sudokufile + str(h) + "-" + str(k) + ".txt")
			order, m = 9, 3
			n = 3
			sudoku_list = [f.readline().split() for i in range(order)]

			# Encode Sudoku to Dimacs CNF Formula
			initial_time = time.clock()
			s=sudoku.sudoku(args.sudokufile + str(h) + "-" + str(k) + ".txt")
			if args.encoding == "extended": cnf, decoding_map = s.extended_translate_to_CNF()
			elif args.encoding == "optimized": cnf, decoding_map = s.optimized_translate_to_CNF()
			else:
				print "Invalid Encoding Option."
				sys.exit()
			if cnf:

				cnf.print_dimacs(args.output + str(h) + "-" + str(k))
				encoding_time = time.clock() - initial_time
				if args.test: print "Encoding Time:", encoding_time
		except IOError:
			print "No file: " + args.sudokufile + str(h) + "-" + str(k) + ".txt"



def convert_learnt_clause(lc, sud_number):
	converted_clause = []
	for var in lc:
		if int(var) > 0:
			converted_clause.append(int(var) + (729*sud_number))
		else: 
			converted_clause.append(int(var) - (729*sud_number))
	return converted_clause


def print_solution(solution, clause):
	print "learnt clause: ", clause
	counter = 0
	print "|",
	for var in map(int,solution):
		if var > 0:
			counter += 1
			num = decoding_map.index(var)#falten els prefixed true
			real_value = (num - 1) % order
			if (real_value>9) or (order < 10):print real_value,
			else: print '0'+str(real_value),
			if counter % m == 0:
				if counter % order == 0: print "|\n|",
				else:  print "|",
			if counter % (n*(n*m)) == 0:
				print "--------------------- |\n|",
			if counter >= order**2: break


tout = float(args.timeout)/1000
class TimeoutException(Exception): 
	pass

def timeout(timeout_time, default):
    """Time out Decorators from:
	http://programming-guides.com/python/timeout-a-function
	Usage: @timeout(time,return value)"""

    def timeout_function(f):
	def f2(*args):
	    def timeout_handler(signum, frame):
	        raise TimeoutException()
	    old_handler = signal.signal(signal.SIGALRM, timeout_handler) 
	    signal.setitimer(signal.ITIMER_REAL, timeout_time) # triger alarm in timeout_time seconds
	    try: 
	        retval = f()
	    except TimeoutException:
	        return default
	    finally:
	        signal.signal(signal.SIGALRM, old_handler) 
	    signal.alarm(0)
	    return retval
	return f2
    return timeout_function

@timeout(tout, "timeout")
def execute_glucose():
	output = subprocess.Popen(['./glucose_1.0/glucose.sh',args.output],stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate()[0].split()
	if output[1] == 'SATISFIABLE':
		if args.solve: print_solution(output[3:-1])
	else: print "UNSATISFABLE"

def execute_crypto(h):
	sudoku_number = h
	cf = open("converted_clauses/" + "sud" + str(sudoku_number), "w")
	ff = open("clauses/" + "sud" + str(sudoku_number), "w")
	total_conflicts = 0
	for i in range(9):
		sudfile = args.output + str(h) + "-" + str(i)
		print(sudfile)
		output = subprocess.Popen(['cryptominisat5', '--verb', '10', '--maxsol', '1',sudfile],stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate()[0].split()
		output = [ x for x in output if x != 'v' ]
		depth = i
		clauses_to_save = []
		converted_to_save = []
		converted_file = ""
		if 'SATISFIABLE' in output:
			output_indices = [i for i, x in enumerate(output) if x == "SATISFIABLE"]
			return_indices = [i for i, x in enumerate(output) if x == "Returned"]
			conflict_indices = [i for i, x in enumerate(output) if x == "conflicts"]
			for i in range(len(output_indices)):
				search_string = "clause:"
				index = return_indices[i]
				if 'clause:' in output[:index]:
					output_rev = output[:index][::-1]
					total_conflicts += int(output[conflict_indices[i] + 2])
					learnt_clause_index = len(output_rev) - output_rev.index(search_string)
					end_of_clause = output[learnt_clause_index:-1].index("c")
					learnt_clause = output[learnt_clause_index:learnt_clause_index + end_of_clause]
					if "Detaching" in learnt_clause:
						temp_index = learnt_clause.index("Detaching")
						learnt_clause = learnt_clause[:temp_index]
				else:
					learnt_clause = []
				converted_learnt_clause = convert_learnt_clause(learnt_clause, depth)
				#print "converted learnt clause: ", converted_learnt_clause
				output_index = output_indices[i]
				if i == (len(output_indices) - 1):
					end_index = len(output[output_index + 1: -1])
				else:
					end_index = output[output_index + 1: -1].index("c")
				if learnt_clause not in clauses_to_save:
					clauses_to_save.append(learnt_clause)
					converted_to_save.append(converted_learnt_clause)
				#print_solution(output[output_index + 1: output_index + 1 + end_index], learnt_clause)
			for clause in converted_to_save:
				if len(clause) > 0:
					for var in clause:
						cf.write(str(var))
						cf.write(" ")
					cf.write(" 0 \n")
			for clause in clauses_to_save:
				if len(clause) > 0:
					ff.write("depth" + str(depth) + " ")
					for var in clause:
						ff.write(str(var))
						ff.write(" ")
					ff.write(" 0 \n")
		else: print "UNSATISFABLE"
	ff.write("conflicts: " + str(total_conflicts))
	conflict_file.write("sud" + str(h) + "-" + str(total_conflicts) + "\n")

	
# If option -solve or -test: execute SatSolver
if args.solve or args.test:

	if args.output == None:
		print "Argument 'Ouptupt file' (-o, --output) required to print Sudoku solution"
		sys.exit()

	initial_time = time.clock()
	execute_glucose()
	solver_time = time.clock() - initial_time
	if args.test: print "SatSolver Time:", solver_time

if args.crypto:
	if args.output == None:
		print "Argument 'Ouptupt file' (-o, --output) required to print Sudoku solution"
		sys.exit()
	for h in range(AMOUNT):
		execute_crypto(h)


