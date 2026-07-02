import random, sys, webbrowser
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton, QWidget, QLineEdit,QLayout
from PyQt5.QtCore import Qt, QTimer

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BongCloud")
        self.setGeometry(0,0,800,800)
        self.gameover=False
        self.boardstate=[[""for row in range(8)] for col in range(8)]#make empty 8 by 8 list of lists
        self.pieces = {"P":"♟","R":"♜","N":"♞","B":"♝","Q":"♛","K":"♚",}
        self.allowed=[]#contains allowed moves for selected piece as list of numbers n=row*10+col
        self.currentplayer="w"
        self.prev=[8,0] 
        self.choosingpromotion=(8,0) 
        self.castleinfo={"Kw":False,"Kb":False,"Rwl":False,"Rwr":False,"Rbl":False,"Rbr":False} #have the pieces that affect castling moved
        self.setboard()
        self.initUI()

    def setboard(self):
        self.boardstate = [
    ["Rb","Nb","Bb","Qb","Kb","Bb","Nb","Rb"],
    ["Pb","Pb","Pb","Pb","Pb","Pb","Pb","Pb"],
    ["","","","","","","",""],
    ["","","","","","","",""],
    ["","","","","","","",""],
    ["","","","","","","",""],
    ["Pw","Pw","Pw","Pw","Pw","Pw","Pw","Pw"],
    ["Rw","Nw","Bw","Qw","Kw","Bw","Nw","Rw"],
    ]

    def pieceicon(self,row,col): #cuts the color off the piece name and takes the icon from the dictionary
        piece=self.boardstate[row][col]
        if piece=="":
            return ""
        else: 
            return self.pieces[piece[:-1]]

    def initUI(self):
        self.boardUI=[[QPushButton("",self) for row in range(8)] for col in range(8)] #makes an 8x8 2d LIST of pushbuttons
        self.boardlayout=QGridLayout() #the grid
        self.boardlayout.setHorizontalSpacing(0) 
        self.boardlayout.setVerticalSpacing(0)
        self.boardlayout.setContentsMargins(0, 0, 0, 0)
        self.boardlayout.setSizeConstraint(QLayout.SetFixedSize)

        for row in range(8):
            for col in range(8):
                self.boardlayout.addWidget(self.boardUI[row][col],row,col) #adds psuhbuttons to grid layout
                self.boardUI[row][col].setFixedSize(100,100)
                if (row+col)%2==0:                                         #black and white colors
                    self.boardUI[row][col].setStyleSheet("background-color: #ddddc6;")
                else:
                    self.boardUI[row][col].setStyleSheet("background-color: #55aa55;")

        for row in range(8):
            for col in range(8): 
                self.boardUI[row][col].setText(self.pieceicon(row,col))  #places piecies on the board and gives them the correct color
                self.makecolor(row,col)
                self.boardUI[row][col].clicked.connect(lambda checked, r=row,c=col: self.checkmove(r,c))#creates 64 anonimous function that retain grid coordonate at creation,connected to the buttons

        self.info=QLabel("White turn")
        self.info.setAlignment(Qt.AlignCenter)
        self.info.setStyleSheet("background-color: #ddddc6;")

        self.board_and_info=QVBoxLayout() #layout for the status bar and board
        self.board_and_info.addWidget(self.info,Qt.AlignTop)
        self.board_and_info.addLayout(self.boardlayout,Qt.AlignBottom)
        self.board_and_info.setContentsMargins(0, 0, 0, 0)
        self.board_and_info.setSizeConstraint(QLayout.SetFixedSize)
    
        self.mainlayout=QVBoxLayout() #layout that holds the widget
        self.mainlayout.addLayout(self.board_and_info)
        self.mainlayout.setAlignment(self.board_and_info, Qt.AlignCenter)
        self.mainlayout.setContentsMargins(0, 0, 0, 0)

        main_widget=QWidget(self) #mainwidget color and layout
        main_widget.setStyleSheet("background-color: #2b2b2b;")
        self.setCentralWidget(main_widget)
        main_widget.setLayout(self.mainlayout)
        
        self.setStyleSheet("""
        QPushButton{
            text-align: center;
            font-size: 80px;
        }
        QPushButton:pressed{
            padding 0px;
        } 
        QLabel{
            font-size: 24px;
            font-weight: bold;
            background-color: #ddddc6;
            color: #333333;
            border-bottom: 3px solid #55aa55;
            padding: 8px 0px;
            letter-spacing: 1px;
        }                  
        """)

    def checkmove(self,row,col):
        if self.choosingpromotion[0]!=8: 
            self.promotion(row,col)
            return
        if row*10+col in self.allowed:  #if the clicked move for selected piece is allowed, move the piece
            self.movepiece(row,col)
            return
        if self.boardstate[row][col]!="" and self.currentplayer in self.boardstate[row][col]: 
            if self.prev[0]!=8:         #for changing selected piece 
                self.makecolor(self.prev[0],self.prev[1])
            self.pieceselect(row,col)
        if self.boardstate[row][col]=="" or (row==self.prev[0] and col==self.prev[1]) or self.prev[0]==8 : #dont do anything if empty,same square or wrong color
            return 
        
    def pieceselect(self,row,col): #makes square red, saves previous click, calls find allowed moves, shows allowed moves on the board
            self.clearshownmoves()
            self.allowed=[] #clears prev allowed in case of change
            clr="Black"
            opclr="White"
            if 'w' in self.boardstate[row][col]: 
                clr="White"
                opclr="Black"
            self.boardUI[row][col].setStyleSheet(f"background-color: #ddaaaa;color:{clr}")
            self.prev=[row,col]
            if 'R' in self.boardstate[row][col]: #finds allowed move by looking at piece time
                self.Rfindallowed(row,col)
            elif 'B' in self.boardstate[row][col]:
                self.Bfindallowed(row,col)
            elif 'Q' in self.boardstate[row][col]:
                self.Rfindallowed(row,col)
                self.Bfindallowed(row,col)
            elif 'K' in self.boardstate[row][col]: #queen is just bishop+rook
                self.Rfindallowed(row,col)
                self.Bfindallowed(row,col)
                if self.currentplayer=='w' and self.castleinfo["Kw"]==False:
                    if self.castleinfo["Rwl"]==False and self.boardstate[7][1]=="" and self.boardstate[7][2]=="" and self.boardstate[7][3]=="" and ("Rw" in self.boardstate[7][0]):
                        self.allowed.append(72)
                    if self.castleinfo["Rwr"]==False and self.boardstate[7][6]=="" and self.boardstate[7][5]=="" and ("Rw" in self.boardstate[7][7]):
                        self.allowed.append(76)
                if self.currentplayer=='b' and self.castleinfo["Kb"]==False:
                    if self.castleinfo["Rbl"]==False and self.boardstate[0][1]=="" and self.boardstate[0][2]=="" and self.boardstate[0][3]=="" and ("Rb" in self.boardstate[0][0]):
                        self.allowed.append(2)
                    if self.castleinfo["Rbr"]==False and self.boardstate[0][6]=="" and self.boardstate[0][5]=="" and ("Rb" in self.boardstate[0][7]):
                        self.allowed.append(6)
            elif 'N' in self.boardstate[row][col]:
                self.Nfindallowed(row,col)
            elif 'P' in self.boardstate[row][col]:
                self.Pfindallowed(row,col)
            self.checkfilter(row,col)
            for move in self.allowed:
                r=move//10
                c=move%10
                if self.boardstate[r][c]=="":self.boardUI[r][c].setText("•")
                else: self.boardUI[r][c].setStyleSheet(f"background-color: #ddaaaa;color:{opclr}")
    
    def movepiece(self,row,col):
        self.clearshownmoves()
        affectscastling=[(7,4),(0,4),(7,0),(7,7),(0,0),(0,7)]
        for i in range (6):
            r,c=affectscastling[i]
            if r==self.prev[0] and c==self.prev[1]:
                if i==0:self.castleinfo["Kw"]=True
                elif i==1:self.castleinfo["Kb"]=True
                elif i==2:self.castleinfo["Rwl"]=True
                elif i==3:self.castleinfo["Rwr"]=True
                elif i==4:self.castleinfo["Rbl"]=True
                elif i==5:self.castleinfo["Rbr"]=True

        self.moveto(row,col,self.prev[0],self.prev[1])
        if 'K' in self.boardstate[row][col] and abs(col-self.prev[1])==2: #castle move, moves rook as well
            if col<self.prev[1] and self.currentplayer=="w": #left
                self.moveto(7,3,7,0)
            if col<self.prev[1] and self.currentplayer=="b":
                self.moveto(0,3,0,0)
            if col>self.prev[1] and self.currentplayer=="w": #right
                self.moveto(7,5,7,7)
            if col>self.prev[1] and self.currentplayer=="b":
                self.moveto(0,5,0,7)

        self.allowed=[]
        if 'P' in self.boardstate[row][col] and (row==0 or row==7): 
            self.promotion(row,col)  
            return   
        self.prev[0]=8 #if 8 it means no piece is selected
        if self.currentplayer=='w': 
            self.currentplayer='b' #turn change
            self.info.setText("Black turn")
        elif self.currentplayer=='b': 
            self.currentplayer='w'
            self.info.setText("White turn")
        self.statecheck()
        self.allowed=[]
        if ai and not self.gameover: 
            self.aiturn() #ai always black
            self.statecheck()
            self.currentplayer='w'
            self.info.setText("White turn")
            self.statecheck()
            self.allowed=[]

    def aiturn(self): 
        for col in range(8):
            if self.boardstate[6][col]=="Pb":
                self.boardstate[6][col]=""
                self.makecolor(6,col)
                self.boardUI[6][col].setText(self.pieceicon(6,col))
                if self.boardstate[7][col]=="" or col==0 or col==7:
                    self.boardstate[7][col]="Qb"
                    self.makecolor(7,col)
                    self.boardUI[7][col].setText(self.pieceicon(7,col))
                    return
                if 'w' in self.boardstate[7][col-1] and "Kw" not in self.boardstate[7][col-1]:
                    self.boardstate[7][col-1]="Qb"
                    self.makecolor(7,col-1)
                    self.boardUI[7][col-1].setText(self.pieceicon(7,col-1))
                    return
                if 'w' in self.boardstate[7][col+1] and "Kw" not in self.boardstate[7][col+1]:
                    self.boardstate[7][col+1]="Qb"
                    self.makecolor(7,col+1)
                    self.boardUI[7][col+1].setText(self.pieceicon(7,col+1))
                    return

        piecepoints = {"Kb":0,"":0,"Pw":1,"Rw":5,"Nw":3,"Bw":3,"Qw":9,"Pb":1,"Rb":5,"Nb":3,"Bb":3,"Qb":9,}
        highest=-1 #if -1 then it does trades, if its 0 it doesnt
        randval=0 #used to make the safe move choice random
        move=(0,0,0,0)
        for row in range(8):
            for col in range(8):
                if 'b' in self.boardstate[row][col]:
                    self.allowed=[]
                    if 'R' in self.boardstate[row][col]:
                        self.Rfindallowed(row,col)
                    elif 'B' in self.boardstate[row][col]:
                        self.Bfindallowed(row,col)
                    elif 'Q' in self.boardstate[row][col]:
                        self.Rfindallowed(row,col)
                        self.Bfindallowed(row,col)
                    elif 'K' in self.boardstate[row][col]:
                        self.Rfindallowed(row,col)
                        self.Bfindallowed(row,col)
                    elif 'N' in self.boardstate[row][col]:
                        self.Nfindallowed(row,col)
                    elif 'P' in self.boardstate[row][col]:
                        self.Pfindallowed(row,col)
                    self.checkfilter(row,col)
                    for rowcol in self.allowed:
                        r=rowcol//10
                        c=rowcol%10
                        if self.boardstate[r][c]=="": 
                            if self.is_square_safe(r,c) and highest==-1: #safe moves are better than unsafe or random moves
                                if randval<random.randint(0,10):
                                    randval=random.randint(0,10)
                                    move=(row,col,r,c)
                            continue
                        if self.is_square_safe(r,c): value=piecepoints[self.boardstate[r][c]]
                        else: value=piecepoints[self.boardstate[r][c]]-piecepoints[self.boardstate[row][col]]
                        if 'Q' not in self.boardstate[row][col] and 'Q' in self.boardstate[r][c] and 100-piecepoints[self.boardstate[row][col]]>highest: #taking queen without queen trade has priority
                            highest=100-piecepoints[self.boardstate[row][col]]
                            move=(row,col,r,c)
                        if value>highest: 
                            highest=value
                            move=(row,col,r,c)
                        
        self.allowed=[]
    
        if move!=(0,0,0,0):
            self.moveto(move[2],move[3],move[0],move[1])
            self.allowed=[]
            return
                
        blackpieces=[]       #random move sequence, if no promotion or take
        for row in range(8):
            for col in range(8):
                if 'b' in self.boardstate[row][col]:
                    if 'R' in self.boardstate[row][col]: self.Rfindallowed(row,col)
                    elif 'B' in self.boardstate[row][col]: self.Bfindallowed(row,col)
                    elif 'Q' in self.boardstate[row][col]: self.Rfindallowed(row,col); self.Bfindallowed(row,col)
                    elif 'K' in self.boardstate[row][col]: self.Rfindallowed(row,col); self.Bfindallowed(row,col)
                    elif 'N' in self.boardstate[row][col]: self.Nfindallowed(row,col)
                    elif 'P' in self.boardstate[row][col]: self.Pfindallowed(row,col)
                    self.checkfilter(row,col)
                    if self.allowed:
                        blackpieces.append(row*10+col)
                    self.allowed = []
        randrange=len(blackpieces)
        if randrange==1:
            rowcol=0
        else:
            rowcol=random.randint(0,randrange-1)
        row=blackpieces[rowcol]//10
        col=blackpieces[rowcol]%10 
        self.allowed=[]
        if 'R' in self.boardstate[row][col]:
            self.Rfindallowed(row,col)
        elif 'B' in self.boardstate[row][col]:
            self.Bfindallowed(row,col)
        elif 'Q' in self.boardstate[row][col]:
            self.Rfindallowed(row,col)
            self.Bfindallowed(row,col)
        elif 'K' in self.boardstate[row][col]:
            self.Rfindallowed(row,col)
            self.Bfindallowed(row,col)
        elif 'N' in self.boardstate[row][col]:
            self.Nfindallowed(row,col)
        elif 'P' in self.boardstate[row][col]:
            self.Pfindallowed(row,col)
        self.checkfilter(row,col)
        randrange=len(self.allowed)
        if randrange==1:
            randmove=0
        else:
            randmove=random.randint(0,randrange-1)
        r=self.allowed[randmove]//10
        c=self.allowed[randmove]%10 
        self.moveto(r,c,row,col)
        self.allowed=[]

    def is_square_safe(self, searched_row, searched_col):
        rowcol=searched_row*10+searched_col
        tempstorage=self.allowed[:]
        initialcolor=self.currentplayer
        piece_in_checked_square=self.boardstate[searched_row][searched_col]
        self.boardstate[searched_row][searched_col]="Pb" #for the Pfindallowed to consider diagonal attacks, we temporarily place a black pawn in the square being checked
        safe=True
        self.currentplayer='w'
        for row in range(8):
            for col in range(8):
                piece=self.boardstate[row][col]
                if 'w' in piece:
                    self.allowed=[]
                    if 'R' in piece:
                        self.Rfindallowed(row,col)
                        if rowcol in self.allowed: safe=False
                    elif 'B' in piece:
                        self.Bfindallowed(row,col)
                        if rowcol in self.allowed: safe=False
                    elif 'Q' in piece:
                        self.Rfindallowed(row,col)
                        self.Bfindallowed(row,col)
                        if rowcol in self.allowed: safe=False
                    elif 'K' in piece:
                        self.Rfindallowed(row,col)
                        self.Bfindallowed(row,col)
                        if rowcol in self.allowed: safe=False
                    elif 'N' in piece:
                        self.Nfindallowed(row,col)
                        if rowcol in self.allowed: safe=False
                    elif 'P' in piece:
                        self.Pfindallowed(row,col)
                        if rowcol in self.allowed: safe=False
                    if safe==False:               
                        self.allowed=tempstorage[:]
                        self.currentplayer=initialcolor
                        self.boardstate[searched_row][searched_col]=piece_in_checked_square
                        return False
        self.allowed=tempstorage[:]
        self.currentplayer=initialcolor
        self.boardstate[searched_row][searched_col]=piece_in_checked_square
        return True

    def moveto(self,rd,cd,rs,cs):
        self.boardstate[rd][cd]=self.boardstate[rs][cs] #moves piece from prev spot to new in the background
        self.boardstate[rs][cs]="" #clears prev spot in the background
        self.makecolor(rs,cs) #makes the selected square not red anymore
        self.makecolor(rd,cd)  #makes piece the correct color
        self.boardUI[rd][cd].setText(self.pieceicon(rd,cd)) #shows piece on the square it was moved to
        self.boardUI[rs][cs].setText("") #clears previous selected square

    def promotion(self,row,col):
        if self.choosingpromotion[0]==8:
            self.boardstate[row][col]=""
            decrement=-1
            clr="Black"
            self.choosingpromotion=(row,col)
            self.buttonenable(False)
            if self.currentplayer=="w": 
                decrement=1
                clr="White"
            for n in range(4):
                self.boardUI[row+n*decrement][col].setStyleSheet(f"background-color: #aaaaaa;color:{clr}")
                self.boardUI[row+n*decrement][col].setEnabled(True)
                if n==0:self.boardUI[row+n*decrement][col].setText("♛")
                elif n==1:self.boardUI[row+n*decrement][col].setText("♞")
                elif n==2:self.boardUI[row+n*decrement][col].setText("♝") #bishop
                elif n==3:self.boardUI[row+n*decrement][col].setText("♜")
            return
        else:
            r=self.choosingpromotion[0]
            c=self.choosingpromotion[1]
            decrement=-1
            if self.currentplayer=="w": 
                decrement=1
            if abs(r-row)==0:self.boardstate[r][c]=f"Q{self.currentplayer}"
            elif abs(r-row)==2:self.boardstate[r][c]=f"B{self.currentplayer}"
            elif abs(r-row)==1:self.boardstate[r][c]=f"N{self.currentplayer}"
            elif abs(r-row)==3:self.boardstate[r][c]=f"R{self.currentplayer}"
            for n in range(4):
                self.makecolor(r+n*decrement,c)
                if n==0:self.boardUI[r+n*decrement][c].setText(self.pieceicon(r+n*decrement,c))
                if n==1:self.boardUI[r+n*decrement][c].setText(self.pieceicon(r+n*decrement,c))
                if n==2:self.boardUI[r+n*decrement][c].setText(self.pieceicon(r+n*decrement,c))
                if n==3:self.boardUI[r+n*decrement][c].setText(self.pieceicon(r+n*decrement,c))
            self.boardUI[r][c].setText(self.pieceicon(r,c))
            self.choosingpromotion=(8,0)
            self.buttonenable(True)
            if self.currentplayer=='w': 
                self.currentplayer='b' #turn change
                self.info.setText("Black turn")
            elif self.currentplayer=='b': 
                self.currentplayer='w'
                self.info.setText("White turn")
            self.statecheck()
            self.allowed=[]
            if ai and not self.gameover: 
                self.aiturn() #ai always black
                self.statecheck()
                self.currentplayer='w'
                self.info.setText("White turn")
                self.statecheck()
                self.allowed=[]
            
    def buttonenable(self,bool):
        for row in range(8):
            for col in range(8): 
                self.boardUI[row][col].setEnabled(bool)

    def makecolor(self,row,col):
        if (row+col)%2==0:
            bg="#ddddc6"
        else:
            bg="#55aa55"
        if 'w' in self.boardstate[row][col]: self.boardUI[row][col].setStyleSheet(f"color: White;background-color:{bg};")
        elif 'b' in self.boardstate[row][col]: self.boardUI[row][col].setStyleSheet(f"color: Black;background-color:{bg};")
        else:self.boardUI[row][col].setStyleSheet(f"background-color:{bg};")

    def clearshownmoves(self):
        for move in self.allowed:
                r=move//10
                c=move%10
                if self.boardstate[r][c]=="":self.boardUI[r][c].setText("")
                else:self.makecolor(r,c)
        
    def Rfindallowed(self,row,col):
        directions = [(1,0),(-1,0),(0,1),(0,-1)]

        for dr,dc in directions: #dr=first in tuple, dc second in tuple
            r,c=row+dr,col+dc #increments with direction once

            while 0 <= r<8 and 0<=c<8: #goes through direction increments until edge of board or intersection with piece
                if self.boardstate[r][c] != "":
                    if self.currentplayer not in self.boardstate[r][c]: 
                        self.allowed.append(r*10+c) #taking enemy piece is allowed , then stop loop so you dont phase through it
                        break
                    else:
                        break   
                self.allowed.append(r*10+c)
                if 'K' in self.boardstate[row][col]:break #if its a kind it only does it once
                r+=dr
                c+=dc
    
    def Bfindallowed(self,row,col):
        directions = [(1,1),(1,-1),(-1,-1),(-1,1)]

        for dr,dc in directions: #dr=first in tuple, dc second in tuple
            r,c=row+dr,col+dc #increments with direction once

            while 0 <= r<8 and 0<=c<8: #goes through direction increments until edge of board or intersection with piece
                if self.boardstate[r][c] != "":
                    if self.currentplayer not in self.boardstate[r][c]: 
                        self.allowed.append(r*10+c) #taking enemy piece is allowed , then stop loop so you dont phase through it
                        break
                    else:
                        break   
                self.allowed.append(r*10+c)
                if 'K' in self.boardstate[row][col]:break #if its a king it only does it once
                r+=dr
                c+=dc

    def statecheck(self):
        if self.currentplayer=='w': 
            otherplayer='b'
            currentfull="White"
            otherfull="Black"
        elif self.currentplayer=='b': 
            otherplayer='w'
            currentfull="Black"
            otherfull="White"
        if not self.kingincheck(otherplayer): #removes red highlight from king if not in check
            for row in range(8):
                for col in range(8):
                    if self.boardstate[row][col]==f"K{otherplayer}":
                        self.makecolor(row,col)
        if self.kingincheck(self.currentplayer) and not self.hasmoves(): #checkmate
            self.gameover=True
            self.info.setText(f"{currentfull} is in checkmate, {otherfull} wins")
        elif not self.hasmoves(): #stalemate
            self.gameover=True
            self.info.setText(f"Stalemate: {currentfull} has no valid moves, Game ends in tie")
        if self.kingincheck(self.currentplayer): #highlights king in red if in check
            clr="Black"
            if self.currentplayer=="w":clr="White"
            for row in range(8):
                for col in range(8):
                    if self.boardstate[row][col]==f"K{self.currentplayer}":
                        self.boardUI[row][col].setStyleSheet(f"background-color: #ddaaaa;color:{clr}")

    def hasmoves(self):
        self.allowed=[]
        for row in range(8):
            for col in range(8):
                if self.currentplayer in self.boardstate[row][col]:
                    piece=self.boardstate[row][col]
                    if 'R' in piece:
                        self.Rfindallowed(row,col)
                    elif 'B' in piece:
                        self.Bfindallowed(row,col)
                    elif 'Q' in piece:
                        self.Rfindallowed(row,col)
                        self.Bfindallowed(row,col)
                    elif 'K' in piece:
                        self.Rfindallowed(row,col)
                        self.Bfindallowed(row,col)
                    elif 'N' in piece:
                        self.Nfindallowed(row,col)
                    elif 'P' in piece:
                        self.Pfindallowed(row,col)
                    self.checkfilter(row,col)
                    if self.allowed!=[]:return 1
        self.allowed=[]
        return 0

    def checkfilter(self,row,col):
        clr=self.currentplayer
        piece=self.boardstate[row][col]
        self.boardstate[row][col]=""
        legal=[]
        for square in self.allowed:
            r=square//10
            c=square%10
            state_of_checked_square=self.boardstate[r][c]
            self.boardstate[r][c]=piece
            if not self.kingincheck(self.currentplayer):
                legal.append(square)
            self.boardstate[r][c]=state_of_checked_square
        self.boardstate[row][col]=piece
        self.allowed=legal

    def kingincheck(self,color):
        tempstorage=self.allowed[:]
        self.allowed=[]
        if color=='w':
            opcolor='b'
        elif color=='b':
            opcolor='w'
        initialcolor=self.currentplayer #so we know what color to switch back to 
        self.currentplayer=opcolor #so the find allowed works
        in_check=False
        for row in range(8):
            for col in range(8):
                piece=self.boardstate[row][col]
                if opcolor in piece:
                    if 'R' in piece:
                        self.Rfindallowed(row,col)
                        in_check=self.cantakeking(color)
                    elif 'B' in piece:
                        self.Bfindallowed(row,col)
                        in_check=self.cantakeking(color)
                    elif 'Q' in piece:
                        self.Rfindallowed(row,col)
                        self.Bfindallowed(row,col)
                        in_check=self.cantakeking(color)
                    elif 'K' in piece:
                        self.Rfindallowed(row,col)
                        self.Bfindallowed(row,col)
                        in_check=self.cantakeking(color)
                    elif 'N' in piece:
                        self.Nfindallowed(row,col)
                        in_check=self.cantakeking(color)
                    elif 'P' in piece:
                        self.Pfindallowed(row,col)
                        in_check=self.cantakeking(color)
        self.allowed=tempstorage[:]
        self.currentplayer=initialcolor
        if in_check:return 1
        else: return 0

    def cantakeking(self,color):
        for rowcol in self.allowed:
            r=rowcol//10
            c=rowcol%10
            if f"K{color}" in self.boardstate[r][c]:return 1
        return 0

    def Pfindallowed(self,row,col): #I HATE PAWNS, 2 separate ifs for black and white since they are opposite
        move=1
        if ('w' in self.boardstate[row][col] and row==6) or ('b' in self.boardstate[row][col] and row==1):
            move=2   
        if 'w' in self.boardstate[row][col]:
            for i in range(1,move+1):
                if self.boardstate[row-i][col]=="":self.allowed.append((row-i)*10+col)
                else:break
            if row>0 and col!=0 and self.currentplayer not in self.boardstate[row-1][col-1] and self.boardstate[row-1][col-1]!="":
                self.allowed.append((row-1)*10+(col-1))
            if row>0 and col!=7 and self.currentplayer not in self.boardstate[row-1][col+1] and self.boardstate[row-1][col+1]!="":
                self.allowed.append((row-1)*10+(col+1))
        elif 'b' in self.boardstate[row][col]:
            for i in range(1,move+1):
                if self.boardstate[row+i][col]=="":self.allowed.append((row+i)*10+col)
                else:break
            if  row<7 and col!=0 and self.currentplayer not in self.boardstate[row+1][col-1] and self.boardstate[row+1][col-1]!="":
                self.allowed.append((row+1)*10+(col-1))
            if  row<7 and col!=7 and self.currentplayer not in self.boardstate[row+1][col+1] and self.boardstate[row+1][col+1]!="":
                self.allowed.append((row+1)*10+(col+1))

    def Nfindallowed(self,row,col):
        moves=[(2,-1),(2,1),(-1,2),(1,2),(-2,1),(-2,-1),(1,-2),(-1,-2)]
        for dr,dc in moves:
            r,c=row+dr,col+dc
            if 0<=r<8 and 0<=c<8 and self.currentplayer not in self.boardstate[r][c]:
                self.allowed.append(r*10+c)
       
if __name__=="__main__":
    app=QApplication(sys.argv)
    window=MainWindow()
    selection=0
    ai=False
    while selection!=1 and selection!=2:
        try:
            selection=int(input("Select mode(press 1 or 2):\n 1.Single player\n 2.Two players\n"))
        except ValueError:
            print("Please enter a number (1 or 2).\n")
    if selection==1:ai=True
    window.show()
    sys.exit(app.exec())