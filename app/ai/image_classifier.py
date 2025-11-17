import tensorflow as tf
from tensorflow import keras
import numpy as np
from PIL import Image
import io
from typing import Tuple, Optional
import os


class ImageComplaintClassifier:
    """
    Classifies road incident images (accident vs fight vs other).
    Can be extended to detect other types of incidents.
    """
    
    def __init__(self, model_path: Optional[str] = None):
        self.img_height = 224
        self.img_width = 224
        self.model = None
        self.class_names = ["accident", "fight", "other"]
        
        # Try to load model if path provided
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
        else:
            print("No pre-trained model found. Using rule-based classification.")
            self.model = None
    
    def load_model(self, model_path: str):
        """Load pre-trained TensorFlow model"""
        try:
            self.model = keras.models.load_model(model_path)
            print(f"Image classifier model loaded from {model_path}")
        except Exception as e:
            print(f"Failed to load model: {e}")
            self.model = None
    
    async def classify_image(self, image_bytes: bytes) -> Tuple[str, float]:
        """
        Classify an image complaint.
        
        Args:
            image_bytes: Raw image bytes
            
        Returns:
            Tuple of (complaint_type, confidence_score)
        """
        
        # If no model is loaded, return a default classification
        if self.model is None:
            return self._rule_based_classification(image_bytes)
        
        try:
            # Preprocess image
            img = Image.open(io.BytesIO(image_bytes))
            img = img.convert('RGB')
            img = img.resize((self.img_height, self.img_width))
            img_array = np.array(img) / 255.0
            img_array = np.expand_dims(img_array, axis=0)
            
            # Predict
            predictions = self.model.predict(img_array, verbose=0)
            
            # Get class and confidence
            if len(predictions.shape) == 2 and predictions.shape[1] == 1:
                # Binary classification (accident vs fight)
                confidence = float(predictions[0][0])
                if confidence > 0.5:
                    complaint_type = "fight"
                    confidence_score = confidence
                else:
                    complaint_type = "accident"
                    confidence_score = 1 - confidence
            else:
                # Multi-class classification
                class_idx = np.argmax(predictions[0])
                confidence_score = float(predictions[0][class_idx])
                complaint_type = self.class_names[class_idx] if class_idx < len(self.class_names) else "other"
            
            return complaint_type, confidence_score
            
        except Exception as e:
            print(f"Error classifying image: {e}")
            return "image_complaint", 0.5
    
    def _rule_based_classification(self, image_bytes: bytes) -> Tuple[str, float]:
        """
        Fallback rule-based classification when no model is available.
        This is a placeholder - you can enhance it with basic image analysis.
        """
        try:
            img = Image.open(io.BytesIO(image_bytes))
            
            # Simple heuristics based on image properties
            # This is just a placeholder - replace with actual logic
            width, height = img.size
            
            # Example: Classify based on image characteristics
            # In production, you'd use proper CV techniques or API calls
            return "image_complaint", 0.7
            
        except Exception as e:
            print(f"Error in rule-based classification: {e}")
            return "unknown", 0.5
    
    def generate_image_description(self, complaint_type: str, confidence: float) -> str:
        """Generate a description based on the classification"""
        
        descriptions = {
            "accident": f"The image appears to show a road accident (confidence: {confidence:.2%})",
            "fight": f"The image appears to show a physical altercation (confidence: {confidence:.2%})",
            "traffic": f"The image shows a traffic-related issue (confidence: {confidence:.2%})",
            "infrastructure": f"The image shows an infrastructure problem (confidence: {confidence:.2%})",
            "other": f"The image shows a general complaint (confidence: {confidence:.2%})",
            "image_complaint": "Image-based complaint received"
        }
        
        return descriptions.get(complaint_type, "Image complaint received")