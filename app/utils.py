from easyocr import Reader 
import cv2
import difflib
import matplotlib.pyplot as plt

import cv2
import numpy as np
from matplotlib import pyplot as plt
from easyocr import Reader
import difflib

from ultralytics import YOLO
model = YOLO('./runs/detect/train19/weights/best.pt')

f = open('./areas.txt', 'r', encoding='utf-8')
words = f.read().splitlines()

vclass = [
    'গ','হ','ল','ঘ','চ','ট','থ','এ',
    'ক','খ','ভ','প','ছ','জ','ঝ','ব',
    'স','ত','দ','ফ','ঠ','ম','ন','অ',
    'ড','উ','ঢ','শ','ই','য','র'
]

dict = []

for w in words:
    for c in vclass:
        dict.append(f'{w}-{c}')



reader = Reader(['bn'], verbose = False, recog_network = 'bn_license_tps', model_storage_directory = "./models/models/EasyOCR/models",user_network_directory="./models/models/EasyOCR/user_network", download_enabled = False)

nums = set('০১২৩৪৫৬৭৮৯')

def extract_license_text(path, reader = reader):
    img = path
    if isinstance(path, str):
        img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
            
    
    result = reader.readtext(img, detail = False, paragraph = True)
    area = ""
    number = ""

    for c in "".join(result)[::-1]:
        if c == "-":
            if len(number) <= 4:
                number += "-"
            else:
                area += "-"
        elif c in nums:
            number += c
        else:
            area += c
    
    area = area[::-1]
    match = difflib.get_close_matches(area, dict, n = 1, cutoff = 0.5)

    if match:
        area = match[0]

    number = number[::-1]

    if number.find("-") == -1 and len(number) == 6:
        number = number[:2] + "-" + number[2:]
    
    return area.strip(), number.strip()



# Function to check image quality
def check_image_quality(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Measure brightness
    brightness = np.mean(gray)
    
    # Measure contrast
    contrast = np.std(gray)
    
    # Measure sharpness
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()

    return brightness, contrast, laplacian_var

# Adaptive preprocessing function
def preprocess_image(img):
    # Check image quality
    brightness, contrast, sharpness = check_image_quality(img)
    print(f"Image Quality - Brightness: {brightness}, Contrast: {contrast}, Sharpness: {sharpness}")
    
    # Skip preprocessing if the image is already good
    if brightness > 80 and contrast > 40 and sharpness > 100:
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # If brightness is too low or contrast is too low, enhance it
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    if brightness < 80 or contrast < 40:
        gray = cv2.normalize(gray, None, 0, 255, cv2.NORM_MINMAX)

    # Apply CLAHE if contrast is very low
    if contrast < 30:
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        gray = clahe.apply(gray)
    
    # Apply light Gaussian blur to denoise
    gray = cv2.GaussianBlur(gray, (3, 3), 0)

    # If the sharpness is very low, apply thresholding
    if sharpness < 50:
        _, gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    return gray

def load_image(path):
    print(f"Attempting to load image from path: {path}")  # Debugging
    img = cv2.imread(path)
    if img is None:
        print(f"load_image(): {path} not found or invalid")
    return img

# Function to display images
def show_image(img):
    plt.axis("off")
    if isinstance(img, str):
        img = cv2.imread(img)
    plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    plt.show()
    


def detect_license_plate(img):
    detection = model.predict(img, conf=0.5, verbose=False)
    if detection is None:
        print(f"detect_license_plate(): img is null")
        return
    return detection[0]


# Improved license plate text extraction pipeline
def detect_and_extract_lp_text(path, show_cropped_image=False):
    # Load image
    img = load_image(path)
    if img is None:
        return None

    # Detect license plate
    detection_result = detect_license_plate(img)
    bbox = detection_result.boxes.data.numpy()

    # Crop the detected license plate region
    xmin, ymin = bbox[0][:2].astype(int)
    xmax, ymax = bbox[0][2:4].astype(int)
    cropped_img = img[ymin:ymax, xmin:xmax]

    if cropped_img is None or cropped_img.size == 0:
        print("Cropped image is empty. Detection failed.")
        return None

    # Show cropped image if needed
    if show_cropped_image:
        show_image(cropped_img)

    # Preprocess cropped image adaptively
    preprocessed_img = preprocess_image(cropped_img)

    # Extract text using EasyOCR
    lp_text = extract_license_text(preprocessed_img)
    print(lp_text)
    return lp_text

