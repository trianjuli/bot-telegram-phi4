# Bot-telegram-phi4

Bot Telegram untuk penilaian Diskusi dan Tugas Mahasiswa menggunakan Agentic AI (Phi4 via Ollama).

Fitur utama:
- Evaluasi otomatis diskusi dan tugas berdasarkan rubrik yang dapat dikustomisasi
- Feedback terstruktur, skor, dan saran perbaikan
- Antarmuka Telegram sederhana untuk dosen/instruktur

---

## Persyaratan
- Python 3.10+
- Telegram Bot Token (dapat dibuat melalui @BotFather)
- Ollama (jika menggunakan model Phi4 lokal) atau endpoint model LLM yang kompatibel

File penting di repo:
- `bot.py` — file utama untuk menjalankan bot Telegram
- `core/knowledge_base.py` — modul untuk mengelola rubrik dan knowledge base
- `core/agent.py` — agent yang menghubungkan ke Phi4 (via Ollama) dan menjalankan evaluasi
- `config/rubric.json` — rubrik default untuk diskusi dan tugas
- `config/knowledge_base.json` — knowledge base / instruksi penilaian
- `.env.example` — contoh konfigurasi environment
- `requirements.txt` — dependencies Python

---

## Setup (lokal)
1. Clone repo:
   git clone https://github.com/trianjuli/Bot-telegram-phi4.git
   cd Bot-telegram-phi4

2. Buat virtual environment dan install dependency:
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install --upgrade pip
   pip install -r requirements.txt

3. Konfigurasi environment:
   cp .env.example .env
   Edit `.env` dan isi nilai:
   - TELEGRAM_BOT_TOKEN=... (token dari @BotFather)
   - OLLAMA_BASE_URL (default http://localhost:11434 jika menggunakan Ollama)
   - MODEL_NAME (default phi4)

4. Jalankan Ollama (apabila menggunakan model lokal):
   - Install dan jalankan Ollama sesuai dokumentasi resmi.
   - Pastikan model `phi4` tersedia di Ollama, atau ubah `MODEL_NAME` di `.env` ke model yang tersedia.

5. Jalankan bot:
   python bot.py

6. Buka Telegram dan cari bot Anda, ketik `/start`.

---

## Cara Pakai (ringkas)
- /start — menampilkan menu dan tombol
- 📝 Evaluasi Diskusi — kirim teks diskusi untuk dievaluasi
- 📄 Evaluasi Tugas — kirim teks tugas untuk dievaluasi
- 💬 Lihat Rubrik — tampilkan rubrik penilaian
- /help — panduan penggunaan

Catatan: Teks minimum 20 karakter untuk evaluasi.

---

## Kustomisasi
- Edit `config/rubric.json` untuk mengubah kriteria dan bobot penilaian.
- Edit `config/knowledge_base.json` untuk menambah contoh, instruksi mata kuliah, dan skala.
- Anda bisa mengubah mapper nilai pada `core/knowledge_base.py` jika ingin skema nilai berbeda.

---

## Contoh Penggunaan
Lihat `examples/sample_submission.txt` untuk contoh teks diskusi/tugas yang bisa dikirimkan ke bot.

---

## Troubleshooting
- Jika bot mengeluh `TELEGRAM_BOT_TOKEN` tidak ditemukan: pastikan `.env` sudah dibuat dan `TELEGRAM_BOT_TOKEN` terisi.
- Jika error koneksi ke Ollama: pastikan Ollama berjalan dan `OLLAMA_BASE_URL` benar.
- Jika output AI tidak berupa JSON: model mungkin menghasilkan teks bebas. Perbaiki prompt atau gunakan model dengan output yang lebih deterministic (atur temperature rendah).

---

## Keamanan & Privasi
Jangan mengirim data pribadi mahasiswa (NIM, alamat, data sensitif) melalui Telegram. Jika Anda butuh penyimpanan hasil evaluasi, pertimbangkan database terenkripsi dan kebijakan retensi data.

---

Jika Anda ingin, saya bisa:
- Menambahkan fitur upload file (PDF/DOC) dengan ekstraksi teks
- Menyimpan hasil evaluasi ke database (SQLite/Postgres)
- Menambahkan autentikasi untuk instruktur

Beritahu saya fitur mana yang ingin ditambahkan selanjutnya.
