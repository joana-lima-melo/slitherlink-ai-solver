#!/usr/bin/python3
# slitherlink.py: Template para implementação do projeto de Inteligência Artificial 2025/2026.
# Devem alterar as classes e funções neste ficheiro de acordo com as instruções do enunciado.
# Além das funções e classes sugeridas, podem acrescentar outras que considerem pertinentes.

# Grupo 23:
# 113929 Guilherme Azevedo
# 114255 Joana Melo

import random, copy
from sys import stdin
from collections import defaultdict

import utils
from utils import *

from search import (
    Problem,
    Node,
    astar_search,
    breadth_first_tree_search,
    depth_first_tree_search,
    greedy_search,
    recursive_best_first_search,
)


class SlitherlinkState:
    state_id = 0

    def __init__(self, board):
        self.board = board
        self.id = SlitherlinkState.state_id
        SlitherlinkState.state_id += 1
    
    def __lt__(self, other):
        return self.id < other.id

    # TODO: outros metodos da classe

class Board:
    """Representação interna de um tabuleiro de Slitherlink."""

    def __init__(self, rows, cols, activeEdges, blockedEdges, grid):
        self.rows = rows
        self.cols = cols
        self.activeEdges = activeEdges
        self.blockedEdges = blockedEdges
        self.grid = grid

        self.total_edges = ((rows + 1) * cols) + (rows * (cols + 1))

    def adjacent_cell(self, cell:tuple) -> list:
        """Devolve uma lista das células que fazem
        fronteira com a célula enviada no argumento"""

        res = []

        if cell[0] > 0:
            res.append((cell[0] - 1, cell[1]))

        if cell[1] != self.cols - 1:
            res.append((cell[0], cell[1] + 1))

        if cell[0] != self.rows - 1:
            res.append((cell[0] + 1, cell[1]))

        if cell[1] > 0:
            res.append((cell[0], cell[1] - 1))
        
        return res
    
    def get_upper_and_right_adjacent_cell(self, cell:tuple) -> list:
        res = []

        if cell[0] > 0:
            res.append((cell[0] - 1, cell[1]))

        if cell[1] != self.cols - 1:
            res.append((cell[0], cell[1] + 1))

        return res
    
    def get_diagonal_cell(self, cell:tuple) -> list:
        """Devolve uma lista das células na diagonal com a célula enviada no argumento.
        Ordem: horária, a começar na diagonal superior esquerda"""

        res = []

        if cell[0] > 0 and cell[1] > 0:
            res.append((cell[0] - 1, cell[1] - 1))
        
        if cell[0] > 0 and cell[1] < self.cols - 1:
            res.append((cell[0] - 1, cell[1] + 1))
        
        if cell[0] < self.rows - 1 and cell[1] < self.cols - 1:
            res.append((cell[0] + 1, cell[1] + 1))

        if cell[0] < self.rows - 1 and cell[1] > 0:
            res.append((cell[0] + 1, cell[1] - 1))

        return res

    def get_upper_diagonal_cell(self, cell:tuple) -> list:
        res = []

        if cell[0] > 0 and cell[1] > 0:
            res.append((cell[0] - 1, cell[1] - 1))
        
        if cell[0] > 0 and cell[1] < self.cols - 1:
            res.append((cell[0] - 1, cell[1] + 1))
    
        return res
    

    def get_cell_edges(self, row:int, col:int) -> list:
        """Devolve os arestas da célula enviada no argumento"""

        return [(row, col, 'v'), (row, col, 'h'), (row, col + 1, 'v'), (row + 1, col, 'h')] 

    def get_active_edges(self, row:int, col:int) -> int:
        """Devolve o número de arestas ativas"""
        
        edges = self.get_cell_edges(row, col)
        res = 0

        for edge in edges:
            if(edge in self.activeEdges):
                res += 1

        return res
    
    def get_blocked_edges(self, row: int, col: int) -> int:
        """Devolve o número de arestas bloqueadas"""

        edges = self.get_cell_edges(row, col)
        res = 0

        for edge in edges:
            if(edge in self.blockedEdges):
                res += 1
        
        return res
    
    def get_next_edges(self, row: int, col: int, direction: str) -> list:
        res = []

        if direction not in ('h', 'v'):
            return res

        if direction == 'h':
            res.append((row, col - 1, 'h'))
            res.append((row, col, 'v'))
            res.append((row - 1, col, 'v'))
            res.append((row, col + 1, 'h'))
            res.append((row, col + 1, 'v'))
            res.append((row - 1, col + 1, 'v'))

        #falta se a aresta for vertical, mas é a mesma lógica, só que com as coordenadas trocadas
        
        if direction == 'v':
            res.append((row - 1, col, 'v'))
            res.append((row, col - 1, 'h'))
            res.append((row, col, 'h'))
            res.append((row + 1, col, 'v'))
            res.append((row + 1, col - 1, 'h'))
            res.append((row + 1, col, 'h'))


        return res

    def get_next_cells(self, row: int, col: int, direction: str) -> list:
        res = []

        if direction == 'v':
            res.append((row, col - 1)) #esquerda
            res.append((row, col)) #direita

        elif direction == 'h':
            res.append((row - 1, col)) #cima
            res.append((row, col)) #baixo

        return res

    def get_all_edges(self) -> list:
        res = []
        for row in range(self.rows + 1):
            for col in range(self.cols + 1):
                if row < self.rows:
                    res.append((row, col, 'v'))

                if col < self.cols:
                    res.append((row, col, 'h'))
                
        return res
    

    def activate_edge(self, edge: tuple):
        if edge not in self.activeEdges and edge not in self.blockedEdges:
            self.activeEdges.add(edge)

    def block_edge(self, edge: tuple):
        if edge not in self.activeEdges and edge not in self.blockedEdges:
            self.blockedEdges.add(edge)

    @staticmethod
    def parse_instance():
        """Lê o test do standard input (stdin) que é passado como argumento
        e retorna uma instância da classe Board.

        Por exemplo:
            $ python3 pipe.py < test-01.txt

            > from sys import stdin
            > line = stdin.readline().split() 
        """

        grid = []

        
        for line in stdin: 
            line = line.strip()
            if line:
                if '\t' in line:
                    grid.append(line.split('\t'))
                else:
                    grid.append(line.split()) #há um erro no da stora
        
        rows = len(grid)
        cols = len(grid[0])
        activeEdges = set()
        blockedEdges = set()

        #Bloquear o contorno do tabuleiro

        for row in range(-1, rows + 1):
            blockedEdges.add((row, -1, 'h'))
            blockedEdges.add((row, cols, 'h'))

        for col in range(-1, cols + 1):
            blockedEdges.add((-1, col, 'v'))
            blockedEdges.add((rows, col, 'v'))

        return Board(rows, cols, activeEdges, blockedEdges, grid)
    
    def print_board(self):
        for row in range(self.rows):
            for col in range(self.cols):
                edges_in_printing_order= self.get_cell_edges(row, col)[1:]+ [self.get_cell_edges(row, col)[0]]
                for edge in edges_in_printing_order:
                    if edge in self.activeEdges:
                        print('1', end='')
                    else:
                        print('0', end='')
                if col != self.cols - 1:
                    print('\t', end='')
            if row != self.rows - 1:
                print('\n', end='')
    
    def pre_process(self):
        self.search_0_or_3()
        self.rule_cell_3_corner()
        self.rule_cell_2_corner()
        self.rule_cell_1_corner()

        self.propagate()

    def propagate(self) -> bool:
        """
        Iteratively applies forced moves using modular helper functions.
        Returns False instantly if a contradiction is found.
        """
        changed = True
        
        while changed:
            changed = False
            
            # 1. Sweep Cells (Your original logic)
            cells_valid, cells_changed = self.sweep_cells()
            if not cells_valid:
                return False
            if cells_changed:
                changed = True
                
            # 2. Sweep Vertices (The new hyper-fast logic)
            vertices_valid, vertices_changed = self.sweep_vertices()
            if not vertices_valid:
                return False
            if vertices_changed:
                changed = True

        # 3. Final Check
        if self.has_premature_loop():
            return False
            
        return True
            

    def sweep_cells(self) -> tuple[bool, bool]:
        """Applies forced rules to numbered cells. Returns (is_valid, changed)."""
        changed = False
        for row in range(self.rows):
            for col in range(self.cols):
                cell_num = self.grid[row][col]
                if cell_num == '.':
                    continue
                    
                target = int(cell_num)
                active = self.get_active_edges(row, col)
                blocked = self.get_blocked_edges(row, col)
                empty = 4 - active - blocked
                
                if active > target or blocked > 4 - target:
                    return False, False 
                    
                if active == target and empty > 0:
                    for edge in self.get_cell_edges(row, col):
                        if edge not in self.activeEdges and edge not in self.blockedEdges:
                            self.blockedEdges.add(edge)
                            changed = True
                            
                elif active + empty == target and empty > 0:
                    for edge in self.get_cell_edges(row, col):
                        if edge not in self.activeEdges and edge not in self.blockedEdges:
                            self.activeEdges.add(edge)
                            changed = True
                            
        return True, changed


    def sweep_vertices(self) -> tuple[bool, bool]:
        """Applies intersection (vertex) continuity rules. Returns (is_valid, changed)."""
        changed = False
        
        # Loop through every intersection (vertex) on the grid
        for row in range(self.rows + 1):
            for col in range(self.cols + 1):
                # Grab the up to 4 edges touching this specific vertex
                vertex_edges = []
                if row > 0: vertex_edges.append((row - 1, col, 'v'))
                if row < self.rows: vertex_edges.append((row, col, 'v'))
                if col > 0: vertex_edges.append((row, col - 1, 'h'))
                if col < self.cols: vertex_edges.append((row, col, 'h'))

                # Count active vs empty edges using your class sets
                active_count = sum(1 for e in vertex_edges if e in self.activeEdges)
                empty_edges = [e for e in vertex_edges if e not in self.activeEdges and e not in self.blockedEdges]

                # 1. Contradiction: More than 2 lines at a single intersection
                if active_count > 2: 
                    return False, False
                    
                # 2. Perfect: Has 2 lines. Block all remaining empty edges.
                if active_count == 2 and empty_edges:
                    for e in empty_edges: 
                        self.block_edge(e)
                    changed = True
                    
                # 3. Forced: Has 1 line and 1 empty. That empty MUST be active to make 2.
                elif active_count == 1 and len(empty_edges) == 1:
                    self.activate_edge(empty_edges[0])
                    changed = True
                    
                # 4. Dead end: Has 1 line but NO emptys left. The line is trapped.
                elif active_count == 1 and len(empty_edges) == 0:
                    return False, False
                    
                # 5. Useless: Has 0 active lines and only 1 empty. Block it (lines can't start/end nowhere).
                elif active_count == 0 and len(empty_edges) == 1:
                    self.block_edge(empty_edges[0])
                    changed = True

        return True, changed



    def search_0_or_3(self):
        for row in range(self.rows):
            for col in range(self.cols):
                if self.grid[row][col] == '0':
                    cell_edges = self.get_cell_edges(row, col)
                    for edge in cell_edges:
                        self.block_edge(edge)
             
                elif self.grid[row][col] == '3' and self.get_active_edges(row, col) != 3:
                    for (cell_row, cell_col) in self.get_upper_and_right_adjacent_cell((row, col)): #adjacentes
                            if self.grid[cell_row][cell_col] == '3':
                                if col == cell_col: #cima
                                    self.activate_edge((cell_row, col, 'h'))
                                    self.activate_edge((row, col, 'h'))
                                    self.activate_edge((row + 1, col, 'h'))

                                elif row == cell_row: #direita
                                    self.activate_edge((row, cell_col, 'v'))
                                    self.activate_edge((row, col, 'v'))
                                    self.activate_edge((row, col + 1, 'v'))
                                    
                    for (d_row, d_col) in self.get_upper_diagonal_cell((row, col)): #diagonais
                            if self.grid[d_row][d_col] == '3':
                                if d_col < col:
                                    self.activate_edge((row, col + 1, 'v'))
                                    self.activate_edge((row + 1, col, 'h'))
                                    self.activate_edge((d_row, d_col, 'v'))
                                    self.activate_edge((d_row, d_col, 'h'))

                                else:
                                    self.activate_edge((row, col, 'v'))
                                    self.activate_edge((row + 1, col, 'h'))
                                    self.activate_edge((d_row, d_col + 1, 'v'))
                                    self.activate_edge((d_row, d_col, 'h'))

                    for (d_row, d_col) in self.get_diagonal_cell((row, col)):
                        if self.grid[d_row][d_col] == '0':
                            if d_row < row and d_col < col: 
                                if self.grid[row][col] == '3':    
                                    self.activate_edge((row, col, 'v'))
                                    self.activate_edge((row, col, 'h'))
                                if self.grid[row][col] == '1':
                                    self.block_edge((row, col, 'v'))
                                    self.block_edge((row, col, 'h'))

                            elif d_row < row and d_col > col:
                                if self.grid[row][col] == '3':
                                    self.activate_edge((row, col+1, 'v'))
                                    self.activate_edge((row, col, 'h'))
                                if self.grid[row][col] == '1':
                                    self.block_edge((row, col+1, 'v'))
                                    self.block_edge((row, col, 'h'))
                                
                            elif d_row > row and d_col > col:
                                if self.grid[row][col] == '3':
                                    self.activate_edge((row, col+1, 'v'))
                                    self.activate_edge((row+1, col, 'h'))
                                if self.grid[row][col] == '1':
                                    self.block_edge((row, col+1, 'v'))
                                    self.block_edge((row+1, col, 'h'))

                            elif d_row > row and d_col < col:
                                if self.grid[row][col] == '3':
                                    self.activate_edge((row, col, 'v'))
                                    self.activate_edge((row+1, col, 'h'))
                                if self.grid[row][col] == '1':
                                    self.block_edge((row, col, 'v'))
                                    self.block_edge((row+1, col, 'h'))


    def rule_cell_3_corner(self): 
               
        if self.grid[0][0] == '3': 
            self.activate_edge((0, 0, 'h'))
            self.activate_edge((0, 0, 'v'))
        
        if self.grid[0][self.cols - 1] == '3':
            self.activate_edge((0, self.cols - 1, 'h'))
            self.activate_edge((0, self.cols, 'v'))

        if self.grid[self.rows - 1][0] == '3':
            self.activate_edge((self.rows, 0, 'h'))
            self.activate_edge((self.rows - 1, 0, 'v'))
        
        if self.grid[self.rows - 1][self.cols - 1] == '3':
            self.activate_edge((self.rows, self. cols - 1, 'h'))
            self.activate_edge((self.rows - 1, self.cols, 'v'))

    
    def rule_cell_2_corner(self): 
        if self.grid[0][0] == '2':
            self.activate_edge((1, 0, 'v'))
            self.activate_edge((0, 1, 'h'))

        if self.grid[0][self.cols - 1] == '2':
            self.activate_edge((1, self.cols, 'v'))
            self.activate_edge((0, self.cols - 2, 'h'))

        if self.grid[self.rows - 1][self.cols - 1] == '2':
            self.activate_edge((self.rows - 2, self.cols, 'v'))
            self.activate_edge((self.rows, self.cols - 2, 'h'))

        if self.grid[self.rows - 1][0] == '2':
            self.activate_edge((self.rows - 2, 0, 'v'))
            self.activate_edge((self.rows, 1, 'h'))



    def rule_cell_1_corner(self):
        if self.grid[0][0] == '1': 
            self.block_edge((0, 0, 'h'))
            self.block_edge((0, 0, 'v'))
        
        if self.grid[0][self.cols - 1] == '1':
            self.block_edge((0, self.cols - 1, 'h'))
            self.block_edge((0, self.cols, 'v'))

        if self.grid[self.rows - 1][0] == '1':
            self.block_edge((self.rows, 0, 'h'))
            self.block_edge((self.rows - 1, 0, 'v'))
        
        if self.grid[self.rows - 1][self.cols - 1] == '1':
            self.block_edge((self.rows, self. cols - 1, 'h'))
            self.block_edge((self.rows - 1, self.cols, 'v'))
    
    def has_premature_loop(self) -> bool:
        """Uses a Stack (DFS) with vertex-logic to quickly find illegal closed loops."""
        if not self.activeEdges:
            return False

        visited = set()
        total_active = len(self.activeEdges)
        
        # Check every line to see if it's part of an illegal chunk
        for start_edge in self.activeEdges:
            if start_edge in visited:
                continue
                
            stack = [start_edge]
            component = set()
            vertex_degree = defaultdict(int)
            
            while stack:
                edge = stack.pop()
                if edge in component:
                    continue
                    
                component.add(edge)
                visited.add(edge)
                
                # Find the two vertices (intersections) this edge connects
                if edge[2] == 'v':
                    vertices = [(edge[0], edge[1]), (edge[0] + 1, edge[1])]
                else:
                    vertices = [(edge[0], edge[1]), (edge[0], edge[1] + 1)]
                    
                # Look at the neighboring lines extending from these two vertices
                for row, col in vertices:
                    vertex_degree[(row, col)] += 1
                    
                    vertex_edges = []
                    if row > 0: vertex_edges.append((row - 1, col, 'v'))
                    if row < self.rows: vertex_edges.append((row, col, 'v'))
                    if col > 0: vertex_edges.append((row, col - 1, 'h'))
                    if col < self.cols: vertex_edges.append((row, col, 'h'))
                    
                    # Toss all active neighbors onto the stack
                    for neighbor in vertex_edges:
                        if neighbor in self.activeEdges and neighbor not in component:
                            stack.append(neighbor)
                            
            # A chunk is a perfectly closed loop if EVERY vertex in it has exactly 2 lines
            is_closed_loop = all(deg == 2 for deg in vertex_degree.values())
            
            # If we traced a perfect closed loop, but there are other lines elsewhere on the board...
            if is_closed_loop and len(component) < total_active:
                return True # We found an illegal microloop!
                
        return False


    def get_best_empty_edge(self):
        # Search around '3's and '1's first
        for row in range(self.rows):
            for col in range(self.cols):
                if self.grid[row][col] in ('1', '3'):
                    for edge in self.get_cell_edges(row, col):
                        if edge not in self.activeEdges and edge not in self.blockedEdges:
                            return edge
                            
        # Fallback: just return the first unassigned edge you find
        for edge in self.get_all_edges():
            if edge not in self.activeEdges and edge not in self.blockedEdges:
                return edge
        return None

    def is_invalid(self) -> bool:
            """Checks if the current board state violates any basic clues or has premature loops."""
            
            # 1. Check if any numbered clues are mathematically broken
            for row in range(self.rows):
                for col in range(self.cols):
                    cell_val = self.grid[row][col]
                    if cell_val != '.':
                        # Too many active edges?
                        if self.get_active_edges(row, col) > int(cell_val):
                            return True
                        # Too many blocked edges? (Impossible to reach the target)
                        if self.get_blocked_edges(row, col) > 4 - int(cell_val):
                            return True
            
            # 2. Check for illegal premature closed loops
            if self.has_premature_loop():
                return True
                
            return False


class Slitherlink(Problem):
    def __init__(self, board: Board, gui=None):
        """O construtor especifica o estado inicial."""
        
        initial_state = SlitherlinkState(board)
        
        # Initialize the parent 'Problem' class (Standard AIMA framework)
        super().__init__(initial_state)

    def actions(self, state: SlitherlinkState):
        board = state.board
        
        edge = board.get_best_empty_edge()
        if not edge:
            return []
            
        valid_actions = []
        
        # Branch 1: Try Activating
        board_activate = Board(board.rows, board.cols, board.activeEdges.copy(), board.blockedEdges.copy(), board.grid)
        board_activate.activeEdges.add(edge)
        if board_activate.propagate(): # Runs the giant while loop. If True, it's valid!
            valid_actions.append(("activate", edge, board_activate))
            
        # Branch 2: Try Blocking
        board_block = Board(board.rows, board.cols, board.activeEdges.copy(), board.blockedEdges.copy(), board.grid)
        board_block.blockedEdges.add(edge)
        if board_block.propagate():
            valid_actions.append(("block", edge, board_block))
            
        return valid_actions
    
    def result(self, state: SlitherlinkState, action):
        """Retorna o estado resultante de executar a 'action'."""
        # Unpack the tuple we packed in the actions() function
        action_type, edge, pre_calculated_board = action

        # Because we already did all the heavy lifting (copying, advanced rules, and validity checks)
        # in the actions() method, result() becomes incredibly fast.
        return SlitherlinkState(pre_calculated_board)
    def goal_test(self, state: SlitherlinkState):
        board = state.board

        # 1. If there are ANY empty edges left, the board isn't finished.
        # (This bypasses the ghost edge counting problem completely)
        if board.get_best_empty_edge() is not None:
            return False
            
        # 2. Check if every numbered clue is perfectly satisfied
        for row in range(board.rows):
            for col in range(board.cols):
                cell = board.grid[row][col]
                if cell != '.' and board.get_active_edges(row, col) != int(cell):
                    return False
                    
        # 3. Verify there is exactly ONE continuous loop using Vertex logic
        if not board.activeEdges:
            return False

        visited = set()
        start_edge = next(iter(board.activeEdges))
        stack = [start_edge]
        
        while stack:
            edge = stack.pop()
            if edge in visited:
                continue
            visited.add(edge)
            
            # Find the two vertices this edge connects
            if edge[2] == 'v':
                vertices = [(edge[0], edge[1]), (edge[0] + 1, edge[1])]
            else:
                vertices = [(edge[0], edge[1]), (edge[0], edge[1] + 1)]
                
            for row, col in vertices:
                # Grab surrounding edges
                vertex_edges = []
                if row > 0: vertex_edges.append((row - 1, col, 'v'))
                if row < board.rows: vertex_edges.append((row, col, 'v'))
                if col > 0: vertex_edges.append((row, col - 1, 'h'))
                if col < board.cols: vertex_edges.append((row, col, 'h'))
                
                for neighbor in vertex_edges:
                    if neighbor in board.activeEdges and neighbor not in visited:
                        stack.append(neighbor)
                        
        # If the single connected component contains all active edges, it's a valid single loop!
        return len(visited) == len(board.activeEdges)
    def h(self, node: Node):
        """Função heuristica utilizada para a procura A*."""
        # TODO
        pass 

    


if __name__ == "__main__":
    board = Board.parse_instance()
    board.pre_process()
    problem = Slitherlink(board)
    goal = depth_first_tree_search(problem)
    goal.state.board.print_board()