Slitherlink Solver

Este projeto resolve automaticamente puzzles Slitherlink.

O objetivo do jogo é desenhar um único loop fechado numa grelha, ligando pontos adjacentes, respeitando os números em cada célula. Cada número indica quantas arestas dessa célula fazem parte do loop.

O programa lê um puzzle a partir do input e devolve uma solução válida, representando quais as arestas que estão ativas em cada célula.

Como funciona

A solução é baseada em técnicas de procura, onde o programa vai explorando diferentes configurações possíveis até encontrar uma que respeite todas as regras do puzzle.

Input

O input é uma grelha com:

números (0 a 3) → restrições
. → células sem restrição
Output

Para cada célula, o programa indica as arestas ativas usando 4 dígitos binários:

[top, right, bottom, left]
Como correr
python slitherlink.py < input.txt
