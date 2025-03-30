import sys
import os
import argparse

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.nav_graph import NavGraph
from gui.fleet_gui import FleetGUI
import tkinter as tk

def main():
    parser = argparse.ArgumentParser(description='Fleet Management System')
    parser.add_argument('--graph', type=int, choices=[1, 2, 3], default=1,
                      help='Select which navigation graph to use (1, 2, or 3)')
    args = parser.parse_args()

    root = tk.Tk()
    root.title(f"Fleet Management System - Graph {args.graph}")
    
    graph_file = f"nav_graph_{args.graph}.json"
    graph_path = os.path.abspath(os.path.join(os.path.dirname(__file__), f"../data/{graph_file}"))
    graph = NavGraph(graph_path)
    
    app = FleetGUI(root, graph)
    root.mainloop()

if __name__ == "__main__":
    main()
