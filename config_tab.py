import tkinter as tk
from tkinter import ttk
import numpy as np

class ConfigTab:
    def __init__(self, parent_frame, database):
        self.frame = parent_frame
        self.db = database
        self.setup_ui()
    
    def setup_ui(self):
        # Заголовок
        title = tk.Label(self.frame, text="Настройки интеллектуальной системы", 
                        font=("Arial", 14, "bold"), pady=20)
        title.pack()
        
        # Создаем фрейм для трех столбцов
        columns_frame = tk.Frame(self.frame)
        columns_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Столбец 1: Экстрактор признаков
        self.setup_feature_extractor_column(columns_frame)
        
        # Столбец 2: Кластеризация
        self.setup_clustering_column(columns_frame)
        
        # Столбец 3: Динамические веса
        self.setup_dynamic_weights_column(columns_frame)
        
        # Разделительная линия
        separator = ttk.Separator(self.frame, orient='horizontal')
        separator.pack(fill='x', padx=20, pady=20)
        
        # Панель кнопок управления
        self.setup_control_buttons()
        
        # Статус
        self.status_label = tk.Label(self.frame,
                                   text="Система не инициализирована", 
                                   font=("Arial", 9),
                                   fg="red")
        self.status_label.pack(pady=10)
    
    def setup_feature_extractor_column(self, parent):
        # Фрейм для столбца
        col_frame = tk.Frame(parent)
        col_frame.pack(side='left', fill='both', expand=True, padx=10)
        
        # Заголовок столбца
        title = tk.Label(col_frame, text="Экстрактор признаков", 
                        font=("Arial", 11, "bold"), pady=10)
        title.pack()
        
        # Архитектура экстрактора
        arch_label = tk.Label(col_frame, text="Архитектура:", anchor='w')
        arch_label.pack(fill='x', pady=(10, 2))
        
        self.arch_var = tk.StringVar(value="Маленький перцептрон")
        arch_combo = ttk.Combobox(col_frame, textvariable=self.arch_var,
                                 values=["Простая CNN", "Маленький перцептрон", "Предобученная модель"],
                                 state="readonly")
        arch_combo.pack(fill='x', pady=(0, 10))
        
        # Размерность вектора признаков
        dim_label = tk.Label(col_frame, text="Размерность вектора:", anchor='w')
        dim_label.pack(fill='x', pady=2)
        
        dim_frame = tk.Frame(col_frame)
        dim_frame.pack(fill='x', pady=(0, 10))
        
        self.dim_var = tk.IntVar(value=32)
        dim_scale = tk.Scale(dim_frame, from_=32, to=512, orient='horizontal',
                           variable=self.dim_var, showvalue=True, length=150)
        dim_scale.pack(side='left', fill='x', expand=True)
        
        dim_value = tk.Label(dim_frame, textvariable=self.dim_var, width=3)
        dim_value.pack(side='right', padx=(5, 0))
        
        # === НАСТРОЙКИ ДАННЫХ ===
        data_label = tk.Label(col_frame, text="Обучающая выборка:", 
                             font=("Arial", 10, "bold"), pady=5)
        data_label.pack(fill='x')
        
        # Количество реальных данных MNIST
        real_label = tk.Label(col_frame, text="Реальные данные (MNIST):", anchor='w')
        real_label.pack(fill='x', pady=(5, 2))
        
        real_frame = tk.Frame(col_frame)
        real_frame.pack(fill='x', pady=(0, 5))
        
        self.real_data_var = tk.IntVar(value=1000)
        real_scale = tk.Scale(real_frame, from_=100, to=10000, orient='horizontal',
                             variable=self.real_data_var, showvalue=True, length=150,
                             resolution=100)
        real_scale.pack(side='left', fill='x', expand=True)
        
        real_value = tk.Label(real_frame, textvariable=self.real_data_var, width=5)
        real_value.pack(side='right', padx=(5, 0))
        
        # Количество синтетических зашумленных данных
        synth_label = tk.Label(col_frame, text="Синтетические данные:", anchor='w')
        synth_label.pack(fill='x', pady=(5, 2))
        
        synth_frame = tk.Frame(col_frame)
        synth_frame.pack(fill='x', pady=(0, 10))
        
        self.synth_data_var = tk.IntVar(value=500)
        synth_scale = tk.Scale(synth_frame, from_=0, to=5000, orient='horizontal',
                              variable=self.synth_data_var, showvalue=True, length=150,
                              resolution=100)
        synth_scale.pack(side='left', fill='x', expand=True)
        
        synth_value = tk.Label(synth_frame, textvariable=self.synth_data_var, width=5)
        synth_value.pack(side='right', padx=(5, 0))
        
        # Информация об общем размере выборки
        self.data_info = tk.Label(col_frame, text="", font=("Arial", 8),
                                justify='left', fg="gray")
        self.data_info.pack(fill='x', pady=(0, 10))
        
        # Обновляем информацию при изменении слайдеров
        def update_data_info(*args):
            real_count = self.real_data_var.get()
            synth_count = self.synth_data_var.get()
            total = real_count + synth_count
            synth_percent = (synth_count / total) * 100 if total > 0 else 0
            
            info_text = f"Всего данных: {total:,}\n"
            info_text += f"Синтетика: {synth_percent:.1f}%"
            
            # Цветовая индикация
            if synth_percent > 50:
                self.data_info.config(fg="red")
            elif synth_percent > 20:
                self.data_info.config(fg="orange")  
            else:
                self.data_info.config(fg="green")
                
            self.data_info.config(text=info_text)
        
        self.real_data_var.trace('w', update_data_info)
        self.synth_data_var.trace('w', update_data_info)
        update_data_info()  # Initial call
        
        # Уровень шума в синтетических данных
        noise_label = tk.Label(col_frame, text="Уровень шума в синтетике:", anchor='w')
        noise_label.pack(fill='x', pady=(5, 2))
        
        self.noise_var = tk.DoubleVar(value=0.5)
        noise_scale = tk.Scale(col_frame, from_=0.1, to=0.9, orient='horizontal',
                              variable=self.noise_var, resolution=0.1, 
                              showvalue=True, length=150)
        noise_scale.pack(fill='x', pady=(0, 10))
        
        # Кнопка обучения экстрактора
        self.train_extractor_btn = tk.Button(col_frame, 
                                           text="Обучить Экстрактор",
                                           command=self.train_extractor,
                                           state="normal")
        self.train_extractor_btn.pack(fill='x', pady=5)
    
    def setup_clustering_column(self, parent):
        # Фрейм для столбца
        col_frame = tk.Frame(parent)
        col_frame.pack(side='left', fill='both', expand=True, padx=10)
        
        # Заголовок столбца
        title = tk.Label(col_frame, text="Кластеризация", 
                        font=("Arial", 11, "bold"), pady=10)
        title.pack()
        
        # Алгоритм кластеризации
        algo_label = tk.Label(col_frame, text="Алгоритм:", anchor='w')
        algo_label.pack(fill='x', pady=(10, 2))
        
        self.algo_var = tk.StringVar(value="K-Means")
        algo_combo = ttk.Combobox(col_frame, textvariable=self.algo_var,
                                 values=["K-Means", "DBSCAN", "Mean Shift"],
                                 state="readonly")
        algo_combo.pack(fill='x', pady=(0, 10))
        algo_combo.bind('<<ComboboxSelected>>', self.on_algorithm_change)
        
        # Параметры алгоритма (динамически меняются)
        self.param_frame = tk.Frame(col_frame)
        self.param_frame.pack(fill='x', pady=(0, 10))
        self.setup_algorithm_params()  # Начальная настройка для K-Means
        
        # Метрика расстояния
        metric_label = tk.Label(col_frame, text="Метрика расстояния:", anchor='w')
        metric_label.pack(fill='x', pady=2)
        
        self.metric_var = tk.StringVar(value="Косинусное")
        metric_combo = ttk.Combobox(col_frame, textvariable=self.metric_var,
                                   values=["Евклидово", "Косинусное"],
                                   state="readonly")
        metric_combo.pack(fill='x', pady=(0, 10))
    
    def setup_algorithm_params(self):
        # Очищаем предыдущие параметры
        for widget in self.param_frame.winfo_children():
            widget.destroy()
        
        algorithm = self.algo_var.get()
        
        if algorithm == "K-Means":
            # Число кластеров для K-Means
            k_label = tk.Label(self.param_frame, text="Число кластеров (K):", anchor='w')
            k_label.pack(fill='x', pady=2)
            
            self.k_var = tk.IntVar(value=15)
            k_scale = tk.Scale(self.param_frame, from_=2, to=100, orient='horizontal',
                             variable=self.k_var, showvalue=True, length=150)
            k_scale.pack(fill='x', pady=(0, 5))
            
        elif algorithm == "DBSCAN":
            # Макс. расстояние для DBSCAN
            eps_label = tk.Label(self.param_frame, text="Макс. расстояние (eps):", anchor='w')
            eps_label.pack(fill='x', pady=2)
            
            self.eps_var = tk.DoubleVar(value=0.8)
            eps_entry = tk.Entry(self.param_frame, textvariable=self.eps_var, width=10)
            eps_entry.pack(fill='x', pady=(0, 5))
            
            # Мин. samples для DBSCAN
            min_samples_label = tk.Label(self.param_frame, text="Мин. samples:", anchor='w')
            min_samples_label.pack(fill='x', pady=2)
            
            self.min_samples_var = tk.IntVar(value=5)
            min_samples_scale = tk.Scale(self.param_frame, from_=2, to=20, orient='horizontal',
                                       variable=self.min_samples_var, showvalue=True, length=150)
            min_samples_scale.pack(fill='x', pady=(0, 5))
    
    def setup_dynamic_weights_column(self, parent):
        # Фрейм для столбца
        col_frame = tk.Frame(parent)
        col_frame.pack(side='left', fill='both', expand=True, padx=10)
        
        # Заголовок столбца
        title = tk.Label(col_frame, text="Динамические веса", 
                        font=("Arial", 11, "bold"), pady=10)
        title.pack()
        
        # Alpha (μ-фидбек)
        self.create_parameter_slider(col_frame, "Alpha (μ-фидбек):", 
                                   self.create_double_var(0.2), 0.01, 0.5)
        
        # Beta (Верификация)
        self.create_parameter_slider(col_frame, "Beta (Верификация):", 
                                   self.create_double_var(0.5), 0.05, 1.0)
        
        # Gamma (Штраф 'Нет')
        self.create_parameter_slider(col_frame, "Gamma (Штраф 'Нет'):", 
                                   self.create_double_var(0.5), 0.1, 0.95)
        
        # Мин. вес
        self.create_parameter_slider(col_frame, "Мин. вес:", 
                                   self.create_double_var(0.05), 0.001, 0.1)
        
        # Порог нового кластера
        self.create_parameter_slider(col_frame, "Порог нового кластера:", 
                                   self.create_double_var(1.2), 0.5, 3.0)
    
    def create_double_var(self, value):
        var = tk.DoubleVar(value=value)
        # Сохраняем ссылку на переменную
        if not hasattr(self, 'weight_vars'):
            self.weight_vars = []
        self.weight_vars.append(var)
        return var
    
    def create_parameter_slider(self, parent, label, var, from_, to):
        label_widget = tk.Label(parent, text=label, anchor='w')
        label_widget.pack(fill='x', pady=(10, 2))
        
        slider_frame = tk.Frame(parent)
        slider_frame.pack(fill='x', pady=(0, 5))
        
        slider = tk.Scale(slider_frame, from_=from_, to=to, orient='horizontal',
                        variable=var, resolution=0.01, showvalue=True, length=150)
        slider.pack(side='left', fill='x', expand=True)
        
        value_label = tk.Label(slider_frame, textvariable=var, width=4)
        value_label.pack(side='right', padx=(5, 0))
    
    def setup_control_buttons(self):
        button_frame = tk.Frame(self.frame)
        button_frame.pack(fill='x', padx=20, pady=10)
        
        # Кнопка инициализации
        self.init_btn = tk.Button(button_frame, 
                                text="Обучить и Инициализировать",
                                command=self.initialize_system,
                                bg="#4CAF50", fg="white", font=("Arial", 10, "bold"))
        self.init_btn.pack(side='left', padx=(0, 10))
        
        # Кнопка перезагрузки
        self.reload_btn = tk.Button(button_frame,
                                  text="Перезагрузить модель из БД",
                                  command=self.reload_from_db,
                                  state="disabled")
        self.reload_btn.pack(side='left', padx=(0, 10))
        
        # Опасная кнопка сброса
        self.reset_btn = tk.Button(button_frame,
                                 text="СБРОСИТЬ ВСЁ ОБУЧЕНИЕ",
                                 command=self.reset_system,
                                 bg="#f44336", fg="white", font=("Arial", 10, "bold"))
        self.reset_btn.pack(side='left')
    
    def on_algorithm_change(self, event):
        self.setup_algorithm_params()
    
    def prepare_training_data(self, feature_config):
        """Подготовить обучающие данные согласно настройкам"""
        try:
            from tensorflow.keras.datasets import mnist
        except ImportError:
            print("❌ TensorFlow не установлен. Используем заглушку.")
            return self.prepare_dummy_data(feature_config)
        
        # Загружаем MNIST
        (x_train, y_train), (x_test, y_test) = mnist.load_data()
        
        # Нормализуем пиксели
        x_train = x_train.astype('float32') / 255.0
        x_test = x_test.astype('float32') / 255.0
        
        # Объединяем для гибкости
        x_all = np.concatenate([x_train, x_test])
        y_all = np.concatenate([y_train, y_test])
        
        # Выбираем случайные реальные данные
        real_count = feature_config['real_data_count']
        if real_count > len(x_all):
            real_count = len(x_all)
            print(f"⚠️  Запрошено больше реальных данных чем есть. Используем {real_count}")
            
        indices = np.random.choice(len(x_all), real_count, replace=False)
        x_real = x_all[indices]
        y_real = y_all[indices]
        
        # Генерируем синтетические данные
        synth_count = feature_config['synthetic_data_count']
        if synth_count > 0:
            x_synth, y_synth = self.generate_synthetic_data(x_real, y_real, 
                                                           synth_count, 
                                                           feature_config['noise_level'])
        else:
            x_synth, y_synth = np.array([]), np.array([])
        
        # Объединяем
        if synth_count > 0:
            x_combined = np.concatenate([x_real, x_synth])
            y_combined = np.concatenate([y_real, y_synth])
        else:
            x_combined = x_real
            y_combined = y_real
        
        print(f"✅ Данные подготовлены: {len(x_real)} реальных + {len(x_synth)} синтетических")
        
        return {
            'x_train': x_combined,
            'y_train': y_combined,
            'x_real': x_real,
            'y_real': y_real,
            'x_synthetic': x_synth if synth_count > 0 else None,
            'y_synthetic': y_synth if synth_count > 0 else None,
            'real_count': len(x_real),
            'synthetic_count': len(x_synth),
            'noise_level': feature_config['noise_level']
        }
    
    def generate_synthetic_data(self, x_real, y_real, synth_count, noise_level):
        """Генерируем зашумленные синтетические данные"""
        if len(x_real) == 0:
            return np.array([]), np.array([])
            
        x_synth = []
        y_synth = []
        
        for i in range(synth_count):
            # Выбираем случайный реальный пример как основу
            base_idx = np.random.randint(0, len(x_real))
            image = x_real[base_idx].copy()
            true_label = y_real[base_idx]
            
            # Применяем различные искажения в зависимости от уровня шума
            if noise_level > 0.3:
                # Поворот
                if np.random.random() < noise_level:
                    k = np.random.randint(1, 4)  # 1, 2 или 3 поворота на 90°
                    image = np.rot90(image, k)
                
                # Отражение
                if np.random.random() < noise_level * 0.7:
                    image = np.flipud(image) if np.random.random() < 0.5 else np.fliplr(image)
            
            if noise_level > 0.5:
                # Добавляем гауссов шум
                noise = np.random.normal(0, noise_level * 0.3, image.shape)
                image = np.clip(image + noise, 0, 1)
                
                # Размытие (простое)
                if np.random.random() < noise_level * 0.5:
                    from scipy.ndimage import gaussian_filter
                    image = gaussian_filter(image, sigma=0.5)
            
            # Иногда меняем метку (ошибочная разметка)
            final_label = true_label
            if np.random.random() < noise_level * 0.3:  # До 30% ошибок при высоком шуме
                wrong_label = np.random.randint(0, 10)
                while wrong_label == true_label:
                    wrong_label = np.random.randint(0, 10)
                final_label = wrong_label
            
            x_synth.append(image)
            y_synth.append(final_label)
        
        return np.array(x_synth), np.array(y_synth)
    
    def prepare_dummy_data(self, feature_config):
        """Заглушка если нет TensorFlow"""
        print("🔶 Используем заглушечные данные (без TensorFlow)")
        return {
            'x_train': np.random.random((100, 28, 28)),
            'y_train': np.random.randint(0, 10, 100),
            'real_count': feature_config['real_data_count'],
            'synthetic_count': feature_config['synthetic_data_count'],
            'noise_level': feature_config['noise_level']
        }
    
    def train_feature_extractor_and_cluster(self, training_data, feature_config, clustering_config):
        """ЗАГЛУШКА: Здесь будет реальное обучение экстрактора и кластеризация"""
        print("🔶 Заглушка: обучение экстрактора и кластеризация")
        
        # Временные данные для демонстрации
        clusters_data = []
        for i in range(clustering_config.get('k_value', 5)):  # Используем K из настроек
            cluster = {
                'centroid': np.random.random(feature_config['embedding_size']),
                'params': clustering_config,
                'weights': {digit: np.random.random() for digit in range(10)}
            }
            # Нормализуем веса чтобы сумма была = 1
            total = sum(cluster['weights'].values())
            for digit in cluster['weights']:
                cluster['weights'][digit] /= total
            clusters_data.append(cluster)
        
        print(f"✅ Создано {len(clusters_data)} кластеров")
        return clusters_data
    
    def initialize_system(self):
        """Инициализировать всю систему и сохранить настройки в БД"""
        try:
            # 1. Собираем настройки из интерфейса
            feature_config = {
                'architecture': self.arch_var.get(),
                'embedding_size': self.dim_var.get(),
                'real_data_count': self.real_data_var.get(),
                'synthetic_data_count': self.synth_data_var.get(),
                'noise_level': self.noise_var.get()
            }
            
            clustering_config = {
                'algorithm': self.algo_var.get(),
                'k_value': getattr(self, 'k_var', 15).get() if self.algo_var.get() == 'K-Means' else None,
                'eps_value': getattr(self, 'eps_var', 0.8).get() if self.algo_var.get() == 'DBSCAN' else None,
                'min_samples': getattr(self, 'min_samples_var', 5).get() if self.algo_var.get() == 'DBSCAN' else None,
                'metric': self.metric_var.get()
            }
            
            weights_config = {
                'alpha': getattr(self, 'param_0', tk.DoubleVar(value=0.2)).get(),
                'beta': getattr(self, 'param_1', tk.DoubleVar(value=0.5)).get(),
                'gamma': getattr(self, 'param_2', tk.DoubleVar(value=0.5)).get(),
                'min_weight': getattr(self, 'param_3', tk.DoubleVar(value=0.05)).get(),
                'new_cluster_threshold': getattr(self, 'param_4', tk.DoubleVar(value=1.2)).get()
            }
            
            # 2. Сохраняем настройки в БД
            self.db.save_system_config(feature_config, clustering_config, weights_config)
            
            # 3. Генерируем данные согласно настройкам
            training_data = self.prepare_training_data(feature_config)
            
            # 4. Обучаем экстрактор и проводим кластеризацию (пока заглушка)
            clusters_data = self.train_feature_extractor_and_cluster(training_data, feature_config, clustering_config)
            
            # 5. Сохраняем кластеры в БД
            self.db.save_clusters(clusters_data)
            
            self.status_label.config(text="✅ Система инициализирована и готова к работе", fg="green")
            self.reload_btn.config(state="normal")
            
            print("=" * 50)
            print("СИСТЕМА УСПЕШНО ИНИЦИАЛИЗИРОВАНА")
            print(f"Данные: {training_data['real_count']} реальных + {training_data['synthetic_count']} синтетических")
            print(f"Шум: {feature_config['noise_level']}")
            print(f"Кластеров создано: {len(clusters_data)}")
            print("=" * 50)
            
        except Exception as e:
            self.status_label.config(text=f"❌ Ошибка инициализации: {str(e)}", fg="red")
            import traceback
            traceback.print_exc()
    
    def train_extractor(self):
        """Заглушка: Обучение экстрактора признаков"""
        print("🔶 Заглушка: Обучение экстрактора признаков")
        self.status_label.config(text="Экстрактор обучен (заглушка)", fg="orange")
    
    def reload_from_db(self):
        """Перезагрузить модель из БД"""
        try:
            config = self.db.load_system_config()
            if config:
                # Восстанавливаем настройки в интерфейсе
                self.restore_ui_from_config(config)
                self.status_label.config(text="✅ Модель перезагружена из БД", fg="blue")
                print("Настройки загружены из БД")
            else:
                self.status_label.config(text="❌ В БД нет сохраненных настроек", fg="orange")
        except Exception as e:
            self.status_label.config(text=f"❌ Ошибка загрузки: {str(e)}", fg="red")
    
    def restore_ui_from_config(self, config):
        """Восстановить настройки интерфейса из конфигурации"""
        # Заглушка - в реальности нужно восстановить все переменные
        print("🔶 Заглушка: Восстановление настроек из БД")
    
    def reset_system(self):
        """Полный сброс системы"""
        import tkinter.messagebox as messagebox
        if messagebox.askyesno("Подтверждение", 
                              "Вы уверены? Это удалит ВСЕ настройки, кластеры и историю обучения."):
            try:
                self.db.reset_system_config()
                self.status_label.config(text="✅ Система сброшена. Требуется инициализация.", fg="red")
                self.reload_btn.config(state="disabled")
                print("Система полностью сброшена")
            except Exception as e:
                self.status_label.config(text=f"❌ Ошибка сброса: {str(e)}", fg="red")