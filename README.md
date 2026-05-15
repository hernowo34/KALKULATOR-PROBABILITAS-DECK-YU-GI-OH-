# Kalkulator Probabilitas Deck Yu-Gi-Oh! (GUI Edition)

Aplikasi kalkulator probabilitas *Trading Card Game* (TCG) Yu-Gi-Oh! berbasis Python yang dilengkapi dengan *Graphical User Interface* (GUI) interaktif dan terintegrasi langsung dengan **YGOProDeck API**.

Aplikasi ini menggunakan perhitungan **Distribusi Hipergeometrik** untuk membantu pemain kompetitif merancang komposisi *deck* (*deck-building*) dengan menghitung peluang menarik (*draw*) kartu tertentu pada *starting hand*.

![Tangkapan Layar Aplikasi]([https://raw.githubusercontent.com/ygoprodeck/ygoprodeck/master/favicon.ico](https://github.com/hernowo34/KALKULATOR-PROBABILITAS-DECK-YU-GI-OH-/blob/main/Tangkapan%20Layar%20Aplikasi.png))

## 🌟 Fitur Utama

- **Antarmuka Grafis (GUI) Modern:** Dibangun menggunakan `customtkinter` dengan dukungan mode gelap (*dark theme*) yang nyaman di mata.
- **Integrasi YGOProDeck API:** Mencari data kartu secara *real-time* langsung dari server YGOProDeck. Tidak perlu lagi mengetik tipe, atribut, dan level/rank secara manual.
- **Pemuatan Gambar Otomatis:** Mengunduh dan merender (*render*) gambar kartu dari API secara langsung ke dalam aplikasi.
- **Akurasi Matematis:** Menggunakan probabilitas distribusi hipergeometrik murni via modul `math` Python untuk akurasi hitungan 100%.
- **Sistem Penyimpanan Cerdas (JSON):** Kemampuan untuk menyimpan rancangan deck ke file JSON lokal dan memuatnya kembali (*Load/Save Deck*).
- **Multithreading:** Proses pencarian API dan pengunduhan gambar berjalan di latar belakang (asinkron), memastikan UI tetap responsif.

## 🛠️ Persyaratan Sistem (*Prerequisites*)

Sebelum menjalankan program ini, pastikan Anda telah menginstal **Python 3.8+** dan modul/dependensi eksternal berikut:

```bash
pip install customtkinter pillow requests
```

## 🚀 Cara Penggunaan

1. Clone repositori ini atau *download* *source code* ke dalam satu folder (misalnya `Kalkulator Probabilitas Kartu Yu-Go-Oh!`).
2. Buka terminal atau *command prompt*, lalu arahkan ke *directory* proyek Anda.
3. Jalankan titik masuk program (*entry point*):

```bash
python main.py
```

### Langkah Dasar di dalam Aplikasi:
1. Ketikkan nama kartu (misal: `"Blue-Eyes"`) di panel **Cari Kartu (API)**.
2. Klik tombol **Cari**. Gambar kartu dan detail atributnya akan muncul secara otomatis.
3. Tentukan jumlah salinan/copy (*Qty*) yang ingin dimasukkan (maksimal 3), lalu klik **Tambah ke Deck**.
4. Di panel sebelah kanan (**Kalkulasi Probabilitas**), atur "Jumlah Draw (n)" (default: 5 untuk *starting hand*).
5. Klik **Hitung Peluang** untuk melihat persentase keberhasilan (P>=1, P=1, P=2, dst) dari setiap kartu di Main Deck Anda!

## 📁 Struktur Proyek

```text
UTS/
├── main.py              # Entry point utama untuk menjalankan aplikasi GUI
├── gui_app.py           # Kelas antarmuka pengguna berbasis customtkinter
├── api_client.py        # Klien HTTP untuk mengurus request ke YGOProDeck API
├── utils.py             # Modul mesin kalkulasi matematika (Distribusi Hipergeometrik)
├── file_io.py           # Operasi baca/tulis (*Load/Save*) ke format JSON dan TXT
├── deck/
│   └── manager.py       # Logika bisnis untuk menambah, menghapus, dan menghitung limit deck
└── README.md            # File dokumentasi ini
```

## 📚 Dasar Teori
Aplikasi ini dianalisis dan dikembangkan menggunakan pedoman rekayasa perangkat lunak dan rumus **Distribusi Hipergeometrik**:

$$P(X = k) = \frac{\binom{K}{k} \binom{N - K}{n - k}}{\binom{N}{n}}$$

*Aplikasi ini dikembangkan untuk keperluan akademik dan alat bantu analisis TCG.*
