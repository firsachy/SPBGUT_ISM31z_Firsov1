import tkinter as tk
import os
import sqlite3

class DBTab:
    def __init__(self, parent_frame, database):
        self.frame = parent_frame
        self.db = database
        self.setup_ui()
    
    def setup_ui(self):
        title = tk.Label(self.frame, text="Управление базой данных", 
                        font=("Arial", 14), pady=20)
        title.pack()
        
        # Статистика БД
        stats_frame = tk.Frame(self.frame)
        stats_frame.pack(pady=10)
        
        self.stats_label = tk.Label(stats_frame, 
                                   text="Загрузка статистики...",
                                   font=("Arial", 10))
        self.stats_label.pack()
        
        # Кнопки управления
        buttons_frame = tk.Frame(self.frame)
        buttons_frame.pack(pady=20)
        
        # Кнопка сброса БД
        self.reset_btn = tk.Button(buttons_frame,
                                  text="🗑️ Очистить базу данных",
                                  width=20,
                                  height=2,
                                  bg="#FF6B6B",
                                  fg="white",
                                  font=("Arial", 10, "bold"),
                                  command=self.reset_database)
        self.reset_btn.pack(pady=5)
        
        # Кнопка обновления статистики
        self.refresh_btn = tk.Button(buttons_frame,
                                    text="🔄 Обновить статистику",
                                    width=20,
                                    height=2,
                                    bg="#4ECDC4",
                                    fg="white",
                                    font=("Arial", 10, "bold"),
                                    command=self.update_stats)
        self.refresh_btn.pack(pady=5)
        
        # Статус
        self.status_label = tk.Label(self.frame,
                                    text="База данных: активна",
                                    font=("Arial", 9),
                                    fg="green")
        self.status_label.pack(pady=10)
        
        # Первоначальное обновление статистики
        self.update_stats()
    
    def update_stats(self):
        """Обновить статистику БД"""
        try:
            # Здесь позже добавим реальную статистику
            db_path = "data/feedback.db"
            if os.path.exists(db_path):
                size = os.path.getsize(db_path)
                self.stats_label.config(
                    text=f"Размер БД: {size} байт\nЗаписей: 0"  # Временно
                )
                self.status_label.config(
                    text="База данных: активна",
                    fg="green"
                )
            else:
                self.stats_label.config(text="База данных не найдена")
                self.status_label.config(
                    text="База данных: отсутствует",
                    fg="red"
                )
        except Exception as e:
            self.stats_label.config(text=f"Ошибка: {str(e)}")
    
    def reset_database(self):
        """Очистить базу данных"""
        import tkinter.messagebox as msgbox
        
        result = msgbox.askyesno(
            "Подтверждение",
            "Вы уверены, что хотите очистить базу данных?\n\n"
            "Все сохраненные фидбеки будут удалены безвозвратно!"
        )
        
        if result:
            try:
                # Закрываем и пересоздаем БД
                self.db.close_connection()
                import time
                time.sleep(0.5)
                
                db_path = "data/feedback.db"
                if os.path.exists(db_path):
                    os.remove(db_path)
                    
                self.db.reconnect()
                
                self.status_label.config(
                    text="База данных: ОЧИЩЕНА", 
                    fg="orange"
                )
                self.update_stats()
                
                msgbox.showinfo("Успех", "База данных очищена!")
                
            except Exception as e:
                msgbox.showerror("Ошибка", f"Не удалось очистить БД: {str(e)}")