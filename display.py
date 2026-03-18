#!/usr/bin/env python
# -*- coding: utf-8 -*-

HOST = "172.20.10.242"
PORT = 4223
UID = "24KJ"  # Change XYZ to the UID of your E-Paper 296x128 Bricklet

WIDTH = 296   # Columns
HEIGHT = 128  # Rows

from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_e_paper_296x128 import BrickletEPaper296x128
from PIL import Image, ImageDraw


def bool_list_from_pil_image(image, width=296, height=128, color=(0, 0, 0)):
    """Convert PIL image to matching color bool list."""
    image_data = image.load()
    pixels = []
    for row in range(height):
        for column in range(width):
            pixel = image_data[column, row]
            value = (pixel[0] == color[0]) and (pixel[1] == color[1]) and (pixel[2] == color[2])
            pixels.append(value)
    return pixels


def draw_middle_finger(width=296, height=128):
    """
    Draw a pixel-art middle finger centered on a white background.
    Returns a PIL Image in RGB mode with black lines and a red accent.
    """
    image = Image.new("RGB", (width, height), (0xFF, 0xFF, 0xFF))
    draw = ImageDraw.Draw(image)

    BLACK = (0, 0, 0)
    RED   = (0xFF, 0, 0)

    # --- Layout: center the hand horizontally, align to bottom ---
    cx = width // 2      # horizontal center
    base_y = height - 8  # bottom of the palm

    # Palm  (wide rectangle at the bottom)
    palm_w = 36
    palm_h = 28
    palm_x0 = cx - palm_w // 2
    palm_y0 = base_y - palm_h
    palm_x1 = cx + palm_w // 2
    palm_y1 = base_y
    draw.rectangle([palm_x0, palm_y0, palm_x1, palm_y1], fill=BLACK)

    # Four folded fingers (short stumps left + right of middle finger)
    # Left stump
    draw.rectangle([palm_x0, palm_y0 - 10, palm_x0 + 10, palm_y0], fill=BLACK)
    # Second-left stump
    draw.rectangle([palm_x0 + 12, palm_y0 - 8, palm_x0 + 22, palm_y0], fill=BLACK)
    # Right stump
    draw.rectangle([palm_x1 - 10, palm_y0 - 10, palm_x1, palm_y0], fill=BLACK)
    # Second-right stump
    draw.rectangle([palm_x1 - 22, palm_y0 - 8, palm_x1 - 12, palm_y0], fill=BLACK)

    # Middle finger  (tall rectangle, highlighted red)
    mf_w = 16
    mf_h = 55
    mf_x0 = cx - mf_w // 2
    mf_y0 = palm_y0 - mf_h
    mf_x1 = cx + mf_w // 2
    mf_y1 = palm_y0

    # Finger body in black outline, red fill
    draw.rectangle([mf_x0, mf_y0, mf_x1, mf_y1], fill=RED, outline=BLACK, width=2)

    # Fingernail  (small white rectangle near the top of the finger)
    nail_margin = 3
    nail_h = 12
    nail_x0 = mf_x0 + nail_margin
    nail_y0 = mf_y0 + nail_margin
    nail_x1 = mf_x1 - nail_margin
    nail_y1 = mf_y0 + nail_margin + nail_h
    draw.rectangle([nail_x0, nail_y0, nail_x1, nail_y1], fill=(0xFF, 0xFF, 0xFF), outline=BLACK)

    # Knuckle lines on the middle finger
    for offset in [20, 32]:
        y = mf_y0 + offset
        draw.line([(mf_x0 + 2, y), (mf_x1 - 2, y)], fill=BLACK, width=2)

    # Thumb (angled short rectangle on the left of the palm)
    thumb_pts = [
        (palm_x0 - 2,  palm_y0),
        (palm_x0 - 16, palm_y0 - 18),
        (palm_x0 - 6,  palm_y0 - 22),
        (palm_x0 + 8,  palm_y0 - 4),
    ]
    draw.polygon(thumb_pts, fill=BLACK)

    return image


if __name__ == "__main__":
    ipcon  = IPConnection()
    epaper = BrickletEPaper296x128(UID, ipcon)

    ipcon.connect(HOST, PORT)

    # Generate the middle-finger image
    image = draw_middle_finger(WIDTH, HEIGHT)

    # Optionally save a preview so you can check it without hardware
    image.save("middle_finger_preview.png")
    print("Preview saved as middle_finger_preview.png")

    # Write black/white layer
    pixels_bw = bool_list_from_pil_image(image, WIDTH, HEIGHT, (0xFF, 0xFF, 0xFF))
    epaper.write_black_white(0, 0, WIDTH - 1, HEIGHT - 1, pixels_bw)

    # Write red layer
    pixels_red = bool_list_from_pil_image(image, WIDTH, HEIGHT, (0xFF, 0, 0))
    epaper.write_color(0, 0, WIDTH - 1, HEIGHT - 1, pixels_red)

    # Flush to display
    epaper.draw()

    input("Press key to exit\n")
    ipcon.disconnect()