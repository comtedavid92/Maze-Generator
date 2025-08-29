import os
import webbrowser
import requests
import nbtlib


VIEWER_PATH         = os.getcwd() + "/maze_viewer/viewer.html"
DATA_PATH           = "maze_viewer/data.js"

# https://github.com/Niels-NTG/gdmc_http_interface/blob/v1.6.0/docs/Endpoints.md#-read-players-GET-players
# https://github.com/Niels-NTG/gdmc_http_interface/blob/v1.6.0/docs/Endpoints.md#-place-blocks-PUT-blocks

URI_PLAYERS         = "http://localhost:9000/players?includeData=true"
URI_BLOCK           = "http://localhost:9000/blocks"

GRID_OFFSET         = 5 # How far from the player is the maze rendered (Y axis)
WALL_HEIGHT         = 4

BLOCK_TYPE           = "minecraft:stone"
BLOCK_TYPE_BORDER    = "minecraft:stone_bricks"
BLOCK_TYPE_START     = "minecraft:green_wool"
BLOCK_TYPE_END       = "minecraft:red_wool"


class Position:
    def __init__(self, x, z, y):
        self.x = x # W and S keys
        self.z = z # A and D keys
        self.y = y # Space key (jump)


class MinecraftConnector:
    def __init__(self):
        pass

    def get_player_position(self):
        data = None
        try:
            data = requests.get(URI_PLAYERS)
        except:
            raise Exception(
                "Player position is not accessible," \
                "make sure Minecraft is running with the GDMC HTTP interface mod"
            )
        
        nbt = data.json()[0]["data"]
        node = nbtlib.parse_nbt(nbt)
        x, y, z = node["Pos"]
        position = Position(float(x), float(z), float(y))

        return position
    
    def add_blocks(self, blocks, type):
        body = []

        for block in blocks:
            body.append({
                "id" : type,
                "x"  : block.x,
                "z"  : block.z,
                "y"  : block.y 
            })

        data = None
        try:
            data = requests.put(URI_BLOCK, json=body)
        except:
            raise Exception(
                "Blocks cannot be placed," \
                "make sure Minecraft is running with the GDMC HTTP interface mod"
            )
        
        for object in data.json():
            if object["status"] == 0:
                raise Exception(
                    "Blocks cannot be placed," \
                    "make sure the player is on a flat surface with no objects around"
                )


class MazeRendered:
    def __init__(self, height, width, maze, start, end, path_locations):
        self.height = height # Height of the maze
        self.width = width   # Width of the maze
        self.maze = maze     # The maze as a list of tiles, 0 -> empty tile, 1 -> wall tile
        self.start = start   # Start point as a lit [row, col]
        self.end = end       # End point as a lit [row, col]
        self.path_locations = path_locations # Locations to follow from start to end as a list [[row,col], ...]

    # Private
    def _get_maze_blocks(self, x, z, y):
        result = []

        index = 0
        for row in range(self.height):
            for col in range(self.width):
                
                if self.maze[index] == 0:
                    index += 1
                    continue

                px = x + col
                pz = z + row

                for wall in range(WALL_HEIGHT):
                    position = Position(px, pz, y + wall)
                    result.append(position)

                index += 1

        return result

    def _get_surrounding_blocks(self, x, z, y):
        blocks = []

        H, W = self.height, self.width
        start = tuple(self.start)
        end   = tuple(self.end)

        def nearest_border_portal(rc):
            r, c = rc
            d_top, d_bottom = r, (H - 1) - r
            d_left, d_right = c, (W - 1) - c
            dmin = min(d_top, d_bottom, d_left, d_right)
            if dmin == d_top:
                return (-1, c)
            elif dmin == d_bottom:
                return (H, c)
            elif dmin == d_left:
                return (r, -1)
            else:
                return (r, W)

        door_start = nearest_border_portal(start)
        door_end   = nearest_border_portal(end)
        doors = {door_start, door_end}

        for c in range(-1, W + 1):
            for r in (-1, H):
                if (r, c) in doors:
                    continue
                
                px = x + c
                pz = z + r
                for h in range(WALL_HEIGHT):
                    blocks.append(Position(px, pz, y + h))

        for r in range(0, H):
            for c in (-1, W):
                if (r, c) in doors:
                    continue
                px = x + c
                pz = z + r
                for h in range(WALL_HEIGHT):
                    blocks.append(Position(px, pz, y + h))

        return blocks

    def _get_start_block(self, x, z, y):
        px = x + self.start[1]
        pz = z + self.start[0]
        py = y + WALL_HEIGHT - 1
        return Position(px, pz, py)

    def _get_end_block(self, x, z, y):
        px = x + self.end[1]
        pz = z + self.end[0]
        py = y + WALL_HEIGHT - 1
        return Position(px, pz, py)

    # Public    
    def render_web(self):
        data = ""
        data += "var height = " + str(self.height) + ";" + "\n"
        data += "var width = " + str(self.width) + ";" + "\n"
        data += "var maze = " + str(self.maze) + ";" + "\n"
        data += "var start = " + str(self.start) + ";" + "\n"
        data += "var end = " + str(self.end) + ";" + "\n"
        data += "var pathLocations = " + str(self.path_locations) + ";" + "\n"

        with open(DATA_PATH, "w") as f:
            f.write(data)

        webbrowser.open_new_tab(VIEWER_PATH)

    def render_minecraft(self):
        mc = MinecraftConnector()
        
        # Get player position
        position = mc.get_player_position()
        x = int(position.x - self.width / 2)
        z = int(position.z + GRID_OFFSET)
        y = int(position.y)

        # Add blocks to construct maze
        blocks = self._get_maze_blocks(x, z, y)
        mc.add_blocks(blocks, BLOCK_TYPE)

        # Add blocks to construct the surroundings
        blocks = self._get_surrounding_blocks(x, z, y)
        mc.add_blocks(blocks, BLOCK_TYPE_BORDER)

        # Add start blocks
        blocks = [self._get_start_block(x, z, y)]
        mc.add_blocks(blocks, BLOCK_TYPE_START)

        # Add end blocks
        blocks = [self._get_end_block(x, z, y)]
        mc.add_blocks(blocks, BLOCK_TYPE_END)