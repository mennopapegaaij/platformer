# achtergrond.py
# Hier staan de achtergronden voor elk level.
# Elke level heeft een eigen sfeer!

import arcade


def teken_achtergrond(niveau, breedte, hoogte):
    """
    Teken de achtergrond voor het gegeven level.
    niveau = 1 t/m 5
    breedte en hoogte = de grootte van het scherm
    """

    if niveau == 1:
        _level1_beginners_wereld(breedte, hoogte)
    elif niveau == 2:
        _level2_het_bos(breedte, hoogte)
    elif niveau == 3:
        _level3_de_bergen(breedte, hoogte)
    elif niveau == 4:
        _level4_het_kasteel(breedte, hoogte)
    elif niveau == 5:
        _level5_de_eindbaas(breedte, hoogte)


# =============================================
# LEVEL 1: De Beginners Wereld
# Fijne zonnige dag, helder blauw
# =============================================
def _level1_beginners_wereld(w, h):
    # Lucht
    arcade.draw_lrbt_rectangle_filled(0, w, 0, h, arcade.color.SKY_BLUE)

    # Groene heuvels op de achtergrond
    arcade.draw_ellipse_filled(100, 20, 300, 120, (80, 160, 60))
    arcade.draw_ellipse_filled(400, 10, 350, 100, (70, 150, 50))
    arcade.draw_ellipse_filled(700, 20, 280, 110, (85, 165, 65))

    # Zon (geel met een oranje rand)
    arcade.draw_circle_filled(w - 90, h - 70, 50, arcade.color.YELLOW)
    arcade.draw_circle_outline(w - 90, h - 70, 50, arcade.color.ORANGE, 4)

    # Zonnestralen
    for hoek in range(0, 360, 45):
        import math
        rad = math.radians(hoek)
        x1 = (w - 90) + 58 * math.cos(rad)
        y1 = (h - 70) + 58 * math.sin(rad)
        x2 = (w - 90) + 78 * math.cos(rad)
        y2 = (h - 70) + 78 * math.sin(rad)
        arcade.draw_line(x1, y1, x2, y2, arcade.color.ORANGE, 3)

    # Wolken
    _wolk(130, h - 80, 1.0)
    _wolk(370, h - 110, 1.2)
    _wolk(600, h - 75, 0.9)


# =============================================
# LEVEL 2: Het Bos
# Donkerder, veel bomen op de achtergrond
# =============================================
def _level2_het_bos(w, h):
    # Lucht (groenig blauw)
    arcade.draw_lrbt_rectangle_filled(0, w, 0, h, (130, 190, 210))

    # Verre bomen (lichte, vage silhouetten)
    for i in range(10):
        x = i * 85 + 30
        _boom(x, 60, 0.7, (100, 140, 80))

    # Dichterbij: donkerdere bomen
    for i in range(6):
        x = i * 140 + 10
        _boom(x, 80, 1.0, (60, 110, 50))
    for i in range(5):
        x = i * 170 + 90
        _boom(x, 90, 1.1, (50, 95, 40))

    # Wat paddestoelen onderaan
    _paddestoel(200, 40)
    _paddestoel(500, 40)
    _paddestoel(720, 40)


# =============================================
# LEVEL 3: De Bergen
# Paarse lucht, bergen in de verte
# =============================================
def _level3_de_bergen(w, h):
    # Lucht (lichtpaars/blauw)
    arcade.draw_lrbt_rectangle_filled(0, w, 0, h, (170, 200, 230))

    # Verre bergen (lichtgrijs)
    _berg(0, 0, 300, 220, (180, 180, 195))
    _berg(220, 0, 280, 260, (175, 175, 190))
    _berg(430, 0, 300, 200, (185, 185, 200))
    _berg(640, 0, 280, 240, (180, 180, 195))

    # Sneeuwtoppen
    _sneeuwtop(150, 220, 80)
    _sneeuwtop(360, 260, 70)
    _sneeuwtop(580, 200, 75)
    _sneeuwtop(780, 240, 65)

    # Wat wolken
    _wolk(80, h - 90, 0.8)
    _wolk(450, h - 70, 1.1)


# =============================================
# LEVEL 4: Het Kasteel
# Donkere lucht, maan, kasteeltorens
# =============================================
def _level4_het_kasteel(w, h):
    # Donkere nachtlucht
    arcade.draw_lrbt_rectangle_filled(0, w, 0, h, (25, 30, 60))

    # Sterren
    import random
    random.seed(42)  # Altijd dezelfde sterren
    for _ in range(60):
        sx = random.randint(0, w)
        sy = random.randint(h // 3, h)
        arcade.draw_circle_filled(sx, sy, random.choice([1, 1, 2]), arcade.color.WHITE)

    # Maan
    arcade.draw_circle_filled(100, h - 80, 45, (240, 240, 200))
    arcade.draw_circle_filled(120, h - 95, 35, (25, 30, 60))  # Gebeten stukje

    # Kasteelsilhouetten op de achtergrond
    _kasteel_silhouet(0, 40, (40, 45, 70))
    _kasteel_silhouet(350, 30, (35, 40, 65))
    _kasteel_silhouet(600, 35, (40, 45, 70))


# =============================================
# LEVEL 5: De Eindbaas
# Rood/oranje lucht, vuur, dramatisch!
# =============================================
def _level5_de_eindbaas(w, h):
    # Donkerrode lucht (verloop: donker boven, oranje onder)
    arcade.draw_lrbt_rectangle_filled(0, w, h // 2, h, (40, 10, 10))
    arcade.draw_lrbt_rectangle_filled(0, w, 0, h // 2, (80, 20, 0))

    # Gloeiende horizon
    arcade.draw_lrbt_rectangle_filled(0, w, 30, 60, (200, 80, 0))
    arcade.draw_lrbt_rectangle_filled(0, w, 55, 70, (220, 120, 0))

    # Vuurpijlers
    for i in range(8):
        x = i * 115 + 30
        _vuurpijler(x, 40)

    # Donkere rotssilhouetten
    arcade.draw_triangle_filled(0, 0, 80, 0, 40, 70, (20, 10, 10))
    arcade.draw_triangle_filled(150, 0, 270, 0, 210, 90, (20, 10, 10))
    arcade.draw_triangle_filled(450, 0, 570, 0, 510, 80, (20, 10, 10))
    arcade.draw_triangle_filled(650, 0, 800, 0, 725, 100, (20, 10, 10))

    # Omineuze wolken
    arcade.draw_ellipse_filled(200, h - 60, 200, 50, (60, 15, 15))
    arcade.draw_ellipse_filled(600, h - 80, 250, 60, (60, 15, 15))
    arcade.draw_ellipse_filled(400, h - 40, 180, 40, (70, 20, 10))


# =============================================
# Hulpfuncties om dingen te tekenen
# =============================================

def _wolk(x, y, schaal):
    """Teken een wolk op positie (x, y) met de gegeven grootte."""
    kleur = (240, 240, 255)
    arcade.draw_ellipse_filled(x, y, 80 * schaal, 40 * schaal, kleur)
    arcade.draw_ellipse_filled(x - 30 * schaal, y - 5 * schaal, 60 * schaal, 35 * schaal, kleur)
    arcade.draw_ellipse_filled(x + 30 * schaal, y - 5 * schaal, 60 * schaal, 35 * schaal, kleur)


def _boom(x, y, schaal, kleur):
    """Teken een spar (driehoekige boom) op positie (x, y)."""
    # Stam
    arcade.draw_lrbt_rectangle_filled(x - 5 * schaal, x + 5 * schaal,
                                       y, y + 20 * schaal, (100, 70, 40))
    # Drie lagen driehoeken (steeds kleiner naar boven)
    arcade.draw_triangle_filled(x - 35 * schaal, y + 20 * schaal,
                                 x + 35 * schaal, y + 20 * schaal,
                                 x, y + 70 * schaal, kleur)
    arcade.draw_triangle_filled(x - 28 * schaal, y + 50 * schaal,
                                 x + 28 * schaal, y + 50 * schaal,
                                 x, y + 95 * schaal, kleur)
    arcade.draw_triangle_filled(x - 20 * schaal, y + 75 * schaal,
                                 x + 20 * schaal, y + 75 * schaal,
                                 x, y + 115 * schaal, kleur)


def _paddestoel(x, y):
    """Teken een schattige paddestoel."""
    # Stelen
    arcade.draw_lrbt_rectangle_filled(x - 7, x + 7, y, y + 20, (220, 200, 170))
    # Hoed (rood met witte stippen)
    arcade.draw_ellipse_filled(x, y + 25, 36, 24, arcade.color.RED)
    arcade.draw_ellipse_filled(x - 8, y + 28, 8, 6, arcade.color.WHITE)
    arcade.draw_ellipse_filled(x + 8, y + 27, 7, 5, arcade.color.WHITE)
    arcade.draw_ellipse_filled(x, y + 32, 6, 5, arcade.color.WHITE)


def _berg(x, y, breedte, hoogte, kleur):
    """Teken een bergsilhouet."""
    arcade.draw_triangle_filled(x, y, x + breedte, y, x + breedte // 2, y + hoogte, kleur)


def _sneeuwtop(x, y, breedte):
    """Teken een witte sneeuwkap op een bergtop."""
    arcade.draw_triangle_filled(x - breedte // 2, y - 30,
                                 x + breedte // 2, y - 30,
                                 x, y, (240, 240, 255))


def _kasteel_silhouet(x, y, kleur):
    """Teken een eenvoudig kasteelsilhouet."""
    # Muur
    arcade.draw_lrbt_rectangle_filled(x, x + 300, y, y + 80, kleur)
    # Torens
    arcade.draw_lrbt_rectangle_filled(x, x + 60, y, y + 130, kleur)
    arcade.draw_lrbt_rectangle_filled(x + 240, x + 300, y, y + 120, kleur)
    arcade.draw_lrbt_rectangle_filled(x + 120, x + 180, y, y + 110, kleur)
    # Kantelen op de torens
    for tx in [x, x + 20, x + 240, x + 260, x + 120, x + 140]:
        arcade.draw_lrbt_rectangle_filled(tx, tx + 15, y + 130, y + 150, kleur)


def _vuurpijler(x, y):
    """Teken een vuurpijler."""
    # Oranje vlam
    arcade.draw_triangle_filled(x - 12, y, x + 12, y, x, y + 50, (220, 100, 0))
    # Gele kern
    arcade.draw_triangle_filled(x - 7, y, x + 7, y, x, y + 30, (255, 200, 0))
