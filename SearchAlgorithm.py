from collections import deque
import math


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
        
        self.path = None                    # Last node when a path is found
        self.path_locations = []            # Locations from start to end

        self.expanded = 0                   # Number of expanded locations before finding the path
        self.closest_distance = math.inf    # Closest Manhattan distance before finding the path

        self.explored_locations = set()     # Number of accessible locations from start
        self.revisited = 0                  # Number of revisited locations

    # Public    
    def get_path(self):
        return self.path
    
    def get_steps(self):
        result = 0
        if self.path != None:
            result = self.path.steps
        return result

    def get_path_locations(self):
        if self.path == None:
            return self.path_locations
        
        if len(self.path_locations) != 0:
            return self.path_locations

        node = self.path
        while node != None:
            self.path_locations.append(node.location)
            node = node.parent

        # Start to end (and not the inverse)
        self.path_locations.reverse()

        return self.path_locations

    def get_expanded(self):
        return self.expanded

    def get_closest_distance(self):
        return self.closest_distance

    def get_explored_locations(self):
        return self.explored_locations

    def get_explored(self):
        return len(self.explored_locations)
    
    def get_revisited(self):
        return self.revisited

    def run(self):
        self.path = None
        self.path_locations = []

        self.expanded = 0
        self.closest_distance = math.inf

        self.explored_locations = set()
        self.revisited = 0
        
        # Init
        root = Node(None, self.start)
        root.steps = 0
        self.explored_locations.add(root.location)
        frontier = deque([root])

        while len(frontier) > 0:
            node = frontier.popleft()
            location = node.location

            # Count expanded locations
            if self.path == None:
                self.expanded += 1

            # Calculate closest distance
            if self.path == None:
                r1, c1 = location
                r2, c2 = self.end
                distance = abs(r1 - r2) + abs(c1 - c2)
                if distance < self.closest_distance:
                    self.closest_distance = distance

            # Goal reached?
            if location == self.end and self.path == None:
                self.path = node

            # Add children to frontier
            next_locations = self.next_locations(self.grid, location)
            
            for next_location in next_locations:
                # Already explored?
                if next_location in self.explored_locations:
                    # Different from parent ?
                    if node.parent != None and next_location != node.parent.location:
                        self.revisited += 1
                    continue

                # Add to explored
                self.explored_locations.add(next_location)

                # Add to frontier
                child = Node(node, next_location)
                child.steps = node.steps + 1
                frontier.append(child)