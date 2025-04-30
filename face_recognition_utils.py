import os
import cv2
import numpy as np
import logging
from config import FACE_DETECTION_CONFIDENCE, FACE_RECOGNITION_THRESHOLD, STUDENT_IMAGES_DIR
import base64
from PIL import Image
from io import BytesIO

# Load face detection model (Haar Cascade)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def detect_face(image_data):
    """
    Detect faces in the given image data.
    
    Args:
        image_data: Image data as numpy array
    
    Returns:
        detected_face: Cropped face image if face is detected, None otherwise
        face_rect: Rectangle containing the face
    """
    try:
        # Convert to grayscale
        gray = cv2.cvtColor(image_data, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        
        if len(faces) == 0:
            return None, None
        
        # Get the largest face
        largest_face = None
        largest_area = 0
        for (x, y, w, h) in faces:
            if w * h > largest_area:
                largest_area = w * h
                largest_face = (x, y, w, h)
        
        x, y, w, h = largest_face
        face_rect = (x, y, w, h)
        
        # Crop the detected face
        detected_face = image_data[y:y+h, x:x+w]
        
        return detected_face, face_rect
    
    except Exception as e:
        logging.error(f"Error in face detection: {e}")
        return None, None

def save_face_image(face_image, student_id):
    """
    Save the face image to the student images directory.
    
    Args:
        face_image: Face image as numpy array
        student_id: Student ID to use in the filename
    
    Returns:
        str: Path to the saved image or None if error
    """
    try:
        if not os.path.exists(STUDENT_IMAGES_DIR):
            os.makedirs(STUDENT_IMAGES_DIR)
        
        image_path = os.path.join(STUDENT_IMAGES_DIR, f"student_{student_id}.jpg")
        cv2.imwrite(image_path, face_image)
        return image_path
    
    except Exception as e:
        logging.error(f"Error saving face image: {e}")
        return None

def decode_base64_image(base64_data):
    """
    Decode a base64 image to a numpy array.
    
    Args:
        base64_data: Base64 encoded image data
    
    Returns:
        numpy.ndarray: Image data as numpy array
    """
    try:
        # Remove the data URL prefix if present
        if "base64," in base64_data:
            base64_data = base64_data.split("base64,")[1]
        
        # Decode the base64 data
        image_data = base64.b64decode(base64_data)
        
        # Convert to numpy array
        nparr = np.frombuffer(image_data, np.uint8)
        
        # Decode image
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        return img
    
    except Exception as e:
        logging.error(f"Error decoding base64 image: {e}")
        return None

def load_and_preprocess_image(image_path):
    """
    Load and preprocess an image for face recognition.
    
    Args:
        image_path: Path to the image file
    
    Returns:
        numpy.ndarray: Preprocessed image data
    """
    try:
        img = cv2.imread(image_path)
        if img is None:
            logging.error(f"Failed to load image: {image_path}")
            return None
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply histogram equalization for better contrast
        gray = cv2.equalizeHist(gray)
        
        return gray
    
    except Exception as e:
        logging.error(f"Error preprocessing image {image_path}: {e}")
        return None

def recognize_face(face_image, student_images_dir):
    """
    Recognize a face among the registered students.
    
    Args:
        face_image: Face image as numpy array
        student_images_dir: Directory containing student face images
    
    Returns:
        str: Student ID of the matched face or None if no match
    """
    try:
        # If face_image is not grayscale, convert it
        if len(face_image.shape) > 2:
            face_gray = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)
        else:
            face_gray = face_image
        
        # Apply histogram equalization
        face_gray = cv2.equalizeHist(face_gray)
        
        # Resize to standard size for comparison
        face_gray = cv2.resize(face_gray, (100, 100))
        
        best_match = None
        best_score = float('inf')  # Lower is better for MSE
        
        # Check each student's face image
        for filename in os.listdir(student_images_dir):
            if filename.startswith("student_") and filename.endswith(".jpg"):
                student_id = filename.replace("student_", "").replace(".jpg", "")
                
                # Load and preprocess student image
                student_img_path = os.path.join(student_images_dir, filename)
                student_gray = load_and_preprocess_image(student_img_path)
                
                if student_gray is None:
                    continue
                
                # Resize to match face image size
                student_gray = cv2.resize(student_gray, (100, 100))
                
                # Calculate mean squared error for comparison
                mse = np.sum((face_gray.astype("float") - student_gray.astype("float")) ** 2)
                mse /= float(face_gray.shape[0] * face_gray.shape[1])
                
                # Lower MSE is better
                if mse < best_score and mse < FACE_RECOGNITION_THRESHOLD * 10000:
                    best_score = mse
                    best_match = student_id
        
        return best_match
    
    except Exception as e:
        logging.error(f"Error in face recognition: {e}")
        return None
