import tkinter as tk
from tkinter import Canvas, Frame, Label, Button, Listbox
from src.models.nav_graph import NavGraph
from src.models.robot import Robot
import random

class FleetGUI:
    def __init__(self, root, graph):
        self.root = root
        self.graph = graph
        
        # Create main container
        self.main_container = Frame(root)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Canvas setup
        self.canvas_width = 800  
        self.canvas_height = 600  
        self.canvas = Canvas(self.main_container, width=self.canvas_width, height=self.canvas_height, bg='white')
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Side panel setup
        self.side_panel = Frame(self.main_container, width=250, bg='lightgray')
        self.side_panel.pack(side=tk.RIGHT, fill=tk.Y)
        self.side_panel.pack_propagate(False)
        
        # Robot Info Section
        self.info_section = Frame(self.side_panel, bg='lightgray')
        self.info_section.pack(fill=tk.X, padx=10, pady=5)
        Label(self.info_section, text="Robot Information", font=("Arial", 12, "bold"), bg='lightgray').pack(pady=5)
        
        # Robot info display
        self.robot_info_frame = Frame(self.info_section, bg='lightgray')
        self.robot_info_frame.pack(fill=tk.X)
        
        # Initialize robot info labels
        self.info_labels = {}
        self.create_info_labels()
        
        # Robot List Section
        self.list_section = Frame(self.side_panel, bg='lightgray')
        self.list_section.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        Label(self.list_section, text="Available Robots", font=("Arial", 12, "bold"), bg='lightgray').pack(pady=5)
        
        # Robot listbox
        self.robot_listbox = Listbox(self.list_section, font=("Arial", 10))
        self.robot_listbox.pack(fill=tk.BOTH, expand=True)
        self.robot_listbox.bind('<<ListboxSelect>>', self.on_select_robot_from_list)
        
        # Delete button
        self.delete_button = Button(self.list_section, text="Delete Selected Robot", command=self.delete_selected_robot)
        self.delete_button.pack(pady=5)
        
        # Rest of the initialization
        self.robots = []
        self.vertex_map = {}
        self.margin = 50 
        self.scale_factor, self.offset_x, self.offset_y = self.calculate_scaling()
        self.selected_robot = None
        self.robot_colors = {}
        self.draw_graph()
        self.canvas.bind("<Button-1>", self.handle_click)
        self.update_robots()

    def create_info_labels(self):
        """Create labels for robot information display"""
        fields = ['ID', 'Status', 'Current Location', 'Destination', 'Path Length']
        for field in fields:
            frame = Frame(self.robot_info_frame, bg='lightgray')
            frame.pack(fill=tk.X, pady=2)
            
            Label(frame, text=f"{field}:", font=("Arial", 10, "bold"), bg='lightgray').pack(side=tk.LEFT)
            label = Label(frame, text="--", font=("Arial", 10), bg='lightgray')
            label.pack(side=tk.LEFT, padx=5)
            self.info_labels[field] = label

    def update_robot_info(self):
        """Update the side panel with robot information"""
        if self.selected_robot:
            robot = self.selected_robot
            current_vertex = self.find_nearest_vertex(robot.x, robot.y)
            current_name = self.graph.vertices[current_vertex][2] if current_vertex is not None else "Moving"
            
            dest_vertex = robot.destination_vertex
            dest_name = self.graph.vertices[dest_vertex][2] if dest_vertex is not None else "None"
            
            self.info_labels['ID'].config(text=robot.id)
            self.info_labels['Status'].config(text=robot.status)
            self.info_labels['Current Location'].config(text=current_name)
            self.info_labels['Destination'].config(text=dest_name)
            self.info_labels['Path Length'].config(text=str(robot.get_path_length()))
            
            # Update colors based on status
            status_color = {
                Robot.STATUS_IDLE: 'green',
                Robot.STATUS_MOVING: 'blue',
                Robot.STATUS_WAITING: 'orange',
                Robot.STATUS_CHARGING: 'purple',
                Robot.STATUS_COMPLETE: 'gray'
            }
            self.info_labels['Status'].config(fg=status_color.get(robot.status, 'black'))
        else:
            for label in self.info_labels.values():
                label.config(text="--")

    def calculate_scaling(self):
        """ Calculate scaling factors to fit the graph within the canvas """
        min_x = min(v[0] for v in self.graph.vertices)
        max_x = max(v[0] for v in self.graph.vertices)
        min_y = min(v[1] for v in self.graph.vertices)
        max_y = max(v[1] for v in self.graph.vertices)

        graph_width = max_x - min_x
        graph_height = max_y - min_y

        scale_x = (self.canvas_width - 2 * self.margin) / graph_width if graph_width > 0 else 1
        scale_y = (self.canvas_height - 2 * self.margin) / graph_height if graph_height > 0 else 1
        scale = min(scale_x, scale_y)  

        offset_x = (self.canvas_width - (graph_width * scale)) / 2 - (min_x * scale)
        offset_y = (self.canvas_height - (graph_height * scale)) / 2 - (min_y * scale)

        return scale, offset_x, offset_y

    def transform_coordinates(self, x, y):
        """ Apply scaling and centering transformations """
        screen_x = x * self.scale_factor + self.offset_x
        screen_y = y * self.scale_factor + self.offset_y
        return screen_x, screen_y

    def draw_graph(self):
        # First create all vertex mappings
        for i, (x, y, name) in enumerate(self.graph.vertices):
            screen_x, screen_y = self.transform_coordinates(x, y)
            self.vertex_map[i] = (screen_x, screen_y)

        # Draw lanes first
        for start, end in self.graph.lanes:
            x1, y1 = self.vertex_map[start]
            x2, y2 = self.vertex_map[end]
            self.canvas.create_line(x1, y1, x2, y2, fill='gray', width=2)

        # Draw vertices with better visibility
        for i, (x, y, name) in enumerate(self.graph.vertices):
            screen_x, screen_y = self.vertex_map[i]
            
            # Draw vertex circle
            self.canvas.create_oval(screen_x - 8, screen_y - 8, screen_x + 8, screen_y + 8, 
                                 fill='lightblue', outline='blue')
            
            # Draw vertex name with background
            text = self.canvas.create_text(screen_x, screen_y - 15, text=name, 
                                         font=("Arial", 10, "bold"))
            bbox = self.canvas.bbox(text)
            if bbox:
                self.canvas.create_rectangle(bbox[0]-2, bbox[1]-2, bbox[2]+2, bbox[3]+2, 
                                          fill='white', outline='')
                self.canvas.tag_raise(text)

    def get_random_color(self):
        """ Generate a random pastel color """
        r = random.randint(180, 255)
        g = random.randint(180, 255)
        b = random.randint(180, 255)
        return f'#{r:02x}{g:02x}{b:02x}'

    def handle_click(self, event):
        # Check if clicked on a robot
        for robot in self.robots:
            if abs(event.x - robot.x) < 10 and abs(event.y - robot.y) < 10:
                self.select_robot(robot)
                return

        # Check if clicked on a vertex
        for i, (screen_x, screen_y) in self.vertex_map.items():
            if abs(event.x - screen_x) < 10 and abs(event.y - screen_y) < 10:
                if self.selected_robot:
                    self.assign_task(self.selected_robot, i)
                else:
                    self.spawn_robot(screen_x, screen_y)
                break

    def spawn_robot(self, x, y):
        robot = Robot(x, y)
        self.robots.append(robot)
        self.robot_colors[robot.id] = self.get_random_color()
        
        # Draw robot with unique color
        self.canvas.create_oval(robot.x - 8, robot.y - 8, robot.x + 8, robot.y + 8, 
                              fill=self.robot_colors[robot.id], outline='black')
        
        # Draw robot ID with background
        text = self.canvas.create_text(robot.x, robot.y - 15, text=robot.id, 
                                     font=("Arial", 8, "bold"))
        bbox = self.canvas.bbox(text)
        if bbox:
            self.canvas.create_rectangle(bbox[0]-2, bbox[1]-2, bbox[2]+2, bbox[3]+2, 
                                      fill='white', outline='')
            self.canvas.tag_raise(text)
        
        # Set initial location
        current_vertex = self.find_nearest_vertex(x, y)
        if current_vertex is not None:
            robot.set_initial_location(current_vertex)
        
        # Update robot list
        self.update_robot_list()

    def select_robot(self, robot):
        self.selected_robot = robot
        # Highlight selected robot
        self.canvas.create_oval(robot.x - 10, robot.y - 10, robot.x + 10, robot.y + 10, 
                              outline='yellow', width=2)
        self.update_robot_info()

    def assign_task(self, robot, destination_vertex):
        """Assign a navigation task to the selected robot"""
        if robot.status == Robot.STATUS_IDLE:
            # Calculate path using navigation graph
            start_vertex = self.find_nearest_vertex(robot.x, robot.y)
            if start_vertex is not None and destination_vertex is not None:
                path = self.graph.find_path(start_vertex, destination_vertex)
                if path:
                    # Convert path vertices to screen coordinates
                    screen_path = [self.vertex_map[v] for v in path]
                    # Assign task with path
                    robot.assign_task(destination_vertex, screen_path)
                else:
                    robot.status = Robot.STATUS_WAITING
                    robot.wait_time = 30  # Wait for 3 seconds
        
        self.selected_robot = None
        # Remove highlight
        self.canvas.create_oval(robot.x - 10, robot.y - 10, robot.x + 10, robot.y + 10, 
                              outline='black', width=1)
        self.update_robot_info()

    def find_nearest_vertex(self, x, y):
        """Find the nearest vertex to given coordinates"""
        min_dist = float('inf')
        nearest_vertex = None
        for i, (vx, vy) in self.vertex_map.items():
            dist = ((x - vx)**2 + (y - vy)**2)**0.5
            if dist < min_dist:
                min_dist = dist
                nearest_vertex = i
        return nearest_vertex

    def update_robot_list(self):
        """Update the robot list in the side panel"""
        self.robot_listbox.delete(0, tk.END)
        for robot in self.robots:
            current_vertex = self.find_nearest_vertex(robot.x, robot.y)
            location = self.graph.vertices[current_vertex][2] if current_vertex is not None else "Unknown"
            self.robot_listbox.insert(tk.END, f"{robot.id} - {location} - {robot.status}")

    def on_select_robot_from_list(self, event):
        """Handle robot selection from the list"""
        selection = self.robot_listbox.curselection()
        if selection:
            index = selection[0]
            selected_robot = self.robots[index]
            self.select_robot(selected_robot)

    def delete_selected_robot(self):
        """Delete the selected robot"""
        if self.selected_robot:
            # Remove all visual elements of the robot
            self.canvas.delete(f"robot_{self.selected_robot.id}")
            self.canvas.delete(f"status_{self.selected_robot.id}")
            self.canvas.delete(f"highlight_{self.selected_robot.id}")  # Remove highlight if any
            self.canvas.delete(f"background_{self.selected_robot.id}")  # Remove text background
            
            # Remove from lists and dictionaries
            self.robots.remove(self.selected_robot)
            del self.robot_colors[self.selected_robot.id]
            
            # Clear selection
            self.selected_robot = None
            self.update_robot_info()
            self.update_robot_list()

    def update_robots(self):
        """Update robot positions and statuses"""
        for robot in self.robots:
            # Store previous position for movement detection
            prev_x, prev_y = robot.x, robot.y
            
            # Update robot state
            robot.update()
            
            # Check if robot has moved from spawn location
            if (robot.x != prev_x or robot.y != prev_y) and not robot.has_moved_from_spawn:
                # Clear any visual elements at spawn location
                self.canvas.delete(f"robot_{robot.id}")
                self.canvas.delete(f"status_{robot.id}")
                self.canvas.delete(f"highlight_{robot.id}")
                self.canvas.delete(f"background_{robot.id}")
                robot.has_moved_from_spawn = True
            
            # Update robot visualization
            self.canvas.delete(f"robot_{robot.id}")
            self.canvas.create_oval(robot.x - 8, robot.y - 8, robot.x + 8, robot.y + 8, 
                                  fill=self.robot_colors[robot.id], outline='black',
                                  tags=f"robot_{robot.id}")
            
            # Update status text with background
            status_text = f"{robot.id} - {robot.status}"
            self.canvas.delete(f"status_{robot.id}")
            text = self.canvas.create_text(robot.x, robot.y - 15, text=status_text,
                                         font=("Arial", 8, "bold"),
                                         tags=f"status_{robot.id}")
            bbox = self.canvas.bbox(text)
            if bbox:
                self.canvas.create_rectangle(bbox[0]-2, bbox[1]-2, bbox[2]+2, bbox[3]+2,
                                          fill='white', outline='',
                                          tags=(f"background_{robot.id}", f"status_{robot.id}"))
                self.canvas.tag_raise(text)

        # Update side panel information
        self.update_robot_info()
        self.update_robot_list()

        # Schedule next update
        self.root.after(100, self.update_robots)
