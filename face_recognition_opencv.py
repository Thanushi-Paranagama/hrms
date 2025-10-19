"""
Alternative face recognition implementation using OpenCV
This provides similar functionality to the face_recognition library
"""
import cv2
import numpy as np
from pathlib import Path

class FaceRecognition:
    def __init__(self):
        # Load OpenCV's pre-trained face detection model
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.face_recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.known_faces = {}
        self.known_names = []
        
    def load_image_file(self, image_path):
        """Load an image file (.jpg, .png, etc.) into a numpy array"""
        image = cv2.imread(str(image_path))
        if image is None:
            raise ValueError(f"Could not load image from {image_path}")
        return image
    
    def face_locations(self, image):
        """Find all face locations in an image"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
        
        # Convert to face_recognition library format (top, right, bottom, left)
        locations = []
        for (x, y, w, h) in faces:
            locations.append((y, x + w, y + h, x))
        
        return locations
    
    def face_encodings(self, image, face_locations=None):
        """Extract face encodings from face locations"""
        if face_locations is None:
            face_locations = self.face_locations(image)
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        encodings = []
        
        for (top, right, bottom, left) in face_locations:
            face_roi = gray[top:bottom, left:right]
            if face_roi.size > 0:
                # Resize face to standard size
                face_roi = cv2.resize(face_roi, (100, 100))
                encodings.append(face_roi.flatten())
        
        return encodings
    
    def compare_faces(self, known_encodings, face_encoding, tolerance=0.6):
        """Compare face encodings to known faces"""
        if not known_encodings:
            return []
        
        matches = []
        for known_encoding in known_encodings:
            # Simple correlation-based comparison
            correlation = cv2.matchTemplate(
                face_encoding.reshape(100, 100).astype(np.uint8),
                known_encoding.reshape(100, 100).astype(np.uint8),
                cv2.TM_CCOEFF_NORMED
            )
            matches.append(correlation[0][0] > tolerance)
        
        return matches

# Example usage functions
def load_known_faces(faces_directory):
    """Load all known faces from a directory"""
    face_rec = FaceRecognition()
    known_encodings = []
    known_names = []
    
    faces_dir = Path(faces_directory)
    if not faces_dir.exists():
        print(f"Directory {faces_directory} does not exist")
        return face_rec, known_encodings, known_names
    
    for image_file in faces_dir.glob("*"):
        if image_file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp']:
            try:
                image = face_rec.load_image_file(image_file)
                encodings = face_rec.face_encodings(image)
                
                if encodings:
                    known_encodings.append(encodings[0])
                    known_names.append(image_file.stem)
                    print(f"Loaded face: {image_file.name}")
            except Exception as e:
                print(f"Error loading {image_file.name}: {e}")
    
    return face_rec, known_encodings, known_names

def recognize_faces_in_image(image_path, known_encodings, known_names, face_rec):
    """Recognize faces in a new image"""
    try:
        image = face_rec.load_image_file(image_path)
        face_locations = face_rec.face_locations(image)
        face_encodings = face_rec.face_encodings(image, face_locations)
        
        results = []
        for face_encoding in face_encodings:
            matches = face_rec.compare_faces(known_encodings, face_encoding)
            name = "Unknown"
            
            if True in matches:
                match_index = matches.index(True)
                name = known_names[match_index]
            
            results.append(name)
        
        return results, face_locations
    except Exception as e:
        print(f"Error recognizing faces: {e}")
        return [], []

# Example usage
if __name__ == "__main__":
    # Example: Load known faces from a 'known_faces' directory
    face_rec, known_encodings, known_names = load_known_faces("known_faces")
    
    # Example: Recognize faces in a test image
    if known_encodings:
        results, locations = recognize_faces_in_image("test_image.jpg", known_encodings, known_names, face_rec)
        print(f"Found faces: {results}")
    else:
        print("No known faces loaded. Add images to 'known_faces' directory.")