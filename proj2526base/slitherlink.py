#!/usr/bin/python3
# slitherlink.py: Template para implementação do projeto de Inteligência Artificial 2025/2026.
# Devem alterar as classes e funções neste ficheiro de acordo com as instruções do enunciado.
# Além das funções e classes sugeridas, podem acrescentar outras que considerem pertinentes.

# Grupo 23:
# 113929 Guilherme Azevedo
# 114255 Joana Melo

import random, copy
from sys import stdin
from collections import deque

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

    def get_all_vertical_edges(self) -> list:
        res = []
        for row in range(self.rows):
            for col in range(self.cols + 1):
                res.append((row, col, 'v'))
        
        return res
    
    def get_all_horizontal_edges(self) -> list:
        res = []
        for row in range(self.rows + 1):
            for col in range(self.cols):
                res.append((row, col, 'h'))
        
        return res
    
    
    def get_numbers_board_order(self) -> list:

        cell3 = []
        cell2 = []
        cell1 = []
        other = []

        for row in range(self.rows):
            for col in range(self.cols):
                if self.grid[row][col] == '3':
                    cell3.append((row, col))
                elif self.grid[row][col] == '2':
                    cell2.append((row, col))
                elif self.grid[row][col] == '1':
                    cell1.append((row, col))
                else:
                    other.append((row, col)) 
         
        cell_order = cell3 + cell2 + cell1 + other
        order = []
        seen = set()
        for cell in cell_order:
            for e in self.get_cell_edges(cell[0], cell[1]):
                if e not in seen:
                    seen.add(e)
                    order.append(e)
        return order


    def activate_edge(self, edge: tuple, res: list = None):
        if edge not in self.activeEdges and edge not in self.blockedEdges:
            self.activeEdges.add(edge)
            if res is not None:
                res.append(edge)

    def block_edge(self, edge: tuple, res: list = None):
        if edge not in self.activeEdges and edge not in self.blockedEdges:
            self.blockedEdges.add(edge)
            if res is not None:
                res.append(edge)


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
                print('\t', end='')
            print('\n', end='')
    
    def pre_process(self):
        self.search_0_or_3()
        self.rule_cell_3_corner()
        self.rule_cell_2_corner()
        self.rule_cell_1_corner()

    
    def apply_advanced_rules(self, seed_edge = None):
        queue = deque()

        if seed_edge is not None:
            queue.append(seed_edge)
        
        else:
            for active_edge in self.activeEdges:
                queue.append(active_edge)

            for blocked_edge in self.blockedEdges:
                queue.append(blocked_edge)

        while queue:
            edge = queue[0]            

            queue.popleft()

            next_cells = self.get_next_cells(edge[0], edge[1], edge[2])
            next_edges = self.get_next_edges(edge[0], edge[1], edge[2])
 
            for cell in next_cells:
                if 0 <= cell[0] < self.rows and 0 <= cell[1] < self.cols:
                    for e in self.rule_complete_cell(cell):
                            queue.append(e)
                    for e in self.rule_general_blocked_edges_3_1(cell):
                            queue.append(e)
                    for e in self.rule_avoid_square(cell):
                            queue.append(e)

            for next_edge in next_edges: 
                if next_edge in self.activeEdges:
                    for e in self.rule_block_sides_continuous_line(next_edge):
                            queue.append(e)
                    for e in self.rule_only_one_possible_way(next_edge):
                            queue.append(e)
                    for e in self.rule_block_adjacent_edges_corner(next_edge):
                            queue.append(e)
                    for e in self.rule_avoid_micro_cycle(next_edge):
                            queue.append(e)
                for e in self.rule_dead_end(next_edge):
                        queue.append(e)


        
    def search_0_or_3(self):
        for row in range(self.rows):
            for col in range(self.cols):
                if self.grid[row][col] == '0':
                    cell_edges = self.get_cell_edges(row, col)
                    for edge in cell_edges:
                        self.block_edge(edge)
             
                elif self.grid[row][col] == '3':
                    for (cell_row, cell_col) in self.adjacent_cell((row, col))[:2]: #adjacentes
                            if self.grid[cell_row][cell_col] == '3':
                                if col == cell_col: #cima
                                    self.activate_edge((cell_row, col, 'h'))
                                    self.activate_edge((row, col, 'h'))
                                    self.activate_edge((row + 1, col, 'h'))

                                elif row == cell_row: #direita
                                    self.activate_edge((row, cell_col, 'v'))
                                    self.activate_edge((row, col, 'v'))
                                    self.activate_edge((row, col + 1, 'v'))
                                    
                    for (d_row, d_col) in self.get_diagonal_cell((row, col))[:2]: #diagonais
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
            self.activate_edge((self.rows, self.cols - 1, 'h'))
            self.activate_edge((self.rows - 1, self.cols, 'v'))


    def rule_complete_cell(self, cell: tuple) -> list:
        res = []
        row = cell[0]
        col = cell[1]
        cell_num = self.grid[row][col]

        if cell_num != '.':
            if self.get_blocked_edges(row, col) == 4 - int(cell_num):
                for edge in self.get_cell_edges(row, col):
                    self.activate_edge(edge, res)
            
            elif self.get_active_edges(row, col) == int(cell_num):
                for edge in self.get_cell_edges(row, col):
                    self.block_edge(edge, res)

        return res      
                    

    def rule_dead_end(self, edge: tuple) -> list:
        res = []

        if edge[2] == 'v':
            row = edge[0]
            col = edge[1]
            next_edges = self.get_next_edges(row, col, 'v')

            if all(x in self.blockedEdges for x in next_edges[:3]):
                self.block_edge(edge, res)
                
            if all(x in self.blockedEdges for x in next_edges[3:]):
                self.block_edge(edge, res)
                
        if edge[2] == 'h':
            row = edge[0]
            col = edge[1]
            next_edges = self.get_next_edges(row, col, 'h')

            if all(x in self.blockedEdges for x in next_edges[:3]):
                self.block_edge(edge, res)
                
            if all(x in self.blockedEdges for x in next_edges[3:]):
                self.block_edge(edge, res)
        
        return res
            

    def rule_only_one_possible_way(self, edge:tuple) -> list:
        res = []
        first_edge_side = self.get_next_edges(edge[0], edge[1], edge[2])[:3]
        possible_ways = []

        for adjacent_edge in first_edge_side:
            if adjacent_edge in self.activeEdges:
                possible_ways = []
                break
            
            if adjacent_edge not in self.blockedEdges:
                possible_ways.append(adjacent_edge)
        
        if len(possible_ways) == 1:
            self.activate_edge(possible_ways[0], res)

        second_edge_side = self.get_next_edges(edge[0], edge[1], edge[2])[3:]
        possible_ways = []

        for adjacent_edge in second_edge_side:
            if adjacent_edge in self.activeEdges:
                possible_ways = []
                break
            
            if adjacent_edge not in self.blockedEdges:
                possible_ways.append(adjacent_edge)
        
        if len(possible_ways) == 1:
            self.activate_edge(possible_ways[0], res)
    
        return res


    def rule_block_sides_continuous_line(self, edge: tuple) -> list:
        res = []
        next_edges = self.get_next_edges(edge[0], edge[1], edge[2])

        if edge[2] == 'h':
            for adjacent_edge in next_edges:
                if adjacent_edge[2] == 'h':
                    if adjacent_edge in self.activeEdges:
                        if edge[1] > adjacent_edge[1]:
                            if edge[0] < self.rows - 1:
                                self.block_edge((edge[0], edge[1], 'v'), res)
                            if edge[0] > 0:
                                self.block_edge((edge[0] - 1, edge[1], 'v'), res)
                        else:
                            if edge[0] < self.rows - 1:
                                self.block_edge((edge[0], adjacent_edge[1], 'v'), res)
                            if edge[0] > 0:
                                self.block_edge((edge[0] - 1, adjacent_edge[1], 'v'), res)

        elif edge[2] == 'v':
            for adjacent_edge in next_edges:
                if adjacent_edge[2] == 'v':
                    if adjacent_edge in self.activeEdges:
                        if edge[0] > adjacent_edge[0]:
                            if edge[1] < self.cols - 1:
                                self.block_edge((edge[0], edge[1], 'h'), res)
                            if edge[1] > 0:
                                self.block_edge((edge[0], edge[1] - 1, 'h'), res)
                        else:
                            if edge[1] < self.cols - 1:
                                self.block_edge((adjacent_edge[0], edge[1], 'h'), res)
                            if edge[1] > 0:
                                self.block_edge((adjacent_edge[0], edge[1] - 1, 'h'), res)

        return res  

    def rule_block_adjacent_edges_corner(self, edge: tuple) -> list:
        res = []
        perpendicular_active_edges = self.get_next_edges(edge[0], edge[1], edge[2])

        for adjacent_edge in list(perpendicular_active_edges):
            if adjacent_edge[2] == edge[2] or adjacent_edge not in self.activeEdges:
                perpendicular_active_edges.remove(adjacent_edge)

        for edge2 in perpendicular_active_edges:
            next_edges1 = set(self.get_next_edges(edge[0], edge[1], edge[2])) # original edge
            next_edges2 = set(self.get_next_edges(edge2[0], edge2[1], edge2[2])) 
            impossible_edges = next_edges1 & next_edges2 # interceta
            for impossible_edge in impossible_edges:
                self.block_edge(impossible_edge, res)
        
        return res

    def rule_avoid_square(self, cell: tuple) -> list:
        res = []
        if self.rows == 1 and self.cols == 1:
            return res
        
        row = cell[0]
        col = cell[1]

        if self.get_active_edges(row, col) == 3:
            for edge in self.get_cell_edges(row, col):
                if edge not in self.activeEdges:
                    self.block_edge(edge, res)

        return res


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
    

    def rule_avoid_micro_cycle(self, edge: tuple) -> list:
        res = []

        if edge in self.blockedEdges:
            return res

        next_edges = self.get_next_edges(edge[0], edge[1], edge[2])

        start = None
        for e in next_edges[:3]:
            if e in self.activeEdges:
                start = e
                break

        target = None
        for e in next_edges[3:]:
            if e in self.activeEdges:
                target = e
                break

        if start is None or target is None:
            return res

        current, previous, visited = start, edge, {edge}

        while current is not None and current not in visited:
            visited.add(current)
            next_current = None
            for next_edge in self.get_next_edges(current[0], current[1], current[2]):
                if next_edge in self.activeEdges and next_edge != previous:
                    next_current = next_edge
                    break
            previous = current
            current = next_current
            
        if target in visited:
            if visited != self.activeEdges | {edge}:
                self.block_edge(edge, res)        
            
            else:
                valid = True
                for row in range(self.rows):
                    for col in range(self.cols):
                        cellNumber = self.grid[row][col]
                        if cellNumber == '.':
                            continue
                        if self.get_active_edges(row, col) != int(cellNumber):
                            valid = False
                            break
                    if not valid:
                        break
                if not valid:
                    self.block_edge(edge, res)

        return res  

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


    def rule_general_blocked_edges_3_1(self, cell: tuple) -> list:
        res = []
        row= cell[0]
        col = cell[1]
        
        if (self.grid[row][col] == '3' and self.get_active_edges(row, col) != 3) or (self.grid[row][col] == '1' and self.get_active_edges(row, col) != 1):
            for (d_row, d_col) in self.get_diagonal_cell((row, col)):

                if d_row < row and d_col < col:     
                    external = [(row-1, col, 'v'), (row, col-1, 'h')]
        
                    if all(edge in self.blockedEdges for edge in external):
                        if self.grid[row][col] == '3':
                            self.activate_edge((row, col, 'v'), res)
                            self.activate_edge((row, col, 'h'), res)
                        if self.grid[row][col] == '1':
                            self.block_edge((row, col, 'v'), res)
                            self.block_edge((row, col, 'h'), res)

                elif d_row < row and d_col > col:
                    external = [(row-1, col+1, 'v'), (row, col+1, 'h')]
                    if all(edge in self.blockedEdges for edge in external):
                        if self.grid[row][col] == '3':
                            self.activate_edge((row, col+1, 'v'), res)
                            self.activate_edge((row, col, 'h'), res)
                        if self.grid[row][col] == '1':
                            self.block_edge((row, col+1, 'v'), res)
                            self.block_edge((row, col, 'h'), res)

                elif d_row > row and d_col > col:
                    external = [(row+1, col+1, 'v'), (row+1, col+1, 'h')]
                    if all(edge in self.blockedEdges for edge in external):
                        if self.grid[row][col] == '3':
                            self.activate_edge((row, col+1, 'v'), res)
                            self.activate_edge((row+1, col, 'h'), res)
                        if self.grid[row][col] == '1':
                            self.block_edge((row, col+1, 'v'), res)
                            self.block_edge((row+1, col, 'h'), res)

                elif d_row > row and d_col < col:
                    external = [(row+1, col, 'v'), (row+1, col-1, 'h')]
                    if all(edge in self.blockedEdges for edge in external):
                        if self.grid[row][col] == '3':
                            self.activate_edge((row, col, 'v'), res)
                            self.activate_edge((row+1, col, 'h'), res)
                        if self.grid[row][col] == '1':
                            self.block_edge((row, col, 'v'), res)
                            self.block_edge((row+1, col, 'h'), res)

        return res

    def is_invalid(self):
        for row in range(self.rows):
            for col in range(self.cols):
                cellNumber = self.grid[row][col]
                if cellNumber == '.':
                    continue
                if self.get_active_edges(row, col) > int(cellNumber):
                    return True
                if self.get_blocked_edges(row, col) > 4 - int(cellNumber):
                    return True
                
                degree = 0
                if row == self.rows - 1 or col == self.cols - 1:
                    for edge in [(row, col + 1, 'v'), (row + 1, col + 1, 'v'), (row + 1, col, 'h'), (row + 1, col + 1, 'h')]: #Vértice inferior direito
                        if edge in self.activeEdges:
                            degree += 1
 
                for edge in [(row - 1, col, 'v'), (row, col, 'v'), (row, col - 1, 'h'), (row, col, 'h')]: #Vértice superior esquerdo
                    if edge in self.activeEdges:
                        degree += 1
                
                if degree > 2:
                    return True
                
        return False
    

class Slitherlink(Problem):
    def __init__(self, board: Board, gui=None):
        """O construtor especifica o estado inicial."""
        
        initial_state = SlitherlinkState(board)
        
        # Initialize the parent 'Problem' class (Standard AIMA framework)
        super().__init__(initial_state)


    def actions(self, state: SlitherlinkState):
        """Retorna uma lista de ações que podem ser executadas a
        partir do estado passado como argumento."""
        board = state.board

        # começar por numeros do board[3,2,1,.]
        if board.is_invalid():
            return []

        for edge in board.get_numbers_board_order():
            if edge not in board.activeEdges and edge not in board.blockedEdges:
                return [("activate", edge), ("block", edge)]
        
        return []
            
    
    def result(self, state: SlitherlinkState, action):
        """Retorna o estado resultante de executar a 'action' sobre
        'state' passado como argumento. A ação a executar deve ser uma
        das presentes na lista obtida pela execução de
        self.actions(state)."""
        board = state.board
        new_board = Board(board.rows, board.cols, board.activeEdges.copy(), board.blockedEdges.copy(), board.grid)
        new_state = SlitherlinkState(new_board)

        # Unpack the action we created in the actions() function
        action_type, edge = action

        # 2. Apply the action
        if action_type == "activate":
            new_board.activeEdges.add(edge)
        elif action_type == "block":
            new_board.blockedEdges.add(edge)

        new_board.apply_advanced_rules(edge) 

        return new_state

    def goal_test(self, state: SlitherlinkState):
        """Retorna True se e só se o estado passado como argumento é
        um estado objetivo. Deve verificar se todas as posições do tabuleiro
        estão preenchidas de acordo com as regras do problema."""
        board = state.board

        if len(board.activeEdges) == 0:
            return False

        for row in range(board.rows):
            for col in range(board.cols):
                cellNumber = board.grid[row][col]
                if cellNumber == '.':
                    continue                
                if board.get_active_edges(row, col) != int(cellNumber):
                    return False
                
        first_edge = list(board.activeEdges)[0]     
        
        next_edges = board.get_next_edges(first_edge[0], first_edge[1], first_edge[2])

        start = None
        end = None

        for edge in next_edges[:3]:
            if edge in board.activeEdges:
                start = edge
                break

        for edge in next_edges[3:]:
            if edge in board.activeEdges:
                end = edge
                break
        
        current = start
        previous = first_edge
        visited = {first_edge}

        if start is not None and end is not None:
            while current != end and current is not None:
                visited.add(current)
                next_current = None
                next_edges = board.get_next_edges(current[0], current[1], current[2])
                for edge in next_edges:
                    if edge in board.activeEdges and edge != previous:
                        next_current = edge
                        break
                
                previous = current
                current = next_current

            visited.add(end)
            if current == end:
                if visited == board.activeEdges:
                    return True

        return False    

    def h(self, node: Node):
        """Função heuristica utilizada para a procura A*."""
        # TODO
        pass

    


if __name__ == "__main__":
    board = Board.parse_instance()
    board.pre_process()
    board.apply_advanced_rules()    
    problem = Slitherlink(board)
    goal = depth_first_tree_search(problem)
    goal.state.board.print_board()

