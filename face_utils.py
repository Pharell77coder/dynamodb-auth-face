import face_recognition
import base64
import numpy as np
import io
from PIL import Image

def process_face_image(base64_string):
    try:
        if "," in base64_string:
            base64_string = base64_string.split(",")[1]
        img_data = base64.b64decode(base64_string)
        img = Image.open(io.BytesIO(img_data)).convert('RGB')
        img_np = np.array(img)
        encodings = face_recognition.face_encodings(img_np)
        return encodings[0].tolist() if encodings else None
    except Exception as e:
        print(f"Erreur IA: {e}")
        return None

def compare_faces(stored_encoding, current_base64_image):
    current_encoding = process_face_image(current_base64_image)
    if current_encoding is None:
        return False
    # On reconvertit les Decimal (DynamoDB) en float (IA)
    results = face_recognition.compare_faces(
        [np.array([float(v) for v in stored_encoding])], 
        np.array(current_encoding), 
        tolerance=0.5
    )
    return bool(results[0])