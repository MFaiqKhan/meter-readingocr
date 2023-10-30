from flask import Flask, request, jsonify
from paddleocr import PaddleOCR
from PIL import Image
import re

app = Flask(__name__)

ocr = PaddleOCR(lang="en", use_gpu=False)

@app.route('/ocr', methods=['POST'])
def perform_ocr():
    try:
        # Get the image from the POST request
        file = request.files['image']

        # Load the image
        image = Image.open(file)

        # Crop the image
        width, height = image.size
        crop_top = height // 4  # Adjust the cropping position here
        cropped_image = image.crop((0, crop_top, width, height))

        # Use the OCR model to extract text and bounding boxes
        result = ocr.ocr(cropped_image, use_gpu=False, output_format='dict')

        # Extract numbers
        numbers = []
        for line in result:
            line_text = ' '.join([word_info['text'] for word_info in line['words']])
            number_matches = re.findall(r'\d+(?:\.\d+)?', line_text)
            numbers.extend(number_matches)

        return jsonify(numbers)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
