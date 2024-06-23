import tkinter as tk
import numpy as np
import os
import csv

GRID_SIZE = 1000
CELL_SIZE = 20  # Size of each grid cell
ARRAY_SIZE = GRID_SIZE // CELL_SIZE  # Size of the array based on cell size
LOAD_FILE = "walls_1000_20_2.csv"

class WallDrawingApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Wall Drawing App")
        self.setup_widgets()
        self.cells = {}  # Dictionary to keep track of cell states
        self.grid_array = self.load_or_initialize_grid()
        self.draw_grid()
        self.setup_bindings()

    def setup_widgets(self):
        self.top_frame = tk.Frame(self.master)
        self.top_frame.pack(side=tk.TOP, fill=tk.X)
        self.save_button = tk.Button(self.top_frame, text="Save Grid to CSV", command=self.save_to_csv)
        self.save_button.pack(pady=10)
        self.canvas = tk.Canvas(self.master, width=GRID_SIZE, height=GRID_SIZE)
        self.canvas.pack()

    def setup_bindings(self):
        self.canvas.bind("<Button-1>", self.color_cell)  # Left click for walls
        self.canvas.bind("<B1-Motion>", self.color_cell)  # Drag left click for walls
        self.canvas.bind("<Button-2>", self.place_charger)  # Middle click for chargers
        self.canvas.bind("<Button-3>", self.clear_cell)  # Right click to clear cells
        self.canvas.bind("<B3-Motion>", self.clear_cell)  # Drag right click to clear cells
        self.master.bind("<Control-s>", lambda event: self.save_to_csv())  # Ctrl+S to save

    def draw_grid(self):
        for x in range(0, GRID_SIZE, CELL_SIZE):
            for y in range(0, GRID_SIZE, CELL_SIZE):
                idx_x, idx_y = x // CELL_SIZE, y // CELL_SIZE
                fill_color = "white"
                if self.grid_array[idx_y, idx_x] == 1:
                    fill_color = "black"
                elif self.grid_array[idx_y, idx_x] == 2:
                    fill_color = "red"
                cell_id = self.canvas.create_rectangle(x, y, x + CELL_SIZE, y + CELL_SIZE, fill=fill_color, outline="gray", dash=(1, 4))
                self.cells[(x, y)] = cell_id

    def color_cell(self, event):
        x = event.x // CELL_SIZE * CELL_SIZE
        y = event.y // CELL_SIZE * CELL_SIZE
        idx_x, idx_y = x // CELL_SIZE, y // CELL_SIZE
        if self.grid_array[idx_y, idx_x] == 0:
            self.canvas.itemconfig(self.cells[(x, y)], fill="black")
            self.grid_array[idx_y, idx_x] = 1

    def place_charger(self, event):
        x = event.x // CELL_SIZE * CELL_SIZE
        y = event.y // CELL_SIZE * CELL_SIZE
        idx_x, idx_y = x // CELL_SIZE, y // CELL_SIZE
        if self.grid_array[idx_y, idx_x] == 0:
            self.canvas.itemconfig(self.cells[(x, y)], fill="red")
            self.grid_array[idx_y, idx_x] = 2

    def clear_cell(self, event):
        x = event.x // CELL_SIZE * CELL_SIZE
        y = event.y // CELL_SIZE * CELL_SIZE
        idx_x, idx_y = x // CELL_SIZE, y // CELL_SIZE
        if self.grid_array[idx_y, idx_x] != 0:
            self.canvas.itemconfig(self.cells[(x, y)], fill="white")
            self.grid_array[idx_y, idx_x] = 0

    def save_to_csv(self):
        num = 0
        filename = f'walls_{GRID_SIZE}_{CELL_SIZE}_{num}.csv'
        while os.path.exists(filename):
            num += 1
            filename = f'walls_{GRID_SIZE}_{CELL_SIZE}_{num}.csv'
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(self.grid_array)
        print(f"Grid saved to {filename}")

    def load_or_initialize_grid(self):
        if os.path.exists(LOAD_FILE):
            with open(LOAD_FILE, newline='') as file:
                grid = list(csv.reader(file))
                if len(grid) == ARRAY_SIZE and all(len(row) == ARRAY_SIZE for row in grid):
                    return np.array(grid, dtype=int)
        return np.zeros((ARRAY_SIZE, ARRAY_SIZE), dtype=int)

def main():
    root = tk.Tk()
    app = WallDrawingApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
