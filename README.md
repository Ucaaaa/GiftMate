# GiftMate

GiftMate adalah proyek chatbot yang membantu pengguna mendapatkan rekomendasi atau bantuan terkait hadiah. Repository ini berisi source code proyek beserta berkas pendukung agar dapat dikelola dan dikembangkan melalui GitHub.

## Fitur

- Source code chatbot GiftMate.
- Struktur proyek dan aset pendukung yang disertakan dalam paket.
- Folder `screenshots/` untuk dokumentasi tampilan aplikasi.
- Berkas antarmuka berbasis HTML.

## Teknologi

- Python
- HTML/CSS/JavaScript untuk bagian antarmuka (jika digunakan oleh konfigurasi proyek).
- Dependensi Python tercantum di `requirements.txt`.

## Struktur Repository

```text
GiftMate/
├── .gitignore
├── CARA-MENJALANKAN.md
├── README.md
├── app.py
├── chatbot/
├── cli.py
├── evaluasi/
├── evaluate.py
├── pytest.ini
├── requirements.txt
├── screenshots/
├── static/
├── templates/
├── tests/
├── themes/
```

Folder dan file di dalam direktori proyek dipertahankan dari arsip sumber, dengan pengecualian virtual environment, cache Python, dan file sementara yang tidak diperlukan untuk repository.

## Instalasi

1. Pastikan Python 3.9 atau versi yang sesuai dengan dependensi proyek sudah terpasang.
2. Clone repository:

   ```bash
   git clone <URL-REPOSITORY-GITHUB>
   cd GiftMate
   ```

3. Buat dan aktifkan virtual environment:

   **Windows (PowerShell):**
   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

   **macOS/Linux:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

4. Instal dependensi:

   ```bash
   pip install -r requirements.txt
   ```

## Menjalankan Aplikasi

Periksa konfigurasi proyek dan file entry point yang tersedia untuk mengetahui perintah menjalankan chatbot. Jika proyek memerlukan token/API key atau konfigurasi lain, simpan nilainya di file `.env` lokal dan jangan unggah file tersebut ke GitHub. Tambahkan contoh variabel tanpa nilai rahasia ke `.env.example` bila diperlukan.

File Python yang berpotensi menjadi entry point:
- `app.py`

Pastikan memilih entry point yang sesuai dengan petunjuk konfigurasi proyek sebelum menjalankan aplikasi.

## Dokumentasi Tampilan

Letakkan screenshot chatbot di folder `screenshots/`. Gunakan format PNG atau JPG dan nama file yang mudah dikenali. Screenshot dapat ditampilkan di README dengan format:

```markdown
![Tampilan GiftMate](screenshots/nama-file-screenshot.png)
```

## Persiapan Upload ke GitHub

1. Ekstrak ZIP ini.
2. Buka folder repository dan periksa kembali konfigurasi lokal.
3. Pastikan token, password, file `.env`, database lokal, dan data pribadi tidak ikut di-commit.
4. Buat repository baru di GitHub.
5. Jalankan perintah berikut dari folder proyek:

   ```bash
   git init
   git add .
   git commit -m "Initial commit GiftMate"
   git branch -M main
   git remote add origin <URL-REPOSITORY-GITHUB>
   git push -u origin main
   ```

## Catatan

- Virtual environment dan cache Python tidak disertakan.
- Folder `screenshots/` sudah disiapkan; tambahkan screenshot asli aplikasi sebelum publikasi agar dokumentasi visual repository lengkap.
- Tinjau kembali `requirements.txt` dan sesuaikan jika ada dependensi yang dipasang secara manual tetapi tidak terdeteksi dari source code.
