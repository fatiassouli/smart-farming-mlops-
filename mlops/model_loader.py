# model_loader.py
import mlflow
import mlflow.sklearn
import pandas as pd
import numpy as np
import os

# Configuration
os.makedirs("mlruns", exist_ok=True)
mlflow.set_tracking_uri("file:./mlruns")

print("✅ MLflow configuré pour le chargement")
print(f"   Tracking URI: {mlflow.get_tracking_uri()}")

class ModelLoader:
    """
    Charge les modèles depuis MLflow pour l'API FastAPI
    """
    
    def __init__(self):
        self.model_cls = None  # Classification (recommandation)
        self.model_reg = None  # Régression (rendement)
        self._load_models()
    
    def _load_models(self):
        """
        Charge les modèles depuis le registry MLflow
        """
        print("\n📂 Chargement des modèles depuis MLflow...")
        
        # 1. Charger le modèle de classification
        try:
            self.model_cls = mlflow.sklearn.load_model(
                "models:/ModeleClassification/Production"
            )
            print("   ✅ Classification chargée (Production)")
        except Exception as e:
            print(f"   ⚠️ Erreur Production: {e}")
            try:
                self.model_cls = mlflow.sklearn.load_model(
                    "models:/ModeleClassification/Staging"
                )
                print("   ✅ Classification chargée (Staging)")
            except Exception as e2:
                print(f"   ❌ Erreur classification: {e2}")
                self.model_cls = None
        
        # 2. Charger le modèle de régression
        try:
            self.model_reg = mlflow.sklearn.load_model(
                "models:/ModeleRegression/Production"
            )
            print("   ✅ Régression chargée (Production)")
        except Exception as e:
            print(f"   ⚠️ Erreur Production: {e}")
            try:
                self.model_reg = mlflow.sklearn.load_model(
                    "models:/ModeleRegression/Staging"
                )
                print("   ✅ Régression chargée (Staging)")
            except Exception as e2:
                print(f"   ❌ Erreur régression: {e2}")
                self.model_reg = None
        
        if self.model_cls is not None and self.model_reg is not None:
            print("\n✅ Tous les modèles chargés avec succès !")
        else:
            print("\n⚠️ Certains modèles n'ont pas pu être chargés.")
    
    def prepare_features(self, data):
        """
        Prépare les features pour la prédiction
        
        Args:
            data: dict avec N, P, K, temperature, humidity, ph, rainfall
        
        Returns:
            DataFrame avec les features
        """
        features = pd.DataFrame([{
            'N': float(data['N']),
            'P': float(data['P']),
            'K': float(data['K']),
            'temperature': float(data['temperature']),
            'humidity': float(data['humidity']),
            'ph': float(data['ph']),
            'rainfall': float(data['rainfall'])
        }])
        return features
    
    def predict_crop(self, data):
        """
        Prédit la culture recommandée (classification)
        
        Args:
            data: dict avec les features
        
        Returns:
            tuple: (crop_name, confidence)
        """
        if self.model_cls is None:
            raise ValueError("❌ Modèle de classification non disponible")
        
        X = self.prepare_features(data)
        prediction = self.model_cls.predict(X)
        probabilities = self.model_cls.predict_proba(X)
        
        crop_name = str(prediction[0])
        confidence = float(np.max(probabilities[0])) * 100
        
        return crop_name, confidence
    
    def predict_yield(self, data):
        """
        Prédit le rendement (régression)
        
        Args:
            data: dict avec les features
        
        Returns:
            float: rendement en tonnes/ha
        """
        if self.model_reg is None:
            raise ValueError("❌ Modèle de régression non disponible")
        
        X = self.prepare_features(data)
        prediction = self.model_reg.predict(X)
        
        return float(prediction[0])
    
    def predict_both(self, data):
        """
        Fait les deux prédictions (recommandation + rendement)
        
        Args:
            data: dict avec les features
        
        Returns:
            dict: {crop_name, confidence, yield_tha, yield_hgha}
        """
        crop_name, confidence = self.predict_crop(data)
        yield_tha = self.predict_yield(data)
        
        return {
            'crop_name': crop_name,
            'confidence': round(confidence, 2),
            'yield_tha': round(yield_tha, 2),
            'yield_hgha': round(yield_tha * 1000, 0)
        }

# ============================================
# SINGLETON POUR L'API
# ============================================
_loader_instance = None

def get_model_loader():
    """
    Retourne l'instance unique du ModelLoader (Singleton)
    """
    global _loader_instance
    if _loader_instance is None:
        _loader_instance = ModelLoader()
    return _loader_instance

# ============================================
# TEST
# ============================================
if __name__ == "__main__":
    print("\n" + "="*60)
    print("🧪 TEST DU MODEL LOADER")
    print("="*60)
    
    loader = get_model_loader()
    
    # Données de test (similaire à ton app)
    test_data = {
        'N': 90,
        'P': 42,
        'K': 43,
        'temperature': 20.88,
        'humidity': 82.00,
        'ph': 6.50,
        'rainfall': 202.94
    }
    
    print("\n📊 Données d'entrée:")
    for key, value in test_data.items():
        print(f"   {key}: {value}")
    
    try:
        result = loader.predict_both(test_data)
        print("\n🌾 Résultat de la prédiction:")
        print(f"   Culture recommandée: {result['crop_name']}")
        print(f"   Confiance: {result['confidence']:.2f}%")
        print(f"   Rendement: {result['yield_tha']:.2f} t/ha")
        print(f"   Rendement: {result['yield_hgha']:.0f} kg/ha")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
    
    print("\n" + "="*60)
    print("✅ Test terminé")
    print("="*60)