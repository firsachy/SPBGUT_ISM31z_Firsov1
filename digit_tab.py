import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageTk
import io
from tensorflow.keras.datasets import mnist
from ml_core import HybridMLCore  # ← ДОБАВИЛИ ИМПОРТ

class DigitTab:
    def __init__(self, parent_frame, database, ml_core):
        self.frame = parent_frame
        self.db = database
        self.ml_core = ml_core
        
        # Загружаем данные MNIST
        (_, _), (self.X_test, self.y_test) = mnist.load_data()
        # Нормализуем как в ConfigTab
        self.X_test = self.X_test.astype('float32') / 255.0
        
        self.current_idx = 0
        self.current_prediction = None
        self.current_confidence = None
        self.current_cluster_id = None
        self.current_features = None

        self.setup_ui()
        self.load_ml_model()  # ← ЗАГРУЖАЕМ МОДЕЛЬ ПРИ СТАРТЕ
        self.show_random_digit()

    def load_ml_model(self):
        """Проверяет готовность ML модели"""
        try:
            if self.ml_core and self.ml_core.is_trained and self.ml_core.clusters:
                print("✅ ML модель готова в DigitTab")
                self.status_label.config(text="✅ Модель загружена - система готова", fg="green")
            else:
                print("⚠️  Модель не готова. Обучите в настройках ИИ.")
                self.status_label.config(text="⚠️  Обучите модель в настройках ИИ", fg="orange")

        except Exception as e:
            print(f"❌ Ошибка проверки модели: {e}")
            self.status_label.config(text="❌ Ошибка загрузки модели", fg="red")
    



    def setup_ui(self):
        # Заголовок для демонстрации
        label = tk.Label(self.frame, text="Работа с цифрами MNIST", font=("Arial", 14, "bold"), pady=20)
        label.pack()

        # Область для изображения цифры
        self.image_label = tk.Label(self.frame, bg="white", relief="solid", bd=1)
        self.image_label.pack(pady=20)

        # Метка с ПРЕДСКАЗАНИЕМ системы (вместо правильного ответа)
        self.prediction_label = tk.Label(self.frame, text="", font=("Arial", 12, "bold"))
        self.prediction_label.pack()

        # Метка с уверенностью системы
        self.confidence_label = tk.Label(self.frame, text="", font=("Arial", 10))
        self.confidence_label.pack()

        # Метка с правильным ответом (для отладки - можно убрать позже)
        #self.answer_label = tk.Label(self.frame, text="", font=("Arial", 10), fg="gray")
        #self.answer_label.pack()

        # Фрейм для кнопок
        button_frame = tk.Frame(self.frame)
        button_frame.pack(pady=20)

        # Кнопки обратной связи
        self.btn_yes = tk.Button(button_frame, 
                                text="✅ Да", 
                                width=12,
                                height=2,
                                bg="#4CAF50",
                                fg="white",
                                font=("Arial", 10, "bold"),
                                command=self.on_yes,
                                state="disabled")  # ← Изначально выключена
        self.btn_yes.pack(side=tk.LEFT, padx=10)

        self.btn_no = tk.Button(button_frame,
                               text="❌ Нет", 
                               width=12,
                               height=2,
                               bg="#F44336", 
                               fg="white",
                               font=("Arial", 10, "bold"),
                               command=self.on_no,
                               state="disabled")  # ← Изначально выключена
        self.btn_no.pack(side=tk.LEFT, padx=10)

        self.btn_later = tk.Button(button_frame,
                                  text="⏰ Не знаю",
                                  width=15,
                                  height=2,
                                  bg="#FF9800",
                                  fg="white",
                                  font=("Arial", 10, "bold"),
                                  command=self.on_later,
                                  state="disabled")  # ← Изначально выключена
        self.btn_later.pack(side=tk.LEFT, padx=10)

        # Кнопка следующего числа
        self.next_btn = tk.Button(self.frame,
                                 text="Следующее число →",
                                 width=15,
                                 height=2,
                                 bg="#2196F3",
                                 fg="white",
                                 font=("Arial", 10, "bold"),
                                 command=self.show_random_digit)
        self.next_btn.pack(pady=10)

        # Статусная строка
        self.status_label = tk.Label(self.frame,
                                    text="Загружаем модель...",
                                    font=("Arial", 9),
                                    fg="orange")
        self.status_label.pack(pady=10)

        # Счетчик
        self.counter_label = tk.Label(self.frame,
                                     text="Обработано: 0 цифр",
                                     font=("Arial", 9))
        self.counter_label.pack()
        
        self.counter = 0

    def array_to_image(self, digit_array):
        """Конвертируем массив numpy в изображение для tkinter"""
        # Денормализуем для отображения
        display_array = (digit_array * 255).astype('uint8')
        
        plt.figure(figsize=(3, 3))
        plt.imshow(display_array, cmap='gray')
        plt.axis('off')
        
        # Сохраняем в буфер вместо файла
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0, dpi=80)
        buf.seek(0)
        plt.close()
        
        return Image.open(buf)
    
    def show_random_digit(self):
        """Показываем случайную цифру и получаем предсказание от системы"""
        if not self.ml_core:
            self.status_label.config(text="❌ Модель не загружена! Обучите в настройках ИИ", fg="red")
            return
        
        self.current_idx = np.random.randint(0, len(self.X_test))
        digit_image = self.X_test[self.current_idx]
        self.current_label = self.y_test[self.current_idx]  # Правильный ответ (для отладки)
        
        # Получаем ПРЕДСКАЗАНИЕ от системы
        try:
            predicted_digit, confidence, cluster_id, features = self.ml_core.predict(digit_image)
            
            self.current_prediction = predicted_digit
            self.current_confidence = confidence
            self.current_cluster_id = cluster_id
            self.current_features = features
            
            # Обновляем интерфейс с предсказанием
            self.prediction_label.config(text=f"Система предполагает: {predicted_digit}")
            self.confidence_label.config(text=f"Уверенность: {confidence:.2%}")
            
            # Цвет уверенности
            if confidence > 0.7:
                self.prediction_label.config(fg="green")
            elif confidence > 0.4:
                self.prediction_label.config(fg="orange")
            else:
                self.prediction_label.config(fg="red")
                
        except Exception as e:
            print(f"❌ Ошибка предсказания: {e}")
            self.prediction_label.config(text="Ошибка предсказания", fg="red")
            self.confidence_label.config(text="")
            return
        
        # Конвертируем и показываем изображение
        image = self.array_to_image(digit_image)
        photo = ImageTk.PhotoImage(image)
        
        self.image_label.configure(image=photo)
        self.image_label.image = photo  # сохраняем ссылку!
        
        # Показываем правильный ответ (для отладки - можно убрать)
        #self.answer_label.config(text=f"Правильный ответ: {self.current_label} (ID: {self.current_idx})")
        
        # АКТИВИРУЕМ кнопки обратной связи
        self.btn_yes.config(state="normal")
        self.btn_no.config(state="normal")
        self.btn_later.config(state="normal")
        
        self.status_label.config(text="✅ Оцените предсказание системы", fg="green")
    
    def on_yes(self):
        """Пользователь подтверждает предсказание"""
        if not self.ml_core or self.current_prediction is None:
            return
            
        self.counter += 1

        # ПРОВЕРЯЕМ что кластер существует перед обновлением
        config = self.db.load_system_config()
        alpha = config['weights']['alpha'] if config else 0.2
        if self.current_cluster_id != -1:  # ← Только если не fallback
            # ОБНОВЛЯЕМ ВЕСА В МОДЕЛИ
            self.ml_core.update_cluster_weights(
                self.current_cluster_id, 
                'yes',
                alpha=alpha  # Можно брать из настроек БД
            )
        
        # СОХРАНЯЕМ В БД
        try:
            sample_id = self.db.save_sample(
                image_data=self.X_test[self.current_idx].tolist(),  # Сохраняем изображение
                features=self.current_features.tolist() if self.current_features is not None else None,
                cluster_id=self.current_cluster_id,
                predicted_label=self.current_prediction,
                user_feedback='yes',
                verified_label=None,
                true_label=self.current_label    # Пока не верифицировано
            )
            print(f"✅ YES сохранен: sample_id={sample_id}, prediction={self.current_prediction}")
        except Exception as e:
            print(f"❌ Ошибка сохранения YES: {e}")
        
        self.status_label.config(text=f"✅ Подтверждено: {self.current_prediction}", fg="green")
        self.counter_label.config(text=f"Обработано: {self.counter} цифр")
        
        # Деактивируем кнопки до следующего предсказания
        self._disable_feedback_buttons()
        self.show_random_digit()
        # ⭐⭐ СОХРАНЯЕМ СТАТИСТИКУ ПОСЛЕ КАЖДОГО ОТВЕТА
        self.db.save_statistics_snapshot()
    
        self._disable_feedback_buttons()
        self.show_random_digit()

    
    def on_no(self):
        """Пользователь отвергает предсказание"""
        if not self.ml_core or self.current_prediction is None:
            return
            
        self.counter += 1
        
        # ОБНОВЛЯЕМ ВЕСА В МОДЕЛИ (только если не fallback)
        config = self.db.load_system_config()
        gamma = config['weights']['gamma'] if config else 0.5
        if self.current_cluster_id != -1:
            self.ml_core.update_cluster_weights(
                self.current_cluster_id, 
                'no',
                gamma=gamma  # Можно брать из настроек БД
            )
        
        # СОХРАНЯЕМ В БД для отложенной верификации
        try:
            sample_id = self.db.save_sample(
                image_data=self.X_test[self.current_idx].tolist(),
                features=self.current_features.tolist() if self.current_features is not None else None,
                cluster_id=self.current_cluster_id,
                predicted_label=self.current_prediction,
                user_feedback='no',
                verified_label=None,
                true_label=self.current_label  # ⭐⭐ СОХРАНЯЕМ ДЛЯ СТАТИСТИКИ, НО НЕ ПОКАЗЫВАЕМ
            )
            print(f"❌ NO сохранен: sample_id={sample_id}, prediction={self.current_prediction}")
        except Exception as e:
            print(f"❌ Ошибка сохранения NO: {e}")
        
        self.status_label.config(text=f"❌ Отвергнуто: {self.current_prediction}", fg="red")
        self.counter_label.config(text=f"Обработано: {self.counter} цифр")
        
        self._disable_feedback_buttons()
        self.show_random_digit()

        self.db.save_statistics_snapshot()
        self._disable_feedback_buttons()
        self.show_random_digit()
    
    def on_later(self):
        """Пользователь не уверен"""
        if not self.ml_core or self.current_prediction is None:
            return
            
        self.counter += 1
        
        # СОХРАНЯЕМ В БД для верификации позже
        try:
            sample_id = self.db.save_sample(
                image_data=self.X_test[self.current_idx].tolist(),
                features=self.current_features.tolist() if self.current_features is not None else None,
                cluster_id=self.current_cluster_id,
                predicted_label=self.current_prediction,
                user_feedback='unsure',
                verified_label=None,
                true_label=self.current_label  # ⭐⭐ СОХРАНЯЕМ - ПОКАЖЕМ ПРИ ВЕРИФИКАЦИИ
            )
            print(f"⏰ LATER сохранен: sample_id={sample_id}, prediction={self.current_prediction}")
        except Exception as e:
            print(f"❌ Ошибка сохранения LATER: {e}")
        
        self.status_label.config(text=f"⏰ Отложено: {self.current_prediction}", fg="orange")
        self.counter_label.config(text=f"Обработано: {self.counter} цифр")
        
        self._disable_feedback_buttons()
        self.show_random_digit()

        self.db.save_statistics_snapshot()
        self._disable_feedback_buttons()
        self.show_random_digit()
    
    def _disable_feedback_buttons(self):
        """Деактивирует кнопки обратной связи"""
        self.btn_yes.config(state="disabled")
        self.btn_no.config(state="disabled")
        self.btn_later.config(state="disabled")