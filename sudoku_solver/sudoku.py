import copy
import re
import numpy as np
from colorama import Fore


class Sudoku(object):
    def __init__(self):
        self.cell = {}
        self.solved = None

    def load_game(self, fn):
        with open(fn, 'r') as f:
            for line in f:
                line = line.strip()
                if line == "":
                    continue
                m = re.match('(\d)x(\d)\s*(\d)', line)
                if m is None:
                    continue
                key = m.group(1) + "x" + m.group(2)
                self.cell[key] = int(m.group(3))
        self.initial_cell = copy.copy(self.cell)

        self.set_grid()

    def get_cell(self, x, y):
        key = f'{x}x{y}'
        if key in self.cell:
            return self.cell[key]
        else:
            return 0

    def set_grid(self):
        global grid
        grid = a = [[self.get_cell(x, y) for x in range(9)] for y in range(9)]
        print(np.matrix(grid))


    def draw(self):
        for y in range(9):
            if y % 3 == 0:
                print(Fore.WHITE + "------------")
            for x in range(9):
                if x % 3 == 0:
                    print(Fore.WHITE + "|", end="")
                key = f'{x}x{y}'
                if key in self.cell:
                    color = Fore.RED
                    if key in self.initial_cell:
                        color = Fore.WHITE

                    v = color + str(self.cell[key])
                else:
                    v = Fore.WHITE + " "
                print(v, end="")

            print()
        print()

    # セルを全て舐めて、正解が１個のセルを決定する
    def step1(self):
        num_solved = 0
        for x in range(9):
            for y in range(9):
                key = f'{x}x{y}'
                c = self.peek(x, y)

                if c is None:
                    continue
                if len(c) == 1:
                    self.cell[key] = c[0]
                    num_solved += 1
                elif len(c) == 0:
                    print(f'step1 {key} no entry')
                    return -1
        return num_solved


    # 空きのセルに候補の数字のリストを設定
    def step2(self):
        remain = {}
        for x in range(9):
            for y in range(9):
                key = f'{x}x{y}'
                c = self.peek(x, y)
                if c is None:
                    continue
                if len(c) > 1:
                    #self.cell[key] = c
                    #print(f'{key} {c}')
                    remain[key] = c

        return remain

    def issolved(self):
        if self.solved:
            return True

        for x in range(9):
            for y in range(9):
                key = f'{x}x{y}'
                if key not in self.cell:
                    return False
        self.solved = True
        return True

    # 指定セルの設置可能数値のリストを取得
    def peek(self, x, y):
        key = f'{x}x{y}'
        if key in self.cell:
            return None
        hlist = self.getHolizonValue(y)
        #print(f'h = {hlist}')
        vlist = self.getVerticalValue(x)
        #print(f'v = {vlist}')
        clist = self.get9CellValue(x, y)
        #print(f'c = {clist}')
        # 現在のセル＋縦リスト＋横リストの重複しないセットを取得
        other_list = set(hlist + vlist + clist)
        #print(f'peek {key} {other_list}')
        candidate = []
        for v in range(1, 10):
            if v not in other_list:
                candidate.append(v)

        return candidate


    # 未設定のセル数を取得
    def get_num_remain(self):
        num = 0
        for x in range(9):
            for y in range(9):
                key = f'{x}x{y}'
                if key in self.cell:
                    c = self.cell[key]
                    if type(c) is list and len(c) > 1:
                        num += 1
                else:
                    num += 1
        return num

    # 横方向の数値のリストを取得
    def getHolizonValue(self, y):
        values = []
        for x in range(9):
            key = f'{x}x{y}'
            if key in self.cell and type(self.cell[key]) is int:
                values.append(self.cell[key])

        return values;

    # 縦方向の数値リストを取得
    def getVerticalValue(self, x):
        values = []
        for y in range(9):
            key = f'{x}x{y}'
            if key in self.cell and type(self.cell[key]) is int:
                values.append(self.cell[key])

        return values;

    # 指定の９セル内の数値リストを取得
    def get9CellValue(self, x, y):
        values = []
        base_x = x // 3 * 3
        base_y = y // 3 * 3
        for x in range(3):
            for y in range(3):
                key = f'{base_x + x}x{base_y + y}'
                if key in self.cell and type(self.cell[key]) is int:
                    values.append(self.cell[key])
        return values;

    def solve_basic(self):
        nstep = 0
        while True:
            nstep += 1
            print(f'solve step {nstep}')
            n = self.step1()
            self.draw()
            if n < 0:
                return -1
            if n == 0:
                break
            #if n > 0:
            #    self.draw()
        return nstep

    def solve2(self, depth=0):
        print(f'solve2 depth {depth}')
        self.draw()
        num_try = 0
        if depth == 0:
            self.cell_current = copy.copy(self.cell)
        if depth >= 10:
            print('depth too deep')
            return -2
        remain = self.step2()
        remain_sorted = sorted(remain.items(), key=lambda x:len(x[1]))
        print(f'remain {remain_sorted}')

        for ntry in range(len(remain_sorted)):
            print(f'solve2 loop ntry {ntry} depth {depth}')
            if num_try > 10:
                print('retry count over')
                break
            if len(remain_sorted) == 0:
                print('--------- no list ----')
                break
            mark_cell = remain_sorted[ntry]
            for i in range(len(mark_cell[1])):
                print(f'trying depth {depth} {i} {mark_cell[1]} {mark_cell[0]} {mark_cell[1][i]}')
                self.cell[mark_cell[0]] = mark_cell[1][i]
                solve_ret = self.solve()
                print(f'solve_ret {solve_ret}')
                if solve_ret > 0:
                    print(f'recursive call solve2 {depth + 1}')
                    solve2_ret = self.solve2(depth + 1)
                    print(f'return from solve2 {depth + 1}')
                    if solve2_ret == 0 and depth == 0:
                        return 0
                    #if solve2_ret < 0 and depth > 0:
                    #    return -1
                    continue
                else:
                    print(f'------- can not solve depth {depth} -----')
                    self.cell = copy.copy(self.cell_current)
                    if depth > 0:
                        return -1
            print(f'--- end of mark loop depth {depth}')
            self.cell = copy.copy(self.cell_current)

        return 0

    def solve(self, deep=0):
        if self.issolved():
            return

        self.draw()
        if self.solve_basic() < 0:
            return
        if self.issolved():
            print("+++++++++ SOLVED ++++++++++++")
            return

        remain = self.step2()
        remain_sorted = sorted(remain.items(), key=lambda x:len(x[1]))
        if len(remain_sorted) == 0:
            return


        #print(f'remain {remain_sorted}')
        mark_cell = remain_sorted[0]
        for i in range(len(mark_cell[1])):
            copy_cell = copy.copy(self.cell)
            self.cell[mark_cell[0]] = mark_cell[1][i]
            solve3_ret = self.solve(deep + 1)
            self.cell = copy.copy(copy_cell)


if __name__ == '__main__':
    sudoku = Sudoku()
    sudoku.load_game('sudoku_ex/ex6.txt')
    sudoku.draw()


    sudoku.solve()


#    solve()


