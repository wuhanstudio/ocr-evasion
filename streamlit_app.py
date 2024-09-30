import cv2
import numpy as np
from PIL import Image

import tempfile
import streamlit as st

st.title('WeChat OCR Filter')

original = cv2.imread("test.jpg")

with st.container():
    f = st.file_uploader("Choose a file")

    if f is not None:
        tfile = tempfile.NamedTemporaryFile(delete=True)
        tfile.write(f.read())

        img = Image.open(tfile).convert('RGB')
        original = np.array(img)

    text_r = st.slider("Select R Channel for the text", 0, 255, value = 200)
    text_g = st.slider("Select G Channel for the text", 0, 255, value = 100)
    text_b = st.slider("Select B Channel for the text", 0, 255, value = 200)

    blur = cv2.GaussianBlur(original, (5,5), 0)

    gray = 0.299 * blur[:, :, 0] + 0.587 * blur[:, :, 1] + 0.114  * blur[:, :, 2]
    gray = gray.astype(np.uint8)

    ret, th = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    output = np.zeros(original.shape)

    # Black: Text
    output[:, :, 0][th==0] = int(text_r)
    output[:, :, 1][th==0] = int(text_g)
    output[:, :, 2][th==0] = int(text_b)

    lumi = 0.299 * int(text_r) + 0.587 * int(text_g) + 0.114 * int(text_b)

    # White: Background
    if lumi > 150:
        output[:, :, 1][th==255] = 255   # max: 149.68
        if lumi - 150 > 77:
            output[:, :, 0][th==255] = 255   # max: 76.25
            output[:, :, 2][th==255] = (lumi - 149.68 - 76.25) / 0.114   # max: 29.07
        else:
            output[:, :, 0][th==255] = (lumi - 150) / 0.299   # max: 76.25
            output[:, :, 2][th==255] = 0 # max:  29.07
    else:
        output[:, :, 0][th==255] = 0 # max:  76.25
        output[:, :, 1][th==255] = lumi / 0.587 # max: 149.68
        output[:, :, 2][th==255] = 0 # max:  29.07

    gray = 0.299 * output[:, :, 0] + 0.587 * output[:, :, 1] + 0.114  * output[:, :, 2]
    gray = gray.astype(np.uint8)

    left_column, middle_column, right_column = st.columns(3)

    left_column.image(original / 255.0, caption = "Input Image")
    middle_column.image(gray / 255.0, caption = "OCR Image")
    right_column.image(output / 255.0 , caption = "output Image")
