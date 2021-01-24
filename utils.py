import cv2
import random
import numpy as np


def xywh2xyxy(box):
    # cx,cy,w,h -> x1,y1,x2,y2
    x, y, w, h = box
    x1 = x - w // 2
    y1 = y - h // 2
    x2 = x + w // 2
    y2 = y + h // 2
    return x1, y1, x2, y2

def xyxy2xywh(box):
    # x1,y1,x2,y2 -> cx,cy,w,h
    x1, y1, x2, y2 = box
    x = (x1 + x2) // 2
    y = (y1 + y2) // 2
    w = x2 - x1
    h = y2 - y1
    return x, y, w, h

def ltwh2xyxy(box):
    # x1,y1,w,h -> x1,y1,x2,y2
    x1, y1, w, h = box
    x2 = x1 + w
    y2 = y1 + h
    return x1, y1, x2, y2

def xyxy2ltwh(box):
    # x1,y1,x2,y2 -> x1,y1,w,h 
    x1, y1, x2, y2 = box
    w = x2 - x1
    h = y2 - y1
    return x1, y1, w, h

def overlay_transparent(background_img, img_to_overlay_t, x, y, overlay_size=None):
    # https://gist.github.com/clungzta/b4bbb3e2aa0490b0cfcbc042184b0b4e
    bg_img = background_img.copy()
    if overlay_size is not None:
        img_to_overlay_t = cv2.resize(img_to_overlay_t.copy(), overlay_size, interpolation=cv2.INTER_CUBIC)
    b, g, r, a = cv2.split(img_to_overlay_t)
    overlay_color = cv2.merge((b, g, r))
    mask = cv2.medianBlur(a, 3)
    # mask = a
    h, w, _ = overlay_color.shape
    roi = bg_img[y:y + h, x:x + w]
    img1_bg = cv2.bitwise_and(roi.copy(), roi.copy(), mask=cv2.bitwise_not(mask))
    img2_fg = cv2.bitwise_and(overlay_color, overlay_color, mask=mask)
    bg_img[y:y + h, x:x + w] = cv2.add(img1_bg, img2_fg)
    return bg_img

def plot_one_box(x, img, color=None, label=None, line_thickness=None):
    # plot a bbox on the image
    tl = line_thickness or round(0.002 * (img.shape[0] + img.shape[1]) / 2) + 1
    color = color or [random.randint(0, 255) for _ in range(3)]
    c1, c2 = (int(x[0]), int(x[1])), (int(x[2]), int(x[3]))
    cv2.rectangle(img, c1, c2, color, thickness=tl, lineType=cv2.LINE_AA)
    if label:
        plot_text(x, img, color=color, text=label, line_thickness=tl)
        
def plot_text(x, img, color=None, text=None, line_thickness=None):
    # plot text on the image
    tl = line_thickness or round(0.002 * (img.shape[0] + img.shape[1]) / 2) + 1
    color = color or [random.randint(0, 255) for _ in range(3)]
    c1 = (int(x[0]), int(x[1]))
    for line in text.split('\n'):
        tf = max(tl - 1, 1)
        t_size = cv2.getTextSize(line, 0, fontScale=tl / 3, thickness=tf)[0]
        c2 = (c1[0] + t_size[0], c1[1] - t_size[1] - 3)
        cv2.rectangle(img, c1, c2, color, -1, cv2.LINE_AA)
        cv2.putText(img, line, (c1[0], c1[1] - 2), 0, tl / 3, [225, 255, 255], thickness=tf, lineType=cv2.LINE_AA)
        c1 = (c1[0], c2[1])
            
def plot_cross(x, img, color=None, size=None, line_thickness=None):
    # draw a cross on the image
    tl = line_thickness or round(0.002 * (img.shape[0] + img.shape[1]) / 2) + 1
    color = color or [random.randint(0, 255) for _ in range(3)]
    size = size or round(0.03 * (img.shape[0] + img.shape[1]) / 2) + 1
    
    x1 = int(x[0]) - size // 2
    y1 = int(x[1]) - size // 2
    x2 = int(x[0]) + size // 2
    y2 = int(x[1]) + size // 2
    cv2.line(img, (x1, y1), (x2, y2), color, thickness=tl, lineType=cv2.LINE_AA)
    x1 = int(x[0]) + size // 2
    y1 = int(x[1]) - size // 2
    x2 = int(x[0]) - size // 2
    y2 = int(x[1]) + size // 2
    cv2.line(img, (x1, y1), (x2, y2), color, thickness=tl, lineType=cv2.LINE_AA)
    