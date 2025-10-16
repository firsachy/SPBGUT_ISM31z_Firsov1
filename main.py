import tkinter as tk
from tkinter import ttk
from digit_tab import DigitTab
from verify_tab import VerifyTab
from config_tab import ConfigTab
from about_tab import AboutTab
from database import Database
#from db_tab import DBTab
from results_tab import ResultsTab

class HybridTrainer:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Тест гибридной модели")
        self.window.geometry("1000x800")

        # Инициализируем БД
        self.db = Database()

        self.setup_tabs()

    def setup_tabs(self):
        #Создаем панедь вкладок
        notebook = ttk.Notebook(self.window)

        #Создаем вкладки
        digit_frame = ttk.Frame(notebook)
        verify_frame = ttk.Frame(notebook)
        config_frame = tk.ttk.Frame(notebook)
        #db_frame = tk.ttk.Frame(notebook)
        results_frame = tk.ttk.Frame(notebook)
        about_frame = tk.ttk.Frame(notebook)

        #Инициируем логику вкладок
        self.digit_tab = DigitTab(digit_frame, self.db)
        self.verify_tab = VerifyTab(verify_frame)
        self.config_tab = ConfigTab(config_frame, self.db)
        #self.db_tab = DBTab(db_frame, self.db)
        self.results_tab = ResultsTab(results_frame, self.db)
        self.about_tab = AboutTab(about_frame)

        #Добавляем вкладки в консоль
        notebook.add(digit_frame, text="Работа с числами")
        notebook.add(verify_frame, text="Верификация")
        notebook.add(config_frame, text="Настройки ИИ")
        #otebook.add(db_frame, text="Управление БД")
        notebook.add(results_frame, text="Результаты")
        notebook.add(about_frame, text="О программе")

        notebook.pack(expand=True, fill='both', padx=10, pady=10)

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = HybridTrainer()
    app.run()
    print("Тест гибридной модели запущен")