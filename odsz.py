import sys
import pandas as pd
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QFileDialog, QTextEdit,QLineEdit,
    QSpinBox
)
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Ustawienia okna głównego
        self.setWindowTitle("Otwieranie pliku CSV")
        self.setGeometry(100, 100, 400, 300)
        
        # Przygotowanie głównego widgetu
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Layout główny
        layout = QVBoxLayout()
        
       # self.line_edit=QLineEdit()
        #self.line_edit.setPlaceholderText("Wpisz kanal do odszumiania [1-]")
        #int_validator = QIntValidator(0,100)
        #self.line_edit.setValidator(int_validator)
        #layout.addWidget(self.line_edit)

        self.spin_box = QSpinBox()
        self.spin_box.setMinimum(1)
        self.spin_box.setMaximum(10)
        self.spin_box.setValue(1)
        self.spin_box.setSingleStep(1)
        self.spin_box.setSuffix(" (nr kanalu do odszumiania)")
        layout.addWidget(self.spin_box)
        # Przyciski
        self.button_open = QPushButton("Otwórz plik CSV")
        self.button_open.clicked.connect(self.open_csv_file)
        layout.addWidget(self.button_open)

        self.button_oscylogram = QPushButton("Oscylogram")
        self.button_oscylogram.clicked.connect(self.show_oscylogram)
        self.button_oscylogram.setDisabled(True)
        layout.addWidget(self.button_oscylogram)

        self.button_odsz1 = QPushButton("Odszumianie 1 - Średnia ruchoma")
        self.button_odsz1.clicked.connect(self.odszumianie1)
        self.button_odsz1.setDisabled(True)
        layout.addWidget(self.button_odsz1)

        self.button_odsz2 = QPushButton("Odszumianie 2 - Filtr dolnoprzepustowy")
        self.button_odsz2.clicked.connect(self.odszumianie2)
        self.button_odsz2.setDisabled(True)
        layout.addWidget(self.button_odsz2)
        
        # Pole tekstowe do wyświetlania zawartości pliku
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        layout.addWidget(self.text_area)

        self.save_signal = QPushButton("Zapisz ostatnio odszumiony sygnał")
        self.save_signal.clicked.connect(self.save_s)
        self.save_signal.setDisabled(True)
        layout.addWidget(self.save_signal)
        # Przypisanie layoutu do centralnego widgetu
        self.central_widget.setLayout(layout)
    

    def save_s(self):
        print(self.smoothed_signal)
        df = self.data
        df.iloc[:,self.spin_box.value()] = self.smoothed_signal
        df.to_csv("odszumiony_sygnal.csv",index=False)
    def moving_average(self,signal, window_size):
        return np.convolve(signal, np.ones(window_size)/window_size, mode='same')


    def lowpass_filter(self,data,cutoff,fs,order=4):
        nyquist = 0.5 * fs
        normal_cutoff = cutoff / nyquist
        b,a = butter(order,normal_cutoff,btype='low',analog=False)
        filtered_data = filtfilt(b,a,data)
        return filtered_data
        

    def odszumianie1(self):
        window_size = 50  # Liczba próbek w oknie
        self.smoothed_signal = self.moving_average(self.data.iloc[:,self.spin_box.value()], window_size)
        plt.figure(figsize=(10, 6))
        plt.plot(self.data.iloc[:,0], self.data.iloc[:,self.spin_box.value()], label="Sygnal oryginalny", alpha=0.7)
        plt.plot(self.data.iloc[:,0], self.smoothed_signal, label="Sygnal odszumiony", color="green")
        plt.title("Odszumianie sygnału")
        plt.xlabel("Czas")
        plt.ylabel("Amplituda")
        plt.legend()
        plt.grid(alpha=0.5)
        plt.show()
        self.save_signal.setDisabled(False)

    def odszumianie2(self):
        cutoff = 10
        fs = 500
        self.smoothed_signal = self.lowpass_filter(self.data.iloc[:,self.spin_box.value()],cutoff,fs)
        plt.figure(figsize=(10, 6))
        plt.plot(self.data.iloc[:,0], self.data.iloc[:,self.spin_box.value()], label="Sygnal oryginalny", alpha=0.7)
        plt.plot(self.data.iloc[:,0], self.smoothed_signal, label="Sygnal odszumiony", color="green")
        plt.title("Odszumianie sygnału")
        plt.xlabel("Czas")
        plt.ylabel("Amplituda")
        plt.legend()
        plt.grid(alpha=0.5)
        plt.show()
        self.save_signal.setDisabled(False)

    def show_oscylogram(self):
        plt.figure(figsize=(10, 6))
        plt.plot(self.data.iloc[:,0],self.data.iloc[:,1], label="Noisy Signal", color="blue", alpha=0.7)
        plt.title("Oscylogram sygnalu", fontsize=14)
        plt.xlabel("Czas [s]", fontsize=12)
        plt.ylabel("Amplituda", fontsize=12)
        plt.legend()
        plt.grid(alpha=0.5)
        plt.show()


    def open_csv_file(self):
        # Otwieranie dialogu do wyboru pliku
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Wybierz plik CSV", "", "CSV Files (*.csv);;All Files (*)", options=options
        )
        
        if file_path:
            try:
                # Wczytanie pliku CSV i wyświetlenie jego zawartości
                self.data = pd.read_csv(file_path)
                self.num_samples = self.data.shape[0]
                

                time_diff = self.data.iloc[:,0].diff().dropna().mean()  
                fs = 1 / time_diff
                self.text_area.setText(f"Liczba próbek: {self.num_samples}.\nCzestotliwosc probkowania: {fs:.2f}Hz")
 
            except Exception as e:
                self.text_area.setText(f"Błąd podczas otwierania pliku:\n{e}")

        self.button_oscylogram.setDisabled(False)
        self.button_odsz1.setDisabled(False)
        self.button_odsz2.setDisabled(False)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()