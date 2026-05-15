# LapakPintar
### Autonomous Business Operating System untuk UMKM Indonesia
**OpenClaw Agenthon 2026 — RISTEK x Build Club**

[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://python.org)
[![QwenPaw](https://img.shields.io/badge/Framework-QwenPaw-teal)](https://github.com/agentscope-ai/QwenPaw)
[![Qwen3](https://img.shields.io/badge/LLM-Qwen3--14B-orange)](https://github.com/QwenLM/Qwen3)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

![NexaPaw Logo](NexaPaw_Logo.png)

---

## Deskripsi Proyek

**LapakPintar** adalah sistem Multi-Agent berbasis QwenPaw yang bekerja **24/7 secara otonom** untuk mengelola operasional bisnis UMKM Indonesia — memantau harga kompetitor, menganalisis tren penjualan, membuat konten promosi, merekonsiliasi pembayaran, hingga menghasilkan laporan bisnis — **tanpa intervensi manual**.

> 65 juta UMKM Indonesia menghabiskan rata-rata 4 jam/hari untuk tugas operasional berulang. LapakPintar hadir untuk mengembalikan waktu itu.

---

## Arsitektur Multi-Agent

```
┌─────────────────────────────────────────────────────────┐
│                  Scheduler / Event Bus                  │
└─────────────────────────┬───────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────┐
│         Orchestrator — Qwen3 + QwenPaw Core             │
│      (Reasoning · Planning · Agent Coordination)        │
└──────┬──────────┬──────────┬──────────┬────────┬────────┘
       │          │          │          │        │
   ┌───▼───┐  ┌───▼───┐  ┌───▼───┐  ┌──▼──┐  ┌──▼───┐
   │Pantau │  │Analitik│  │Konten │  │Bayar│  │Laporan│
   │ Agent │  │ Agent  │  │ Agent │  │Agent│  │ Agent │
   └───┬───┘  └───┬────┘  └───┬───┘  └──┬──┘  └──┬───┘
       │          │           │          │         │
┌──────▼──────────▼───────────▼──────────▼─────────▼─────┐
│            Tool Layer                                   │
│  [Playwright Scraper · DOKU API · Qwen LLM · RAG DB]   │
└─────────────────────────┬───────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────┐
│         QwenPaw Memory Store (Long-Term + Working)      │
└─────────────────────────────────────────────────────────┘
```

### Deskripsi Setiap Agent

| Agent | Peran | Tools |
|-------|-------|-------|
| **Pantau Agent** | Monitor harga & tren kompetitor di Tokopedia/Shopee secara real-time | Playwright, BeautifulSoup4 |
| **Analitik Agent** | Analisis pola penjualan, deteksi anomali, prediksi demand | RAG DB, Qwen3 reasoning |
| **Konten Agent** | Generate deskripsi produk & jadwal konten promosi otomatis | Qwen3 LLM API |
| **Bayar Agent** | Rekonsiliasi transaksi & disbursement via DOKU Payment API | DOKU REST API |
| **Laporan Agent** | Sintesis insight lintas-agent & kirim laporan harian | Qwen3 LLM, Redis |

---

## Cara Menjalankan

### Prasyarat

- Python 3.11+
- Docker & Docker Compose
- DOKU API credentials (untuk fitur pembayaran)
- Qwen API key (DashScope) atau Qwen3-14B lokal via Ollama/vLLM

### 1. Clone Repository

```bash
git clone https://github.com/felixyustian/OpenClaw2026_NexaPaw_LapakPintar.git
cd OpenClaw2026_NexaPaw_LapakPintar
```

### 2. Setup Environment

```bash
cp .env.example .env
# Edit .env dengan credentials Anda:
# QWEN_API_KEY=your_dashscope_key
# DOKU_CLIENT_ID=your_doku_client_id
# DOKU_SECRET_KEY=your_doku_secret_key
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

### 4. Inisialisasi QwenPaw

```bash
qwenpaw init
qwenpaw install skills/pantau_skill.py
qwenpaw install skills/analitik_skill.py
qwenpaw install skills/konten_skill.py
qwenpaw install skills/bayar_skill.py
qwenpaw install skills/laporan_skill.py
```

### 5. Jalankan Sistem

**Mode Docker (Recommended):**
```bash
docker compose up --build
```

**Mode Lokal:**
```bash
# Terminal 1: Redis
redis-server

# Terminal 2: FastAPI Backend
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Terminal 3: QwenPaw Orchestrator
python orchestrator/main.py
```

**Mode Demo (tanpa credentials):**
```bash
python demo/run_demo.py --mock
```

Akses dashboard: `http://localhost:8000`

---

## Struktur Proyek

```
OpenClaw2026_NexaPaw_LapakPintar/
├── agents/
│   ├── pantau_agent.py       # Marketplace monitor agent
│   ├── analitik_agent.py     # Sales analytics agent
│   ├── konten_agent.py       # Content generation agent
│   ├── bayar_agent.py        # DOKU payment agent
│   └── laporan_agent.py      # Report synthesis agent
├── orchestrator/
│   └── main.py               # QwenPaw orchestrator + scheduler
├── skills/                   # QwenPaw custom skills
│   ├── pantau_skill.py
│   ├── bayar_skill.py
│   └── ...
├── tools/
│   ├── scraper.py            # Playwright marketplace scraper
│   ├── doku_client.py        # DOKU API integration
│   └── rag_db.py             # RAG memory store
├── app/
│   ├── main.py               # FastAPI backend
│   └── routes/               # API endpoints
├── demo/
│   └── run_demo.py           # Mock demo mode
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── .env.example
```

---

## AI Tools / Models Used

| Tool/Model | Versi | Kegunaan |
|-----------|-------|---------|
| QwenPaw | Latest (AgentScope) | Agent framework, skill orchestration, memory |
| Qwen3-14B | 14B | LLM reasoning, planning, content generation |
| Qwen3 (DashScope) | `qwen3-14b` | Cloud inference fallback |
| Playwright | 1.44 | Web scraping marketplace |
| BeautifulSoup4 | 4.12 | HTML parsing |
| DOKU REST API | v2 | Payment reconciliation & disbursement |
| FastAPI | 0.111 | Backend API server |
| Redis | 7.2 | Working memory & task queue |
| Docker Compose | 3.8 | Multi-container deployment |

---

## Best Payment Use Case Track

Proyek ini berpartisipasi dalam **Best Payment Use Case** track dengan mengintegrasikan **DOKU REST API** melalui **Bayar Agent** untuk:
- Rekonsiliasi transaksi masuk secara otomatis
- Deteksi anomali pembayaran menggunakan Qwen3 reasoning
- Notifikasi otomatis ke pemilik toko saat ada transaksi gagal
- Disbursement otomatis ke supplier berdasarkan threshold stok

---

## Demo

📹 Demo Video: https://www.youtube.com/watch?v=n798nMT8Ce0

🌐 Live Demo: https://openclaw2026nexapawlapakpintar-production.up.railway.app/docs/

---

## Lisensi

MIT License — lihat [LICENSE](LICENSE) untuk detail.

---

*OpenClaw Agenthon 2026 | RISTEK x Build Club | 15 Mei 2026*
