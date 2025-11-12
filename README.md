# 🕸️✨ Web Scraping → Dataset limpio → Power BI

> **Objetivo:** entender qué es el *web scraping*, por qué se conecta con **análisis**, **diseño de bases de datos** y **Power BI**, y practicar con un mini-proyecto en 2 clases.

---

## 🧠 ¿Qué es el Web Scraping?
El **web scraping** es extraer datos de páginas web de forma **automatizada** usando código (p. ej., **Python** con `requests + BeautifulSoup` o **Selenium**).

- 📥 **Entrada:** HTML público.
- 🧪 **Proceso:** ubicar elementos (selectores CSS/XPath), leer texto/atributos, **limpiar** y **normalizar**.
- 📤 **Salida:** tabla (CSV/Parquet/BD) lista para análisis y visualización.

> Metáfora: un “robot lector” que copia lo que necesitamos, de forma ordenada y repetible.

---

## 🧭 Ética & buenas prácticas
- 🤝 **Respeta** `robots.txt` y Términos del sitio.
- 🕵️ **Identifícate** con `User-Agent`; evita tasas de petición agresivas (usa *delays*).
- 🧹 **Limpia** los datos y **cita** la fuente cuando corresponda.
- 🔒 **No** raspes contenido privado ni con bloqueo de acceso.

---

## 🔗 ¿Por qué se conecta con Bases de Datos y Power BI?
1. **Modelado lógico**: del HTML “desordenado” a **entidades y atributos** (p. ej., `Producto`, `Categoría`, `Precio`).
2. **Normalización**: decidir claves (ID), relaciones (1:*), catálogos (dimensiones) y hechos (ventas).
3. **ETL/ELT**: extracción (scrape) → transformación (limpieza, tipos) → **carga** (CSV/DB).
4. **Analítica/BI**: Power BI consume el **dataset** y permite métricas (DAX), modelos estrella y reportes.

---


---

## 🧰 Herramientas
- **Python 3.10+**
  - `requests`, `beautifulsoup4`, `lxml` (sitios estáticos, rápido)
  - `selenium`, `webdriver-manager` (sitios dinámicos, visible en clase)
  - `pandas` (limpieza + CSV)
- **Power BI Desktop** (modelado, DAX, visuales)

---

## ⚙️ Instalación rápida
```bash
# entorno opcional
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# scraping estático
pip install requests beautifulsoup4 lxml pandas

# scraping con navegador visible (opcional)
pip install selenium webdriver-manager

# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# scraping estático
pip install requests beautifulsoup4 lxml pandas

# scraping con navegador visible (opcional)
pip install selenium webdriver-manager
