# 🎌 Otakudesu Scraper - Pengalaman Nonton Anime Terbaik di Terminal Anda

Selamat datang di **Otakudesu Scraper**, sebuah aplikasi *command-line* yang dirancang untuk memberikan pengalaman terbaik dalam mencari, menjelajahi, dan mendapatkan link unduhan anime favorit Anda langsung dari situs Otakudesu. Dibangun dari awal dengan Python dan dipercantik menggunakan pustaka `rich`, aplikasi ini mengubah terminal Anda menjadi sebuah portal anime yang modern, cepat, dan fungsional.

Lupakan browser, lupakan iklan. Fokus hanya pada anime yang ingin Anda tonton.

---

## 🚀 Fitur Unggulan

Aplikasi ini dikemas dengan berbagai fitur untuk memenuhi semua kebutuhan Anda:

### Fitur Penjelajahan
- **🔍 Pencarian Cepat:** Temukan anime apa pun berdasarkan judul dengan hasil yang instan.
- **📺 Daftar Anime Ongoing & Completed:** Selalu update dengan anime terbaru atau cari tontonan yang sudah tamat.
- **🗓️ Jadwal Rilis:** Lihat jadwal rilis anime mingguan yang dikelompokkan berdasarkan hari, sehingga Anda tidak akan ketinggalan episode baru.
- **🎭 Jelajahi Berdasarkan Genre:** Temukan anime baru dengan menjelajahi daftar lengkap genre yang tersedia.
- **🗂️ Daftar Lengkap A-Z:** Jelajahi ribuan judul anime yang diurutkan berdasarkan abjad.

### Fitur Fungsional
- **📖 Detail Komprehensif:** Dapatkan semua informasi yang Anda butuhkan—mulai dari sinopsis, genre, studio, hingga skor—dalam satu tampilan yang terorganisir.
- **⭐ Manajemen Favorit:** Buat daftar pantauan pribadi Anda. Tambah, lihat, dan hapus anime dari favorit dengan mudah.
- **🧠 Cache Cerdas:** Aplikasi secara otomatis menyimpan data yang sudah diakses, membuat penjelajahan berikutnya menjadi super cepat dan mengurangi beban jaringan.

### Fitur Lanjutan
- **🔔 Notifikasi Episode Baru:** Jangan pernah ketinggalan episode baru! Aplikasi akan secara otomatis memberitahu Anda jika ada episode baru dari anime di daftar favorit Anda.
- **🕘 Riwayat & Penanda Tonton:**
    - Aplikasi mengingat 50 pencarian terakhir Anda.
    - Setiap episode yang link unduhannya Anda lihat akan ditandai (✅), sehingga Anda tahu persis sudah sampai mana Anda menonton.
- **📥 Ekspor Data Fleksibel:** Ingin memindahkan data Anda? Ekspor daftar favorit atau seluruh cache aplikasi ke format `.json` atau `.csv` dengan mudah.
- **📊 Statistik Aplikasi:** Penasaran dengan kebiasaan menonton Anda? Lihat statistik seperti jumlah anime favorit, item di cache, dan lainnya.

---

## 🔧 Instalasi & Penggunaan

Memulai aplikasi ini sangat mudah. Cukup ikuti langkah-langkah berikut:

**1. Persiapan Awal**
   - Pastikan Anda memiliki **Python 3.11** atau versi yang lebih baru.
   - Clone repositori ini atau unduh semua file ke dalam satu folder bernama `otakudesu-scraper`.

**2. Instalasi Dependensi**
   Buka terminal Anda, masuk ke direktori `otakudesu-scraper`, dan jalankan perintah berikut untuk menginstal semua pustaka yang dibutuhkan:
   ```bash
   pip install rich requests bs4 lxml re
   ```

**3. Jalankan Aplikasi**
   Setelah instalasi selesai, jalankan aplikasi dengan perintah sederhana ini:
   ```bash
   python main.py
   ```
   Aplikasi akan dimulai, dan Anda siap untuk menjelajah!

---

## 📂 Struktur Proyek

Kode diatur secara modular untuk kemudahan pemeliharaan dan pengembangan di masa depan.

```
otakudesu-scraper/
├── data/
│   └── cache.json         # File cache untuk menyimpan data
├── exports/               # Folder untuk menyimpan hasil ekspor
├── __init__.py
├── cache_manager.py     # Logika untuk memuat dan menyimpan cache
├── cli.py               # Jantung aplikasi: UI, menu, dan interaksi pengguna
├── constants.py         # Semua konstanta (URL, emoji, path file)
├── main.py              # Titik masuk utama untuk menjalankan aplikasi
├── scraper.py           # Otak di balik layar: semua logika scraping
├── themes.py            # Tema warna kustom untuk Rich
└── utils.py             # Fungsi-fungsi bantuan
```

---

Dibuat dengan semangat oleh seorang Junior Python Developer. Selamat menikmati dunia anime di terminal Anda!
