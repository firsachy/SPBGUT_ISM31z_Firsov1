import sqlite3
import os
import json
import pickle

class Database:
    def __init__(self):
        # создаем папку data если ее нет
        if not os.path.exists('data'):
            os.makedirs('data')

        # Подключаемся к БД
        self.conn = sqlite3.connect('data/feedback.db')
        self.create_tables()
        print("✅ База данных инициализирована")
    
    def create_tables(self):
        """Создаем таблицы если их нет"""
        cursor = self.conn.cursor()

        # Таблица для фидбеков пользователей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedbacks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                image_id INTEGER,
                true_label INTEGER,
                user_feedback TEXT,  -- 'yes', 'no', 'delayed'
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица для настроек системы
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_config (
                id INTEGER PRIMARY KEY CHECK (id = 1),  -- Всегда одна запись
                feature_extractor_config TEXT,          -- JSON с настройками экстрактора
                clustering_config TEXT,                 -- JSON с настройками кластеризации
                weights_config TEXT,                    -- JSON с настройками весов
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица для кластеров
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clusters (
                cluster_id INTEGER PRIMARY KEY AUTOINCREMENT,
                centroid BLOB,                          -- Бинарные данные центроида
                algorithm_params TEXT,                  -- JSON с параметрами алгоритма
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица для весов кластеров
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cluster_weights (
                cluster_id INTEGER,
                digit INTEGER,                          -- Цифра 0-9
                weight REAL DEFAULT 0.1,                -- Вес для этой цифры в кластере
                PRIMARY KEY (cluster_id, digit),
                FOREIGN KEY (cluster_id) REFERENCES clusters(cluster_id)
            )
        ''')
        
        # Таблица для примеров
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS samples (
                sample_id INTEGER PRIMARY KEY AUTOINCREMENT,
                image_data BLOB,                        -- Бинарные данные изображения
                features BLOB,                          -- Вектор признаков от экстрактора
                cluster_id INTEGER,                     -- В какой кластер попал
                predicted_label INTEGER,                -- Что система предположила
                user_feedback TEXT,                     -- 'yes', 'no', 'unsure'
                verified_label INTEGER,                 -- Истинная метка (после верификации)
                is_used BOOLEAN DEFAULT FALSE,          -- Показывалось ли уже пользователю
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cluster_id) REFERENCES clusters(cluster_id)
            )
        ''')
        
        self.conn.commit()
        print("✅ Таблицы созданы")

    # ===== МЕТОДЫ ДЛЯ НАСТРОЕК =====
    
    def save_system_config(self, feature_config, clustering_config, weights_config):
        """Сохранить настройки системы"""
        cursor = self.conn.cursor()
        
        # Преобразуем в JSON
        feature_json = json.dumps(feature_config)
        clustering_json = json.dumps(clustering_config)
        weights_json = json.dumps(weights_config)
        
        cursor.execute('''
            INSERT OR REPLACE INTO system_config 
            (id, feature_extractor_config, clustering_config, weights_config, updated_at)
            VALUES (1, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (feature_json, clustering_json, weights_json))
        
        self.conn.commit()
        print("✅ Настройки системы сохранены")
    
    def load_system_config(self):
        """Загрузить настройки системы"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM system_config WHERE id = 1')
        result = cursor.fetchone()
        
        if result:
            return {
                'feature_extractor': json.loads(result[1]),
                'clustering': json.loads(result[2]),
                'weights': json.loads(result[3]),
                'created_at': result[4],
                'updated_at': result[5]
            }
        else:
            return None
    
    def reset_system_config(self):
        """Удалить все настройки и состояние системы"""
        cursor = self.conn.cursor()
        
        # Удаляем все данные (кроме фидбеков, если хочешь их сохранить)
        cursor.execute('DELETE FROM system_config')
        cursor.execute('DELETE FROM clusters')
        cursor.execute('DELETE FROM cluster_weights')
        cursor.execute('DELETE FROM samples')
        cursor.execute('UPDATE sqlite_sequence SET seq=0 WHERE name="clusters"')  # Сброс автоинкремента
        cursor.execute('UPDATE sqlite_sequence SET seq=0 WHERE name="samples"')
        
        self.conn.commit()
        print("✅ Все настройки и данные системы сброшены")

    # ===== МЕТОДЫ ДЛЯ КЛАСТЕРОВ =====
    
    def save_clusters(self, clusters_data):
        """Сохранить кластеры и их веса"""
        cursor = self.conn.cursor()
        
        for cluster in clusters_data:
            # Сохраняем кластер
            centroid_blob = pickle.dumps(cluster['centroid'])
            algorithm_params = json.dumps(cluster.get('params', {}))
            
            cursor.execute('''
                INSERT INTO clusters (centroid, algorithm_params)
                VALUES (?, ?)
            ''', (centroid_blob, algorithm_params))
            
            cluster_id = cursor.lastrowid
            
            # Сохраняем веса для этого кластера
            for digit, weight in cluster['weights'].items():
                cursor.execute('''
                    INSERT INTO cluster_weights (cluster_id, digit, weight)
                    VALUES (?, ?, ?)
                ''', (cluster_id, digit, weight))
        
        self.conn.commit()
        print(f"✅ Сохранено {len(clusters_data)} кластеров")
    
    def load_clusters(self):
        """Загрузить все кластеры с весами"""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            SELECT c.cluster_id, c.centroid, c.algorithm_params, 
                   cw.digit, cw.weight
            FROM clusters c
            JOIN cluster_weights cw ON c.cluster_id = cw.cluster_id
            ORDER BY c.cluster_id, cw.digit
        ''')
        
        results = cursor.fetchall()
        
        if not results:
            return []
        
        clusters = {}
        for row in results:
            cluster_id, centroid_blob, params_json, digit, weight = row
            
            if cluster_id not in clusters:
                clusters[cluster_id] = {
                    'cluster_id': cluster_id,
                    'centroid': pickle.loads(centroid_blob),
                    'params': json.loads(params_json),
                    'weights': {}
                }
            
            clusters[cluster_id]['weights'][digit] = weight
        
        return list(clusters.values())

    # ===== МЕТОДЫ ДЛЯ ПРИМЕРОВ =====
    
    def save_sample(self, image_data, features, cluster_id, predicted_label, user_feedback, verified_label=None):
        """Сохранить пример с фидбеком"""
        cursor = self.conn.cursor()
        
        image_blob = pickle.dumps(image_data)
        features_blob = pickle.dumps(features)
        
        cursor.execute('''
            INSERT INTO samples 
            (image_data, features, cluster_id, predicted_label, user_feedback, verified_label, is_used)
            VALUES (?, ?, ?, ?, ?, ?, TRUE)
        ''', (image_blob, features_blob, cluster_id, predicted_label, user_feedback, verified_label))
        
        self.conn.commit()
        return cursor.lastrowid

    def get_unused_samples(self, limit=100):
        """Получить примеры, которые еще не показывались пользователю"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT sample_id, image_data, features 
            FROM samples 
            WHERE is_used = FALSE 
            LIMIT ?
        ''', (limit,))
        
        results = cursor.fetchall()
        samples = []
        for row in results:
            sample_id, image_blob, features_blob = row
            samples.append({
                'sample_id': sample_id,
                'image_data': pickle.loads(image_blob),
                'features': pickle.loads(features_blob)
            })
        
        return samples

    # ===== СТАТИСТИКА =====
    
    def get_stats(self):
        """Получить статистику системы"""
        cursor = self.conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM feedbacks')
        total_feedbacks = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM clusters')
        total_clusters = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM samples WHERE is_used = TRUE')
        used_samples = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM samples WHERE verified_label IS NOT NULL')
        verified_samples = cursor.fetchone()[0]
        
        return {
            'total_feedbacks': total_feedbacks,
            'total_clusters': total_clusters,
            'used_samples': used_samples,
            'verified_samples': verified_samples,
            'config_exists': self.load_system_config() is not None
        }

    def close_connection(self):
        """Закрыть соединение с БД"""
        if self.conn:
            self.conn.close()
            print("🔌 Соединение с БД закрыто")
    
    def reconnect(self):
        """Переподключиться к БД"""
        self.close_connection()
        self.conn = sqlite3.connect('data/feedback.db')
        print("🔌 Соединение с БД восстановлено")