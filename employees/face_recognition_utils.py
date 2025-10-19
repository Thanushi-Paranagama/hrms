# employees/face_recognition_utils.py
import face_recognition
import numpy as np
from PIL import Image

def encode_face(image_path):
    """Generate face encoding from image"""
    image = face_recognition.load_image_file(image_path)
    encodings = face_recognition.face_encodings(image)
    if encodings:
        return encodings[0].tolist()
    return None

def verify_face(known_encoding, image_path):
    """Verify face against known encoding"""
    image = face_recognition.load_image_file(image_path)
    unknown_encodings = face_recognition.face_encodings(image)
    
    if not unknown_encodings:
        return False
    
    known = np.array(known_encoding)
    unknown = unknown_encodings[0]
    
    results = face_recognition.compare_faces([known], unknown)
    return results[0]