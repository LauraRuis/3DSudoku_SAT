import cnf

class sudoku3d:

    def __init__(self, fname):
        f = open(fname)
        self.order, self.m = map(int, f.readline().split()[1:3])
        self.n = self.order / self.m
        sudlist = [f.readline().split() for i in range(self.order*self.order)]
        sudoku_list = []
        i = 0
        while i<(self.order*self.order):
                sudoku_list.append(sudlist[i:i+self.order])
                i+=self.order
        self.sudoku = sudoku_list


    def variable(self,z, row,col,num):
        """Return the variable which represents a (z, row,col,num)."""
        return z * self.order**3 + row * self.order**2 + col * self.order + num + 1 # +1 to avoid 0

    def sameCell(self, z, row, col, num ):
        return [self.variable(z, row,col,i) for i in range(self.order) if i != num]

    def sameRow(self, z, row, col, num ):
        return [self.variable(z, row,i,num) for i in range(self.order) if i != col]

    def sameCol(self, z, row, col, num ):
        return [self.variable(z, i,col,num) for i in range(self.order) if i != row]

    def sameZ(self, z, row, col, num ):
        return[self.variable(i, row, col, num) for i in range(self.order) if i!= z]

    def sameBlock(self, z, row, col, num ):
        init_row = (row/self.m)*self.m
        init_col = (col/self.n)*self.n
        init_z = (z/self.m)*self.m
        variables = [[self.variable(z, init_row + i,init_col+j,num) for i in range(self.m) for j in range(self.n) if (i != row%self.m or j != col%self.n)], 
        [self.variable(init_z+i, row,init_col+j,num) for i in range(self.m) for j in range(self.n) if (i != row%self.m or j != col%self.n)], 
        [self.variable(init_z+j, init_row + i, col,num) for i in range(self.m) for j in range(self.n) if (i != row%self.m or j != col%self.n)]]
        return [var for sublist in variables for var in sublist]

    def extended_translate_to_CNF(self): # not edited yet, only use optimized for now
        """ Translate to CNF all restrictions with all variales"""

        cnff = cnf.CNF_formula(self.order**3)
        
        for i in range(self.order):
            for j in range(self.order):
                A = [  self.variable(i,j,k) for k in range(self.order)]
                cnff.exacly_one(A)# Cell restrictions
                B = [  self.variable(i,k,j) for k in range(self.order)]
                cnff.exacly_one(B)# Row restrictions
                C = [  self.variable(k,i,j) for k in range(self.order)]
                cnff.exacly_one(C)# Col restrictions
                if self.sudoku[i][j] != "-1": #Fixed variables restrictions
                    cnff.addclause([self.variable(i,j,int(self.sudoku[i][j]))])

        #Region restrictions
        for region in range(self.order):
            i,j =  (region/self.m)*self.m,(region%self.m)*self.n
            for num in range(self.order):
                D = [ self.variable(i+i_inc,j+j_inc,num)  for i_inc in range(self.n)
                      for j_inc in range(self.m) ]
                cnff.exacly_one(D)
        
        return cnff,[i for i in range((self.order**3)+1)]

    def optimized_translate_to_CNF(self):
        """Translate to CNF with only the unknow variables"""

        useful_vars = [i for i in range((self.order**4)+1)] # length * width * height * numvars
        prefixed=[]
        
        for z in range(self.order):
            for row in range(self.order):
                for col in range(self.order):
                    if self.sudoku[z][row][col] != "-1": #Fixed variables restrictions
                            num = int (self.sudoku[z][row][col])
                        
                            prefixed.extend(self.sameCell(z,row,col,num))
                            prefixed.extend(self.sameRow(z,row,col,num))
                            prefixed.extend(self.sameCol(z,row,col,num))
                            prefixed.extend(self.sameZ(z,row,col,num))
                            
		    
        prefixed = list(set(prefixed)) # Delete duplicates and sort the list

        for var in prefixed:
            useful_vars[var]=-1
        counter = 0
        for i in range(len(useful_vars)):
            if useful_vars[i] >= 0:
                useful_vars[i] = counter
                counter+=1

        cnff = cnf.CNF_formula(counter-1)
 
        def invalid(item):
            return  item != -1
        for h in range(self.order):
            for i in range(self.order):
                for j in range(self.order):
                    #Cell Restrictions: i=rows, j=cols
                    if self.sudoku[h][i][j] == "-1":
                        A = filter(invalid,[ useful_vars[self.variable(h,i,j,k)] for k in range(self.order)])
                        cnff.exacly_one(A)
                    else:
                        cnff.addclause([useful_vars[self.variable(h,i,j,int(self.sudoku[h][i][j]))]])
                    #Row Restrictions:
                    B = filter(invalid,[useful_vars[self.variable(h,i,k,j)] for k in range(self.order)])
                    if B != []: cnff.exacly_one(B)
                    #Col Restrictions:
                    C = filter(invalid,[useful_vars[self.variable(h,k,i,j)] for k in range(self.order)])
                    if C != []: cnff.exacly_one(C)
                    #Z restrictions
                    E = filter(invalid,[useful_vars[self.variable(k,h,i,j)] for k in range(self.order)])
                    if E != []: cnff.exacly_one(E)
        
        #Region restrictions 
        for h in range(self.order):
            for region in range(self.order):
              i,j =  (region/self.m)*self.m,(region%self.m)*self.n
              for num in range(self.order):
                  D = filter(invalid,[ useful_vars[self.variable(h, i+i_inc,j+j_inc,num)]
                              for i_inc in range(self.n) for j_inc in range(self.m)])
                  if D != []:cnff.exacly_one(D)
                  F = filter(invalid,[ useful_vars[self.variable(j+j_inc, h,i+i_inc,num)]
                            for i_inc in range(self.n) for j_inc in range(self.m)])
                  if F != []:cnff.exacly_one(F)
                  G = filter(invalid,[ useful_vars[self.variable(i+i_inc, j+j_inc,h,num)]
                            for i_inc in range(self.n) for j_inc in range(self.m)])
                  if G != []:cnff.exacly_one(G) 

        return cnff,useful_vars

