import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageTk
import io
import pickle

class VerifyTab:
    def __init__(self, parent_frame, database, ml_core):
        self.frame = parent_frame
        self.db = database
        self.ml_core = ml_core
        self.current_sample = None
        self.pending_samples = []
        
        self.setup_ui()
        self.load_pending_samples()
        self.show_next_sample()
        
        # ⭐⭐ ДОБАВЛЯЕМ ОБРАБОТЧИК АКТИВАЦИИ ВКЛАДКИ ⭐⭐
        self._bind_tab_events()

    def _bind_tab_events(self):
        """Привязывает обработчики событий для автоматического обновления"""
        # Находим родительский notebook
        parent = self.frame.winfo_parent()
        if parent:
            notebook = self.frame.nametowidget(parent)
            if isinstance(notebook, ttk.Notebook):
                # Привязываем обработчик когда эта вкладка становится активной
                notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)
    
    def _on_tab_changed(self, event):
        """Обработчик смены вкладки"""
        try:
            notebook = event.widget
            current_tab = notebook.select()
            if current_tab == str(self.frame):
                print("🔁 Активна вкладка VerifyTab - обновляем данные...")
                self.refresh_verification_list()
        except Exception as e:
            print(f"⚠️ Ошибка обработки смены вкладки: {e}")

    def setup_ui(self):
        # Основной контейнер
        main_container = tk.Frame(self.frame)
        main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Заголовок
        title = tk.Label(main_container, text="Отложенная верификация чисел", 
                        font=("Arial", 16, "bold"), pady=10)
        title.pack()

        # Область для изображения с фиксированным размером
        image_container = tk.Frame(main_container, bg="white", relief="solid", bd=2)
        image_container.pack(pady=20)
        
        self.image_label = tk.Label(image_container, bg="white", width=300, height=300)
        self.image_label.pack(padx=10, pady=10)

        # Информация о предсказании системы
        self.prediction_label = tk.Label(main_container, text="", 
                                        font=("Arial", 12), pady=5)
        self.prediction_label.pack()

        # Инструкция
        instruction = tk.Label(main_container, text="Выберите правильную цифру:",
                              font=("Arial", 11), fg="gray")
        instruction.pack(pady=5)

        # Фрейм для кнопок цифр
        digits_container = tk.Frame(main_container)
        digits_container.pack(pady=15)

        # Создаем кнопки цифр 0-9 в две строки
        self.digit_buttons = []
        for i in range(10):
            btn = tk.Button(digits_container, text=str(i), width=6, height=2,
                          font=("Arial", 14, "bold"),
                          bg="#f0f0f0", activebackground="#e0e0e0",
                          command=lambda digit=i: self.on_digit_selected(digit))
            
            if i < 5:
                btn.grid(row=0, column=i, padx=3, pady=3)
            else:
                btn.grid(row=1, column=i-5, padx=3, pady=3)
                
            self.digit_buttons.append(btn)

        # Статус верификации
        self.status_label = tk.Label(main_container, text="", 
                                    font=("Arial", 11), pady=10)
        self.status_label.pack()

        # Счетчик и управление
        control_frame = tk.Frame(main_container)
        control_frame.pack(pady=10)

        self.counter_label = tk.Label(control_frame, text="", 
                                     font=("Arial", 10))
        self.counter_label.pack(side=tk.LEFT, padx=10)

        # Кнопка обновления
        self.refresh_btn = tk.Button(control_frame, text="🔄 Обновить", 
                                   command=self.refresh_verification_list,
                                   font=("Arial", 9))
        self.refresh_btn.pack(side=tk.LEFT, padx=5)

        # Кнопка отладки
        self.debug_btn = tk.Button(control_frame, text="🐛 Отладка", 
                                 command=self.debug_info,
                                 font=("Arial", 9), bg="#ffeb3b")
        self.debug_btn.pack(side=tk.LEFT, padx=5)
        
        # ⭐⭐ КНОПКА ПРИНУДИТЕЛЬНОГО ОБНОВЛЕНИЯ ⭐⭐
        self.force_refresh_btn = tk.Button(control_frame, text="💥 Принудительное обновление", 
                                         command=self.force_refresh,
                                         font=("Arial", 9), bg="#4CAF50", fg="white")
        self.force_refresh_btn.pack(side=tk.LEFT, padx=5)

    def force_refresh(self):
        """Принудительное обновление всего интерфейса"""
        print("💥 ПРИНУДИТЕЛЬНОЕ ОБНОВЛЕНИЕ...")
        
        # Перезагружаем данные
        self.load_pending_samples()
        
        # Принудительно перерисовываем интерфейс
        self.show_next_sample()
        
        # Обновляем все элементы
        self.frame.update_idletasks()

    def load_pending_samples(self):
        """Загружает примеры для отложенной верификации"""
        print("🔍 Загрузка примеров для верификации...")
        
        try:
            cursor = self.db.conn.cursor()
            
            
            
            # Загружаем непроверенные примеры
            cursor.execute('''
                SELECT sample_id, image_data, predicted_label, user_feedback, cluster_id, true_label
                FROM samples 
                WHERE verified_label IS NULL 
                AND user_feedback IN ('no', 'unsure')
                ORDER BY sample_id
                ''')
            
            results = cursor.fetchall()
            self.pending_samples = []
            
            print(f"✅ Найдено для верификации: {len(results)} примеров")
            
            for row in results:
                sample_id, image_blob, predicted_label, user_feedback, cluster_id, true_label = row
                
                if image_blob is None:
                    print(f"⚠️ Пропускаем sample_id {sample_id}: нет изображения")
                    continue
                    
                try:
                    image_data = pickle.loads(image_blob)
                    
                    # Конвертируем в numpy array если нужно
                    if isinstance(image_data, list):
                        image_array = np.array(image_data, dtype=np.float32)
                    else:
                        image_array = image_data
                    
                    # Нормализуем если нужно
                    if image_array.max() > 1.0:
                        image_array = image_array / 255.0

                    # ⭐⭐ ИСПРАВЛЕНИЕ: ПРЕОБРАЗУЕМ TRUE_LABEL В INT ⭐⭐
                    if isinstance(true_label, bytes):
                        true_label = int.from_bytes(true_label, byteorder='little')
                    elif true_label is not None:
                        true_label = int(true_label)
                    
                    self.pending_samples.append({
                        'sample_id': sample_id,
                        'image_data': image_array,
                        'predicted_label': predicted_label,
                        'user_feedback': user_feedback,
                        'cluster_id': cluster_id,
                        'true_label': true_label
                    })
                    
                except Exception as e:
                    print(f"❌ Ошибка загрузки sample_id {sample_id}: {e}")
                    continue
                    
        except Exception as e:
            print(f"❌ Ошибка загрузки из БД: {e}")
            self.pending_samples = []

    def array_to_image(self, digit_array):
        """Конвертируем numpy array в изображение для tkinter"""
        try:
            # Убедимся что это 2D array
            if len(digit_array.shape) == 1:
                side = int(np.sqrt(digit_array.shape[0]))
                digit_array = digit_array.reshape(side, side)
            
            # Денормализуем для отображения
            if digit_array.max() <= 1.0:
                display_array = (digit_array * 255).astype(np.uint8)
            else:
                display_array = digit_array.astype(np.uint8)
            
            # Создаем изображение
            plt.figure(figsize=(4, 4))
            plt.imshow(display_array, cmap='gray')
            plt.axis('off')
            plt.tight_layout()
            
            # Сохраняем в буфер
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight', 
                       pad_inches=0, dpi=70)
            buf.seek(0)
            plt.close()
            
            return Image.open(buf)
            
        except Exception as e:
            print(f"❌ Ошибка создания изображения: {e}")
            # Создаем заглушку
            return Image.new('RGB', (200, 200), color='lightgray')

    def show_next_sample(self):
        """Показывает следующий пример для верификации"""
        # Очищаем текущее состояние
        self.current_sample = None
        
        if not self.pending_samples:
            self.show_no_samples()
            return
        
        # Берем следующий пример
        self.current_sample = self.pending_samples.pop(0)
        
        print(f"🔍 Показываем sample_id {self.current_sample['sample_id']}")
        
        try:
            # Показываем изображение
            image = self.array_to_image(self.current_sample['image_data'])
            photo = ImageTk.PhotoImage(image)
            
            self.image_label.configure(image=photo)
            self.image_label.image = photo
            
            # ⭐⭐ РАЗНАЯ ИНФОРМАЦИЯ В ЗАВИСИМОСТИ ОТ ТИПА ФИДБЕКА ⭐⭐
            if self.current_sample['user_feedback'] == 'no':
                # Для "Нет" - не показываем правильный ответ
                feedback_icon = "❌"
                feedback_text = "Вы отвергли предсказание системы"
                prediction_text = f"{feedback_icon} Система предположила: {self.current_sample['predicted_label']}"
                instruction_text = "Выберите правильную цифру:"
            else:
                # Для "Не знаю" - ПОКАЗЫВАЕМ ПРАВИЛЬНЫЙ ОТВЕТ 
                feedback_icon = "⏰"
                feedback_text = "Вы не были уверены"
                prediction_text = f"{feedback_icon} Система предположила: {self.current_sample['predicted_label']} | Правильно: {self.current_sample['true_label']}"
                instruction_text = "Подтвердите правильную цифру:"
            self.prediction_label.config(
                text=prediction_text,
                fg="red" if self.current_sample['user_feedback'] == 'no' else "orange"
            )
            
            # Обновляем статус
            self.status_label.config(text="Выберите правильную цифру", fg="black")

            # Дополнительная информация о типе фидбека
            info_text = tk.Label(self.frame, text=feedback_text, font=("Arial", 10), fg="gray")
            info_text.pack(pady=2)
            # Сохраняем ссылку чтобы удалить при следующем обновлении
            if hasattr(self, '_info_label'):
                self._info_label.destroy()
            self._info_label = info_text

            
            # Активируем кнопки
            for btn in self.digit_buttons:
                btn.config(state="normal", bg="#f0f0f0")
            
            # Обновляем счетчик
            remaining = len(self.pending_samples)
            self.counter_label.config(text=f"Осталось: {remaining} чисел")
            
        except Exception as e:
            print(f"❌ Ошибка отображения: {e}")
            self.status_label.config(text="❌ Ошибка загрузки изображения", fg="red")
            self.frame.after(1000, self.show_next_sample)

    def show_no_samples(self):
        """Показывает сообщение когда нет примеров"""
        self.image_label.configure(image='')
        self.image_label.config(text="📭 Нет изображения", bg="lightgray", fg="black")
        self.prediction_label.config(text="")
        self.status_label.config(text="🎉 Нет чисел для верификации!", fg="green")
        self.counter_label.config(text="Все числа проверены")
        
        # Деактивируем кнопки но оставляем видимыми
        for btn in self.digit_buttons:
            btn.config(state="disabled", bg="#d0d0d0")

    def on_digit_selected(self, true_digit):
        """Обработчик выбора цифры пользователем"""
        if not self.current_sample:
            return
        
        sample_id = self.current_sample['sample_id']
        predicted_digit = self.current_sample['predicted_label']
        cluster_id = self.current_sample['cluster_id']
        
        print(f"🎯 Верификация: sample_id {sample_id} -> цифра {true_digit} (было: {predicted_digit})")
        
        try:
            # ⭐⭐ ОБНОВЛЯЕМ ВЕСА КЛАСТЕРА ⭐⭐
            if self.ml_core and self.ml_core.is_trained and cluster_id != -1:
                config = self.db.load_system_config()
                if config and 'weights' in config:
                    alpha = config['weights'].get('alpha', 0.2)
                    beta = config['weights'].get('beta', 0.5)
                    gamma = config['weights'].get('gamma', 0.5)
                    min_weight = config['weights'].get('min_weight', 0.05) 
                else:
                    alpha, beta, gamma, min_weight = 0.2, 0.5, 0.5, 0.05
               
                
                self.ml_core.update_cluster_weights(
                    cluster_id, 
                    'verified',
                    true_label=true_digit,
                    alpha=alpha,
                    beta=beta,
                    gamma=gamma,
                    min_weight=min_weight
                )
                print(f"✅ Обновлены веса кластера {cluster_id}")
            elif cluster_id == -1:
                print(f"⚠️  Пропуск обновления весов: cluster_id = -1")
            
            # ⭐⭐ ОБНОВЛЯЕМ БАЗУ ДАННЫХ ⭐⭐
            cursor = self.db.conn.cursor()
            cursor.execute('''
                UPDATE samples 
                SET verified_label = ?, user_feedback = 'verified'
                WHERE sample_id = ?
            ''', (true_digit, sample_id))
            self.db.conn.commit()
            
            print(f"✅ БД обновлена: sample_id {sample_id}")
            
            # Показываем успех
            self.status_label.config(
                text=f"✅ Зафиксировано: цифра {true_digit} (было: {predicted_digit})", 
                fg="green"
            )
            
            # Деактивируем кнопки на время анимации
            for btn in self.digit_buttons:
                btn.config(state="disabled", bg="#d0d0d0")
            
            # ⭐⭐ СОХРАНЯЕМ СТАТИСТИКУ ПОСЛЕ ВЕРИФИКАЦИИ
            self.db.save_statistics_snapshot()
            
            # Переходим к следующему примеру через 1.5 секунды
            self.frame.after(1500, self.show_next_sample)
            
        except Exception as e:
            print(f"❌ Ошибка верификации: {e}")
            self.status_label.config(text=f"❌ Ошибка: {str(e)}", fg="red")

    def refresh_verification_list(self):
        """Обновляет список примеров"""
        print("🔄 Обновление списка верификации...")
        self.load_pending_samples()
        self.show_next_sample()

    def debug_info(self):
        """Показывает отладочную информацию"""
        print("\n=== ОТЛАДОЧНАЯ ИНФОРМАЦИЯ ===")
        print(f"Модель готова: {self.ml_core and self.ml_core.is_trained}")
        print(f"Кластеров: {len(self.ml_core.clusters) if self.ml_core else 0}")
        print(f"Примеров для верификации: {len(self.pending_samples)}")
        print(f"Текущий sample: {self.current_sample['sample_id'] if self.current_sample else 'None'}")
        print("============================\n")
        
        # Показываем всплывающее сообщение
        self.status_label.config(text="🔍 Отладочная информация в консоли", fg="blue")