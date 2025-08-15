class Node:
    def __init__(self, parent, location):
        self.parent = parent
        self.location = location
        self.steps = 0


class SearchAlgorithm:
    def __init__(self, start, end, grid, next_locations):
        self.start = start
        self.end = end
        self.grid = grid
        self.next_locations = next_locations
        
        self.path = None
        self.steps = 0
        self.explored = set()
        self.path_locations = []

    # Public    
    def get_path(self):
        return self.path
    
    def get_steps(self):
        return self.steps
    
    def get_explored(self):
        return self.explored

    def get_path_locations(self):
        if self.path == None or len(self.path_locations) != 0:
            return self.path_locations

        node = self.path
        while node != None:
            self.path_locations.append(node.location)
            node = node.parent

        return self.path_locations

    def run(self):
        self.path = None
        self.steps = 0
        self.explored = set()
        
        # Init
        root = Node(None, self.start)
        root.steps = 0
        self.explored.add(root.location)
        frontier = []
        frontier.append(root)

        while len(frontier) > 0:
            node = frontier.pop(0)
            location = node.location

            # Goal reached?
            if location == self.end and self.path == None:
                self.path = node

            # Add children to frontier
            next_locations = self.next_locations(location, self.grid)
            
            for next_location in next_locations:
                # Already explored?
                if next_location in self.explored:
                    continue

                # Add to explored
                self.explored.add(next_location)

                # Add to frontier
                child = Node(node, next_location)
                child.steps = node.steps + 1
                frontier.append(child)

        # Set number of steps
        if self.path != None:
            self.steps = self.path.steps