import json
from collections import deque

class NavGraph:
    def __init__(self, file_path):
        self.vertices = []
        self.lanes = []
        self.adjacency_list = {}  # For efficient path finding
        self.load_graph(file_path)
        self.build_adjacency_list()

    def load_graph(self, file_path):
        """Load graph data from JSON file"""
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
                level = data["levels"]["level1"]
                self.vertices = [(v[0], v[1], v[2].get("name", "")) for v in level["vertices"]]
                self.lanes = [(l[0], l[1]) for l in level["lanes"]]
        except FileNotFoundError:
            print(f"Error: Could not find navigation graph file at {file_path}")
            raise
        except KeyError as e:
            print(f"Error: Invalid graph file format. Missing key: {e}")
            raise
        except Exception as e:
            print(f"Error loading graph file: {e}")
            raise

    def build_adjacency_list(self):
        """Build adjacency list for efficient path finding"""
        self.adjacency_list = {i: [] for i in range(len(self.vertices))}
        for start, end in self.lanes:
            self.adjacency_list[start].append(end)
            self.adjacency_list[end].append(start)  # Undirected graph

    def find_path(self, start_vertex, end_vertex):
        """Find shortest path between two vertices using BFS"""
        if start_vertex is None or end_vertex is None:
            return None
            
        # Initialize BFS
        queue = deque([(start_vertex, [start_vertex])])
        visited = {start_vertex}
        
        while queue:
            current, path = queue.popleft()
            
            # Check if we reached the destination
            if current == end_vertex:
                return path
                
            # Explore neighbors
            for neighbor in self.adjacency_list[current]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        
        return None  # No path found
