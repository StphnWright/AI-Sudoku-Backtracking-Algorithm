#!/usr/bin/env python
#coding:utf-8

"""
Each sudoku board is represented as a dictionary with string keys and
int values.
e.g. my_board['A1'] = 8
"""
import sys
from copy import deepcopy
import time
import numpy as np

ROW = "ABCDEFGHI"
COL = "123456789"


def print_board(board):
    """Helper function to print board in a square."""
    print("-----------------")
    for i in ROW:
        row = ''
        for j in COL:
            row += (str(board[i + j]) + " ")
        print(row)


def board_to_string(board):
    """Helper function to convert board dictionary to string for writing."""
    ordered_vals = []
    for r in ROW:
        for c in COL:
            ordered_vals.append(str(board[r + c]))
    return ''.join(ordered_vals)


def backtracking(board):
    """Takes a board and returns solved board."""
    b = Sudoku(board)
    s = b.solve()
    if s is None:
        return board
    else:
        return s.board

class Sudoku:

    def __init__(self, board):
        """Initialize Sudoku object."""

        # The board as a dictionary
        self.board = board 

        # List of next guesses (starts empty by default)         
        self.guess_list = []
        
        # List of keys to all 81 squares and of all row constraints
        self.keys = []
        self.constraints_row = [] 
        
        for r in ROW:
            v = []
            for c in COL:
                k = "%s%s" % (r, c)
                v.append(k)
                self.keys.append(k)
            self.constraints_row.append(v)

        # List of all column constraints
        self.constraints_col = []
        
        for c in COL:
            v = []
            for r in ROW:
                v.append("%s%s" % (r, c))
            self.constraints_col.append(v)

        # List of all 3x3 box constraints
        # r_box and c_box are the coordinates of the top-left of each box
        # r and c are the coordinates of the row and column relative to the top-left of each box
        # Thus the row coordinate is 3*r_box + r and similarly column is 3*c_box + c
        self.constraints_box = []     
        for r_box in range(3):
            for c_box in range(3):
                v = []
                for r in range(3):
                    for c in range(3):
                        v.append("%s%s" % (ROW[3*r_box + r], COL[3*c_box + c]))
                self.constraints_box.append(v)

        # List of all constraints sets
        self.constraints_lists_all = [self.constraints_row, self.constraints_col, self.constraints_box]

        # Initialize the domain by marking all nine digits as possibilities in empty squares
        self.domain = {}
        self.unresolved = []  
        for location in self.keys:
            if self.board[location] == 0:
                self.domain[location] = [1, 2, 3, 4, 5, 6, 7, 8, 9]
                self.unresolved.append(location)
    
    def __str__(self):
        """String representation of the board for printing"""
        return board_to_string(self.board)

    def is_incomplete(self):
        """Check if the board is incomplete (contains zeros)"""
        return (0 in self.board.values())

    def is_solved(self):
        """Check if the board is solved"""
        # Check for incomplete or invalid entries
        if self.is_incomplete() or (-1 in self.board.values()):
            return False

        # Check constraints
        for constraints_list in self.constraints_lists_all:
            for constraint_list in constraints_list:
                seen = set()
                for key in constraint_list:
                    if self.board[key] in seen:
                        return False
                    else:
                        seen.add(self.board[key])

        # Board is solved
        return True

    def make_move(self, key, value):
        """ Returns the move for a candidate key and value pair (returns -1 if the move violates a constraint)"""
        for constraints_list in self.constraints_lists_all:
            for constraint_list in constraints_list:
                if key in constraint_list:
                    for k in constraint_list:
                        if value == self.board[k]:
                            return -1
        return value

    def make_moves(self, key, constraint_list):
        """Make moves associated with a given key within a given constraint list"""
        has_changes = False
        continue_loop = True
        while continue_loop:
            continue_loop = False
            for k in constraint_list:
                if self.board[k] != 0 and self.board[k] in self.domain[key]:
                    b = self.domain[key].index(self.board[k])
                    del self.domain[key][b]
                    continue_loop = True
                    has_changes = True
                    if len(self.domain[key]) == 1:
                        self.board[key] = self.make_move(key, int(self.domain[key][0]))
                        self.unresolved.remove(key)
                        del self.domain[key]
                        return False
        return has_changes

    def ac3(self):
        """Run the AC3 algorithm"""
        has_changes = True
        while has_changes:
            has_changes = False
            for constraints_list in self.constraints_lists_all:
                for constraint_list in constraints_list:
                    for key in constraint_list:
                        if key in self.unresolved:
                            has_changes = has_changes or self.make_moves(key, constraint_list)
        return

    def expand_guess_tree(self):
        """Work through the tree of guesses (recursive)"""

        # Generate the guess list
        self.guess_list = []
        for key, value in self.domain.items():
            self.guess_list.append((len(value), key))
        self.guess_list.sort()

        # Extract the first guess and delete it from the list
        next_guess = self.guess_list[0]
        del self.guess_list[0]
        key = next_guess[1]
        values_list = self.domain[key]
        del self.domain[key]
        self.unresolved.remove(key)

        # Try each value in the list
        for value in values_list:
            # Create a copy of the current puzzle
            p = deepcopy(self)

            # Assign the candidate value at the key being tested
            p.board[key] = value
            
            # Run the AC3 algorithm
            p.ac3()
            
            # Check the solution status of p
            if (p.is_solved()):
                # Solved: return p
                return p
            elif (p.is_incomplete()):
                # Incomplete: build the tree for p (recursive)
                p = p.expand_guess_tree()

                # If a valid puzzle is returned, return that
                # If not, move to the next candidate
                if p is not None:
                    return p
          
        # Didn't find any solutions
        return None

    def solve(self):
        """ Attempt to solve the Sudoku using AC3"""
        # Run AC3
        self.ac3()

        # Check the solution status of this puzzle
        if (self.is_solved()):
            # Solved: return this same puzzle
            return self
        elif (self.is_incomplete()):
            # Incomplete: build a tree and return the first valid guess
            return self.expand_guess_tree()
        else:
            # Invalid: return None 
            return None

if __name__ == '__main__':
    if len(sys.argv) > 1:
        
        # Running sudoku solver with one board $python3 sudoku.py <input_string>.
        print(sys.argv[1])
        # Parse boards to dict representation, scanning board L to R, Up to Down
        board = { ROW[r] + COL[c]: int(sys.argv[1][9*r+c])
                  for r in range(9) for c in range(9)}       
        
        solved_board = backtracking(board)
        
        # Write board to file
        out_filename = 'output.txt'
        outfile = open(out_filename, "w")
        outfile.write(board_to_string(solved_board))
        outfile.write('\n')

    else:
        # Running sudoku solver for boards in sudokus_start.txt $python3 sudoku.py

        #  Read boards from source.
        src_filename = 'sudokus_start.txt'
        try:
            srcfile = open(src_filename, "r")
            sudoku_list = srcfile.read()
        except:
            print("Error reading the sudoku file %s" % src_filename)
            exit()

        # Setup output file
        out_filename = 'output.txt'
        outfile = open(out_filename, "w")

        # Solve each board using backtracking
        for line in sudoku_list.split("\n"):

            if len(line) < 9:
                continue

            # Parse boards to dict representation, scanning board L to R, Up to Down
            board = { ROW[r] + COL[c]: int(line[9*r+c])
                      for r in range(9) for c in range(9)}

            # Print starting board. TODO: Comment this out when timing runs.
            print_board(board)

            # Solve with backtracking
            solved_board = backtracking(board)

            # Print solved board. TODO: Comment this out when timing runs.
            print_board(solved_board)

            # Write board to file
            outfile.write(board_to_string(solved_board))
            outfile.write('\n')

        print("Finishing all boards in file.")