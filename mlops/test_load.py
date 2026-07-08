# test_load.py
import pickle
import joblib

print("="*60)
print("🔍 TEST DE CHARGEMENT DES MODÈLES")
print("="*60)

# Tester avec pickle
print("\n📂 Test avec pickle...")
try:
    with open("cls_best_model.pkl", "rb") as f:
        model = pickle.load(f)
    print("   ✅ cls_best_model.pkl chargé avec pickle")
except Exception as e:
    print(f"   ❌ Erreur pickle: {e}")

try:
    with open("reg_best_model.pkl", "rb") as f:
        model = pickle.load(f)
    print("   ✅ reg_best_model.pkl chargé avec pickle")
except Exception as e:
    print(f"   ❌ Erreur pickle: {e}")

# Tester avec joblib
print("\n📂 Test avec joblib...")
try:
    model = joblib.load("cls_best_model.pkl")
    print("   ✅ cls_best_model.pkl chargé avec joblib")
except Exception as e:
    print(f"   ❌ Erreur joblib: {e}")

try:
    model = joblib.load("reg_best_model.pkl")
    print("   ✅ reg_best_model.pkl chargé avec joblib")
except Exception as e:
    print(f"   ❌ Erreur joblib: {e}")

print("\n" + "="*60)