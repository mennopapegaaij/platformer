# infinite_level.py
# Een lichte "chunked" platform-generator voor grote/oneindige levels.
# Genereert alleen platforms voor zichtbare chunks en houdt een kleine cache.

import math
from platforms import Platform
from instellingen import SCHERM_BREEDTE


class InfinitePlatformProvider:
    """Genereert platform-chunks op aanvraag.

    - chunk_size: breedte van één chunk (pixels)
    - pattern_offsets: x-offsets binnen een chunk waar platforms komen
    - heights: herhalende hoogtes voor variatie
    - cache: houdt enkele chunks in het geheugen (niet alles)
    """

    def __init__(self, chunk_size=None, pattern_offsets=None, heights=None,
                 platform_w=120, platform_h=20, extra_offset=180, extra_w=100,
                 max_cache=9):
        self.chunk_size = chunk_size or SCHERM_BREEDTE
        self.pattern_offsets = pattern_offsets or [100, 300, 500, 700]
        self.heights = heights or [130, 160, 200, 130, 170, 150, 190, 160]
        self.platform_w = platform_w
        self.platform_h = platform_h
        self.extra_offset = extra_offset
        self.extra_w = extra_w
        self.cache = {}  # chunk_index -> [Platform, ...]
        self.max_cache = max_cache

    def generate_chunk(self, idx):
        """Maak de platforms voor één chunk (deterministisch)."""
        if idx in self.cache:
            return self.cache[idx]
        base_x = idx * self.chunk_size
        plats = []
        for j, offset in enumerate(self.pattern_offsets):
            x = base_x + offset
            # Kies hoogte met eenvoudige herhaling zodat het voorspelbaar blijft
            height = self.heights[(idx * len(self.pattern_offsets) + j) % len(self.heights)]
            plats.append(Platform(x, height, self.platform_w, self.platform_h))
            # Soms een hoger platform ernaast
            if j % 2 == 0:
                plats.append(Platform(x + self.extra_offset, height + 80, self.extra_w, self.platform_h))
        self.cache[idx] = plats
        return plats

    def ensure_chunks(self, center_x, screen_width):
        """Zorg dat de chunks rond de speler beschikbaar zijn."""
        left = int(math.floor((center_x - screen_width) / self.chunk_size)) - 1
        right = int(math.floor((center_x + 2 * screen_width) / self.chunk_size)) + 1
        for idx in range(left, right + 1):
            if idx not in self.cache:
                self.generate_chunk(idx)
        # Verwijder verafgelegen chunks zodat de cache klein blijft
        keys = sorted(list(self.cache.keys()))
        keep_min = left - 2
        keep_max = right + 2
        for k in keys:
            if k < keep_min or k > keep_max:
                del self.cache[k]

    def __iter__(self):
        """Itereer over alle platforms die momenteel in de cache zijn."""
        for idx in sorted(self.cache.keys()):
            for p in self.cache[idx]:
                yield p

    def __len__(self):
        return sum(len(v) for v in self.cache.values())
