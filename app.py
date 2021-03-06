import numpy as np
from flask import Flask, jsonify, render_template, request
from PIL import Image
import cv2
import pytesseract


import re

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'
custom_config = r'--oem 3 --psm 3'

app= Flask(__name__)


def preprocess_items(text):
    text_new = []

    for row in text:
        # if i==len(text)-1:
        # break
        if len(row) < 1:
            continue
        row = row.split(' ')
        l = [row[0], row[1]]
        for i in range(2, len(row)):

            res = re.match('[a-zA-z]', row[i])
            if res:

                l[1] += (' ' + row[i])
            elif re.match('[$0-9]', row[i]):
                l.append(row[i])

        text_new.append(l)

    return text_new


def for_items(img):
    item_crop = img.crop((0, 380, 1000, 740))
    text = pytesseract.image_to_string(item_crop)
    rows = text.split('\n')
    text_n = preprocess_items(rows)
    info_dict = {}
    items = [text for text in text_n if len(text) == 5]
    info_dict['items'] = items
    info_dict['Sub_Total'] = text_n[-1][-1]

    return info_dict

# You may need to convert the color.
def cnvrt_cv2topil(img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    im_pil = Image.fromarray(img)
    return im_pil

# For reversing the operation:
def cnvrt_pil2cv2(im_pil):
    im_np = np.asarray(im_pil)
    img = cv2.cvtColor(im_np, cv2.COLOR_RGB2BGR)
    return img

def preprocess_pay(text):
    text=[t for t in text.split('\n') if len(t)>0]
    payment_info={t.split(':')[0].replace('&', 'Number'):t.split(':')[1]  for t in text if len(t.split(':')[1])>0 }
    return payment_info


def for_payment(img):
    pay_crop = img.crop((250, 700, 500, 760))
    im_cv = cnvrt_pil2cv2(pay_crop)
    im_cv = cv2.resize(im_cv, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC)
    im_pil = cnvrt_cv2topil(im_cv)
    text = pytesseract.image_to_string(im_pil, config=custom_config)
    pay_dict = preprocess_pay(text)

    return pay_dict









@app.route('/')
def home():
    return  render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    name = request.form['image']
    #img = Image.open("templates/"+name)
    img = Image.open(name)
    info_dict = for_items(img)
    pay_dict = for_payment(img)
    info_dict['Payment information'] = pay_dict



    return render_template('index.html', ** {'prediction_text' :info_dict})


if __name__=="__main__":
    app.run(port=5000, debug=True)
