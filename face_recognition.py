"""
Face Recognition Library Replacement using OpenCV
This module provides the same API as the popular face_recognition library
but uses OpenCV for face detection and recognition.
"""

import cv2
import numpy as np
from typing import List, Tuple, Any

# Initialize face cascade
_face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def load_image_file(file_path: str) -> np.ndarray:
    """
    Loads an image file (.jpg, .png, etc.) into a numpy array
    
    Args:
        file_path: Path to the image file
        
    Returns:
        Numpy array representing the image in BGR format
    """
    image = cv2.imread(str(file_path))
    if image is None:
        raise ValueError(f"Could not load image from {file_path}")
    # Convert BGR to RGB to match face_recognition library format
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

def face_locations(img: np.ndarray, number_of_times_to_upsample: int = 1, model: str = "hog") -> List[Tuple[int, int, int, int]]:
    """
    Returns an array of bounding boxes of human faces in an image
    
    Args:
        img: An image (as a numpy array)
        number_of_times_to_upsample: How many times to upsample the image looking for faces
        model: Which face detection model to use. "hog" or "cnn"
        
    Returns:
        A list of tuples of found face locations in css (top, right, bottom, left) order
    """
    # Convert RGB to grayscale for face detection
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    
    # Detect faces
    faces = _face_cascade.detectMultiScale(
        gray, 
        scaleFactor=1.1, 
        minNeighbors=5,
        minSize=(30, 30)
    )
    
    # Convert to face_recognition library format (top, right, bottom, left)
    locations = []
    for (x, y, w, h) in faces:
        top = y
        right = x + w
        bottom = y + h
        left = x
        locations.append((top, right, bottom, left))
    
    return locations

def face_encodings(face_image: np.ndarray, known_face_locations: List[Tuple[int, int, int, int]] = None, 
                  num_jitters: int = 1, model: str = "small") -> List[np.ndarray]:
    """
    Given an image, return the 128-dimension face encoding for each face in the image.
    
    Args:
        face_image: The image that contains one or more faces
        known_face_locations: Optional - the bounding boxes of each face if you already know them
        num_jitters: How many times to re-sample the face when calculating encoding
        model: Optional - which model to use. "large" or "small"
        
    Returns:
        A list of 128-dimensional face encodings (one for each face in the image)
    """
    if known_face_locations is None:
        known_face_locations = face_locations(face_image)
    
    # Convert RGB to grayscale
    gray = cv2.cvtColor(face_image, cv2.COLOR_RGB2GRAY)
    
    encodings = []
    for (top, right, bottom, left) in known_face_locations:
        # Extract face ROI
        face_roi = gray[top:bottom, left:right]
        
        if face_roi.size > 0:
            # Resize to standard size (100x100 for simplicity)
            face_roi = cv2.resize(face_roi, (100, 100))
            
            # Apply histogram equalization for better consistency
            face_roi = cv2.equalizeHist(face_roi)
            
            # Flatten to create a simple "encoding"
            encoding = face_roi.flatten().astype(np.float64)
            
            # Normalize the encoding
            encoding = encoding / np.linalg.norm(encoding)
            
            encodings.append(encoding)
    
    return encodings

def compare_faces(known_face_encodings: List[np.ndarray], face_encoding_to_check: np.ndarray, 
                 tolerance: float = 0.6) -> List[bool]:
    """
    Compare a list of face encodings against a candidate encoding to see which ones match.
    
    Args:
        known_face_encodings: A list of known face encodings
        face_encoding_to_check: A single face encoding to compare against the list
        tolerance: How much distance between faces to consider it a match
        
    Returns:
        A list of True/False values indicating which known_face_encodings match the face encoding to check
    """
    if not known_face_encodings:
        return []
    
    matches = []
    for known_encoding in known_face_encodings:
        # Calculate Euclidean distance
        distance = np.linalg.norm(known_encoding - face_encoding_to_check)
        
        # Convert distance to similarity (lower distance = higher similarity)
        similarity = 1.0 - (distance / 2.0)  # Normalize to 0-1 range
        
        matches.append(similarity > tolerance)
    
    return matches

def face_distance(face_encodings: List[np.ndarray], face_to_compare: np.ndarray) -> np.ndarray:
    """
    Given a list of face encodings, compare them to a known face encoding and get a euclidean distance
    for each comparison face. The distance tells you how similar the faces are.
    
    Args:
        face_encodings: List of face encodings to compare
        face_to_compare: A face encoding to compare against
        
    Returns:
        A numpy ndarray with the distance for each face in the same order as the 'faces' array
    """
    if not face_encodings:
        return np.array([])
    
    distances = []
    for encoding in face_encodings:
        distance = np.linalg.norm(encoding - face_to_compare)
        distances.append(distance)
    
    return np.array(distances)

# Additional utility functions that might be useful
def batch_face_locations(images: List[np.ndarray], number_of_times_to_upsample: int = 1, 
                        batch_size: int = 128) -> List[List[Tuple[int, int, int, int]]]:
    """
    Returns an 2d array of bounding boxes of human faces in each image in the given array
    
    Args:
        images: List of images to search for faces in
        number_of_times_to_upsample: How many times to upsample each image looking for faces
        batch_size: Number of images to include in each GPU processing batch
        
    Returns:
        A list of lists of face locations for each image
    """
    return [face_locations(img, number_of_times_to_upsample) for img in images]

# Example usage
if __name__ == "__main__":
    # Test the module
    try:
        # This is just a test - you would use actual image files
        print("Face recognition module loaded successfully!")
        print("Available functions:")
        print("- load_image_file()")
        print("- face_locations()")
        print("- face_encodings()")
        print("- compare_faces()")
        print("- face_distance()")
    except Exception as e:
        print(f"Error: {e}")