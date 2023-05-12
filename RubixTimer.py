from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QThread, pyqtSignal
from datetime import datetime, timedelta
import random
import csv

from view import Ui_MainWindow
QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

class Timer(QThread):
    """
    A timer that runs in a separate thread and emits a signal when the time is updated.

    Attributes:
        time_updated (pyqtSignal): A signal that is emitted when the time is updated.
        is_running (bool): Whether the timer is currently running.
        start_time (datetime): The time when the timer was started.
        elapsed_time (timedelta): The elapsed time since the timer was started.
        scramble (str): The scramble that was used to start the timer.
    """

    time_updated = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.is_running: bool = False
        self.start_time: datetime = None
        self.elapsed_time: timedelta = timedelta(0)
        self.scramble: str = None

    def run(self) -> None:
        """
        Runs the timer loop until the timer is stopped.
        Updates the elapsed time and emits the time updated signal every 10 milliseconds.
        """
        while self.is_running:
            self.elapsed_time = datetime.now() - self.start_time
            time_str = "{:02d}.{:02d}".format(
                self.elapsed_time.seconds,
                self.elapsed_time.microseconds // 10000)
            self.time_updated.emit(time_str)
            self.msleep(10)

    def start_timer(self) -> None:
        """
        Starts the timer and sets the start time and is_running attribute.
        """
        self.start_time = datetime.now()
        self.is_running = True
        self.start()

    def stop_timer(self) -> None:
        """
        Stops the timer and waits for the thread to finish.
        """
        self.is_running = False
        self.wait()

    def generate_scramble(self) -> str:
        """
        Generates a random scramble of 15 moves and returns it.
        """
        moves = ["U", "D", "L", "R", "F", "B"]
        modifiers = ["", "'", "2"]
        scramble = " ".join([random.choice(moves) + random.choice(modifiers) for _ in range(15)])
        self.scramble = scramble
        return scramble

    def save_time(self, username: str, time: str) -> None:
        """
        Saves the given username, time, and scramble to a CSV file.
        Raises a ValueError if the username is empty.
        """
        if not username:
            raise ValueError("Username cannot be empty.")
        with open("times.csv", "a", newline="") as f:
            writer = csv.writer(f)
            if f.tell() == 0:
                writer.writerow(['Username', 'Time', 'Scramble'])
            writer.writerow([username, time, self.scramble])

    def reset_timer(self) -> None:
        """
        Resets the elapsed time to zero and emits the time updated signal with "00.00".
        """
        self.elapsed_time = timedelta(0)
        self.time_updated.emit("00.00")


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.timer = Timer()
        self.timer.time_updated.connect(self.Timer_stopwatch.setText)

        self.New_Scramble.clicked.connect(self.generate_scramble)
        self.StartandStop.clicked.connect(self.start_stop_timer)
        self.Save.clicked.connect(self.save_time)

    def generate_scramble(self) -> None:
        """
        Generates a new scramble and sets the text of the Scramble_Output label to it.
        """
        scramble = self.timer.generate_scramble()
        self.Scramble_Output.setText(scramble)

    def start_stop_timer(self) -> None:
        """
        Starts or stops the timer and updates the text of the StartandStop button accordingly.
        """
        if not self.timer.is_running:
            self.timer.start_timer()
            self.StartandStop.setText("Stop")
        else:
            self.timer.stop_timer()
            self.StartandStop.setText("Start")

    def save_time(self) -> None:
        """
        Saves the time, username and scramble to a csv file and resets the timer.
        Displays an error message if the username is empty.
        """
        username: str = self.Username.text()
        time: str = "{:02d}.{:02d}".format(
            self.timer.elapsed_time.seconds,
            self.timer.elapsed_time.microseconds // 10000)
        try:
            self.timer.save_time(username, time)
        except ValueError as e:
            QtWidgets.QMessageBox.critical(self, "Input Username Please", str(e))
        else:
            self.timer.reset_timer()



