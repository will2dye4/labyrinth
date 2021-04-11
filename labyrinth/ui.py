import time
import tkinter as tk

from labyrinth.maze import Direction, Maze


class MazeApp(tk.Frame):

    BORDER_WIDTH = 4
    BORDER_OFFSET = BORDER_WIDTH * 2

    CELL_WIDTH = 35
    CELL_HEIGHT = CELL_WIDTH

    PATH_COLOR = '#C3E3F7'

    TICK_DELAY_MILLIS = 500

    def __init__(self, master=None, width=10, height=10, validate_moves=True):
        if master is None:
            master = tk.Tk()
            master.title('Maze Generator')

        super().__init__(master)

        self.width = width
        self.height = height
        self.validate_moves = validate_moves
        self.drawing_path = False
        self.maze = None
        self.path = []
        self.pack()
        self.canvas = self.create_canvas()
        self.stats = self.create_stats_display()
        self.create_menu()
        self.start_time = None
        self.end_time = None
        self.generate_new_maze()

    def create_canvas(self):
        width = self.CELL_WIDTH * self.width + self.BORDER_OFFSET
        height = self.CELL_HEIGHT * self.height + self.BORDER_OFFSET
        canvas = tk.Canvas(width=width, height=height, borderwidth=0)
        canvas.bind('<Button-1>', self.click_handler)
        canvas.bind('<Motion>', self.motion_handler)
        canvas.pack(side='top')
        return canvas

    @staticmethod
    def create_stats_display():
        stats = tk.Label(pady=5)
        stats.pack(side='top')
        return stats

    def create_menu(self):
        menu = tk.Frame()
        new_button = tk.Label(menu, fg='blue', text='[ New Maze ]', cursor='hand2')
        new_button.bind('<Button-1>', self.generate_new_maze)
        new_button.pack(side='left')
        menu.pack(side='top')

    def click_handler(self, event):
        if self.drawing_path:
            self.drawing_path = False
            if self.path and self.path[-1].column == self.width - 1:
                self.end_time = time.time()
        else:
            coordinates = self.get_selected_cell_coordinates(event)
            self.select_cell(*coordinates)
            self.drawing_path = True

    def motion_handler(self, event):
        if self.drawing_path:
            coordinates = self.get_selected_cell_coordinates(event)
            if coordinates != self.path[-1].coordinates:
                if len(self.path) > 1 and coordinates == self.path[-2].coordinates:
                    # moved back one, deselect the most recent cell
                    self.select_cell(*self.path[-1].coordinates)
                else:
                    self.select_cell(*coordinates)

    def generate_new_maze(self, event=None):
        for obj in self.canvas.find_all():
            self.canvas.delete(obj)

        self.maze = Maze(self.width, self.height)
        self.path.clear()

        for row in range(self.height):
            for column in range(self.width):
                cell = self.maze[row, column]
                x0 = self.CELL_WIDTH * column + self.BORDER_OFFSET
                y0 = self.CELL_HEIGHT * row + self.BORDER_OFFSET
                x1 = x0 + self.CELL_WIDTH
                y1 = y0 + self.CELL_HEIGHT
                directions = {
                    Direction.N: ((x0, y0, x1, y0), lambda r, c: r == 0),
                    Direction.S: ((x0, y1, x1, y1), lambda r, c: r == self.height - 1),
                    Direction.E: ((x1, y0, x1, y1), lambda r, c: c == self.width - 1),
                    Direction.W: ((x0, y0, x0, y1), lambda r, c: c == 0),
                }
                for direction in directions:
                    coordinates, width_predicate = directions[direction]
                    width = 1
                    if direction not in cell.open_walls:
                        if width_predicate(row, column):
                            width = self.BORDER_WIDTH
                        self.canvas.create_line(*coordinates, width=width)

        self.start_time = time.time()
        self.end_time = None

    def get_selected_cell_coordinates(self, event):
        row = max(0, min(event.y // self.CELL_HEIGHT, self.height - 1))
        column = max(0, min(event.x // self.CELL_WIDTH, self.width - 1))
        return row, column

    def select_cell(self, row, column):
        clicked_cell = self.maze[row, column]
        add = True

        if not self.path:
            if self.validate_moves and (row, column) != (0, 0):
                # print('Path must start at (0, 0)')
                return
        else:
            last_cell = self.path[-1]
            if clicked_cell in self.path:
                if self.validate_moves and clicked_cell != last_cell:
                    # print('Can only undo the last move')
                    return
                add = False
            elif self.validate_moves and clicked_cell not in self.maze.neighbors(last_cell.row, last_cell.column):
                # print('Path must be continuous')
                return
            elif self.validate_moves:
                direction = Direction.between(last_cell, clicked_cell)
                if direction not in last_cell.open_walls:
                    # print(f'Invalid move (through {direction.name} wall)')
                    return

        row_offset = 2 if row in {0, self.height - 1} else 1
        column_offset = 2 if column in {0, self.width - 1} else 1
        x0 = self.CELL_WIDTH * column + self.BORDER_OFFSET + column_offset
        y0 = self.CELL_HEIGHT * row + self.BORDER_OFFSET + row_offset
        x1 = x0 + self.CELL_WIDTH - (2 if column == self.width - 1 else 1) * column_offset
        y1 = y0 + self.CELL_HEIGHT - (2 if row == self.height - 1 else 1) * row_offset
        color = self.PATH_COLOR if add else 'white'
        self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, width=0)

        if add:
            self.path.append(clicked_cell)
        else:
            self.path = self.path[:-1]

    @property
    def elapsed_time(self):
        if self.start_time is not None:
            end_time = self.end_time or time.time()
            return end_time - self.start_time
        return 0

    def tick(self):
        self.stats['text'] = (f'Maze Size: {self.width} x {self.height}         '
                              f'Current Path Length: {len(self.path)}        '
                              f'Elapsed Time: {int(self.elapsed_time)} sec')
        self.after(self.TICK_DELAY_MILLIS, self.tick)

    def run(self):
        self.tick()
        super().mainloop()


if __name__ == '__main__':
    MazeApp(width=25, height=25).run()
