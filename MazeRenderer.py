import webbrowser
import os


VIEWER_PATH = os.getcwd() + "/maze_viewer/viewer.html"
DATA_PATH = "maze_viewer/data.js"


class MazeRendered:
    def __init__(self, height, width, maze, start, end, path_locations):
        self.height = height
        self.width = width
        self.maze = maze
        self.start = start
        self.end = end
        self.path_locations = path_locations

    # Public    
    def render(self):
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