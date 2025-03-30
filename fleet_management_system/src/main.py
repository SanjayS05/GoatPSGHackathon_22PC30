import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.nav_graph import NavGraph
from gui.fleet_gui import FleetGUI
import tkinter as tk

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Fleet Management System")
    graph = NavGraph(os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/nav_graph_1.json")))
    app = FleetGUI(root, graph)
    root.mainloop()
