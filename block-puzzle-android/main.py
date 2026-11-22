"""
main.py - Tampilan Block Puzzle untuk Android/PC dengan Kivy
============================================================
Cara main: sentuh dan seret salah satu dari 3 blok di bawah ke papan 8x8,
lepas untuk menaruh. Baris/kolom penuh terhapus. Game over kalau tidak ada
blok yang muat; ketuk layar untuk main lagi.

Catatan koordinat Kivy: titik (0,0) ada di KIRI-BAWAH, sumbu y naik ke atas.
Sedangkan baris papan dihitung dari ATAS, jadi ada konversi di beberapa tempat.
"""

from kivy.app import App
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.utils import get_color_from_hex

from logika import GRID, Papan, bentuk_acak

Window.clearcolor = get_color_from_hex("#1e1e2e")

RASIO_TRAY = 0.5   # ukuran kotak di tray dibanding kotak papan
RASIO_ANGKAT = 1.0 # blok diangkat sekian kotak di atas jari saat diseret


class AreaGame(Widget):
    """Widget tempat papan, tray blok, dan seluruh sentuhan ditangani."""

    def __init__(self, label, **kwargs):
        super().__init__(**kwargs)
        self.label = label            # label skor di atas
        self.papan = Papan()
        self.skor_tertinggi = 0
        self.bind(pos=self.gambar, size=self.gambar)  # gambar ulang saat ukuran berubah
        self.mulai_baru()

    # ---------- Alur permainan ----------
    def mulai_baru(self):
        self.papan.reset()
        self.skor = 0
        self.selesai = False
        self.seret = None          # index blok yang sedang diseret
        self.mx = self.my = 0      # posisi jari
        self.bentuk = [bentuk_acak() for _ in range(3)]
        self.gambar()

    def cek_game_over(self):
        sisa = [b for b in self.bentuk if b is not None]
        if not any(self.papan.masih_muat(b) for b in sisa):
            self.selesai = True
            self.skor_tertinggi = max(self.skor_tertinggi, self.skor)

    # ---------- Geometri ----------
    def ukuran_sel(self):
        """Ukuran 1 kotak papan; sisakan tinggi 3 kotak untuk tray."""
        return min(self.width / GRID, self.height / (GRID + 3))

    def kiri_papan(self, sel):
        return self.x + (self.width - GRID * sel) / 2

    def posisi_grid(self, b, sel):
        """Ubah posisi jari jadi (baris, kolom) papan untuk bentuk b."""
        x0 = self.mx - b.lebar * sel / 2
        atas = self.my + sel * RASIO_ANGKAT + b.tinggi * sel / 2
        kolom = round((x0 - self.kiri_papan(sel)) / sel)
        baris = round((self.top - atas) / sel)
        return baris, kolom

    # ---------- Sentuhan ----------
    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return False
        if self.selesai:
            self.mulai_baru()
            return True
        sel = self.ukuran_sel()
        if touch.y < self.top - GRID * sel:           # sentuh area tray
            slot = int((touch.x - self.x) // (self.width / 3))
            slot = max(0, min(slot, 2))
            if self.bentuk[slot] is not None:
                self.seret = slot
                self.mx, self.my = touch.pos
                self.gambar()
        return True

    def on_touch_move(self, touch):
        if self.seret is not None:
            self.mx, self.my = touch.pos
            self.gambar()
            return True
        return False

    def on_touch_up(self, touch):
        if self.seret is None:
            return False
        self.mx, self.my = touch.pos
        sel = self.ukuran_sel()
        b = self.bentuk[self.seret]
        baris, kolom = self.posisi_grid(b, sel)

        if self.papan.bisa_taruh(b, baris, kolom):
            self.papan.taruh(b, baris, kolom)
            self.skor += len(b.kotak)
            garis = self.papan.hapus_garis()
            if garis:
                self.skor += garis * garis * 10       # bonus combo
            self.bentuk[self.seret] = None
            if all(x is None for x in self.bentuk):
                self.bentuk = [bentuk_acak() for _ in range(3)]
            self.cek_game_over()

        self.seret = None
        self.gambar()
        return True

    # ---------- Tampilan ----------
    def kotak(self, x, y, ukuran, warna):
        """Gambar satu kotak berwarna (dengan celah tipis antar kotak)."""
        Color(*get_color_from_hex(warna))
        Rectangle(pos=(x + 1, y + 1), size=(ukuran - 2, ukuran - 2))

    def gambar(self, *args):
        self.canvas.clear()
        sel = self.ukuran_sel()
        kiri = self.kiri_papan(sel)
        atas = self.top

        with self.canvas:
            # papan
            for r in range(GRID):
                for c in range(GRID):
                    warna = self.papan.sel[r][c] or "#2b2b40"
                    self.kotak(kiri + c * sel, atas - (r + 1) * sel, sel, warna)

            # bayangan posisi jatuh (ghost)
            if self.seret is not None:
                b = self.bentuk[self.seret]
                baris, kolom = self.posisi_grid(b, sel)
                if self.papan.bisa_taruh(b, baris, kolom):
                    for r, c in b.kotak:
                        self.kotak(kiri + (kolom + c) * sel,
                                   atas - (baris + r + 1) * sel, sel, "#555577")

            # blok di tray
            ts = sel * RASIO_TRAY
            cy = self.y + (self.height - GRID * sel) / 2
            for i, b in enumerate(self.bentuk):
                if b is None or i == self.seret:
                    continue
                cx = self.x + self.width / 3 * (i + 0.5)
                x0 = cx - b.lebar * ts / 2
                top0 = cy + b.tinggi * ts / 2
                for r, c in b.kotak:
                    self.kotak(x0 + c * ts, top0 - (r + 1) * ts, ts, b.warna)

            # blok yang sedang diseret (ukuran penuh, di atas jari)
            if self.seret is not None:
                b = self.bentuk[self.seret]
                x0 = self.mx - b.lebar * sel / 2
                top0 = self.my + sel * RASIO_ANGKAT + b.tinggi * sel / 2
                for r, c in b.kotak:
                    self.kotak(x0 + c * sel, top0 - (r + 1) * sel, sel, b.warna)

            # lapisan gelap saat game over
            if self.selesai:
                Color(0, 0, 0, 0.6)
                Rectangle(pos=(kiri, atas - GRID * sel), size=(GRID * sel, GRID * sel))

        # teks skor di label atas
        if self.selesai:
            self.label.text = (f"GAME OVER - Skor {self.skor}\n"
                               f"Ketuk layar untuk main lagi")
        else:
            self.label.text = (f"Skor: {self.skor}    "
                               f"Tertinggi: {self.skor_tertinggi}")


class BlockPuzzleApp(App):
    title = "Block Puzzle"

    def build(self):
        root = BoxLayout(orientation="vertical")
        label = Label(size_hint_y=0.1, font_size="18sp", halign="center")
        root.add_widget(label)
        root.add_widget(AreaGame(label))
        return root


if __name__ == "__main__":
    BlockPuzzleApp().run()
