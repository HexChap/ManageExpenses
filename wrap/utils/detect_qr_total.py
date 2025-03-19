import io
from typing import BinaryIO
import numpy as np
from qreader import QReader
import cv2
import re

TOTAL_PATTERN = r"(\d+\.\d{2})"


def detect_qr_total(image: BinaryIO):
    qreader = QReader()

    # Get the image that contains the QR code
    img_buf = np.frombuffer(image.read(), np.uint8)
    image = cv2.cvtColor(cv2.imdecode(img_buf, 1), cv2.COLOR_BGR2RGB)

    # Use the detect_and_decode function to get the decoded QR data
    decoded_data = qreader.detect_and_decode(image=image)
    decoded_data = decoded_data[0] or "" if decoded_data else ""

    # Check if the decoded data contains a match for TOTAL_PATTERN
    match = re.search(TOTAL_PATTERN, decoded_data)

    # Return the matched total or an empty string if no match is found
    return match.group(1) if match else ""