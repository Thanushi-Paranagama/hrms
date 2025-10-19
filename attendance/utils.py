# Create this file: attendance/utils.py

import face_recognition
import numpy as np
from PIL import Image
from io import BytesIO


def encode_face_from_file(image_file):
    """
    Generate face encoding from uploaded image file
    Returns: face encoding as list or None if no face found
    """
    try:
        # Load image
        image = face_recognition.load_image_file(image_file)
        
        # Get face encodings
        encodings = face_recognition.face_encodings(image)
        
        if encodings:
            # Return the first face encoding as a list
            return encodings[0].tolist()
        else:
            return None
    except Exception as e:
        print(f"Error encoding face: {str(e)}")
        return None


def verify_face_match(known_encoding_str, image_file, tolerance=0.6):
    """
    Verify if the face in the image matches the known encoding
    
    Args:
        known_encoding_str: String representation of known face encoding
        image_file: Uploaded image file
        tolerance: How much distance between faces to consider a match (lower is more strict)
    
    Returns: (is_match: bool, confidence: float)
    """
    try:
        # Convert string encoding back to numpy array
        import json
        known_encoding = np.array(json.loads(known_encoding_str))
        
        # Load the image to verify
        image = face_recognition.load_image_file(image_file)
        
        # Find face encodings in the image
        unknown_encodings = face_recognition.face_encodings(image)
        
        if not unknown_encodings:
            return False, 0.0
        
        # Compare faces
        unknown_encoding = unknown_encodings[0]
        results = face_recognition.compare_faces([known_encoding], unknown_encoding, tolerance=tolerance)
        
        # Calculate face distance (lower = more similar)
        face_distance = face_recognition.face_distance([known_encoding], unknown_encoding)[0]
        
        # Convert distance to confidence percentage
        confidence = (1 - face_distance) * 100
        
        return results[0], confidence
        
    except Exception as e:
        print(f"Error verifying face: {str(e)}")
        return False, 0.0


def detect_faces_count(image_file):
    """
    Count the number of faces in an image
    Returns: number of faces detected
    """
    try:
        image = face_recognition.load_image_file(image_file)
        face_locations = face_recognition.face_locations(image)
        return len(face_locations)
    except:
        return 0

