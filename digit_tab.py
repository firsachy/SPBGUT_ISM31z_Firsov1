import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageTk
import io
from tensorflow.keras.datasets import mnist

class DigitTab:
    def __init__(self, parent_frame, database):
        self.frame = parent_frame
        self.bd = database

        #Загружаем данные mnist
        (_, _), (self.X_test, self.y_test) = mnist.load_data()
        self.current_idx = 0


        self.setup_ui()
        self.show_random_digit()



    def setup_ui(self):
        # Заголовок для демонстрации
        label = tk.Label(self.frame, text="Работа с цифрами MNIST", font=("Arial", 14, "bold"), pady=20)
        label.pack()

        #бласть для изображения цифры
        self.image_label = tk.Label(self.frame, bg="white", relief="solid", bd=1)
        self.image_label.pack(pady=20)

        # Метка с правильным ответом (для отладки)
        self.answer_label = tk.Label(self.frame, text="", font=("Arial", 10), fg="gray")
        self.answer_label.pack()

        # Фрейм для кнопок
        button_frame = tk.Frame(self.frame)
        button_frame.pack(pady=20)

        #Кнопки обратной связи
        self.btn_yes = tk.Button(button_frame, 
                                text="✅ Да", 
                                width=12,
                                height=2,
                                bg="#4CAF50",
                                fg="white",
                                font=("Arial", 10, "bold"),
                                command=self.on_yes)
        self.btn_yes.pack(side=tk.LEFT, padx=10)

        self.btn_no = tk.Button(button_frame,
                               text="❌ Нет", 
                               width=12,
                               height=2,
                               bg="#F44336", 
                               fg="white",
                               font=("Arial", 10, "bold"),
                               command=self.on_no)
        self.btn_no.pack(side=tk.LEFT, padx=10)

        self.btn_later = tk.Button(button_frame,
                                  text="⏰ Ответить позже",
                                  width=15,
                                  height=2,
                                  bg="#FF9800",
                                  fg="white",
                                  font=("Arial", 10, "bold"),
                                  command=self.on_later)
        self.btn_later.pack(side=tk.LEFT, padx=10)

        # Статусная строка
        self.status_label = tk.Label(self.frame,
                                    text="Готов к работе",
                                    font=("Arial", 9),
                                    fg="green")
        self.status_label.pack(pady=10)

        # Счетчик
        self.counter_label = tk.Label(self.frame,
                                     text="Обработано: 0 цифр",
                                     font=("Arial", 9))
        self.counter_label.pack()
        
        self.counter = 0


    def array_to_image(self, digit_array):
        """Конвертируем массив numpy в изображение для tkinter"""
        plt.figure(figsize=(3, 3))
        plt.imshow(digit_array, cmap='gray')
        plt.axis('off')
        
        # Сохраняем в буфер вместо файла
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0, dpi=80)
        buf.seek(0)
        plt.close()
        
        return Image.open(buf)
    
    def show_random_digit(self):
        """Показываем случайную цифру из MNIST"""
        self.current_idx = np.random.randint(0, len(self.X_test))
        digit = self.X_test[self.current_idx]
        self.current_label = self.y_test[self.current_idx]
        
        # Конвертируем и показываем
        image = self.array_to_image(digit)
        photo = ImageTk.PhotoImage(image)
        
        self.image_label.configure(image=photo)
        self.image_label.image = photo  # сохраняем ссылку!
        
        # Показываем правильный ответ (для отладки)
        self.answer_label.config(text=f"Правильный ответ: {self.current_label}")
    
    def on_yes(self):
        self.counter += 1
        
        # ПОКА ЗАГЛУШКА - просто выводим в консоль
        print(f"✅ YES: image_id={self.current_idx}, label={self.current_label}")
        # Позже здесь будет: self.db.save_feedback(...)
        
        self.status_label.config(text=f"✅ Подтверждено: {self.current_label}", fg="green")
        self.counter_label.config(text=f"Обработано: {self.counter} цифр")
        self.show_random_digit()
    
    def on_no(self):
        self.counter += 1
        print(f"❌ NO: image_id={self.current_idx}, label={self.current_label}")
        
        self.status_label.config(text=f"❌ Отвергнуто: {self.current_label}", fg="red")
        self.counter_label.config(text=f"Обработано: {self.counter} цифр")
        self.show_random_digit()
    
    def on_later(self):
        self.counter += 1
        print(f"⏰ LATER: image_id={self.current_idx}, label={self.current_label}")
        
        self.status_label.config(text=f"⏰ Отложено: {self.current_label}", fg="orange")
        self.counter_label.config(text=f"Обработано: {self.counter} цифр")
        self.show_random_digit()