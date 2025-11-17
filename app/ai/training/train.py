import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras import layers, models
import json
import os

IMG_SIZE = (224, 224)
BATCH_SIZE = 16

# Ensure required folders exist
os.makedirs("saved_model", exist_ok=True)

# Data augmentation + split
train_datagen = ImageDataGenerator(
    rescale=1./255,
    validation_split=0.2,
    horizontal_flip=True,
    zoom_range=0.2,
)

# Training data
train_data = train_datagen.flow_from_directory(
    "dataset",                 # لأنك داخل training
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    subset="training",
    class_mode="categorical"
)

# Validation data
val_data = train_datagen.flow_from_directory(
    "dataset",                 # نفس الفكرة
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    subset="validation",
    class_mode="categorical"
)

# Save class labels (important for prediction later)
with open("labels.json", "w", encoding="utf-8") as f:
    json.dump(train_data.class_indices, f, indent=4, ensure_ascii=False)

print("Saved labels.json:", train_data.class_indices)

# Load EfficientNetB0
base_model = EfficientNetB0(
    include_top=False,
    weights="imagenet",
    input_shape=(224,224,3)
)
base_model.trainable = False

# Build model
model = models.Sequential([
    base_model,
    layers.GlobalAveragePooling2D(),
    layers.Dropout(0.3),
    layers.Dense(train_data.num_classes, activation="softmax")
])

model.compile(
    optimizer="adam",
    loss="categorical_crossentropy",
    metrics=["accuracy"]
)

# Train model
model.fit(
    train_data,
    validation_data=val_data,
    epochs=10
)

# Save model
model.save("saved_model/model.h5")
model.save("saved_model/model.keras")

print("Model saved in saved_model/model.h5")
