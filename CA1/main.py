# SNAKE WITH PORTALS!

# needed libraries
import os
import sys
import asyncio
import websockets
import json
import webbrowser
import time
# from IPython.display import display, HTML
from functools import partial
from copy import deepcopy
import heapq
import itertools
from queue import deque
from game import *



# ---------------
# Configs
map_dir_path = "maps"

DIRS = {"U": (-1, 0), "D": (1, 0), "L": (0, -1), "R": (0, 1)}

DFS_limit = None
IDS_max_depth = 1000
time_limit = 100.0

# ---------------
"""
Snake Needs Your HELP!!

---

Your time to code !

step 1. define your state,

 when traversing the game graph, what would be apporpiate for nodes to contain?

"""
# ------ TODO ------

def get_initial_state(game):

    snake_body = tuple(game.snake.body)
    apples = frozenset(game.board.apples)
    state = (snake_body, apples)
    
    return state

# ---------------

"""
step 2. now you need to calculate the next state,

 think in the game graph when snake makes a move, what would the next
child node be?
"""
# ------ TODO ------


def next_state(state, board, action):

    snake_body, apples = state
    head_r, head_c = snake_body[0]
    
    if action not in DIRS:
        return None
        
    dr, dc = DIRS[action]
    
    new_r = (head_r + dr) % board.height
    new_c = (head_c + dc) % board.width
    new_head = (new_r, new_c)

    

    if new_head in board.portals:
        new_head = board.portals[new_head]
        

    if new_head in board.walls:
        return None
        

    if new_head in apples:
        new_snake_body = (new_head,) + snake_body
        new_apples = frozenset(apple for apple in apples if apple != new_head)
    else:
 
        new_snake_body = (new_head,) + snake_body[:-1]
        new_apples = apples
        
 
    if new_head in new_snake_body[1:]:
        return None
        
    return (new_snake_body, new_apples)




# ---------------

"""
step 3. implement solvers!

if the solver finds a path then return path and number of visited nodes

if the solver doesn't find a path or exceeds the time limit return an empty list and number of visited nodes 

you can check if it exceeds the time limit using time.perf_counter() which returns systems current time and time_limit variable defined in config above
"""

# ------ TODO ------




def solve_bfs(game):
    board = game.board
    initial_snake = tuple(game.snake.body)
    initial_apples = frozenset(board.apples)
    initial_state = (initial_snake, initial_apples)
    queue = deque([(initial_state, [])])
    visited = set()
    visited.add(initial_state)
    visited_nodes = 0
    
    while queue:
    
        current_state, path = queue.popleft()
        visited_nodes += 1
        current_snake, current_apples = current_state

        if len(current_apples) == 0:
            return path, visited_nodes 
            
        for action in game.DIRECTIONS:

            next_st = next_state(current_state, board, action)
            
    
            if next_st is not None and next_st not in visited:
                visited.add(next_st)              
                new_path = path + [action]     
                queue.append((next_st, new_path)) 
                

    return None, visited_nodes






import time

def solve_dfs(game, depth_limit=None):
    board = game.board
    initial_state = (tuple(game.snake.body), frozenset(board.apples))
    stack = [initial_state]
    visited = set([initial_state])
    parent_map = {initial_state: (None, None)}
    visited_nodes = 0
    start_time = time.perf_counter()

    while stack:

        if time.perf_counter() - start_time > 10:
            break

        current_state = stack.pop()
        visited_nodes += 1
        snake, apples = current_state

        if len(apples) == 0:
           
            path = []
            curr = current_state
            while parent_map[curr][0] is not None:
                prev_state, action = parent_map[curr]
                path.append(action)
                curr = prev_state
            path.reverse() 
            return path, visited_nodes

        for action in reversed(game.DIRECTIONS):
            next_st = next_state(current_state, board, action)
            
            if next_st is not None and next_st not in visited:
                visited.add(next_st)
                parent_map[next_st] = (current_state, action)
                stack.append(next_st)

    return [], visited_nodes







def depth_limited_search(board, state, depth_limit, visited, total_visited_set):
    total_visited_set.add(state)
    current_snake, current_apples = state

    if len(current_apples) == 0:
        return [], False 
        
    if depth_limit == 0:
        return None, True  
        
    cutoff_occurred = False
    directions = ['U', 'D', 'L', 'R']
    
    for action in directions:
        next_st = next_state(state, board, action)
      
        if next_st is not None and next_st not in visited:
         
            visited.add(next_st)
    
            result_path, is_cutoff = depth_limited_search(
                board, next_st, depth_limit - 1, visited, total_visited_set
            )
            
            visited.remove(next_st)
            
            if is_cutoff:
                cutoff_occurred = True
 
            elif result_path is not None:
                return [action] + result_path, False
                
 
    return None, cutoff_occurred


def solve_ids(game, max_depth=IDS_max_depth):
    board = game.board
    initial_snake = tuple(game.snake.body)
    initial_apples = frozenset(board.apples)
    initial_state = (initial_snake, initial_apples)
    total_visited_set = set()
    
    for depth in range(max_depth + 1):
        visited = set()
        visited.add(initial_state)
        path, is_cutoff = depth_limited_search(
            board, initial_state, depth, visited, total_visited_set
        )
    
        if path is not None:
            return path, len(total_visited_set)
            
        if not is_cutoff:
            return [], len(total_visited_set)
            
    return [], len(total_visited_set)



"""
DO NOT FORGET TO ADD YOUR HEURISTIC FUNCTIONS' NAME TO THE heuristics LIST BELOW, 
OTHERWISE THE GUI WOULDN'T RECOGNIZE IT."""

# ------ TODO ------





def toroidal_distance(p1, p2, width, height):
    r1, c1 = p1
    r2, c2 = p2
    dr = min(abs(r1 - r2), height - abs(r1 - r2))
    dc = min(abs(c1 - c2), width - abs(c1 - c2))
    return dr + dc






def dummy_heuristic(state, board):
    return 0




def h_apple_count(state, board):
    _, apples = state
    return len(apples)




def h_closest_apple(state, board):
    snake_body, apples = state
    if not apples:
        return 0
    head = snake_body[0]
    return min(toroidal_distance(head, a, board.width, board.height) for a in apples)





def h_furthest_apple(state, board):
    snake_body, apples = state
    if not apples:
        return 0

    head = snake_body[0]
    return max(toroidal_distance(head, a, board.width, board.height) for a in apples)

heuristics = [dummy_heuristic, h_apple_count, h_closest_apple, h_furthest_apple]
heuristic_map = {func.__name__: func for func in heuristics}









def solve_a_star(game, heuristic, weight=1):
    board = game.board
    initial_snake = tuple(game.snake.body)
    initial_apples = frozenset(board.apples)
    initial_state = (initial_snake, initial_apples)
    counter = 0 
    pq = []
    g_start = 0
    h_start = heuristic(initial_state, board)
    f_start = g_start + (weight * h_start)
    heapq.heappush(pq, (f_start, g_start, counter, initial_state, []))
    visited = {initial_state: g_start}
    visited_nodes = 0
    
    while pq:
        f, g, _, current_state, path = heapq.heappop(pq)
        visited_nodes += 1
        
        current_snake, current_apples = current_state
        
        if len(current_apples) == 0:
            return path, visited_nodes
            
        if g > visited.get(current_state, float('inf')):
            continue
            
        for action in game.DIRECTIONS:
            next_st = next_state(current_state, board, action)
            
            if next_st is not None:
                new_g = g + 1
        
                if next_st not in visited or new_g < visited[next_st]:
                    visited[next_st] = new_g
                    new_h = heuristic(next_st, board)
                    new_f = new_g + (weight * new_h)
                    counter += 1
                    new_path = path + [action]
                    heapq.heappush(pq, (new_f, new_g, counter, next_st, new_path))
                    

    return [], visited_nodes



# ---------------

"""
Time to see our snake ! 
"""

def is_running_in_jupyter():
    try:
        # shell = get_ipython().__class__.__name__
        
        # if shell == 'ZMQInteractiveShell':
        #     return True 
        # elif shell == 'TerminalInteractiveShell':
        #     return False
        # else:
            return False
            
    except NameError:
        return False

async def handler(websocket, game, shutdown_event):
    print("Browser connected.")

    await websocket.send(
            json.dumps(
                {
                    "type": "env",
                    "env": "jupyter" if is_running_in_jupyter() else "shell"
                }
            )
        )
    

    try:
        async for message in websocket:
            data = json.loads(message)
            msg_type = data.get("type")

            if msg_type == "init":
                game.reset(map_dir_path + "/" + data.get("map"))
                await websocket.send(json.dumps(game.get_state_dict()))

            elif msg_type == "move":
                key = data.get("key")
                game.move(key)
                await websocket.send(json.dumps(game.get_state_dict()))
            elif msg_type == "solve_ai":
                algo = data.get("algorithm")
                heuristic_name = heuristic_map.get(data.get("heuristic"))
                weight = None
                try:
                    weight = float(data.get("weight"))
                except:
                    pass
                game.reset(map_dir_path + "/" + data.get("map"))
                await websocket.send(json.dumps(game.get_state_dict()))

                moves = []
                start_time = time.perf_counter()

                if algo == "BFS":
                    moves, visited_nodes = solve_bfs(game)
                elif algo == "DFS":
                    moves, visited_nodes = solve_dfs(game, DFS_limit)
                elif algo == "IDS":
                    moves, visited_nodes = solve_ids(game, IDS_max_depth)
                elif algo == "A_STAR":
                    moves, visited_nodes = solve_a_star(game, heuristic_name, 1)
                elif algo == "WEIGHTED_A_STAR":
                    moves, visited_nodes = solve_a_star(game, heuristic_name, weight)

                end_time = time.perf_counter()

                execution_time_ms = (end_time - start_time) * 1000

                await websocket.send(
                    json.dumps(
                        {
                            "type": "ai_solution",
                            "moves": moves,
                            "executionTimeMs": execution_time_ms,
                            "visitedNodes": visited_nodes,
                        }
                    )
                )

            elif msg_type == "get-maps":
                map_files = [f for f in os.listdir(map_dir_path) if f.endswith(".txt")]

                await websocket.send(json.dumps({"type": "maps", "maps": map_files}))

            elif msg_type == "get-heuristics":
                await websocket.send(
                    json.dumps(
                        {"type": "heuristics", "heuristics": list(heuristic_map.keys())}
                    )
                )

            elif msg_type == "print-logs":
                log_text = data.get("text")
                print(log_text)

    except websockets.exceptions.ConnectionClosed:
        print("Browser closed.")
        shutdown_event.set()
    finally:
        print("Browser closed.")
        shutdown_event.set()


async def run_ui(game):

    file_path = os.path.abspath("index.html")
    if not os.path.isfile(file_path):
        print("index.html not found!!, make sure it's in the same path as this file")

    shutdown_event = asyncio.Event()
    bound_handler = partial(handler, game=game, shutdown_event=shutdown_event)

    print("Runnig server on port 8765...")
    async with websockets.serve(bound_handler, "localhost", 8765):
        webbrowser.open(f"file://{file_path}")
        await shutdown_event.wait()


map_file_path = "maps/map01.txt"

print("Welcome to Snake Portals!")
game_instance = Game(map_file_path)
asyncio.run(run_ui(game_instance))
