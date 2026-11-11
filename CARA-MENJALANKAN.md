# Cara Menjalankan GiftMate

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Buka browser ke `http://127.0.0.1:5000`. Untuk berhenti tekan `Ctrl + C`.

## Uji cepat
1. Klik Mulai cari hadiah.
2. Kirim `rekomendasi hadiah`.
3. Jawab berurutan: `sahabat`, `ulang tahun`, `100 ribu`, `membaca`.
4. Coba tombol saran, mode belajar, dan hapus riwayat.

## Uji otomatis dan evaluasi
```powershell
pytest -q
python evaluate.py
```
