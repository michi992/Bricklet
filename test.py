#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ============================================================
#  GOLLUM MIT MITTELFINGER  –  E-Paper 296x128
#  "We hates it. We shows it. Nassty displayss!"
# ============================================================

HOST = "172.20.10.242"
PORT = 4223
UID  = "24KJ"

WIDTH  = 296
HEIGHT = 128

from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_e_paper_296x128 import BrickletEPaper296x128
from PIL import Image, ImageDraw, ImageFont


def draw_gollum_mittelfinger(width=296, height=128):
    img  = Image.new("RGB", (width, height), (0xFF, 0xFF, 0xFF))
    draw = ImageDraw.Draw(img)

    BLACK = (0, 0, 0)
    RED   = (0xFF, 0, 0)

    cx_body = 80
    base_y  = height - 6

    # Beine
    draw.rectangle([cx_body - 18, base_y - 22, cx_body - 10, base_y], fill=BLACK)
    draw.rectangle([cx_body +  8, base_y - 22, cx_body + 16, base_y], fill=BLACK)

    # Füße
    draw.ellipse([cx_body - 22, base_y - 8,  cx_body - 4,  base_y + 4], fill=BLACK)
    draw.ellipse([cx_body +  4, base_y - 8,  cx_body + 22, base_y + 4], fill=BLACK)

    # Torso
    draw.rectangle([cx_body - 16, base_y - 50, cx_body + 14, base_y - 22], fill=BLACK)

    # Hals
    draw.rectangle([cx_body - 5, base_y - 62, cx_body + 5, base_y - 50], fill=BLACK)

    # Kopf
    draw.ellipse([cx_body - 22, base_y - 92, cx_body + 22, base_y - 58], fill=BLACK)

    # Augen – rot
    draw.ellipse([cx_body - 16, base_y - 84, cx_body - 6,  base_y - 74], fill=RED, outline=BLACK)
    draw.ellipse([cx_body +  4, base_y - 84, cx_body + 14, base_y - 74], fill=RED, outline=BLACK)
    draw.ellipse([cx_body - 13, base_y - 81, cx_body - 9,  base_y - 77], fill=BLACK)
    draw.ellipse([cx_body +  7, base_y - 81, cx_body + 11, base_y - 77], fill=BLACK)

    # Mund
    draw.arc([cx_body - 10, base_y - 72, cx_body + 8, base_y - 62], start=10, end=170, fill=BLACK, width=2)
    draw.rectangle([cx_body - 5, base_y - 70, cx_body - 2, base_y - 66], fill=(0xFF, 0xFF, 0xFF))
    draw.rectangle([cx_body + 1, base_y - 70, cx_body + 4, base_y - 66], fill=(0xFF, 0xFF, 0xFF))

    # Ohren
    draw.polygon([(cx_body-22, base_y-80), (cx_body-34, base_y-95), (cx_body-20, base_y-70)], fill=BLACK)
    draw.polygon([(cx_body+20, base_y-80), (cx_body+32, base_y-95), (cx_body+18, base_y-70)], fill=BLACK)

    # Linker Arm + Klaue
    draw.polygon([(cx_body-14, base_y-48), (cx_body-30, base_y-30), (cx_body-24, base_y-26), (cx_body-10, base_y-44)], fill=BLACK)
    draw.ellipse([cx_body-36, base_y-32, cx_body-20, base_y-18], fill=BLACK)

    # Rechter Arm
    draw.polygon([
        (cx_body+12, base_y-46),
        (cx_body+42, base_y-60),
        (cx_body+44, base_y-54),
        (cx_body+14, base_y-40),
    ], fill=BLACK)

    # Hand-Basis
    hx = cx_body + 52
    hy = base_y - 68
    draw.rectangle([hx - 14, hy, hx + 14, hy + 20], fill=BLACK)

    # Vier eingeklappte Finger
    draw.rectangle([hx - 14, hy - 8, hx -  6, hy], fill=BLACK)
    draw.rectangle([hx -  5, hy - 6, hx +  2, hy], fill=BLACK)
    draw.rectangle([hx +  3, hy - 6, hx + 10, hy], fill=BLACK)
    draw.rectangle([hx +  8, hy - 8, hx + 14, hy], fill=BLACK)

    # Mittelfinger – rot & aufrecht
    mf_x0, mf_y0 = hx - 6, hy - 40
    mf_x1, mf_y1 = hx + 6, hy
    draw.rectangle([mf_x0, mf_y0, mf_x1, mf_y1], fill=RED, outline=BLACK, width=2)
    draw.rectangle([mf_x0+2, mf_y0+2, mf_x1-2, mf_y0+10], fill=(0xFF, 0xFF, 0xFF), outline=BLACK)
    for off in [15, 24]:
        draw.line([(mf_x0+2, mf_y0+off), (mf_x1-2, mf_y0+off)], fill=BLACK, width=2)

    # Daumen
    draw.polygon([(hx-14, hy+12), (hx-26, hy+2), (hx-20, hy-4), (hx-10, hy+8)], fill=BLACK)

    # Text
    try:
        font_big   = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 10)
    except Exception:
        font_big = font_small = ImageFont.load_default()

    draw.text((165,  8), "We hates you.",    font=font_big,   fill=BLACK)
    draw.text((165, 28), "We shows you,",    font=font_big,   fill=BLACK)
    draw.text((165, 48), "nassty thing!",    font=font_big,   fill=RED)
    draw.text((165, 72), "- Gollum",         font=font_small, fill=BLACK)

    draw.line([(155, 0), (155, height)], fill=BLACK, width=2)

    return img


def bool_list_from_pil_image(image, width, height, color):
    image_data = image.load()
    pixels = []
    for row in range(height):
        for column in range(width):
            pixel = image_data[column, row]
            pixels.append(pixel[0] == color[0] and pixel[1] == color[1] and pixel[2] == color[2])
    return pixels


if __name__ == "__main__":
    ipcon  = IPConnection()
    epaper = BrickletEPaper296x128(UID, ipcon)
    ipcon.connect(HOST, PORT)

    print("🖼  Zeichne Gollum mit Mittelfinger...")
    image = draw_gollum_mittelfinger(WIDTH, HEIGHT)
    image.save("gollum_mittelfinger_preview.png")
    print("   Vorschau: gollum_mittelfinger_preview.png")

    pixels_bw  = bool_list_from_pil_image(image, WIDTH, HEIGHT, (0xFF, 0xFF, 0xFF))
    pixels_red = bool_list_from_pil_image(image, WIDTH, HEIGHT, (0xFF, 0, 0))
    epaper.write_black_white(0, 0, WIDTH-1, HEIGHT-1, pixels_bw)
    epaper.write_color(      0, 0, WIDTH-1, HEIGHT-1, pixels_red)
    epaper.draw()
    print("✅ Display aktualisiert.")

    input("\nDrücke Enter zum Beenden\n")
    ipcon.disconnect()