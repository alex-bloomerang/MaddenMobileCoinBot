import logging
import math

import cv2
import pytesseract

from databaseController import update_price

log = logging.getLogger(__name__)


def extract_pricing_data(response, db, modifier):
    with open("screenshot.png", "wb") as f:
        f.write(response.content)
    return parse_ocr(process_image(), db, modifier)


def crop_img(img, left_width_scale=1.0, right_width_scale=1.0, top_height_scale=1.0, bottom_height_scale=1.0):
    center_x, center_y = img.shape[1] / 2, img.shape[0] / 2
    right_width_scaled = img.shape[1] * right_width_scale
    left_width_scaled = img.shape[1] * left_width_scale
    top_height_scaled = img.shape[0] * top_height_scale
    bottom_height_scaled = img.shape[0] * bottom_height_scale
    left_x = center_x - left_width_scaled / 2
    right_x = center_x + right_width_scaled / 2
    top_y, bottom_y = center_y - top_height_scaled / 2, center_y + bottom_height_scaled / 2
    img_cropped = img[int(top_y):int(bottom_y), int(left_x):int(right_x)]
    return img_cropped


def process_image():
    # Grayscale, Gaussian blur, Otsu's threshold
    image = cv2.imread('screenshot.png')
    image = crop_img(image, 0.48, 0.3, 0.74, 0.85)
    image = cv2.resize(image, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    return pytesseract.image_to_string(thresh, lang='eng', config='--psm 6')


def parse_ocr(message, db, modifier):
    message = message[:-6]
    added_players = []
    even_line = True
    for line in message.split("\n"):
        if (line != "") and ("Expired" not in line):
            if even_line:
                surname = []
                first_inital = line[:1]
                for char in line[1:].split(" ")[0]:
                    if char.isalpha():
                        surname.append(char)
                even_line = False
            else:
                rating = line[:2]
                price = []
                for char in line[2:]:
                    if char.isnumeric():
                        price.append(char)
                added_players.append(
                    update_price(int(rating), first_inital + " " + "".join(surname),
                                 math.ceil(int(''.join(price)) / modifier), db))
                even_line = True
    return "\n".join(added_players)
