import pygame as pg
import ast
from pygame.locals import (
    MOUSEBUTTONUP,
    K_ESCAPE,
    K_SPACE,
    KEYDOWN,
)

def get_rect(x, y):
    return x * TILE, y * TILE, TILE - 0, TILE - 0

def get_position(pos):
    "Преобразование координат клика мышки по комнате лабиринта в координаты самой комнаты"
    x = pos[0] // TILE
    y = pos[1] // TILE
    return (TILE * x, TILE * y)

def lab_to_graph(lab):
    "Преобразование лабиринта в граф. В форме списка смежности"
    graph = {}
    for x in range(0, len(lab)):
        for y in range(0, len(lab[0])):
            if lab[x][y] == 0:
                graph[(x, y)] = []
    for x, y in graph.keys():
        if y < len(lab[0]) - 1:
            if lab[x][y + 1] == 0:
                graph[(x, y)].append((x, y + 1))
                graph[(x, y + 1)].append((x, y))
        if x < len(lab) - 1:
            if lab[x + 1][y] == 0:
                graph[(x, y)].append((x + 1, y))
                graph[(x + 1, y)].append((x, y))
    return graph

def sort_graph(graph):
    """Сортируем граф по количеству ребер"""
    sorted_graph = {}
    sorted_keys = sorted(graph, key=graph.get)
    for w in sorted_keys:
        sorted_graph[w] = graph[w]
    return sorted_graph

def del_bad_paths(graph, x, y, end_x, end_y):
    """
    Функция для удаления висячих вершин графа
    Упрощаем граф перед рекурсией
    """
    for key in list(graph.keys()):
        if len(graph[key]) == 1 and key != (x,y) and key != (end_x, end_y):
            value = graph[key]
            graph.pop(key)
            graph[value[0]].remove(key)

def find_all_paths(graph, x, y, end_x, end_y, path):
    """
    Рекурсивная функция для поиска всех путей в графе.
    """
    key = (x, y)
    if len(graph[key]) == 1:
        path.append(key)
        value = graph[key]
        key = value[0]

    while len(graph[key]) == 2:
        if key in path:
            return
        else:
            path.append(key)
            value = graph[key]
            if value[0] in path:
                key = value[1]
            else:
                key = value[0]
            if key == (end_x, end_y):
                print(path, file=file1)
                return

    value = graph[key]
    path.append(key)
    for item in value:
        if item not in path:
            path1 = path.copy()
            find_all_paths(graph, item[0], item[1], end_x, end_y, path1)

def find_all_paths_alter(graph, x, y, end_x, end_y):
    """
    Алгоритм BFS для поиска кратчайшего пути в графе.
    """
    queue = [[(x, y)]]
    visited = []
    if (x, y) == (end_x, end_y):
        print("Same Node")
        return
    while queue:
        path = queue.pop(0)
        current = path[-1]
        if current not in visited:
            neighbours = graph[current]

            for neighbour in neighbours:
                new_path = list(path)
                new_path.append(neighbour)
                queue.append(new_path)

                if neighbour == (end_x, end_y):
                    print(path, file=file1)  # Записываем путь в файл all_paths.txt
                    return path
            visited.append(current)



cols, rows = 201, 201
TILE = 5

pg.init()
sc = pg.display.set_mode([cols * TILE, rows * TILE])
clock = pg.time.Clock()
Labyrintian = open('Labyrint', 'r+')
grid = []
filecontents = Labyrintian.readlines()  # Получаем лабиринт из файла Labyrint
for line in filecontents:
    obs = ast.literal_eval(line)  # Преобразуем сторку в список
    grid.append(obs)

Labyrintian.close()
graph = lab_to_graph(grid)
sc.fill(pg.Color('white'))
[[pg.draw.rect(sc, pg.Color('black'), get_rect(x, y))
  for x, col in enumerate(row) if col] for y, row in enumerate(grid)]
pg.display.flip()
count = 0
all_coordinates =[]
running = True

while running:
    if count == 3:
        file1 = open('all_paths.txt', 'r+')
        count += 1
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                running = False
            if event.key == K_SPACE and count == 4:
                sc.fill(pg.Color('white')) # Обновляем лабиринт
                [[pg.draw.rect(sc, pg.Color('black'), get_rect(x, y))
                  for x, col in enumerate(row) if col] for y, row in enumerate(grid)]
                pg.display.flip()
                currentPlace = file1.readline()  # Считываем пути из файла all_paths.txt
                data = ast.literal_eval(currentPlace)
                if data == [10]:  # Испоьзую как флаг для своевременной остановки считывания
                    file1.close()
                    count += 1
                else:
                    data.sort(key = len) # Сортируем список путей по длине
                    for x in data:
                        surf = pg.Surface((TILE, TILE))
                        surf.fill('red')
                        rect = surf.get_rect()
                        sc.blit(surf, (x[1] * TILE, x[0] * TILE))
                    pg.display.flip()
        if event.type == MOUSEBUTTONUP and count < 2:
            count += 1
            pos = pg.mouse.get_pos()  # Получаем координаты клика мышкой по лабиринту (начало и конец пути)
            coordinates = get_position(pos)
            all_coordinates.append(coordinates)
            print(coordinates, all_coordinates)
            surf = pg.Surface((TILE, TILE))  # Перекрашиваем начало и конец в красный цвет
            surf.fill((255, 0, 0))
            rect = surf.get_rect()
            sc.blit(surf, (coordinates[0], coordinates[1]))
            pg.display.flip()
        if event.type == MOUSEBUTTONUP and count == 2:
            count += 1
            if (all_coordinates[0][1] // TILE, all_coordinates[0][0] // TILE) == (all_coordinates[1][1] // TILE, all_coordinates[1][0] // TILE):
                print("Same Node")
                running = False
            if (all_coordinates[0][1] // TILE, all_coordinates[0][0] // TILE) not in graph.keys():
                print("Выбирая конец или начало пути, вы кликнули на стенку лабиринта")
                running = False
            if (all_coordinates[1][1] // TILE, all_coordinates[1][0] // TILE) not in graph.keys():
                print("Выбирая конец или начало пути, вы кликнули на стенку лабиринта")
                running = False
            path = []
            file1 = open('all_paths.txt', 'w+')  # Функция find_all_paths_alter запишет пути в файл all_paths.txt
            graph = sort_graph(graph)
            run = True
            if running == True:
                while run:
                    del_bad_paths(graph, all_coordinates[0][1] // TILE, all_coordinates[0][0] // TILE,
                                    all_coordinates[1][1] // TILE, all_coordinates[1][0] // TILE)
                    run = False
                    for key in list(graph.keys()):
                        if len(graph[key]) == 1 and key != (all_coordinates[0][1] // TILE, all_coordinates[0][0] // TILE) \
                                and key != (all_coordinates[1][1] // TILE, all_coordinates[1][0] // TILE):
                            run = True
                find_all_paths(graph, all_coordinates[0][1] // TILE, all_coordinates[0][0] // TILE,
                                    all_coordinates[1][1] // TILE, all_coordinates[1][0] // TILE, path)
            file1.write('[10]')  # Флаг конца списка путей
            file1.close()

    clock.tick(30)