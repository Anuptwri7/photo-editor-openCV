# server-side processing using OpenCV (sharpen, hdr approximation)
import cv2
import numpy as np
from PIL import Image
import io
from PIL import Image
import io
import numpy as np
import cv2

from PIL import Image
import io
import os
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect


def read_bytes_to_cv(img_bytes):
    nparr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img


def cv_to_png_bytes(img):
    success, buf = cv2.imencode('.png', img)
    return buf.tobytes() if success else None

def sharpen(img_bytes):
    img = read_bytes_to_cv(img_bytes)
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    sharp = cv2.filter2D(img, -1, kernel)
    # Force same size
    sharp = cv2.resize(sharp, (img.shape[1], img.shape[0]))

    return cv_to_png_bytes(sharp)


def hdr_approximate(img_bytes):
    img = read_bytes_to_cv(img_bytes)
    # Detail enhance for HDR effect
    hdr = cv2.detailEnhance(img, sigma_s=12, sigma_r=0.15)
    return cv_to_png_bytes(hdr)


def oil_painting(img_bytes):
    img = read_bytes_to_cv(img_bytes)
    oil = cv2.bilateralFilter(img, 9, 75, 75)
    oil = cv2.bilateralFilter(oil, 9, 75, 75)

    return cv_to_png_bytes(oil)

def blur(img_bytes, ksize=5):

    img = read_bytes_to_cv(img_bytes)

    if ksize % 2 == 0:
        ksize += 1
    blurred = cv2.GaussianBlur(img, (ksize, ksize), 0)
    return cv_to_png_bytes(blurred)

def sepia(img_bytes):

    img = read_bytes_to_cv(img_bytes)

    sepia_filter = np.array([[0.272, 0.534, 0.131],
                             [0.349, 0.686, 0.168],
                             [0.393, 0.769, 0.189]])
    sepia_img = cv2.transform(img, sepia_filter)

    sepia_img = np.clip(sepia_img, 0, 255).astype(np.uint8)
    return cv_to_png_bytes(sepia_img)

def grey_hd(img_bytes):
    img = read_bytes_to_cv(img_bytes)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)
    color = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    return cv_to_png_bytes(color)

def fullhd_quality(img_bytes, detail_factor=0.05, sharpen_factor=0.3, contrast_factor=1.05, saturation_factor=1.03):

    img = read_bytes_to_cv(img_bytes)

    enhanced = cv2.detailEnhance(img, sigma_s=10, sigma_r=detail_factor)

    # 2. Gentle sharpening
    kernel = np.array([[0, -sharpen_factor, 0],
                       [-sharpen_factor, 1 + 4*sharpen_factor, -sharpen_factor],
                       [0, -sharpen_factor, 0]])
    sharpened = cv2.filter2D(enhanced, -1, kernel)

    # 3. Mild contrast adjustment using LAB light channel
    lab = cv2.cvtColor(sharpened, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    # Scale lightness slightly
    l = np.clip(l * contrast_factor, 0, 255).astype(np.uint8)
    lab_merged = cv2.merge((l, a, b))
    final = cv2.cvtColor(lab_merged, cv2.COLOR_LAB2BGR)

    # 4. Mild saturation boost
    hsv = cv2.cvtColor(final, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[:, :, 1] = np.clip(hsv[:, :, 1] * saturation_factor, 0, 255)
    final = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)

    return cv_to_png_bytes(final)



def add_frame(img_bytes, frame_path=None):
    if frame_path is None:
        frame_path = os.path.join(settings.BASE_DIR, 'photo_editor_sample', 'static', 'editor', 'frames', 'frame1.png')

    # Load original image
    img = Image.open(io.BytesIO(img_bytes)).convert("RGBA")
    width, height = img.size

    # Load frame image
    frame = Image.open(frame_path).convert("RGBA")
    # Use new Pillow resampling
    frame = frame.resize((width, height), Image.Resampling.LANCZOS)

    # Overlay frame
    combined = Image.alpha_composite(img, frame)

    # Convert back to bytes
    out_bytes = io.BytesIO()
    combined.convert("RGB").save(out_bytes, format="PNG")
    return out_bytes.getvalue()
def add_frame2(img_bytes, frame_path=None):
    if frame_path is None:
        frame_path = os.path.join(settings.BASE_DIR, 'photo_editor_sample', 'static', 'editor', 'frames', 'frame2.png')

    # Load original image
    img = Image.open(io.BytesIO(img_bytes)).convert("RGBA")
    width, height = img.size

    # Load frame image
    frame = Image.open(frame_path).convert("RGBA")
    # Use new Pillow resampling
    frame = frame.resize((width, height), Image.Resampling.LANCZOS)

    # Overlay frame
    combined = Image.alpha_composite(img, frame)

    # Convert back to bytes
    out_bytes = io.BytesIO()
    combined.convert("RGB").save(out_bytes, format="PNG")
    return out_bytes.getvalue()


def apply_server_filter(img_bytes, name, **kwargs):
    if name == 'sharpen':
        return sharpen(img_bytes)
    if name == 'hdr':
        return hdr_approximate(img_bytes)
    if name == 'oil':
        return oil_painting(img_bytes)
    if name == 'greyhd':
        print("Applying greyhd filter")
        return grey_hd(img_bytes)
    if name == 'sepia':
        return sepia(img_bytes)
    if name == 'fullhd':
        return fullhd_quality(img_bytes)
    if name == 'frame1':
        frame_path = kwargs.get('frame_path', 'static/editor/frames/frame1.png')
        return add_frame(img_bytes, frame_path)
    if name == 'frame2':
        frame_path = kwargs.get('frame_path', 'static/editor/frames/frame2.png')
        return add_frame2(img_bytes, frame_path)
    if name == 'blur':
        # optionally accept kernel size from kwargs
        ksize = kwargs.get('ksize', 5)
        return blur(img_bytes, ksize)

    return None
