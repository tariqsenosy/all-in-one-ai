import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing import image
import json
import os

# Paths relative to training folder
MODEL_PATH = "saved_model/model.keras"   
LABELS_PATH = "labels.json"

# Load model
model = tf.keras.models.load_model(MODEL_PATH)

# Load label mapping
with open(LABELS_PATH, "r", encoding="utf-8") as f:
    class_indices = json.load(f)

idx_to_label = {v: k for k, v in class_indices.items()}

def predict_image(img_path):
    img = image.load_img(img_path, target_size=(224, 224))
    x = image.img_to_array(img) / 255.0
    x = np.expand_dims(x, axis=0)

    pred = model.predict(x)[0]
    idx = int(pred.argmax())
    label = idx_to_label[idx]
    confidence = float(pred[idx])

    return {
        "label": label,
        "confidence": round(confidence, 3)
    }
