import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/deepak-bhagat/Downloads/iprc-456620-6454ff816526.json"

from google.cloud import vision

# Initialize client
client = vision.ImageAnnotatorClient()

# Load image
with open("image.jpg", "rb") as image_file:
    content = image_file.read()

image = vision.Image(content=content)

# Perform text detection
response = client.text_detection(image=image)
texts = response.text_annotations

if texts:
    print("Extracted Text:")
    print(texts[0].description)
else:
    print("No text found.")

# Error handling
if response.error.message:
    raise Exception(response.error.message)
