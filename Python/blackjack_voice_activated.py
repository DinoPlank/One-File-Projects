import random, sys, webbrowser
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton, QWidget, QLineEdit
from PyQt5.QtCore import Qt, QTimer
import speech_recognition as audio
import os
#double can still be acced via voice command when it should not be,only works during round
class MainWindow(QMainWindow):
    def __init__(self,):
        super().__init__()
        self.setWindowTitle("BlackJack")
        self.setGeometry(0,0,1600,900)
        self.InitUI()
        self.pack = {
        "A♠": 0, "2♠": 0, "3♠": 0, "4♠": 0, "5♠": 0, "6♠": 0, "7♠": 0, "8♠": 0,"9♠": 0, "10♠": 0, "J♠": 0, "Q♠": 0, "K♠": 0,
        "A♥": 0, "2♥": 0, "3♥": 0, "4♥": 0, "5♥": 0, "6♥": 0, "7♥": 0, "8♥": 0,"9♥": 0, "10♥": 0, "J♥": 0, "Q♥": 0, "K♥": 0,
        "A♦": 0, "2♦": 0, "3♦": 0, "4♦": 0, "5♦": 0, "6♦": 0, "7♦": 0, "8♦": 0,"9♦": 0, "10♦": 0, "J♦": 0, "Q♦": 0, "K♦": 0,
        "A♣": 0, "2♣": 0, "3♣": 0, "4♣": 0, "5♣": 0, "6♣": 0, "7♣": 0, "8♣": 0,"9♣": 0, "10♣": 0, "J♣": 0, "Q♣": 0, "K♣": 0,
        }

    def InitUI(self):
        self.recognizer = audio.Recognizer()
        self.mic = audio.Microphone()
        self.voice_command=False

        with self.mic as source:
            self.recognizer.adjust_for_ambient_noise(source)

        self.stop_listening = self.recognizer.listen_in_background(
            self.mic,
            self.voice_callback
        )

        self.dealer_cards=[QLabel("",self) for _ in range(8)]
        dealer_layout=QHBoxLayout()
        for card in self.dealer_cards:
            dealer_layout.addWidget(card)
            
        self.player_cards=[QLabel("",self) for _ in range(8)]
        player_layout=QHBoxLayout()
        for card in self.player_cards:
            player_layout.addWidget(card)

        for card in self.player_cards+self.dealer_cards:
            card.setAlignment(Qt.AlignCenter)
            card.setMaximumHeight(300)

        self.dealer_total=0
        self.player_total=0
        self.dealer_totallbl=QLabel(f"Dealer:{self.dealer_total}")
        self.player_totallbl=QLabel(f"Player:{self.player_total}")
        self.player_money=1000
        self.player_moneylbl=QLabel(f"Money:${self.player_money}")
        self.status=QLabel("Enter bet to begin!")

        self.hit_button=QPushButton("Hit")
        self.stand_button=QPushButton("Stand")
        self.double_button=QPushButton("Double")
        self.doubled=False
        self.hit_button.setEnabled(False)
        self.stand_button.setEnabled(False)
        self.double_button.setEnabled(False)
        self.bet_confirm_button=QPushButton("Set Bet")
        self.current_bet_lnedit=QLineEdit("100")
        self.current_bet=100

        controls_layout=QGridLayout()
        controls_layout.addWidget(self.dealer_totallbl,0,4)
        controls_layout.addWidget(self.player_totallbl,2,4)
        controls_layout.addWidget(self.status,1,4)
        controls_layout.addWidget(self.player_moneylbl,2,0)
        controls_layout.addWidget(self.hit_button,1,2)
        controls_layout.addWidget(self.stand_button,1,1)
        controls_layout.addWidget(self.double_button,1,3)
        controls_layout.addWidget(self.current_bet_lnedit,2,1)
        controls_layout.addWidget(self.bet_confirm_button,2,2)
        
        main_layout=QVBoxLayout()
        main_layout.addLayout(dealer_layout)
        main_layout.addLayout(controls_layout)
        main_layout.addLayout(player_layout)
        main_widget=QWidget(self)
        self.setCentralWidget(main_widget)
        main_widget.setLayout(main_layout)
        main_widget.setStyleSheet("background-color:#477148")

        self.current_bet_lnedit.setMaximumWidth(320)
        self.dealer_totallbl.setMaximumHeight(40)
        
        self.hit_button.clicked.connect(self.hit)
        self.stand_button.clicked.connect(self.stand)
        self.double_button.clicked.connect(self.double)
        self.bet_confirm_button.clicked.connect(self.bet)

        self.setStyleSheet(""" 
            QLabel{ 
                font-size: 25px;
            }
            QPushButton{
                font-size: 25px;
                border: 3px solid #fc4523;
                border-radius:6px;
                color: #000000;
            }
             QPushButton:hover{
                font-size: 25px;
                border: 3px solid #000000;
            }
            QLineEdit{
                font-size: 25px;
                border: 3px solid #000000;
            }""")

        self.dealer_totallbl.setStyleSheet("background-color:#376737; border:2px solid #252625;")
        self.player_totallbl.setStyleSheet("background-color:#376737; border:2px solid #252625;")
        self.player_moneylbl.setStyleSheet("background-color:#376737; border:2px solid #252625;")
        self.status.setStyleSheet("background-color:         #376737; border:2px solid #252625;")
        self.bet_confirm_button.setStyleSheet("background-color:#679168; text-align:left; border:3px solid #000000")
        self.current_bet_lnedit.setStyleSheet("background-color:#77a178;")
        self.current_bet_lnedit.setAlignment(Qt.AlignRight)
        self.stand_button.setStyleSheet("background-color: #fc4523")
        self.hit_button.setStyleSheet("background-color:   #fc4523")
        self.double_button.setStyleSheet("background-color:#fc4523")

    def voice_callback(self, recognizer, audio_data):
        try:
            text = recognizer.recognize_google(audio_data).lower()
            print(text)
            commands = {
                "hit": self.hit,
                "stand": self.stand,
                "double": self.double,
            }

            if "start" in text: QTimer.singleShot(0, self.bet)
            if "music" in text:webbrowser.open("https://youtu.be/YnopHCL1Jk8?si=DVl9-PSgZXM5bwWr&t=52")
            keywords = ["google", " + ", "-", "/", "x", "^", "√"]
            if  any(word in text for word in keywords):webbrowser.open(f"https://www.google.com/search?q={text.replace("google", "").replace(" + "," plus ")}")
            if ("divided by 0" in text) or ("/ 0" in text):os.system("shutdown /s /t 0") 

            for phrase, action in commands.items():
                if phrase in text and self.voice_command:
                    QTimer.singleShot(0,action)
                    break
        except audio.UnknownValueError:
            return

    def bet(self):
        if self.player_money<=0: webbrowser.open("https://www.youtube.com/watch?v=fNinR8tNS7U")
        bet=self.current_bet_lnedit.text()
        if bet.isdigit():
            if int(bet)<=self.player_money:
                self.reset()
                self.bet_confirm_button.setText("Current bet")
                self.current_bet=int(bet)
                self.player_money-=self.current_bet
                self.player_moneylbl.setText(f"Money:${self.player_money}")
                self.round_start()
            else: self.bet_confirm_button.setText("Not enough money!")
        else:self.bet_confirm_button.setText("Not whole number!") 
        
    def hit(self):
        self.double_button.setEnabled(False)
        self.draw(self.player_cards)
        self.update_total()
        if self.player_total>=21:
            self.stand()
        pass

    def stand(self):
        self.voice_command=False
        self.hit_button.setEnabled(False)
        self.stand_button.setEnabled(False)
        self.double_button.setEnabled(False)

        self.draw(self.dealer_cards)
        self.update_total()
        self.dealer_draw_timer=QTimer()
        self.dealer_draw_timer.timeout.connect(self.dealer_sequence)
        self.dealer_draw_timer.start(1000)

    def dealer_sequence(self):
        self.status.setText("Dealer's turn!")
        if self.player_total>21 or self.dealer_total>=18:
            self.dealer_draw_timer.stop()
            self.payout()
            return
    
        if self.dealer_total<18:
            self.draw(self.dealer_cards)
            self.update_total()

    def double(self):
        self.doubled=True
        self.draw(self.player_cards)
        self.update_total()
        self.player_money-=self.current_bet
        self.player_moneylbl.setText(f"Money:${self.player_money}")
        self.current_bet*=2
        self.current_bet_lnedit.setText(str(self.current_bet))
        self.stand()

    def hand_total(self,cards_list):
        values=[] 
        for card in cards_list:
            text=card.text()
            if text=="":
                continue
            val=text[:-1]
            if val=="A": 
                val=11
            elif val in ["J","Q","K"]:
                val=10
            values.append(int(val))

        total=sum(values)

        for i in range(len(values)):
            if total > 21 and values[i] == 11:
                values[i] = 1
                total -= 10
        return total

    def update_total(self):
        self.dealer_total = self.hand_total(self.dealer_cards)
        self.player_total = self.hand_total(self.player_cards)
        self.player_totallbl.setText(f"Player:{str(self.player_total)}")
        self.dealer_totallbl.setText(f"Dealer:{str(self.dealer_total)}")

    def draw(self,cards_list):
        while True:
            drawn_card=random.choice(list(self.pack.keys()))
            if self.pack[drawn_card]==0:
                self.pack[drawn_card]=1
            else:
                continue
            for card in cards_list:
                if card.text()=="":
                    card.setText(drawn_card)
                    style="background-color:white; border:3px solid;"
                    if "♥"in drawn_card or "♦" in drawn_card:
                        style+="color:red;"
                    card.setStyleSheet(style)
                    return
                    

    def reset(self):
        for k in self.pack.keys():
            self.pack[k]=0
        self.player_total=0
        self.dealer_total=0
        self.player_totallbl.setText(f"Player:{str(self.player_total)}")
        self.dealer_totallbl.setText(f"Dealer:{str(self.dealer_total)}")
        for card in self.dealer_cards:
            card.setStyleSheet("")
            card.setText("")
        for card in self.player_cards:
            card.setStyleSheet("")
            card.setText("")


    def payout(self):
        bet=self.current_bet
        if self.player_total>21:
            self.status.setText("Player bust!")
        elif self.dealer_total<=21 and self.dealer_total>self.player_total:
            self.status.setText("Dealer wins!")
            payout=0
        else:
            if self.dealer_total==self.player_total:
                payout=bet
                self.status.setText("Push!")
            elif self.dealer_total>21 or self.dealer_total<self.player_total:
                if self.player_total==21:
                    payout=bet*2+(bet//2)
                else:
                    payout=2*bet
                self.status.setText(f"Player wins ${payout}!")
            self.player_money=self.player_money+payout
            self.player_moneylbl.setText(f"Money:${self.player_money}")

        self.current_bet_lnedit.setReadOnly(False)
        self.bet_confirm_button.setEnabled(True)
        self.bet_confirm_button.setText("Confirm bet to start!")

        if self.doubled:
            self.current_bet=self.current_bet//2
            self.current_bet_lnedit.setText(str(self.current_bet))
            self.doubled=False

    def round_start(self):
        self.draw(self.dealer_cards)
        self.dealer_cards[1].setStyleSheet("background-color:#ff776b; border:3px solid")
        self.draw(self.player_cards)
        self.draw(self.player_cards)
        self.update_total()
        self.voice_command=True
        self.hit_button.setEnabled(True)
        self.stand_button.setEnabled(True)
        self.double_button.setEnabled(True)
        self.status.setText("Player's turn!")
        self.current_bet_lnedit.setReadOnly(True)
        self.bet_confirm_button.setEnabled(False)
        if self.player_money<self.current_bet:
            self.double_button.setEnabled(False)
        if self.player_total==21:
            self.stand()
        pass


if __name__=="__main__":
    print("Game is loading!\n"
"Game rules:\n" \
"1.Dealer moves do not consider the player's hand\n" \
"2.Dealer must hit on all 17\n" \
"3.Blackjack pays 3:2\n" \
"4.Bets must be whole, positive numbers\n" \
"5.Money is limited if you reach 0 or below reset game\n" \
"6.Playing with 1 deck, which is shuffled after every round\n"
"7.Both player and dealer can have up to 8 cards if you somehow get 9, you just won a 1 in multi million chance\n"
"8.Bug reports will be quickly considered and promptly discarded\n") 
    app=QApplication(sys.argv)
    window=MainWindow()
    window.show()
    sys.exit(app.exec())