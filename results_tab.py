import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from datetime import datetime, timedelta

class ResultsTab:
    def __init__(self, parent_frame, database):
        self.frame = parent_frame
        self.db = database
        self.setup_ui()
        self.refresh_data()

        self.auto_refresh()

    def auto_refresh(self):
        """Автоматическое обновление данных"""
        try:
            self.refresh_data()
            # Если успешно, продолжаем автообновление
            self.frame.after(5000, self.auto_refresh)
        except Exception as e:
            print(f"⚠️ Остановлено автообновление из-за ошибки: {e}")
            # Не планируем следующее обновление при ошибке

    def setup_ui(self):
        # Основной контейнер с прокруткой
        main_container = tk.Frame(self.frame)
        main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Заголовок
        title = tk.Label(main_container, text="Аналитика и результаты системы", 
                        font=("Arial", 16, "bold"), pady=10)
        title.pack()

        # Кнопка обновления
        refresh_btn = tk.Button(main_container, text="🔄 Обновить данные", 
                               command=self.refresh_data,
                               font=("Arial", 10))
        refresh_btn.pack(pady=5)

        # Фрейм для основных метрик
        self.setup_metrics_section(main_container)
        
        # Фрейм для графиков
        self.setup_charts_section(main_container)
        
        # Фрейм для детальной статистики
        self.setup_detailed_stats_section(main_container)

    def setup_metrics_section(self, parent):
        """Секция с основными метриками"""
        metrics_frame = tk.LabelFrame(parent, text="Основные метрики системы", 
                                    font=("Arial", 12, "bold"), pady=10, padx=10)
        metrics_frame.pack(fill='x', pady=10)
        
        # Сетка для метрик
        metrics_grid = tk.Frame(metrics_frame)
        metrics_grid.pack(fill='x')
        
        # Метрика 1: Общая точность
        self.accuracy_label = self.create_metric_card(metrics_grid, "Общая точность", "0%", 0)
        
        # Метрика 2: Обработано цифр
        self.processed_label = self.create_metric_card(metrics_grid, "Обработано цифр", "0", 1)
        
        # Метрика 3: Активных кластеров
        self.clusters_label = self.create_metric_card(metrics_grid, "Активных кластеров", "0", 2)
        
        # Метрика 4: Эффективность фидбека
        self.feedback_label = self.create_metric_card(metrics_grid, "Эффективность фидбека", "0%", 3)

    def create_metric_card(self, parent, title, value, column):
        """Создает карточку с метрикой"""
        card = tk.Frame(parent, relief='solid', bd=1, padx=10, pady=10)
        card.grid(row=0, column=column, padx=5, sticky='ew')
        
        title_label = tk.Label(card, text=title, font=("Arial", 9), fg="gray")
        title_label.pack()
        
        value_label = tk.Label(card, text=value, font=("Arial", 14, "bold"))
        value_label.pack()
        
        return value_label

    def setup_charts_section(self, parent):
        """Секция с графиками"""
        charts_frame = tk.LabelFrame(parent, text="Визуализация данных", 
                                   font=("Arial", 12, "bold"), pady=10, padx=10)
        charts_frame.pack(fill='x', pady=10)
        
        # Фрейм для двух графиков
        charts_container = tk.Frame(charts_frame)
        charts_container.pack(fill='x')
        
        # График 1: Распределение ответов
        self.setup_feedback_chart(charts_container)
        
        # График 2: Точность по цифрам
        self.setup_accuracy_chart(charts_container)

    def setup_feedback_chart(self, parent):
        """График распределения фидбеков"""
        chart_frame = tk.Frame(parent)
        chart_frame.pack(side='left', padx=5, fill='x', expand=True)
        
        chart_title = tk.Label(chart_frame, text="Распределение ответов", 
                              font=("Arial", 10, "bold"))
        chart_title.pack()
        
        self.feedback_fig, self.feedback_ax = plt.subplots(figsize=(5, 3))
        self.feedback_canvas = FigureCanvasTkAgg(self.feedback_fig, chart_frame)
        self.feedback_canvas.get_tk_widget().pack(fill='x')

    def setup_accuracy_chart(self, parent):
        """График точности по цифрам"""
        chart_frame = tk.Frame(parent)
        chart_frame.pack(side='left', padx=5, fill='x', expand=True)
        
        chart_title = tk.Label(chart_frame, text="Точность по цифрам", 
                              font=("Arial", 10, "bold"))
        chart_title.pack()
        
        self.accuracy_fig, self.accuracy_ax = plt.subplots(figsize=(5, 3))
        self.accuracy_canvas = FigureCanvasTkAgg(self.accuracy_fig, chart_frame)
        self.accuracy_canvas.get_tk_widget().pack(fill='x')

    def setup_detailed_stats_section(self, parent):
        """Секция с детальной статистикой"""
        stats_frame = tk.LabelFrame(parent, text="Детальная статистика", 
                                  font=("Arial", 12, "bold"), pady=10, padx=10)
        stats_frame.pack(fill='x', pady=10)
        
        # Таблица со статистикой
        columns = ('metric', 'value')
        self.stats_tree = ttk.Treeview(stats_frame, columns=columns, show='headings', height=8)
        self.stats_tree.heading('metric', text='Метрика')
        self.stats_tree.heading('value', text='Значение')
        self.stats_tree.column('metric', width=250)
        self.stats_tree.column('value', width=150)
        self.stats_tree.pack(fill='x')

    def refresh_data(self):
        """Обновляет все данные на вкладке"""
        try:
            print("🔍 DEBUG: Начинаем обновление результатов...")
            stats = self.calculate_statistics()
            print(f"🔍 DEBUG: Статистика получена: {stats.keys()}")
            self.update_metrics(stats)
            self.update_charts(stats)
            self.update_detailed_stats(stats)
            print("✅ Результаты успешно обновлены")
            
        except Exception as e:
            print(f"❌ Ошибка обновления результатов: {e}")
            import traceback
            traceback.print_exc()  # ⭐⭐ ДОБАВИМ ПОДРОБНЫЙ ТРЕЙСБЭК

    def calculate_statistics(self):
        """Вычисляет всю статистику системы"""
        try:
            cursor = self.db.conn.cursor()
        
            # Получаем последнюю статистику из таблицы statistics
            latest_stats = self.db.get_latest_statistics()
        
            if latest_stats:
                print(f"🔍 DEBUG: latest_stats = {latest_stats}")
                # ⭐⭐ ПРЕОБРАЗУЕМ БАЙТЫ В ЧИСЛА ЕСЛИ НУЖНО
                def safe_convert(value):
                    if isinstance(value, bytes):
                        return int.from_bytes(value, byteorder='little')
                    return value
            
                stats = {
                    'total_samples': safe_convert(latest_stats[2]),
                    'correct_predictions': safe_convert(latest_stats[3]),
                    'overall_accuracy': safe_convert(latest_stats[4]),
                    'total_clusters': safe_convert(latest_stats[5]),
                    'feedback_stats': {
                        'yes': safe_convert(latest_stats[6]),
                        'no': safe_convert(latest_stats[7]),
                        'unsure': safe_convert(latest_stats[8]),
                        'verified': safe_convert(latest_stats[9])
                    }
                }
            else:
                print("🔍 DEBUG: Нет saved statistics, вычисляем вручную")
                # Fallback: вычисляем вручную
                cursor.execute("SELECT COUNT(*) FROM samples")
                total_samples = cursor.fetchone()[0]
            
                cursor.execute("SELECT COUNT(*) FROM samples WHERE user_feedback = 'yes'")
                correct_predictions = cursor.fetchone()[0]
            
                cursor.execute("SELECT COUNT(*) FROM clusters")
                total_clusters = cursor.fetchone()[0]
            
                cursor.execute('SELECT user_feedback, COUNT(*) FROM samples GROUP BY user_feedback')
                feedback_results = cursor.fetchall()
                feedback_stats = {}
                for feedback, count in feedback_results:
                    # ⭐⭐ ПРЕОБРАЗУЕМ БАЙТЫ ЕСЛИ НУЖНО
                    if isinstance(feedback, bytes):
                        feedback = feedback.decode('utf-8')
                    if isinstance(count, bytes):
                        count = int.from_bytes(count, byteorder='little')
                    feedback_stats[feedback] = count
            
                stats = {
                    'total_samples': total_samples,
                    'correct_predictions': correct_predictions,
                    'total_clusters': total_clusters,
                    'feedback_stats': feedback_stats,
                    'overall_accuracy': correct_predictions / total_samples if total_samples > 0 else 0
                }
        
            # Дополнительно: точность по цифрам
            cursor.execute('''
                SELECT predicted_label, true_label, verified_label 
                FROM samples 
                WHERE verified_label IS NOT NULL AND true_label IS NOT NULL
            ''')
            accuracy_data = cursor.fetchall()
        
            digit_accuracy = {i: {'correct': 0, 'total': 0} for i in range(10)}
            for row in accuracy_data:
                pred, true, verified = row
            
                # ⭐⭐ ПРЕОБРАЗУЕМ БАЙТЫ ЕСЛИ НУЖНО
                if isinstance(true, bytes):
                    true = int.from_bytes(true, byteorder='little')
                if isinstance(verified, bytes):
                    verified = int.from_bytes(verified, byteorder='little')
            
                digit_accuracy[true]['total'] += 1
                if verified == true:
                    digit_accuracy[true]['correct'] += 1
        
            stats['digit_accuracy'] = digit_accuracy
            return stats
        
        except Exception as e:
            print(f"❌ Ошибка вычисления статистики: {e}")
            import traceback
            traceback.print_exc()
            return self.get_fallback_stats()

    def update_metrics(self, stats):
        """Обновляет основные метрики"""
        self.accuracy_label.config(text=f"{stats['overall_accuracy']:.1%}")
        self.processed_label.config(text=f"{stats['total_samples']}")
        self.clusters_label.config(text=f"{stats['total_clusters']}")
        
        # Эффективность фидбека = (correct + verified) / total
        feedback_eff = (stats['correct_predictions'] + 
                       stats['feedback_stats'].get('verified', 0)) / stats['total_samples']
        self.feedback_label.config(text=f"{feedback_eff:.1%}")

    def update_charts(self, stats):
        """Обновляет графики"""
        # График распределения фидбеков
        self.feedback_ax.clear()
        feedback_types = ['yes', 'no', 'unsure', 'verified']
        feedback_counts = [stats['feedback_stats'].get(fb, 0) for fb in feedback_types]
        feedback_labels = ['✅ Да', '❌ Нет', '⏰ Не знаю', '🎯 Верификация']
        
        bars = self.feedback_ax.bar(feedback_labels, feedback_counts, color=['green', 'red', 'orange', 'blue'])
        self.feedback_ax.set_title('Распределение ответов пользователя')
        self.feedback_ax.tick_params(axis='x', rotation=45)
        
        # Добавляем подписи значений
        for bar, count in zip(bars, feedback_counts):
            height = bar.get_height()
            self.feedback_ax.text(bar.get_x() + bar.get_width()/2., height,
                                f'{count}', ha='center', va='bottom')
        
        self.feedback_fig.tight_layout()
        self.feedback_canvas.draw()
        
        # График точности по цифрам
        self.accuracy_ax.clear()
        digits = list(range(10))
        accuracies = []
        
        for digit in digits:
            data = stats['digit_accuracy'][digit]
            accuracy = data['correct'] / data['total'] if data['total'] > 0 else 0
            accuracies.append(accuracy)
        
        bars = self.accuracy_ax.bar(digits, accuracies, color='skyblue')
        self.accuracy_ax.set_title('Точность по цифрам')
        self.accuracy_ax.set_xlabel('Цифра')
        self.accuracy_ax.set_ylabel('Точность')
        self.accuracy_ax.set_ylim(0, 1)
        
        # Добавляем подписи значений
        for bar, acc in zip(bars, accuracies):
            height = bar.get_height()
            self.accuracy_ax.text(bar.get_x() + bar.get_width()/2., height,
                                f'{acc:.1%}', ha='center', va='bottom')
        
        self.accuracy_fig.tight_layout()
        self.accuracy_canvas.draw()

    def update_detailed_stats(self, stats):
        """Обновляет детальную статистику"""
        # Очищаем таблицу
        for item in self.stats_tree.get_children():
            self.stats_tree.delete(item)
        
        detailed_stats = [
            ("Всего обработано цифр", f"{stats['total_samples']}"),
            ("Правильных предсказаний", f"{stats['correct_predictions']}"),
            ("Общая точность", f"{stats['overall_accuracy']:.1%}"),
            ("Количество кластеров", f"{stats['total_clusters']}"),
            ("Ответов 'Да'", f"{stats['feedback_stats'].get('yes', 0)}"),
            ("Ответов 'Нет'", f"{stats['feedback_stats'].get('no', 0)}"), 
            ("Ответов 'Не знаю'", f"{stats['feedback_stats'].get('unsure', 0)}"),
            ("Верифицировано", f"{stats['feedback_stats'].get('verified', 0)}"),
            ("Эффективность микрофидбека", f"{(stats['correct_predictions'] / stats['total_samples']):.1%}"),
        ]
        
        # Добавляем точность по цифрам
        for digit in range(10):
            data = stats['digit_accuracy'][digit]
            if data['total'] > 0:
                accuracy = data['correct'] / data['total']
                detailed_stats.append((f"Точность цифры {digit}", f"{accuracy:.1%}"))
        
        for metric, value in detailed_stats:
            self.stats_tree.insert('', 'end', values=(metric, value))

    def get_fallback_stats(self):
        """Возвращает статистику по умолчанию при ошибках"""
        return {
            'total_samples': 0,
            'correct_predictions': 0,
            'overall_accuracy': 0,
            'total_clusters': 0,
            'feedback_stats': {'yes': 0, 'no': 0, 'unsure': 0, 'verified': 0},
            'digit_accuracy': {i: {'correct': 0, 'total': 0} for i in range(10)}
        }