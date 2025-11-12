
# ------------------------------------------------------------
import re
import time
import random
import argparse
from datetime import datetime, timedelta

import pandas as pd
from bs4 import BeautifulSoup

# === Selenium ===
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

BASE = "https://books.toscrape.com/"
HEADERS = {"User-Agent": "Mozilla/5.0 (educational scraping demo)"}  


# --------------------- Helpers ---------------------
def make_soup(html: str):
    try:
        return BeautifulSoup(html, "lxml")
    except Exception:
        return BeautifulSoup(html, "html.parser")


def parse_precio(texto: str) -> float:

    return float(re.sub(r"[^\d.]", "", texto))


def parse_disponibilidad(texto: str) -> int:
    
    m = re.search(r"(\d+)", texto)
    return int(m.group(1)) if m else 0


def parse_rating_from_card(card) -> int | None:
   
    tag = card.select_one(".star-rating")
    if not tag:
        return None
    clases = tag.get("class", [])
    mapa = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
    for c in clases:
        if c in mapa:
            return mapa[c]
    return None


# --------------------- Selenium driver ---------------------
def build_driver(show_browser: bool = True):
    opts = Options()
    if not show_browser:
        opts.add_argument("--headless=new")
    opts.add_argument("--start-maximized")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=opts)  # Selenium 4 OK
    return driver


# --------------------- Scraping con Selenium ---------------------
def scrape_catalogo_selenium(paginas: int = 3, pausa: float = 0.6, show_browser: bool = True) -> pd.DataFrame:
    """
    Navega con Selenium por 'Books to Scrape', hace click en NEXT y raspa N páginas.
    Devuelve un DataFrame con: titulo, precio, stock_disponible, rating, url, categoria, fecha_extraccion
    """
    driver = build_driver(show_browser=show_browser)
    wait = WebDriverWait(driver, 10)

    filas = []
    try:
   
        driver.get(BASE + "catalogue/page-1.html")

        for page in range(1, paginas + 1):
          
            wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "article.product_pod")))

           
            soup = make_soup(driver.page_source)
            tarjetas = soup.select("article.product_pod")
            print(f"[INFO] Página {page}: {len(tarjetas)} productos")

            for t in tarjetas:
                titulo = t.h3.a.get("title", "").strip()
                price_text = t.select_one(".price_color").get_text(strip=True)
                price = parse_precio(price_text)
                stock_text = t.select_one("p.instock.availability").get_text(" ", strip=True)
                stock = parse_disponibilidad(stock_text)
                rating = parse_rating_from_card(t)
                href = t.h3.a.get("href", "")
                if href and not href.startswith("http"):
                    href = BASE + "catalogue/" + href.replace("../../", "")

                filas.append({
                    "titulo": titulo,
                    "precio": price,
                    "stock_disponible": stock,
                    "rating": rating,
                    "url": href,
                })

           
            if page < paginas:
                try:
                    next_a = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "li.next > a")))
                    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", next_a)
                    time.sleep(0.2)   # pausa para que se vea el scroll
                    next_a.click()
                    time.sleep(pausa)  # pausa didáctica para que los estudiantes vean el cambio
                except Exception:
                    print("[WARN] No se encontró botón NEXT; deteniendo en esta página.")
                    break

        
        out = []
        for f in filas:
            try:
                driver.get(f["url"])
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "ul.breadcrumb")))
                soup = make_soup(driver.page_source)
                migas = [li.get_text(strip=True) for li in soup.select("ul.breadcrumb li")]
                f["categoria"] = migas[2] if len(migas) >= 3 else "Desconocida"
            except Exception:
                f["categoria"] = "Desconocida"
            out.append(f)
            time.sleep(0.1)

        df = pd.DataFrame(out)
        df["fecha_extraccion"] = pd.Timestamp.utcnow().normalize()

  
        requeridas = {"titulo", "precio", "stock_disponible", "rating", "url"}
        faltantes = requeridas - set(df.columns)
        if faltantes:
            raise RuntimeError(f"Faltan columnas requeridas: {faltantes}")

        if "categoria" not in df.columns:
            df["categoria"] = "Desconocida"

        return df

    finally:
       
        driver.quit()



def guardar_productos_csv(df: pd.DataFrame, ruta: str = "productos.csv") -> str:
    if df.empty:
        raise RuntimeError("DataFrame vacío.")
    for col in ["precio", "stock_disponible", "rating"]:
        if col not in df.columns:
            raise RuntimeError(f"Columna faltante: {col}")
    df["precio"] = pd.to_numeric(df["precio"], errors="coerce")
    df["stock_disponible"] = pd.to_numeric(df["stock_disponible"], errors="coerce").fillna(0).astype(int)
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
    cols = ["titulo", "categoria", "precio", "stock_disponible", "rating", "url", "fecha_extraccion"]
    df[cols].to_csv(ruta, index=False, encoding="utf-8")
    return ruta


def generar_ventas_simuladas(df_prod: pd.DataFrame, dias: int = 60, max_items_por_dia: int = 30, ruta: str = "ventas.csv") -> str:
    random.seed(42)
    hoy = datetime.utcnow().date()
    ventas = []
    productos = df_prod.reset_index(drop=True)
    if productos.empty:
        raise RuntimeError("No hay productos para simular ventas.")
    max_items_por_dia = min(max_items_por_dia, max(5, len(productos)//2 or 5))
    for i in range(dias):
        fecha = hoy - timedelta(days=i)
        num_items = random.randint(5, max_items_por_dia)
        for _ in range(num_items):
            p = productos.iloc[random.randint(0, len(productos)-1)]
            cantidad = random.randint(1, 3)
            ventas.append({
                "fecha": fecha.isoformat(),
                "titulo": p["titulo"],
                "categoria": p["categoria"],
                "precio_unitario": float(p["precio"]),
                "cantidad": cantidad,
                "importe": round(float(p["precio"]) * cantidad, 2),
            })
    dv = pd.DataFrame(ventas)
    dv["cantidad"] = dv["cantidad"].astype(int)
    dv["precio_unitario"] = pd.to_numeric(dv["precio_unitario"], errors="coerce")
    dv["importe"] = pd.to_numeric(dv["importe"], errors="coerce")
    dv.to_csv(ruta, index=False, encoding="utf-8")
    return ruta


# --------------------- CLI ---------------------
def parse_args():
    ap = argparse.ArgumentParser(description="Scraping Books to Scrape con Selenium (visible o headless).")
    ap.add_argument("--paginas", type=int, default=3, help="Número de páginas a raspar (default: 3)")
    ap.add_argument("--pausa", type=float, default=0.8, help="Pausa entre páginas para la demo (default: 0.8s)")
    ap.add_argument("--headless", action="store_true", help="Ejecuta Chrome en modo headless (sin UI)")
    return ap.parse_args()


# --------------------- Main ---------------------
if __name__ == "__main__":
    args = parse_args()
    show_browser = not args.headless

    df = scrape_catalogo_selenium(paginas=args.paginas, pausa=args.pausa, show_browser=show_browser)
    print("Columnas:", list(df.columns))
    print("Filas:", len(df))
    print(df.head(3))

    productos_path = guardar_productos_csv(df, "productos.csv")
    ventas_path = generar_ventas_simuladas(df, dias=60, max_items_por_dia=30, ruta="ventas.csv")
    print("OK →", productos_path, " | ", ventas_path)
