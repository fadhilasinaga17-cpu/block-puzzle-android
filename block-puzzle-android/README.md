# Block Puzzle (Python + Kivy, Android)

Game puzzle blok dengan konsep PBO. Ditulis dengan Python dan Kivy, di-build jadi APK Android lewat GitHub Actions.

## Cara main
Sentuh dan seret salah satu dari 3 blok di bawah ke papan 8x8, lepas untuk menaruh.
Baris atau kolom penuh terhapus. Ketuk layar saat game over untuk main lagi.

## File
- `logika.py` : aturan game (class Bentuk, Papan)
- `main.py` : tampilan dan sentuhan (Kivy)
- `buildozer.spec` : pengaturan pembuatan APK
- `.github/workflows/build.yml` : build APK otomatis di GitHub

## Menjalankan di PC (untuk dites)
    pip install kivy
    python main.py

## Download di HP
Buka tab **Releases** repo ini, unduh file `.apk`, buka di HP Android, lalu izinkan "Install dari sumber tidak dikenal".
