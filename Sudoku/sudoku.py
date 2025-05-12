import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import random
import time
import os
import pickle

class Sudoku:
    def __init__(self):
        self.board = [[0 for _ in range(9)] for _ in range(9)]

    def generate(self, difficulty='fácil'):
        self.board = [[0 for _ in range(9)] for _ in range(9)]
        self.solve()  # cria uma solução completa
        filled = {'fácil': 36, 'médio': 30, 'difícil': 24}[difficulty]
        cells = [(i, j) for i in range(9) for j in range(9)]
        random.shuffle(cells)
        for i, j in cells[:81-filled]:
            self.board[i][j] = 0

    def is_valid(self, board, row, col, num):
        for i in range(9):
            if i != col and board[row][i] == num:
                return False
            if i != row and board[i][col] == num:
                return False
        start_row, start_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(start_row, start_row+3):
            for j in range(start_col, start_col+3):
                if (i != row or j != col) and board[i][j] == num:
                    return False
        return True

    def find_empty(self):
        for i in range(9):
            for j in range(9):
                if self.board[i][j] == 0:
                    return i, j
        return None

    def solve(self):
        empty = self.find_empty()
        if not empty:
            return True
        row, col = empty
        nums = list(range(1, 10))
        random.shuffle(nums)
        for num in nums:
            if self.is_valid(self.board, row, col, num):
                self.board[row][col] = num
                if self.solve():
                    return True
                self.board[row][col] = 0
        return False

class SudokuGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Sudoku")
        self.sudoku = Sudoku()
        self.entries = []
        self.difficulty = tk.StringVar(value='fácil')
        self.start_time = time.time()
        self.elapsed_time = 0
        self.timer_running = False
        self.count_labels = {}
        self.show_errors = tk.BooleanVar(value=True)
        self.build_ui()
        self.new_game('fácil')

    def build_ui(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        frame = tk.Frame(self.root)
        frame.pack()

        self.entries = [[None for _ in range(9)] for _ in range(9)]
        for i in range(9):
            for j in range(9):
                entry = tk.Entry(frame, width=2, font=('Arial', 18), justify='center')
                entry.grid(row=i, column=j, padx=1, pady=1, ipadx=5, ipady=5)
                val = self.sudoku.board[i][j]
                if val != 0:
                    entry.insert(0, str(val))
                    entry.config(state='disabled', disabledforeground='black')
                else:
                    entry.bind("<KeyRelease>", lambda e: self.update_number_counts_and_validate())
                self.entries[i][j] = entry

        bottom = tk.Frame(self.root)
        bottom.pack(pady=5)

        ttk.Combobox(bottom, values=['fácil', 'médio', 'difícil'], textvariable=self.difficulty, width=8).pack(side='left', padx=5)
        tk.Button(bottom, text="Novo Jogo", command=lambda: self.new_game(self.difficulty.get())).pack(side='left', padx=5)
        tk.Button(bottom, text="Verificar", command=self.check_solution).pack(side='left', padx=5)
        tk.Button(bottom, text="Salvar", command=self.save_game).pack(side='left', padx=5)
        tk.Button(bottom, text="Ranking", command=self.show_ranking).pack(side='left', padx=5)
        tk.Checkbutton(bottom, text="Mostrar erros", variable=self.show_errors, command=self.update_number_counts_and_validate).pack(side='left', padx=5)

        self.timer_label = tk.Label(bottom, text="Tempo: 0s")
        self.timer_label.pack(side='left', padx=5)

        self.count_frame = tk.Frame(self.root)
        self.count_frame.pack(pady=10)
        self.count_labels = {}
        for num in range(1, 10):
            lbl = tk.Label(self.count_frame, text=f"{num}: 9", font=('Arial', 12), width=6)
            lbl.pack(side='left', padx=3)
            self.count_labels[num] = lbl

        self.update_timer()
        self.update_number_counts_and_validate()

    def update_number_counts_and_validate(self):
        board = self.get_board_from_entries()
        count = {i: 0 for i in range(1, 10)}
        for row in board:
            for val in row:
                if val in count:
                    count[val] += 1

        for num in range(1, 10):
            restante = 9 - count[num]
            restante = max(0, restante)
            label = self.count_labels[num]
            label.config(text=f"{num}: {restante}")
            if restante == 0:
                label.config(fg='gray')
            else:
                label.config(fg='black')

        for i in range(9):
            for j in range(9):
                entry = self.entries[i][j]
                if entry['state'] == 'disabled':
                    continue
                val = entry.get()
                if not self.show_errors.get():
                    entry.config(bg='white')
                    continue
                try:
                    num = int(val)
                    if num < 1 or num > 9:
                        raise ValueError
                    if not self.sudoku.is_valid(board, i, j, num):
                        entry.config(bg='misty rose')
                    else:
                        entry.config(bg='white')
                except:
                    entry.config(bg='white' if not val else 'misty rose')

    def get_board_from_entries(self):
        board = []
        for row in self.entries:
            board_row = []
            for entry in row:
                val = entry.get()
                board_row.append(int(val) if val.isdigit() else 0)
            board.append(board_row)
        return board

    def check_solution(self):
        board = self.get_board_from_entries()
        for i in range(9):
            for j in range(9):
                val = board[i][j]
                if val == 0 or not self.sudoku.is_valid(board, i, j, val):
                    messagebox.showerror("Erro", "Há erros ou espaços em branco no tabuleiro.")
                    return
        elapsed = int(time.time() - self.start_time)
        messagebox.showinfo("Parabéns!", f"Você completou em {elapsed} segundos!")
        self.save_to_ranking(elapsed)

    def update_timer(self):
        if self.timer_running:
            self.elapsed_time = int(time.time() - self.start_time)
            self.timer_label.config(text=f"Tempo: {self.elapsed_time}s")
        self.root.after(1000, self.update_timer)

    def new_game(self, difficulty):
        self.sudoku.generate(difficulty)
        self.start_time = time.time()
        self.timer_running = True
        self.build_ui()

    def save_game(self):
        with open("sudoku_save.pkl", "wb") as f:
            pickle.dump((self.get_board_from_entries(), self.difficulty.get(), self.start_time), f)
        messagebox.showinfo("Salvo", "Jogo salvo com sucesso!")

    def save_to_ranking(self, tempo):
        nome = simpledialog.askstring("Ranking", "Digite seu nome:")
        if not nome:
            return
        ranking_file = "ranking.txt"
        with open(ranking_file, "a") as f:
            f.write(f"{nome},{tempo},{self.difficulty.get()}\n")

    def show_ranking(self):
        ranking_file = "ranking.txt"
        if not os.path.exists(ranking_file):
            messagebox.showinfo("Ranking", "Nenhum ranking salvo ainda.")
            return
        with open(ranking_file, "r") as f:
            dados = [linha.strip().split(',') for linha in f.readlines()]
        dados.sort(key=lambda x: int(x[1]))
        texto = "\n".join([f"{nome} - {tempo}s - {dif}" for nome, tempo, dif in dados[:10]])
        messagebox.showinfo("Top 10", texto)

if __name__ == "__main__":
    root = tk.Tk()
    app = SudokuGUI(root)
    root.mainloop()
