from tkinter import *
from tkinter.messagebox import showerror, showwarning, showinfo
from random import sample
from dataclasses import dataclass
from itertools import chain


buttons_count = 10
button_side = 24
mines_count = 10
CH_F = chr(128204) # 'P' - flag 
CH_M = chr(128165) # '*' - mine
CH_M_SHOW = chr(128163) # '*'

@dataclass
class Cell:
    row:  int
    col:  int
    mine: bool = False
    neighbours: int = 0
    open: bool = False
    flag: bool = False
    
    def __hash__(self):
        return hash((self.row, self.col))
    
class Game:
        
    def __set_mines(self):
        mine_cells = sample(list(chain.from_iterable(self.board)), k=self.mines)

        for row in range(self.rows):
            for col in range(self.cols):
                cell = self.board[row][col]
                if cell in mine_cells:
                    cell.mine = True
                for r,c in ((row+x, col+y) for x in range(-1,2) for y in range(-1,2)):
                    if 0<=r<self.rows and 0<=c<self.cols:
                        if self.board[r][c] in mine_cells:
                            cell.neighbours += 1
    
    def __init__(self, rows: int, cols: int, mines: int):
        self.rows = rows
        self.cols = cols
        self.mines = mines
        self.flags = mines
        self.board = [[Cell(row, col) for col in range(cols)] for row in range(rows)]
        self.__set_mines()
        self.over = False
        self.won = False
        self.safe_moves = rows*cols-mines
        
    def show(self, show_all=False):
        print('   ', end='') 
        for c in range(self.cols):
            print(str.center(f'{c+1}',3), end='')
        print()        
        
        for row in range(self.rows):
            print(str.center(f'{row+1}',3), end='')
            
            for col in range(self.cols):
                cell = self.board[row][col]
                if cell.open or show_all:
                    ch = '[x]' if cell.mine else f'[{cell.neighbours}]'
                else:
                    ch = '[P]' if cell.flag else '[ ]'
                print(ch, end='')
            print()    


    def move(self, row, col, flag=False):
        
        if row<0 or row>=self.rows or col<0 or col>=self.cols:
            return
                    
        cell = self.board[row][col]
        
        if not cell.open:        
            if flag:
                if cell.flag:
                    cell.flag = False
                    self.flags += 1                    
                else:
                    if self.flags:
                        cell.flag = True
                        self.flags -= 1
                
            else:
                cell.open = True
                if cell.flag:
                    cell.flag = False
                    self.flags += 1 
                
                if cell.mine:
                    self.over = True
                else:
                    self.safe_moves -= 1
                    if self.safe_moves == 0:
                        self.won = True
        return cell                


class SquareButton(Button):
    def __init__(self, master=None, **kwargs):
        
        self.row = kwargs.pop('row', None)
        self.col = kwargs.pop('col', None)
        
        self.img = PhotoImage()
        side = kwargs.pop('side_length', None)
        
        Button.__init__(self, master, image=self.img, compound='center', **kwargs)
        if side:
            self.config(width=side, height=side)


def open_neighbour_cells(row, col):
    zero_cells = []
    for dr,dc in ((-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)):
        r = min(max(0,row+dr), game.rows-1)
        c = min(max(0,col+dc), game.cols-1)

        cell = game.board[r][c]
        if not cell.open:
            cell = game.move(r,c)
            idx = r*buttons_count+c
            
            ch = ' ' if cell.neighbours==0 else str(cell.neighbours)     
            btn[idx].config(text=ch, state=DISABLED, relief=SUNKEN, bg=DEFAULT_BUTTON_COLOR, disabledforeground=get_fg(cell.neighbours))                           
            
            if cell.neighbours == 0:
                zero_cells.append(cell)
                
    for cell in zero_cells:
        open_neighbour_cells(cell.row, cell.col)


def mouse_click(idx, flag=False):
         
    row = btn[idx].row
    col = btn[idx].col
    
    flag_update_status = game.board[row][col].flag or flag
    
    cell = game.move(row, col, flag)  
     
    if flag:
        ch = CH_F if cell.flag else ' '
        btn[idx].config(text=ch, bg='yellow' if cell.flag else DEFAULT_BUTTON_COLOR)
    else:    
        btn_bg = DEFAULT_BUTTON_COLOR
        btn_fg = DEFAULT_TEXT_COLOR
        
        if cell.mine:
            ch = CH_M
            btn_bg = 'red'
        else:
            if cell.neighbours==0:
                ch = ' ' 
                open_neighbour_cells(row, col)
                flag_update_status = True
            else:
                ch = str(cell.neighbours)
                btn_fg = get_fg(cell.neighbours)
         
                
        btn[idx].config(text=ch, state=DISABLED, relief=SUNKEN, bg=btn_bg, disabledforeground=btn_fg)
        #btn[idx].config(text=ch, relief=SUNKEN, bg=btn_bg, fg=btn_fg)
        
    if flag_update_status:
        update_status()
             
                
def show_mines(bgcolor='red'):
    for b in btn:
        cell = game.board[b.row][b.col]
        if cell.mine and not cell.open:
            b.config(text=CH_M_SHOW, state=DISABLED, bg=bgcolor)

                                   
def button_click(idx):
    def click(event):
        if game.over or game.won:
            return
        if btn[idx]['relief'] == SUNKEN:
            return        
        
        if event.num==1:
            mouse_click(idx)
        elif event.num==3:    
            mouse_click(idx, True)  
            
        if game.over:
            show_mines()
            showerror(title="Miner", message="Game over!")
        elif game.won:
            show_mines('yellow')
            showinfo(title="Miner", message="You won!")       
                
    return click


def update_status():
    statusbar.config(text=f'Flags left: {game.flags}')


def get_fg(neighbours):
    return n_colors.get(neighbours, '#00097B')


def restart_game():
    global game 
    game = Game(buttons_count, buttons_count, mines_count) # global
    
    update_status()
    
    for b in btn:
        b.config(text=' ', state=NORMAL, bg=DEFAULT_BUTTON_COLOR, fg=DEFAULT_TEXT_COLOR, relief=RAISED)
        
tk = Tk() 
tk.title('Miner')
tk.resizable(False, False) 
window_side = buttons_count * (button_side + 8)
tk.geometry(f'{window_side}x{window_side+20}')

n_colors = {1: '#001EF5',
            2: '#377D22',
            3: '#EB3323',
            4: '#00097B'}


menubar = Menu(tk)
tk.config(menu=menubar)
file_menu = Menu(menubar, tearoff=False)

# add a menu item to the menu
file_menu.add_command(
    label = 'Restart',
    command = restart_game
)

# add a menu item to the menu
file_menu.add_command(
    label = 'Exit',
    command = tk.destroy
)

# add the File menu to the menubar
menubar.add_cascade(
    label="File",
    menu=file_menu
)

# create StatusBar
statusbar = Label(tk, text=' ', bd=1, relief=SUNKEN, anchor=W)
statusbar.pack(side=BOTTOM, fill=X)

#create Game
game = Game(buttons_count, buttons_count, mines_count) 

update_status()

frm = []; btn = [] # Списки с фреймами и кнопками

default_button = Button()
DEFAULT_BUTTON_COLOR = default_button['bg']
DEFAULT_TEXT_COLOR   = default_button['fg']

for row in range(buttons_count):
    
    frm.append(Frame())
    frm[row].pack(expand=YES, fill=BOTH)
    
    for col in range(buttons_count):
        idx = row*buttons_count+col
        btn.append(SquareButton(frm[row], row=row, col=col, side_length = button_side, text=' ', font=('mono', 16, 'bold')))
        btn[idx].pack(side=LEFT, expand=YES, fill=BOTH)
        
        btn[idx].bind('<Button>', button_click(idx))



mainloop()