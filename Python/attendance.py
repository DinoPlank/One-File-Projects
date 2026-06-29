#arata mesajele:apropiati cardul, introduceti nume, procesare date, LEDUL LUI DAVID
import gspread,time,sys
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton, QWidget, QLineEdit
from PyQt5.QtCore import Qt, QTimer

class Verde(QMainWindow):
    def __init__(self,):
        super().__init__()
        self.setWindowTitle("LED-ul verde al lui David")
        self.setGeometry(0,0,300,300)
        self.initUI()
    
    def initUI(self):
        self.main_widget=QWidget(self)
        self.setCentralWidget(self.main_widget)
        self.main_widget.setStyleSheet("background-color:#00ff00")

class Rosu(QMainWindow):
    def __init__(self,):
        super().__init__()
        self.setWindowTitle("LED-ul rosu al lui David")
        self.setGeometry(0,0,300,300)
        self.initUI()
    
    def initUI(self):
        self.main_widget=QWidget(self)
        self.setCentralWidget(self.main_widget)
        self.main_widget.setStyleSheet("background-color:#ff0000")

app=QApplication(sys.argv)
ledv=Verde()
ledr=Rosu()
ledv.show()

def parse_sheet_timestamp(value, timestamp_format: str = "%Y-%m-%d %H:%M:%S"):
    if value is None:
        return None
    text = str(value).replace("\u00A0", " ").strip()
    if not text:
        return None
    try:
        return datetime.strptime(text, timestamp_format)
    except ValueError:
        return None


def get_rightmost_timestamp_col_and_latest_dt(
    worksheet,
    min_row: int = 2,
    start_col: int = 3,
    timestamp_format: str = "%Y-%m-%d %H:%M:%S",
):
    """Return (rightmost_col_with_ts, latest_dt_in_that_col).

    Only scans rows >= min_row.
    If no timestamps are found, returns (start_col + 1, None) (i.e. default OUT col = D).
    """

    max_col = max(getattr(worksheet, "col_count", 0) or 0, len(worksheet.row_values(1)), start_col)

    for col in range(max_col, start_col - 1, -1):
        col_values = worksheet.col_values(col)
        latest_dt = None
        for idx in range(min_row - 1, len(col_values)):
            dt = parse_sheet_timestamp(col_values[idx], timestamp_format)
            if dt and (latest_dt is None or dt > latest_dt):
                latest_dt = dt
        if latest_dt is not None:
            return col, latest_dt

    return start_col + 1, None

def mainbody(): #!!nu era functie inainte
    #se poate face ca si functie ce se acativeaza din termminal linux raspberryPI
    # Setup Google Sheets API
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("C:\\Users\\acatr\\Desktop\\Code\\Programe_RPi\\simulareprezenta-eace2ba65836.json", scope)
    client = gspread.authorize(creds)

    sheet = client.open("simulare_prezenta").sheet1 #Aici selectam documentul in care vrem sa lucram

    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")

            # Find the biggest timestamp column with data (rows>=2) and decide where to write.
    biggest_ts_col, biggest_ts_dt = get_rightmost_timestamp_col_and_latest_dt(sheet, min_row=2, start_col=3)

    print("coloana este:",biggest_ts_col)
    print("ultima data este:",biggest_ts_dt) 

            # Treat the pair as (IN=even-1, OUT=even). If biggest is odd (IN), normalize to its OUT.
    current_out_col = biggest_ts_col if (biggest_ts_col % 2 == 0) else (biggest_ts_col + 1)
    current_out_col = max(current_out_col, 4)  # at least D

    if biggest_ts_dt is None:
                past_week_or_more = False
    else:
                now_iso = now.isocalendar()
                print("now:", now_iso)
                last_iso = biggest_ts_dt.isocalendar()
                print("last:", last_iso)
                past_week_or_more = (now_iso.year, now_iso.weekday) != (last_iso.year, last_iso.weekday)
                print("now", now_iso.weekday)
                print("last", last_iso.weekday)
                print("past:",past_week_or_more)

    if past_week_or_more:
                in_col = current_out_col + 1
                out_col = current_out_col + 2
    else:
                out_col = current_out_col
                in_col = current_out_col - 1
    print("out_col",out_col)
    print("in_col",in_col)

    try:
        while True:
        
            # Get user input
            print('Apropie cardul')
            ledr.hide()
            ledv.show()
            search_term =input("Apropiati cardul(introduceti un id)\n")
            ledv.hide()
            ledr.show()
            now = datetime.now()
            current_time = now.strftime("%Y-%m-%d %H:%M:%S")
            print("Datele se proceseaza")
            # Read column A
            
            column_a = sheet.col_values(1)
            # Search for the term
            found = False
            for index, value in enumerate(column_a, start=1):
                if index < 2:
                    continue  # compare only from row 2
            
                if value == str(search_term):
                    found=True
                    cell_in = sheet.cell(index, in_col).value
                    last_time = parse_sheet_timestamp(cell_in) #!!cod nou
                    if last_time and (now-last_time).total_seconds() <= 60: break
                    if parse_sheet_timestamp(sheet.cell(index,out_col).value):break
                    if cell_in: #!!cod nou, conditia 2 si 3,trebuie testat
                        sheet.update_cell(index, out_col, current_time)
                        print("Citire Reusita")
                        time.sleep(1)
                    else:
                        sheet.update_cell(index, in_col, current_time)
                        print("Citire Reusita")
                        time.sleep(1)
                    found = True
                    
                    break

            if found == False:
                specialcase = input("Scrieti numele:")

                # Append a row, placing the timestamp in the computed IN column.
                row_values = [""] * max(out_col, 2)
                row_values[0] = str(search_term)
                row_values[1] = str(specialcase)
                if in_col - 1 >= len(row_values):
                    row_values.extend([""] * (in_col - len(row_values)))
                row_values[in_col - 1] = current_time

                sheet.append_row(row_values)

                print(f"➕ '{search_term}' added to the sheet.")


    except KeyboardInterrupt:
        print("\n🛑 Program stopped by user.")

selection=1
#selection=int(input("Apasati 1 pentru a incepe rularea codului")) #!!daca se doreste pornirea automata a ecodului se marcheaza linia ca si comentariu
if selection==1:
    mainbody()
     #schimbari: se poate alege cand ruleaza codul,interval minim de scriere a timpului de iesire fata de cel de intrare
