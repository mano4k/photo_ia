import os
import sys
import json
from dotenv import load_dotenv

# --- Configuration pour l'Importation ---
# Ajouter le répertoire parent au PYTHONPATH pour pouvoir importer app.py
# (Utile si test_vision.py est dans un sous-dossier, mais bonne pratique)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# --- Import de la fonction ---
# Assurez-vous que le nom du fichier principal est bien 'app'
try:
    from app import detecter_ingredients_gvision
    print("Importation de detecter_ingredients_gvision réussie.")
except ImportError:
    print("Erreur: Impossible d'importer la fonction 'detecter_ingredients_gvision'.")
    print("Vérifiez que 'app.py' existe et est dans le même répertoire.")
    sys.exit(1)


def test_detection_locale():
    # --- PRÉREQUIS ---
    # 1. Charger les variables d'environnement (authentification Google Cloud)
    load_dotenv()

    # 2. Définir le chemin de l'image de test
    # Assurez-vous que cette image existe dans le même répertoire !
    TEST_IMAGE_PATH = "Ingredients-de-cuisine.jpg" 

    if not os.path.exists(TEST_IMAGE_PATH):
        print("\n--- ERREUR DE FICHIER ---")
        print(f"Le fichier de test '{TEST_IMAGE_PATH}' n'a pas été trouvé.")
        print("Veuillez créer une image nommée 'test_ingredients.jpg' dans ce dossier.")
        return

    print(f"\n--- Démarrage du Test avec l'image : {TEST_IMAGE_PATH} ---")
    
    try:
        # 3. Appel de la fonction
        ingredients = detecter_ingredients_gvision(TEST_IMAGE_PATH)

        # 4. Affichage des résultats
        print("\n--- RÉSULTATS DE L'ANALYSE VISION API ---")
        if ingredients:
            print(f"Ingrédients détectés (Score > 0.70) : {len(ingredients)}")
            for i, ing in enumerate(ingredients):
                print(f"  {i+1}. {ing}")
            
            # Vérification simple de succès (non obligatoire)
            if any(ing in ingredients for ing in ["Food", "Ingredient", "Produce"]):
                print("\n✅ TEST RÉUSSI : L'API a répondu avec des étiquettes pertinentes.")
            else:
                 print("\n⚠️ AVERTISSEMENT : L'API a répondu, mais les résultats sont inattendus. Vérifiez l'image.")
            
        else:
            print("❌ TEST RÉUSSI, MAIS AUCUN INGRÉDIENT DÉTECTÉ (ou faible confiance).")
            print("Vérifiez la qualité de l'image ou si l'API a renvoyé des résultats sous le seuil de 0.70.")
            
    except Exception as e:
        print("\n❌ TEST ÉCHOUÉ : Erreur lors de l'appel à l'API Vision.")
        if "Authentication" in str(e) or "credentials" in str(e):
            print("\n🚨 ERREUR D'AUTHENTIFICATION ! Assurez-vous que:")
            print("1. Votre fichier .env est chargé correctement.")
            print("2. La variable GOOGLE_APPLICATION_CREDENTIALS pointe vers le bon fichier JSON.")
            print("3. Votre rôle 'Utilisateur de l'API Cloud Vision' est bien activé dans GCP.")
        else:
            print(f"Erreur détaillée: {e}")

if __name__ == "__main__":
    test_detection_locale()