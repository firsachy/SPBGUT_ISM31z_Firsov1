import numpy as np
from sklearn.cluster import KMeans, DBSCAN
from sklearn.metrics.pairwise import cosine_distances, euclidean_distances
import tensorflow as tf
from tensorflow import keras
import pickle
import os

class HybridMLCore:
    def __init__(self):
        self.feature_extractor = None
        self.clusterer = None
        self.clusters = []  # Текущие кластеры с весами
        self.is_trained = False
        self.cluster_metric = 'cosine'  # Метрика по умолчанию
    
    def create_feature_extractor(self, architecture, embedding_size):
        """Создает нейросеть-экстрактор признаков"""
        try:
            if architecture == "Маленький перцептрон":
                model = keras.Sequential([
                    keras.layers.Flatten(input_shape=(28, 28)),
                    keras.layers.Dense(128, activation='relu'),
                    keras.layers.Dense(64, activation='relu'),
                    keras.layers.Dense(embedding_size, activation='relu', name='embedding')
                ])
            elif architecture == "Простая CNN":
                model = keras.Sequential([
                    keras.layers.Reshape((28, 28, 1), input_shape=(28, 28)),
                    keras.layers.Conv2D(32, (3, 3), activation='relu'),
                    keras.layers.MaxPooling2D((2, 2)),
                    keras.layers.Conv2D(64, (3, 3), activation='relu'),
                    keras.layers.MaxPooling2D((2, 2)),
                    keras.layers.Flatten(),
                    keras.layers.Dense(embedding_size, activation='relu', name='embedding')
                ])
            elif architecture == "Предобученная модель":
                # Используем упрощенную CNN как предобученную
                model = keras.Sequential([
                    keras.layers.Reshape((28, 28, 1), input_shape=(28, 28)),
                    keras.layers.Conv2D(16, (3, 3), activation='relu'),
                    keras.layers.MaxPooling2D((2, 2)),
                    keras.layers.Flatten(),
                    keras.layers.Dense(embedding_size, activation='relu', name='embedding')
                ])
            else:
                raise ValueError(f"Неизвестная архитектура: {architecture}")
            
            self.feature_extractor = model
            print(f"✅ Создан экстрактор: {architecture}, размерность: {embedding_size}")
            return model
            
        except Exception as e:
            print(f"❌ Ошибка создания экстрактора: {e}")
            raise
    
    def train_feature_extractor(self, training_data, epochs=5):
        """Обучает экстрактор признаков на наших данных"""
        try:
            if self.feature_extractor is None:
                raise ValueError("Сначала создайте экстрактор!")
            
            x_train = training_data['x_train']
            y_train = training_data['y_train']
            
            # Проверяем форму данных
            if len(x_train.shape) == 3:  # (samples, 28, 28)
                x_train = x_train.astype('float32')
            else:
                raise ValueError(f"Неожиданная форма данных: {x_train.shape}")
            
            # Добавляем выходной слой для обучения
            training_model = keras.Sequential([
                self.feature_extractor,
                keras.layers.Dense(64, activation='relu'),
                keras.layers.Dense(10, activation='softmax')
            ])
            
            training_model.compile(
                optimizer='adam',
                loss='sparse_categorical_crossentropy',
                metrics=['accuracy']
            )
            
            print(f"🎯 Обучаем экстрактор на {len(x_train)} примерах...")
            
            # Обучаем
            history = training_model.fit(
                x_train, y_train,
                epochs=epochs,
                batch_size=32,
                validation_split=0.2,
                verbose=1
            )
            
            self.is_trained = True
            final_accuracy = history.history['accuracy'][-1]
            print(f"✅ Экстрактор обучен! Точность: {final_accuracy:.3f}")
            
            return history.history
            
        except Exception as e:
            print(f"❌ Ошибка обучения экстрактора: {e}")
            raise
    
    def extract_features(self, images):
        """Извлекает признаки из изображений"""
        if not self.is_trained:
            raise ValueError("Экстрактор не обучен!")
        
        # Подготавливаем данные
        if len(images.shape) == 3:
            images = images.astype('float32')
        
        # Извлекаем признаки
        features = self.feature_extractor.predict(images, verbose=0)
        return features
    
    def perform_clustering(self, features, clustering_config):
        """Выполняет кластеризацию признаков с настройками из интерфейса"""
        try:
            algorithm = clustering_config['algorithm']
            self.cluster_metric = clustering_config.get('metric', 'cosine')
            
            print(f"📊 Запускаем {algorithm} кластеризацию...")
            
            if algorithm == "K-Means":
                n_clusters = clustering_config.get('k_value', 15)
                self.clusterer = KMeans(
                    n_clusters=n_clusters,
                    random_state=42,
                    n_init=10
                )
                print(f"   K-Means с {n_clusters} кластерами")
                
            elif algorithm == "DBSCAN":
                eps = clustering_config.get('eps_value', 0.8)
                min_samples = clustering_config.get('min_samples', 5)
                self.clusterer = DBSCAN(
                    eps=eps,
                    min_samples=min_samples,
                    metric=self.cluster_metric
                )
                print(f"   DBSCAN с eps={eps}, min_samples={min_samples}")
                
            elif algorithm == "Mean Shift":
                from sklearn.cluster import MeanShift
                bandwidth = clustering_config.get('bandwidth', 0.5)
                self.clusterer = MeanShift(bandwidth=bandwidth)
                print(f"   Mean Shift с bandwidth={bandwidth}")
                
            else:
                raise ValueError(f"Неизвестный алгоритм: {algorithm}")
            
            # Выполняем кластеризацию
            cluster_labels = self.clusterer.fit_predict(features)
            
            # Создаем структуру кластеров
            self._initialize_clusters(features, cluster_labels, clustering_config)
            
            print(f"✅ Кластеризация завершена! Создано {len(self.clusters)} кластеров")
            return cluster_labels
            
        except Exception as e:
            print(f"❌ Ошибка кластеризации: {e}")
            # Создаем fallback кластеры
            self._create_fallback_clusters(features, clustering_config)
            return np.zeros(len(features))  # Все в одном кластере
    
    def _initialize_clusters(self, features, cluster_labels, params):
        """Инициализирует кластеры с начальными весами"""
        self.clusters = []
        unique_clusters = np.unique(cluster_labels)
        
        # Обработка случая когда нет кластеров (DBSCAN)
        if len(unique_clusters) == 1 and unique_clusters[0] == -1:
            print("⚠️  DBSCAN не нашел кластеров. Создаем общий кластер.")
            self._create_fallback_clusters(features, params)
            return
        
        # Убираем шумовые точки (-1)
        unique_clusters = unique_clusters[unique_clusters != -1]
        
        if len(unique_clusters) == 0:
            print("⚠️  Нет валидных кластеров. Создаем общий кластер.")
            self._create_fallback_clusters(features, params)
            return
        
        for cluster_id in unique_clusters:
            # Находим центроид кластера
            cluster_mask = cluster_labels == cluster_id
            cluster_points = features[cluster_mask]
            
            if len(cluster_points) == 0:
                continue
                
            centroid = np.mean(cluster_points, axis=0)
            
            # Начальные веса (равномерное распределение)
            weights = {digit: 1.0/10 for digit in range(10)}
            
            cluster_data = {
                'cluster_id': int(cluster_id),
                'centroid': centroid,
                'weights': weights,
                'params': params,
                'size': len(cluster_points)
            }
            
            self.clusters.append(cluster_data)
            print(f"   Кластер {cluster_id}: {len(cluster_points)} примеров")
    
    def _create_fallback_clusters(self, features, params):
        """Создает резервные кластеры когда алгоритм не нашел кластеры"""
        print("🔄 Создаем резервные кластеры...")
        
        # Простой K-Means как fallback
        from sklearn.cluster import KMeans
        n_clusters = min(10, len(features))
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=5)
        cluster_labels = kmeans.fit_predict(features)
        
        self.clusterer = kmeans
        self._initialize_clusters(features, cluster_labels, params)
    
    def find_nearest_cluster(self, features):
        """Находит ближайший кластер для данных признаков"""
        if not self.clusters:
            raise ValueError("Кластеры не инициализированы!")
        
        # Для одного примера
        if len(features.shape) == 1:
            features = features.reshape(1, -1)
        
        nearest_cluster_id = None
        min_distance = float('inf')
        
        for cluster in self.clusters:
            if self.cluster_metric == 'cosine':
                dist = cosine_distances(features, [cluster['centroid']])[0][0]
            else:  # euclidean
                dist = np.linalg.norm(features - cluster['centroid'])
            
            if dist < min_distance:
                min_distance = dist
                nearest_cluster_id = cluster['cluster_id']
        
        return nearest_cluster_id, min_distance
    
    def predict(self, image):
        """Предсказывает цифру для одного изображения"""
        try:
            # Извлекаем признаки
            features = self.extract_features(np.array([image]))
            features = features[0]  # Берем первый (и единственный) пример
            
            # Находим ближайший кластер
            cluster_id, distance = self.find_nearest_cluster(features)
            cluster = self.get_cluster_by_id(cluster_id)
            
            # Выбираем цифру с наибольшим весом в кластере
            predicted_digit = max(cluster['weights'].items(), key=lambda x: x[1])[0]
            confidence = cluster['weights'][predicted_digit]
            
            return predicted_digit, confidence, cluster_id, features
            
        except Exception as e:
            print(f"❌ Ошибка предсказания: {e}")
            return 0, 0.1, 0, None  # Fallback prediction
    
    def get_cluster_by_id(self, cluster_id):
        """Возвращает кластер по ID"""
        for cluster in self.clusters:
            if cluster['cluster_id'] == cluster_id:
                return cluster
        raise ValueError(f"Кластер с ID {cluster_id} не найден")
    
    def update_cluster_weights(self, cluster_id, user_feedback, true_label=None, 
                             alpha=0.2, beta=0.5, gamma=0.5, min_weight=0.05):
        """Обновляет веса в кластере на основе обратной связи"""
        try:
            cluster = self.get_cluster_by_id(cluster_id)
            
            if user_feedback == 'yes':
                # Увеличиваем вес предсказанной цифры
                predicted_digit = max(cluster['weights'].items(), key=lambda x: x[1])[0]
                old_weight = cluster['weights'][predicted_digit]
                cluster['weights'][predicted_digit] = old_weight + alpha * (1 - old_weight)
                print(f"✅ Увеличили вес цифры {predicted_digit} в кластере {cluster_id}")
                
            elif user_feedback == 'no':
                # Уменьшаем вес предсказанной цифры
                predicted_digit = max(cluster['weights'].items(), key=lambda x: x[1])[0]
                cluster['weights'][predicted_digit] *= gamma
                print(f"✅ Уменьшили вес цифры {predicted_digit} в кластере {cluster_id}")
                
            elif user_feedback == 'verified' and true_label is not None:
                # Сильное обновление на основе верификации
                old_weight = cluster['weights'][true_label]
                cluster['weights'][true_label] = old_weight + beta * (1 - old_weight)
                print(f"✅ Верификация: усилили вес цифры {true_label} в кластере {cluster_id}")
            
            # Нормализуем веса и применяем минимальный порог
            self._normalize_weights(cluster, min_weight)
            
        except Exception as e:
            print(f"❌ Ошибка обновления весов: {e}")
    
    def _normalize_weights(self, cluster, min_weight):
        """Нормализует веса и применяет минимальный порог"""
        # Применяем минимальный порог
        for digit in cluster['weights']:
            cluster['weights'][digit] = max(cluster['weights'][digit], min_weight)
        
        # Нормализуем чтобы сумма была = 1
        total = sum(cluster['weights'].values())
        for digit in cluster['weights']:
            cluster['weights'][digit] /= total
    
    def get_clusters_data_for_db(self):
        """Подготавливает данные кластеров для сохранения в БД"""
        # Конвертируем numpy arrays в списки для сериализации
        clusters_data = []
        for cluster in self.clusters:
            cluster_copy = cluster.copy()
            cluster_copy['centroid'] = cluster['centroid'].tolist()  # numpy -> list
            clusters_data.append(cluster_copy)
        
        return clusters_data
    
    def load_clusters_from_db(self, clusters_data):
        """Загружает кластеры из данных БД"""
        # Конвертируем списки обратно в numpy arrays
        self.clusters = []
        for cluster in clusters_data:
            cluster_copy = cluster.copy()
            cluster_copy['centroid'] = np.array(cluster['centroid'])  # list -> numpy
            self.clusters.append(cluster_copy)
        
        print(f"✅ Загружено {len(self.clusters)} кластеров из БД")
    
    def get_system_info(self):
        """Возвращает информацию о системе"""
        return {
            'is_trained': self.is_trained,
            'clusters_count': len(self.clusters),
            'extractor_architecture': self.feature_extractor._name if self.feature_extractor else None,
            'clusterer_type': type(self.clusterer).__name__ if self.clusterer else None
        }
    
    def save_models(self, filepath='models/hybrid_system'):
        """Сохраняет обученные модели"""
        try:
            os.makedirs('models', exist_ok=True)
            
            if self.feature_extractor:
                self.feature_extractor.save(f'{filepath}_extractor.h5')
            if self.clusterer:
                with open(f'{filepath}_clusterer.pkl', 'wb') as f:
                    pickle.dump(self.clusterer, f)
            
            print("✅ Модели сохранены")
        except Exception as e:
            print(f"❌ Ошибка сохранения моделей: {e}")
    
    def load_models(self, filepath='models/hybrid_system'):
        """Загружает обученные модели"""
        try:
            if os.path.exists(f'{filepath}_extractor.h5'):
                self.feature_extractor = keras.models.load_model(f'{filepath}_extractor.h5')
            if os.path.exists(f'{filepath}_clusterer.pkl'):
                with open(f'{filepath}_clusterer.pkl', 'rb') as f:
                    self.clusterer = pickle.load(f)
            
            self.is_trained = True
            print("✅ Модели загружены")
        except Exception as e:
            print(f"❌ Ошибка загрузки моделей: {e}")