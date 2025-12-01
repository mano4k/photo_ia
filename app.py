from flask import Flask, render_template,request, jsonify
import requests
import json
import os
from google.api_core.exceptions import GoogleAPICallError
import re
import base64
import openai   
from openai import OpenAI
from datetime import datetime
from google.cloud import vision
from dotenv import load_dotenv

app = Flask(__name__)

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), 'temp_uploads')
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

load_dotenv() 
OpenAI.api_key=os.getenv("OPENAI_API_KEY")
app.secret_key=os.getenv("SECRET_KEY") or "dev-secret-key"
vision_client = vision.ImageAnnotatorClient()
def detecter_ingredients_gvision(chemin_fichier: str) -> list:
    """
    Détecte les étiquettes (labels) dans une image en utilisant Google Vision API.
    Utilise la librairie google-cloud-vision.
    """
    
    # 1. Lire et charger le contenu binaire de l'image
    with open(chemin_fichier, 'rb') as image_file:
        content = image_file.read()

    # 2. Créer l'objet Image pour l'API Vision
    image = vision.Image(content=content)
    
    # 3. Appeler la méthode de détection d'étiquettes
    # C'est ici que l'image est envoyée via le client
    response = vision_client.label_detection(image=image)
    labels = response.label_annotations
    
    # 4. Traiter et retourner les résultats
    ingredients = [label.description for label in labels if label.score > 0.70]
    
    print(ingredients)
            
    return ingredients



def appl_gpt(listes: str, model: str = "gpt-5") -> str:
    prompt = f"""en tant que specialiste json Analyse la liste suivante:
    voici la liste: {listes}
    1) identifie les ingredients de nourrirure
       exemple: tomates, sel, poivre, carottes etc.
    2) ne pas faire de commentaire
    3) format de sortie: json contenant ces ingredients
    """.strip()

    try:
        completion = openai.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
        )
        return completion.choices[0].message.content.strip()

    except Exception as e:
        return f"[Erreur OpenAI] {e}"
    
    


@app.route('/')
def open_camera():
    return render_template('index.html')



@app.route("/analyze", methods=["POST"])
def analyze():
    # 1. Lire le JSON reçu
   #

    # 1. Lire le JSON reçu
    data = request.get_json(silent=True)
    print(">>> /analyze appelé")
    print("JSON reçu :", data)

    if not data or "image" not in data:
        print(" Aucune image dans le JSON")
        print("❌ Aucune image dans le JSON")
        return jsonify({"error": "Aucune image reçue"}), 400

    data_url = data["image"]
    print("Début data_url :", data_url[:50], "...")
    print("Début data_url :", data_url[:50], "...")

    # data:image/jpeg;base64,....
    match = re.match(r"^data:image/(png|jpeg);base64,(.+)$", data_url)
    if not match:
        print(" Regex n'a pas matché la dataURL")
        print("❌ Regex n'a pas matché la dataURL")
        return jsonify({"error": "Format d'image invalide"}), 400

    ext = match.group(1)
    img_b64 = match.group(2)
    print("Extension détectée :", ext)
    print("Extension détectée :", ext)

    try:
        img_bytes = base64.b64decode(img_b64)
    except Exception as e:
        print("Erreur décodage base64 :", e)
    except Exception as e:
        print("❌ Erreur décodage base64 :", e)
        return jsonify({"error": "Impossible de décoder l'image"}), 400

    filename = datetime.utcnow().strftime("%Y%m%d_%H%M%S%f") + f".{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    print("Chemin de sauvegarde :", filepath)

    # Initialisation du chemin pour le bloc finally
    uploaded_filepath = None

    print("Chemin de sauvegarde :", filepath)

    # Initialisation du chemin pour le bloc finally
    uploaded_filepath = None

    try:
        # 2. Sauvegarde temporaire du fichier
        # 2. Sauvegarde temporaire du fichier
        with open(filepath, "wb") as f:
            f.write(img_bytes)


        uploaded_filepath = filepath
        print(" Image bien sauvegardée :", uploaded_filepath)

        print("✅ Image bien sauvegardée :", uploaded_filepath)

        # 3. Analyse avec Google Vision
        ingredients_detectes = detecter_ingredients_gvision(uploaded_filepath)
        print("Ingrédients détectés :", ingredients_detectes)

        print("✅ Ingrédients détectés :", ingredients_detectes)
        ingrediant_json=appl_gpt(ingredients_detectes)
        print("✅ Ingrédients détectés :", ingrediant_json)
        # 4. Retourner la réponse JSON
        resultat_json = {
            "statut": "succes",
            "ingredients_detectes": ingrediant_json,
           
        }


        return jsonify(resultat_json)


    except GoogleAPICallError as e:
        print(" Erreur API Vision :", e)
        print("❌ Erreur API Vision :", e)
        return jsonify({"erreur": f"Erreur de l'API Google Vision: {e.message}"}), 500


    except Exception as e:
        print(" Erreur interne analyze():", e)
        print("❌ Erreur interne analyze():", e)
        return jsonify({"erreur": f"Erreur interne du serveur: {str(e)}"}), 500


    finally:
        # 5. Nettoyage
        # 5. Nettoyage
        if uploaded_filepath and os.path.exists(uploaded_filepath):
            os.remove(uploaded_filepath)

            print("🧹 Fichier temporaire supprimé :", uploaded_filepath)


    

if __name__ == "__main__":
    app.run(debug=True)