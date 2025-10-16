import tkinter as tk

class AboutTab:
    def __init__(self, parent_frame):
        self.frame = parent_frame
        self.setup_ui()
    
    def setup_ui(self):
        # Основной контейнер с отступами
        main_container = tk.Frame(self.frame, padx=20, pady=20)
        main_container.pack(expand=True, fill='both')
        
        # Заголовок
        title = tk.Label(main_container, 
                        text="Экспериментальная платформа гибридного обучения",
                        font=("Arial", 16, "bold"),
                        fg="#2E86AB",
                        pady=20)
        title.pack()
        
        # Разделитель
        separator = tk.Frame(main_container, height=2, bg="#E0E0E0")
        separator.pack(fill='x', pady=10)
        
        # Информация об авторе
        author_frame = tk.Frame(main_container)
        author_frame.pack(pady=15, anchor='w')
        
        tk.Label(author_frame, text="Автор:", 
                font=("Arial", 11, "bold")).grid(row=0, column=0, sticky='w')
        tk.Label(author_frame, text="Фирсов Виталий Николаевич",
                font=("Arial", 11)).grid(row=0, column=1, sticky='w', padx=(10, 0))
        
        tk.Label(author_frame, text="ВУЗ:", 
                font=("Arial", 11, "bold")).grid(row=1, column=0, sticky='w', pady=(5, 0))
        tk.Label(author_frame, 
                text="СПбГУТ им. проф. М.А. Бонч-Бруевича",
                font=("Arial", 11)).grid(row=1, column=1, sticky='w', padx=(10, 0), pady=(5, 0))
        
        tk.Label(author_frame, text="Факультет:", 
                font=("Arial", 11, "bold")).grid(row=2, column=0, sticky='w', pady=(5, 0))
        tk.Label(author_frame, text="ИНО, группа ИСМ-31з",
                font=("Arial", 11)).grid(row=2, column=1, sticky='w', padx=(10, 0), pady=(5, 0))
        
        # Цель программы
        goal_frame = tk.Frame(main_container)
        goal_frame.pack(pady=20, fill='x')
        
        goal_title = tk.Label(goal_frame, 
                             text="Цель программы:",
                             font=("Arial", 12, "bold"),
                             fg="#A23B72",
                             anchor='w')
        goal_title.pack(fill='x')
        
        goal_text = tk.Label(goal_frame,
                           text="Практическая апробация гибридного метода машинного обучения, \n"
                                "сочетающего микро-обратную связь и отложенную верификацию данных.\n"
                                "Программа предназначена для сбора экспериментальных данных \n"
                                "и оценки эффективности предложенного подхода.",
                           font=("Arial", 10),
                           justify=tk.LEFT,
                           pady=10)
        goal_text.pack(fill='x')
        
        # Методология
        method_frame = tk.Frame(main_container)
        method_frame.pack(pady=15, fill='x')
        
        method_title = tk.Label(method_frame,
                               text="Методология:",
                               font=("Arial", 12, "bold"),
                               fg="#A23B72",
                               anchor='w')
        method_title.pack(fill='x')
        
        method_text = tk.Label(method_frame,
                             text="• Микро-обратная связь: оперативные реакции пользователя (Да/Нет/Не знаю)\n"
                                  "• Отложенная верификация: точное подтверждение диагнозов после проверки\n"
                                  "• Адаптивное обучение: динамическая корректировка весов модели\n"
                                  "• Кластерный анализ: группировка схожих случаев для глобальных обновлений",
                             font=("Arial", 9),
                             justify=tk.LEFT,
                             pady=8)
        method_text.pack(fill='x')
        
        # Статус
        status_frame = tk.Frame(main_container)
        status_frame.pack(side=tk.BOTTOM, pady=20)
        
        status_label = tk.Label(status_frame,
                               text="🚀 Система готова к экспериментам",
                               font=("Arial", 10, "bold"),
                               fg="#18A558")
        status_label.pack()
        
        # Декоративный элемент внизу
        footer = tk.Label(main_container,
                         text="Магистерская диссертация • 2024",
                         font=("Arial", 8),
                         fg="#888888")
        footer.pack(side=tk.BOTTOM, pady=5)