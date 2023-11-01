from flask import Flask, request, jsonify
from paddleocr import PaddleOCR
from PIL import Image
import numpy as np
import cv2
import os
import tempfile
import re

app = Flask(__name__)

@app.route('/electric_meter', methods=['POST'])
def extract_numbers():
  try:
    # Get the image from the POST request
    file = request.files['image']

    # Load the image
    image = Image.open(file)

    # Crop the image
    width, height = image.size
    crop_top = height // 4 # Adjust the cropping position here
    cropped_image = image.crop((0, crop_top, width, height))

    # Save the cropped image to a temporary file
    _, temp_filename = tempfile.mkstemp(suffix=".png")
    cropped_image.save(temp_filename, format='PNG')

    img = cv2.imread(temp_filename)

    # Sharpen the image
    #kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
    #sharpened_img = cv2.filter2D(img, -1, kernel)

    # Save the sharpened image to a temporary file
    #_, temp_filename_sharpened = tempfile.mkstemp(suffix=".png")
    #cv2.imwrite(temp_filename_sharpened, sharpened_img)

    # Use the OCR model to extract text and bounding boxes
    ocr = PaddleOCR(lang="en")
    result = ocr.ocr(temp_filename)

    # Extract numbers
    numbers = []
    confidence_threshold = 0.9
    for line in result:
        line_text = line[1][0]
        confidence = line[1][1]
        if confidence > confidence_threshold:
          number_matches = re.findall(r'\b\d{7}\.\d\b|\b\d{6}\.\d{2}\b|\b\d{6}\.\d\b|\b\d{5}\.\d{2}\b|\b\d{5}\.\d\b|\b\d{6}\b|\b\d{4}\.\d{2}\b|\b\d{4}\.\d\b|\b\d{2}\.\d{2}\b'
, str(line_text))
          if number_matches:
            for num in number_matches:
               numbers.append({"number": num, "confidence": confidence})

    return jsonify(numbers=numbers)
  except Exception as e:
    return jsonify(error=str(e)), 500
  

@app.route('/water_meter', methods=['POST'])
def extract_water():
  try:
    # Get the image from the POST request
    file = request.files['image']

    # Load the image
    image = Image.open(file)

    # Crop the image
    width, height = image.size
    crop_top = height // 4 # Adjust the cropping position here
    cropped_image = image.crop((0, crop_top, width, height))

    # Save the cropped image to a temporary file
    _, temp_filename = tempfile.mkstemp(suffix=".png")
    cropped_image.save(temp_filename, format='PNG')

    #img = cv2.imread(temp_filename)


    # Use the OCR model to extract text and bounding boxes
    ocr = PaddleOCR(lang="en")
    result = ocr.ocr(temp_filename)

    # Extract numbers
    numbers = []
    confidence_threshold = 0.9
    for line in result:
        line_text = line[1][0]
        confidence = line[1][1]
        if confidence > confidence_threshold:
          number_matches = re.findall(r'\b\d{5}\b', str(line_text))
          if number_matches:
            for num in number_matches:
               numbers.append({"number": num, "confidence": confidence})

    return jsonify(numbers=numbers)
  except Exception as e:
    return jsonify(error=str(e)), 500

@app.errorhandler(404)
def resource_not_found(e):
    return jsonify(error=str(e)), 404

@app.errorhandler(500)
def internal_server_error(e):
    return jsonify(error=str(e)), 500

@app.errorhandler(Exception)
def handle_unexpected_error(e):
    return jsonify(error="An unexpected error occurred"), 500

if __name__ == '__main__':
   app.run(debug=True) 
