"""
logika.py - Otak permainan Block Puzzle (tanpa tampilan)
========================================================
File ini hanya berisi aturan game, jadi bisa dites tanpa layar.
Tampilan (Kivy) ada di main.py.

Konsep PBO:
  - class Bentuk : satu potongan blok (daftar kotak + warna)
  - class Papan  : papan 8x8 (cek muat, taruh, hapus baris/kolom)
"""

import random

GRID = 8  # papan 8 x 8

WARNA = ["#e74c3c", "#3498db", "#2ecc71", "#f1c40f", "#9b59b6", "#e67e22", "#1abc9c"]

# Setiap bentuk = daftar (baris, kolom) kotak yang terisi
DAFTAR_BENTUK = [
    [(0, 0)],                                   # 1x1
    [(0, 0), (0, 1)],                           # 1x2
    [(0, 0), (1, 0)],                           # 2x1
    [(0, 0), (0, 1), (0, 2)],                   # 1x3
    [(0, 0), (1, 0), (2, 0)],                   # 3x1
    [(0, 0), (0, 1), (0, 2), (0, 3)],           # 1x4
    [(0, 0), (1, 0), (2, 0), (3, 0)],           # 4x1
    [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4)],   # 1x5
    [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0)],   # 5x1
    [(0, 0), (0, 1), (1, 0), (1, 1)],           # kotak 2x2
    [(r, c) for r in range(3) for c in range(3)],  # kotak 3x3
    [(0, 0), (1, 0), (1, 1)],                   # L kecil (4 rotasi)
    [(0, 0), (0, 1), (1, 0)],
    [(0, 0), (0, 1), (1, 1)],
    [(0, 1), (1, 0), (1, 1)],
    [(0, 0), (1, 0), (2, 0), (2, 1), (2, 2)],   # L besar
    [(0, 0), (0, 1), (0, 2), (1, 0), (2, 0)],
    [(0, 0), (0, 1), (0, 2), (1, 1)],           # T
    [(0, 1), (0, 2), (1, 0), (1, 1)],           # S
    [(0, 0), (0, 1), (1, 1), (1, 2)],           # Z
]


class Bentuk:
    """Satu potongan blok."""

    def __init__(self, kotak, warna):
        self.kotak = kotak
        self.warna = warna
        self.tinggi = max(r for r, c in kotak) + 1
        self.lebar = max(c for r, c in kotak) + 1


def bentuk_acak():
    """Buat satu Bentuk dengan model dan warna acak."""
    return Bentuk(random.choice(DAFTAR_BENTUK), random.choice(WARNA))


class Papan:
    """Papan permainan 8x8. Sel berisi None (kosong) atau kode warna."""

    def __init__(self):
        self.reset()

    def reset(self):
        self.sel = [[None] * GRID for _ in range(GRID)]

    def bisa_taruh(self, bentuk, baris, kolom):
        """True jika bentuk muat jika kotak kiri-atasnya di (baris, kolom)."""
        for r, c in bentuk.kotak:
            rr, cc = baris + r, kolom + c
            if not (0 <= rr < GRID and 0 <= cc < GRID):
                return False          # keluar papan
            if self.sel[rr][cc] is not None:
                return False          # sudah terisi
        return True

    def taruh(self, bentuk, baris, kolom):
        for r, c in bentuk.kotak:
            self.sel[baris + r][kolom + c] = bentuk.warna

    def hapus_garis(self):
        """Hapus semua baris/kolom penuh. Return jumlah garis yang terhapus."""
        baris_penuh = [r for r in range(GRID)
                       if all(self.sel[r][c] is not None for c in range(GRID))]
        kolom_penuh = [c for c in range(GRID)
                       if all(self.sel[r][c] is not None for r in range(GRID))]
        for r in baris_penuh:
            for c in range(GRID):
                self.sel[r][c] = None
        for c in kolom_penuh:
            for r in range(GRID):
                self.sel[r][c] = None
        return len(baris_penuh) + len(kolom_penuh)

    def masih_muat(self, bentuk):
        """True jika bentuk bisa ditaruh di salah satu posisi papan."""
        return any(self.bisa_taruh(bentuk, r, c)
                   for r in range(GRID) for c in range(GRID))
