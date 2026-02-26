# 🌍 World Globe Explorer

A **premium interactive 3D globe** built with Python, Plotly & Dash.
Explore 22 world cities across 6 continents with stunning visuals.

![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square&logo=python)
![Dash](https://img.shields.io/badge/Dash-2.14-blueviolet?style=flat-square)
![Plotly](https://img.shields.io/badge/Plotly-5.18-orange?style=flat-square)
![Deploy](https://img.shields.io/badge/Deploy-Render.com-green?style=flat-square)

---

## ✨ Features

| Feature | Description |
|---|---|
| **3D Globe** | Orthographic projection — drag to rotate, scroll to zoom |
| **Flat Map** | Natural Earth projection — toggle with one click |
| **City Markers** | 22 cities, sized by population, colour-coded by continent |
| **Glow Effect** | Triple-layer halo on each marker for a premium neon look |
| **City Panel** | Slide-in panel: flag, description, stats, attractions, fun facts |
| **Continent Filter** | Dropdown to focus on any continent |
| **Dark Space Theme** | Deep navy/black background with gradient accent colours |
| **Responsive** | Works on desktop and mobile |

---

## 🚀 Run Locally

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the app
```bash
python app.py
```

Open your browser at **http://localhost:8050**

---

## 📤 Push to GitHub

```bash
# 1. Create a new repo on github.com (don't add README/gitignore — repo must be empty)

# 2. Add remote and push
git remote add origin https://github.com/YOUR_USERNAME/world-globe-explorer.git
git branch -M main
git push -u origin main
```

---

## ☁️ Deploy to Render (Free)

### Option A — Automatic via render.yaml (recommended)

1. Push your code to GitHub (step above)
2. Go to **https://dashboard.render.com**
3. Click **New → Web Service**
4. Connect your GitHub account → select the `world-globe-explorer` repo
5. Render detects `render.yaml` automatically — click **Deploy**
6. Wait ~2 minutes → your app is live at `https://world-globe-explorer.onrender.com`

### Option B — Manual setup

| Setting | Value |
|---|---|
| **Environment** | Python |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn app:server --bind 0.0.0.0:$PORT --workers 1 --timeout 120` |
| **Plan** | Free |

> **Note:** On Render's free tier, the app sleeps after 15 minutes of inactivity.
> First load after sleep takes ~30 seconds (spin-up time).

---

## 📁 Project Structure

```
world-globe-explorer/
├── app.py                 # Main Dash application
├── data/
│   ├── __init__.py
│   └── cities_data.py     # 22 cities with rich data
├── assets/
│   └── style.css          # Premium dark theme CSS
├── requirements.txt       # Python dependencies
├── render.yaml            # Render.com deployment config
├── Procfile               # Gunicorn start command
└── .gitignore
```

---

## 🗺 Cities Included

| City | Country | Continent |
|---|---|---|
| Tokyo | Japan | Asia |
| Beijing | China | Asia |
| Mumbai | India | Asia |
| Dubai | UAE | Asia |
| Singapore | Singapore | Asia |
| Bangkok | Thailand | Asia |
| Seoul | South Korea | Asia |
| Istanbul | Turkey | Asia |
| London | United Kingdom | Europe |
| Paris | France | Europe |
| Rome | Italy | Europe |
| Amsterdam | Netherlands | Europe |
| Barcelona | Spain | Europe |
| New York | USA | North America |
| Los Angeles | USA | North America |
| Mexico City | Mexico | North America |
| São Paulo | Brazil | South America |
| Buenos Aires | Argentina | South America |
| Cairo | Egypt | Africa |
| Cape Town | South Africa | Africa |
| Lagos | Nigeria | Africa |
| Sydney | Australia | Oceania |

---

## 🛠 Tech Stack

- **[Dash](https://dash.plotly.com/)** — Python web framework for interactive apps
- **[Plotly](https://plotly.com/python/)** — Interactive globe/map visualisation
- **[Gunicorn](https://gunicorn.org/)** — WSGI production server
- **[Render](https://render.com/)** — Free cloud hosting
- **Google Fonts** — Orbitron & Exo 2 for premium typography

---

*Built with ♥ using Python & Plotly Dash*
