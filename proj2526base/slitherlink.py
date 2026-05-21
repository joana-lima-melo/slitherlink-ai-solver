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

    def get_cell_edges(self, row:int, col:int) -> list:
        """Devolve os arestas da célula enviada no argumento"""

        return [(row, col, 'v'), (row, col, 'h'), (row, col + 1, 'v'), (row + 1, col, 'h')] #mudar a ordem do tuplo para ser (row, col, direction) para ser mais fácil de comparar com as arestas ativas e bloqueadas

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

        return Board(rows, cols, activeEdges, blockedEdges, grid)
    
    def pre_process(self):
        ""
        changed = True
        while changed:
            before_count = len(self.activeEdges) + len(self.blockedEdges)
            
            self.rule_cell_0()
            self.rule_cell_3_corner()
            self.rule_complete_cell()
            self.rule_dead_end()
            self.rule_adjacent_3()
            self.rule_only_one_possible_way()
            
            after_count = len(self.activeEdges) + len(self.blockedEdges)
            changed = (before_count != after_count)

    def rule_cell_0(self):
        for row in range(self.rows):
            for col in range(self.cols):
                if self.grid[row][col] == '0':
                    cell_edges = self.get_cell_edges(row, col)
                    for edge in cell_edges:
                        self.blockedEdges.add(edge)

    def rule_cell_3_corner(self):
        for row in range(self.rows):
            for col in range(self.cols):
                if self.grid[row][col] == '3':
                    cell_edges = self.get_cell_edges(row, col)
'''
                    if (row-1, col, 'v') and (row,col-1, 'h') in self.blockedEdges or row == 0 or col == 0 :
                        self.activeEdges.add((row, col, 'v'))
                        self.activeEdges.add((row, col, 'h'))
                    if (row+1, col-1, 'v') and (row,col+1, 'h') in self.blockedEdges or row == self.rows - 1 or col == self.cols - 1:
                        self.activeEdges.add((row, col, 'v'))
                        self.activeEdges.add((row, col + 1, 'h'))
                        if edge not in self.blockedEdges:
                            self.activeEdges.add(edge)
                    '''
        # to do
        pass
                    
    def rule_complete_cell(self):
        for row in range(self.rows):
            for col in range(self.cols):
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


    def rule_adjacent_3(self):
        for row in range(self.rows):
            for col in range(self.cols):
                if self.grid[row][col] == '3':
                    for (cell_row, cell_col) in self.adjacent_cell((row, col)):
                        if self.grid[cell_row][cell_col] == '3':
                            if row == cell_row:
                                if col > cell_col:
                                    self.activeEdges.add((row, cell_col, 'v'))
                                    self.activeEdges.add((row, col, 'v'))
                                    self.activeEdges.add((row, col + 1, 'v'))
                                else:
                                    self.activeEdges.add((row, col, 'v'))
                                    self.activeEdges.add((row, cell_col, 'v'))
                                    self.activeEdges.add((row, cell_col + 1, 'v'))

                            elif col == cell_col:
                                if row > cell_row:
                                    self.activeEdges.add((cell_row, col, 'h'))
                                    self.activeEdges.add((row, col, 'h'))
                                    self.activeEdges.add((row + 1, col, 'h'))
                                else:
                                    self.activeEdges.add((row, col, 'h'))
                                    self.activeEdges.add((cell_row, col, 'h'))
                                    self.activeEdges.add((cell_row + 1, col, 'h'))
    

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

class Slitherlink(Problem):
    def __init__(self, board: Board, gui=None):
        """O construtor especifica o estado inicial."""
        # TODO
        pass


    def actions(self, state: SlitherlinkState):
        """Retorna uma lista de ações que podem ser executadas a
        partir do estado passado como argumento."""
        # TODO
        pass


    def result(self, state: SlitherlinkState, action):
        """Retorna o estado resultante de executar a 'action' sobre
        'state' passado como argumento. A ação a executar deve ser uma
        das presentes na lista obtida pela execução de
        self.actions(state)."""
        # TODO
        pass

    def goal_test(self, state: SlitherlinkState):
        """Retorna True se e só se o estado passado como argumento é
        um estado objetivo. Deve verificar se todas as posições do tabuleiro
        estão preenchidas de acordo com as regras do problema."""
        board = state.board
        numRows = board.rows
        numCols = board.cols
        allActiveEdges = list(board.activeEdges)
        grid = board.grid

        if len(allActiveEdges) == 0:
            return False

        firstEdge = allActiveEdges[0]
        allActiveEdges.remove(firstEdge)
        nextEdges = board.get_next_edges(firstEdge[0], firstEdge[1], firstEdge[2])
        adjacent_active_edges = []
        nextEdge = ()
        for edge in nextEdges:
            if edge in allActiveEdges:
                adjacent_active_edges.append(edge)
        
        if len(adjacent_active_edges) == 0:
            return False
        nextEdge = adjacent_active_edges[0]
        allActiveEdges.remove(nextEdge)
        
        while (nextEdge != firstEdge):
            nextEdges = board.get_next_edges(nextEdge[0], nextEdge[1], nextEdge[2])
            adjacent_active_edges = []
            for edge in nextEdges:
                if edge in allActiveEdges or edge == firstEdge:
                    adjacent_active_edges.append(edge)
            if len(adjacent_active_edges) != 1:
                return False
            nextEdge = adjacent_active_edges[0]
            if nextEdge != firstEdge:
                allActiveEdges.remove(nextEdge)

        if len(allActiveEdges) != 0:
            return False

        for row in range(numRows):
            for col in range(numCols):
                cellNumber = grid[row][col]
                if cellNumber == '.':
                    continue                
                if board.get_active_edges(row, col) != int(cellNumber):
                    return False
        
        return True        

    def h(self, node: Node):
        """Função heuristica utilizada para a procura A*."""
        # TODO
        pass

    


if __name__ == "__main__":
    # TODO:
    # Ler o ficheiro do standard input,
    # Usar uma técnica de procura para resolver a instância,
    # Retirar a solução a partir do nó resultante,
    # Imprimir para o standard output no formato indicado.
    pass







