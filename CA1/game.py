import sys


class Map:
    def __init__(self, map_string):
        """Takes the map as a string and extracts the needed information"""
        self.walls = set()
        self.apples = set()
        self.portals = {} # maps same-type portal locations
        self.p_portals = set() 
        self.q_portals = set()
        self.snake_start = None
        self.width = 0
        self.height = 0
        self._parse(map_string)

    def _parse(self, map_string):
        rows = [line.strip().split() for line in map_string.strip().split('\n') if line.strip()]
        self.height = len(rows)
        self.width = len(rows[0]) if self.height > 0 else 0

        p_locations, q_locations = [], []

        for r, row in enumerate(rows):
            for c, char in enumerate(row):
                pos = (r, c)
                if char == 'W': self.walls.add(pos)
                elif char == 'A': self.apples.add(pos)
                elif char == 'S': self.snake_start = pos
                elif char == 'P': 
                    p_locations.append(pos)
                    self.p_portals.add(pos)
                elif char == 'Q': 
                    q_locations.append(pos)
                    self.q_portals.add(pos)

        if len(p_locations) == 2:
            self.portals[p_locations[0]] = p_locations[1]
            self.portals[p_locations[1]] = p_locations[0]
        if len(q_locations) == 2:
            self.portals[q_locations[0]] = q_locations[1]
            self.portals[q_locations[1]] = q_locations[0]


class Snake:
    def __init__(self, start_pos):
        self.body = [start_pos]


class Game:
    DIRECTIONS = {'U': (-1, 0), 'D': (1, 0), 'L': (0, -1), 'R': (0, 1)}

    def __init__(self, map_file_path):
        try:
            with open(map_file_path, 'r') as file:
                map_data = file.read()
        except FileNotFoundError:
            print(f"Error: Could not find the file '{map_file_path}'.")
            print("Please make sure map.txt is in the same folder as this script.")
            sys.exit(1)

        self.board = Map(map_data)
        if not self.board.snake_start: raise ValueError("No Snake start position (S) found!")

        self.map_file_path = map_file_path
        self.snake = Snake(self.board.snake_start)
        self.state = "PLAYING"
        self.score = 0

    def reset(self, map_file_path):
        try:
            with open(map_file_path, 'r') as file:
                map_data = file.read()
        except FileNotFoundError:
            print(f"Error: Could not find the file '{map_file_path}'.")
            print("Please make sure map.txt is in the same folder as this script.")
            sys.exit(1)

        self.board = Map(map_data)
        if not self.board.snake_start: raise ValueError("No Snake start position (S) found!")

        self.map_file_path = map_file_path
        self.snake = Snake(self.board.snake_start)
        self.state = "PLAYING"
        self.score = 0



    def move(self, direction_key):
        if self.state != "PLAYING" or direction_key not in self.DIRECTIONS:
            return self.state
            
        dr, dc = self.DIRECTIONS[direction_key]
        head_r, head_c = self.snake.body[0]
        
        new_r = (head_r + dr) % self.board.height
        new_c = (head_c + dc) % self.board.width
        
        if (new_r, new_c) in self.board.portals:
            new_r, new_c = self.board.portals[(new_r, new_c)]
            
        new_head = (new_r, new_c)
        
        if new_head in self.board.apples:
            self.board.apples.remove(new_head)
            self.score += 1
        else:
            self.snake.body.pop()

        if new_head in self.board.walls or new_head in self.snake.body:
            self.state = "LOSS"
            self.snake.body.insert(0, new_head)
            return self.state
            
        self.snake.body.insert(0, new_head)
        if len(self.board.apples) == 0: self.state = "WIN"
        return self.state
    
    def get_state_dict(self):
        def to_list(items):
            return [[r, c] for r, c in items]
    
        return {
        "type": "state",
        "width": self.board.width,
        "height": self.board.height,
        "snake": to_list(self.snake.body),
        "apples": to_list(self.board.apples),
        "walls": to_list(self.board.walls),
        "p_portals": to_list(self.board.p_portals),
        "q_portals": to_list(self.board.q_portals),
        "score": self.score,
        "state": self.state
        }
