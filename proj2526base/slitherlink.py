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

    def propagate_edge(self):
        
        next_edges = self.get_next_edges(edge[0], edge[1], edge[2])
        cells= 
        

        changed = True

        while changed:
            before_count = len(self.activeEdges) + len(self.blockedEdges)

            self.rule_complete_cell(cells)
            self.rule_dead_end()
            self.rule_only_one_possible_way()
            self.rule_block_sides_continuous_line()
            self.rule_block_adjacent_edges_corner()
            self.rule_block_remaining_cell_edges()
            self.rule_avoid_square()
            self.rule_adjacent_blocked_edges_3()
            self.rule_adjacent_blocked_edges_1()
            self.rule_avoid_micro_cycle()
            
            after_count = len(self.activeEdges) + len(self.blockedEdges)
            changed = (before_count != after_count)

    
    def search_0_or_3(self):
        for row in range(self.rows):
            for col in range(self.cols):
                if self.grid[row][col] == '0':
                    cell_edges = self.get_cell_edges(row, col)
                    for edge in cell_edges:
                        self.blockedEdges.add(edge)

                
                elif self.grid[row][col] == '3':
                    for (cell_row, cell_col) in self.adjacent_cell((row, col))[:2]: #adjacentes
                            if self.grid[cell_row][cell_col] == '3':
                                if col == cell_col: #cima
                                    self.activeEdges.add((cell_row, col, 'h'))
                                    self.activeEdges.add((row, col, 'h'))
                                    self.activeEdges.add((row + 1, col, 'h'))
                                
                                elif row == cell_row: #direita
                                    self.activeEdges.add((row, cell_col, 'v'))
                                    self.activeEdges.add((row, col, 'v'))
                                    self.activeEdges.add((row, col + 1, 'v'))
                                    
                    for (d_row, d_col) in self.get_diagonal_cell((row, col))[:2]: #diagonais
                            if self.grid[d_row][d_col] == '3':
                                if d_col < col:
                                    self.activeEdges.add((row, col + 1, 'v'))
                                    self.activeEdges.add((row + 1, col, 'h'))
                                    self.activeEdges.add((d_row, d_col, 'v'))
                                    self.activeEdges.add((d_row, d_col, 'h'))

                                else:
                                    self.activeEdges.add((row, col, 'v'))
                                    self.activeEdges.add((row + 1, col, 'h'))
                                    self.activeEdges.add((d_row, d_col + 1, 'v'))
                                    self.activeEdges.add((d_row, d_col, 'h'))


    def rule_cell_3_corner(self):
        
               
        if self.grid[0][0] == '3': 
            self.activeEdges.add((0, 0, 'h'))
            self.activeEdges.add((0, 0, 'v'))
        
        if self.grid[0][self.cols - 1] == '3':
            self.activeEdges.add((0, self.cols - 1, 'h'))
            self.activeEdges.add((0, self.cols, 'v'))

        if self.grid[self.rows - 1][0] == '3':
            self.activeEdges.add((self.rows, 0, 'h'))
            self.activeEdges.add((self.rows - 1, 0, 'v'))
        
        if self.grid[self.rows - 1][self.cols - 1] == '3':
            self.activeEdges.add((self.rows, self. cols - 1, 'h'))
            self.activeEdges.add((self.rows - 1, self.cols, 'v'))

                    
    def rule_complete_cell():
                
                cell_num = self.grid[row][col]

                if cell_num == '.':
                    continue
                
                if self.get_blocked_edges(row, col) == 4 - int(cell_num):
                    for edge in self.get_cell_edges(row, col):
                        if edge not in self.blockedEdges:
                            self.activeEdges.add(edge)
                    

    def rule_dead_end(self):
        for vertical in self.get_all_vertical_edges():
            row = vertical[0]
            col = vertical[1]
            next_edges = self.get_next_edges(row, col, 'v')

            if all(x in self.blockedEdges for x in next_edges[:3]):
                self.blockedEdges.add(vertical)
                continue

            if all(x in self.blockedEdges for x in next_edges[3:]):
                self.blockedEdges.add(vertical)
                continue

        for horizontal in self.get_all_horizontal_edges():
            row = horizontal[0]
            col = horizontal[1]
            next_edges = self.get_next_edges(row, col, 'h')

            if all(x in self.blockedEdges for x in next_edges[:3]):
                self.blockedEdges.add(horizontal)
                continue

            if all(x in self.blockedEdges for x in next_edges[3:]):
                self.blockedEdges.add(horizontal)
                continue

    

    def rule_only_one_possible_way(self):
        for edge in list(self.activeEdges):
            first_edge_side = self.get_next_edges(edge[0], edge[1], edge[2])[:3]
            possible_ways = []

            for adjacent_edge in first_edge_side:
                if adjacent_edge in self.activeEdges:
                    possible_ways = []
                    break
                
                if adjacent_edge not in self.blockedEdges:
                    possible_ways.append(adjacent_edge)
            
            if len(possible_ways) == 1:
                self.activeEdges.add(possible_ways[0])

            second_edge_side = self.get_next_edges(edge[0], edge[1], edge[2])[3:]
            possible_ways = []

            for adjacent_edge in second_edge_side:
                if adjacent_edge in self.activeEdges:
                    possible_ways = []
                    break
                
                if adjacent_edge not in self.blockedEdges:
                    possible_ways.append(adjacent_edge)
            
            if len(possible_ways) == 1:
                self.activeEdges.add(possible_ways[0])


    def rule_block_sides_continuous_line(self):
        for edge in self.activeEdges:
            next_edges = self.get_next_edges(edge[0], edge[1], edge[2])

            if edge[2] == 'h':
                for adjacent_edge in next_edges:
                    if adjacent_edge[2] == 'h':
                        if adjacent_edge in self.activeEdges:
                            if edge[1] > adjacent_edge[1]:
                                if edge[0] < self.rows - 1:
                                    self.blockedEdges.add((edge[0], edge[1], 'v'))
                                if edge[0] > 0:
                                    self.blockedEdges.add((edge[0] - 1, edge[1], 'v'))
                            else:
                                if edge[0] < self.rows - 1:
                                    self.blockedEdges.add((edge[0], adjacent_edge[1], 'v'))
                                if edge[0] > 0:
                                    self.blockedEdges.add((edge[0] - 1, adjacent_edge[1], 'v'))

            elif edge[2] == 'v':
                for adjacent_edge in next_edges:
                    if adjacent_edge[2] == 'v':
                        if adjacent_edge in self.activeEdges:
                            if edge[0] > adjacent_edge[0]:
                                if edge[1] < self.cols - 1:
                                    self.blockedEdges.add((edge[0], edge[1], 'h'))
                                if edge[1] > 0:
                                    self.blockedEdges.add((edge[0], edge[1] - 1, 'h'))
                            else:
                                if edge[1] < self.cols - 1:
                                    self.blockedEdges.add((adjacent_edge[0], edge[1], 'h'))
                                if edge[1] > 0:
                                    self.blockedEdges.add((adjacent_edge[0], edge[1] - 1, 'h'))
    

    def rule_block_adjacent_edges_corner(self):
        for edge in self.activeEdges:
            perpendicular_active_edges = self.get_next_edges(edge[0], edge[1], edge[2])
            for adjacent_edge in list(perpendicular_active_edges):
                if adjacent_edge[2] == edge[2] or adjacent_edge not in self.activeEdges:
                    perpendicular_active_edges.remove(adjacent_edge)

            for edge2 in perpendicular_active_edges:
                next_edges1 = set(self.get_next_edges(edge[0], edge[1], edge[2])) # original edge
                next_edges2 = set(self.get_next_edges(edge2[0], edge2[1], edge2[2])) 
                impossible_edges = next_edges1 & next_edges2 #& interceta
                for impossible_edge in impossible_edges:
                    self.blockedEdges.add(impossible_edge)
    

    def rule_block_remaining_cell_edges(self):         
        for row in range(self.rows):
            for col in range(self.cols):
                if self.grid[row][col] == '.':
                    continue
                
                if self.get_active_edges(row, col) == int(self.grid[row][col]):
                    for edge in self.get_cell_edges(row, col):
                        if edge not in self.activeEdges:
                            self.blockedEdges.add(edge)
    

    def rule_avoid_square(self):
        if self.rows == 1 and self.cols == 1: # lol se o tabuleiro for só uma celula
            return

        for row in range(self.rows):
            for col in range(self.cols):
                if self.grid[row][col] == '.':
                    if self.get_active_edges(row, col) == 3:
                        for edge in self.get_cell_edges(row, col):
                            if edge not in self.activeEdges:
                                self.blockedEdges.add(edge)


    def rule_cell_1_corner(self):
        if self.grid[0][0] == '1': 
            self.blockedEdges.add((0, 0, 'h'))
            self.blockedEdges.add((0, 0, 'v'))
        
        if self.grid[0][self.cols - 1] == '1':
            self.blockedEdges.add((0, self.cols - 1, 'h'))
            self.blockedEdges.add((0, self.cols, 'v'))

        if self.grid[self.rows - 1][0] == '1':
            self.blockedEdges.add((self.rows, 0, 'h'))
            self.blockedEdges.add((self.rows - 1, 0, 'v'))
        
        if self.grid[self.rows - 1][self.cols - 1] == '1':
            self.blockedEdges.add((self.rows, self. cols - 1, 'h'))
            self.blockedEdges.add((self.rows - 1, self.cols, 'v'))
    

    def rule_avoid_micro_cycle(self):
        all_edges = self.get_all_horizontal_edges() + self.get_all_vertical_edges()

        for edge in all_edges:
            if edge in self.activeEdges or edge in self.blockedEdges:
                continue

            next_edges = self.get_next_edges(edge[0], edge[1], edge[2])

            start = None
            for edge in next_edges[:3]:
                if edge in self.activeEdges:
                    start = edge
                    break

            target = None
            for edge in next_edges[3:]:
                if edge in self.activeEdges:
                    target = edge
                    break

            if start is None or target is None:
                continue

            current, previous, visited = start, edge, {edge}

            for _ in range(len(self.activeEdges)):
                visited.add(current)
            
                next_step = None
                for edge in self.get_next_edges(current[0], current[1], current[2]):
                    if edge in self.activeEdges and edge != previous:
                        next_step = edge
                        break
                        
                previous = current
                current = next_step
                
                if current is None or current in visited:
                    break

            if target not in visited:
                continue

            if visited - {edge} != self.activeEdges:
                self.blockedEdges.add(edge)
            else:

                invalid_cells = False
                for r in range(self.rows):
                    for c in range(self.cols):
                        if self.grid[r][c] != '.' and self.get_active_edges(r, c) != int(self.grid[r][c]):
                            invalid_cells = True
                            break
                    if invalid_cells:
                        break
                        
                if invalid_cells:
                    self.blockedEdges.add(edge)           


    def rule_cell_2_corner(self): # good but i should do also do one for the edges, or just like blocked adjacent
        if self.grid[0][0] == '2':
            self.activeEdges.add((1, 0, 'v'))
            self.activeEdges.add((0, 1, 'h'))

        if self.grid[0][self.cols - 1] == '2':
            self.activeEdges.add((1, self.cols, 'v'))
            self.activeEdges.add((0, self.cols - 2, 'h'))

        if self.grid[self.rows - 1][self.cols - 1] == '2':
            self.activeEdges.add((self.rows - 2, self.cols, 'v'))
            self.activeEdges.add((self.rows, self.cols - 2, 'h'))

        if self.grid[self.rows - 1][0] == '2':
            self.activeEdges.add((self.rows - 2, 0, 'v'))
            self.activeEdges.add((self.rows, 1, 'h'))


    def rule_adjacent_blocked_edges_3(self):
        for row in range(self.rows):
            for col in range(self.cols):
                if self.grid[row][col] != '3' or self.get_active_edges(row, col) == 3:
                    continue
                for (d_row, d_col) in self.get_diagonal_cell((row, col)):

                    if d_row < row and d_col < col:     
                        external = [(row-1, col, 'v'), (row, col-1, 'h')]
                        if all(edge in self.blockedEdges for edge in external):
                            self.activeEdges.add((row, col, 'v'))
                            self.activeEdges.add((row, col, 'h'))

                    elif d_row < row and d_col > col:
                        external = [(row-1, col+1, 'v'), (row, col+1, 'h')]
                        if all(edge in self.blockedEdges for edge in external):
                            self.activeEdges.add((row, col+1, 'v'))
                            self.activeEdges.add((row, col, 'h'))

                    elif d_row > row and d_col > col:
                        external = [(row+1, col+1, 'v'), (row+1, col+1, 'h')]
                        if all(edge in self.blockedEdges for edge in external):
                            self.activeEdges.add((row, col+1, 'v'))
                            self.activeEdges.add((row+1, col, 'h'))

                    elif d_row > row and d_col < col:
                        external = [(row+1, col, 'v'), (row+1, col-1, 'h')]
                        if all(edge in self.blockedEdges for edge in external):
                            self.activeEdges.add((row, col, 'v'))
                            self.activeEdges.add((row+1, col, 'h'))


    def rule_adjacent_blocked_edges_1(self):
        for row in range(self.rows):
            for col in range(self.cols):
                if self.grid[row][col] != '1' or self.get_active_edges(row, col) == 1:
                    continue
                for (d_row, d_col) in self.get_diagonal_cell((row, col)):

                    if d_row < row and d_col < col:
                        external = [(row-1, col, 'v'), (row, col-1, 'h')]
                        if all(edge in self.blockedEdges for edge in external):
                            self.blockedEdges.add((row, col, 'v'))
                            self.blockedEdges.add((row, col, 'h'))

                    elif d_row < row and d_col > col:
                        external = [(row-1, col+1, 'v'), (row, col+1, 'h')]
                        if all(edge in self.blockedEdges for edge in external):
                            self.blockedEdges.add((row, col+1, 'v'))
                            self.blockedEdges.add((row, col, 'h'))

                    elif d_row > row and d_col > col:
                        external = [(row+1, col+1, 'v'), (row+1, col+1, 'h')]
                        if all(edge in self.blockedEdges for edge in external):
                            self.blockedEdges.add((row, col+1, 'v'))
                            self.blockedEdges.add((row+1, col, 'h'))

                    elif d_row > row and d_col < col:
                        external = [(row+1, col, 'v'), (row+1, col-1, 'h')]
                        if all(edge in self.blockedEdges for edge in external):
                            self.blockedEdges.add((row, col, 'v'))
                            self.blockedEdges.add((row+1, col, 'h'))

        

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

        # começar por arestas ativas
        for active_edge in board.activeEdges:
            next_to_active_edge = board.get_next_edges(active_edge[0], active_edge[1], active_edge[2])
            for edge in next_to_active_edge:
                if edge not in board.activeEdges and edge not in board.blockedEdges:
                    return [("activate", edge), ("block", edge)]

        # ver qualquer uma se ainda não houver arestas ativas
        all_edges = board.get_all_horizontal_edges() + board.get_all_vertical_edges()
        for edge in all_edges:
            if edge not in board.activeEdges and edge not in board.blockedEdges:
                return [("activate", edge), ("block", edge)]

        return []

    def result(self, state: SlitherlinkState, action):
        """Retorna o estado resultante de executar a 'action' sobre
        'state' passado como argumento. A ação a executar deve ser uma
        das presentes na lista obtida pela execução de
        self.actions(state)."""
        new_state = copy.deepcopy(state)
        new_board = new_state.board

        # Unpack the action we created in the actions() function
        action_type, edge = action

        # 2. Apply the action
        if action_type == "activate":
            new_board.activeEdges.add(edge)
        elif action_type == "block":
            new_board.blockedEdges.add(edge)

        new_board.apply_advanced_rules() 

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
        current_edge = first_edge  
        previous_edge = None      
        count_edges_cicle = 0
        for _ in range(len(board.activeEdges)):
            
            next_edges = board.get_next_edges(current_edge[0], current_edge[1], current_edge[2])

            side1 = []
            side2 =[]

            for edge in next_edges[:3]:
                if edge in board.activeEdges:
                    side1.append(edge)

            for edge in next_edges[3:]:
                if edge in board.activeEdges:
                    side2.append(edge)
            
            if len(side1) != 1 or len(side2) != 1 :
                return False
            
            count_edges_cicle += 1

            active_next_edges = side1 + side2
            
            for edge in active_next_edges:
                if edge != previous_edge:
                    previous_edge = current_edge
                    current_edge = edge
                    break
                    
            if current_edge == first_edge:
                if count_edges_cicle == len(board.activeEdges):
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

