import time
import random
import tls_client
import os
from typing import Optional

# ================= CONFIGURACIÓN =================

# 1) TU WEBHOOK DE DISCORD
#    Opción A (simple): pega aquí tu webhook directamente entre comillas
#    Opción B (pro): usa variable de entorno DISCORD_WEBHOOK_URL en Railway
DISCORD_WEBHOOK_URL = os.getenv(
    "DISCORD_WEBHOOK_URL",
    "https://discord.com/api/webhooks/1443365834893299832/m6R7PP-KjY00thKJosdhVIY7GpCD9hTkkZme27uhsjfLKZ10gvaSFNHtA0MnqGYSKvWW"
)

# 2) PRODUCTOS A MONITOREAR
PRODUCTS = [
    {
        "name": "Compresión negra Batman (4259)",
        "url": "https://www.youngla.com/products/4259"
    },
    {
        "name": "Producto 8004",
        "url": "https://www.youngla.com/products/8004?hcUrl=%2Fes-ES"
    },
    {
        "name": "Producto 5218",
        "url": "https://www.youngla.com/products/5218?_pos=26&_sid=b8554f4f3&_ss=r"
    },
    {
        "name": "Producto 2099",
        "url": "https://www.youngla.com/products/2099?_pos=25&_sid=b8554f4f3&_ss=r&hcUrl=%2Fes-ES"
    },
    {
        "name": "Producto 5214",
        "url": "https://www.youngla.com/products/5214?_pos=17&_sid=b8554f4f3&_ss=r&hcUrl=%2Fes-ES"
    },
    {
        "name": "Producto 5209",
        "url": "https://www.youngla.com/products/5209?_pos=14&_sid=b8554f4f3&_ss=r&hcUrl=%2Fes-ES"
    },
    {
        "name": "Producto 2158 (excluye Joker Goons)",
        "url": "https://www.youngla.com/products/2158?_pos=11&_sid=b8554f4f3&_ss=r&hcUrl=%2Fes-ES"
    },
    {
        "name": "Producto 5173",
        "url": "https://www.youngla.com/products/5173?_pos=10&_sid=b8554f4f3&_ss=r&hcUrl=%2Fes-ES"
    },
    {
        "name": "Producto 2032",
        "url": "https://www.youngla.com/products/2032?_pos=13&_sid=5942173a7&_ss=r"
    },
    {
        "name": "Producto 5094",
        "url": "https://www.youngla.com/products/5094?_pos=12&_sid=5942173a7&_ss=r&hcUrl=%2Fes-ES"
    },
    {
        "name": "Producto 5079",
        "url": "https://www.youngla.com/products/5079?_pos=2&_sid=5942173a7&_ss=r&hcUrl=%2Fes-ES"
    },
    {
        "name": "Producto 4065",
        "url": "https://www.youngla.com/products/4065?_pos=3&_sid=2181e5158&_ss=r&hcUrl=%2Fes-ES"
    },
    {
        "name": "Producto 5174 (excluye Joker H)",
        "url": "https://www.youngla.com/products/5174?_pos=3&_sid=060084b7a&_ss=r&variant=45034422927548&hcUrl=%2Fes-ES"
    },
]

# 3) Intervalo entre rondas (segundos)
#    Cada ronda revisa TODOS los productos una vez
CHECK_INTERVAL_SECONDS = 60  # 1 minuto

OUT_OF_STOCK_KEYWORDS = [
    "sold out",
    "out of stock",
    "email when available",
    "notify me when available",
    "notify me",
]

IN_STOCK_KEYWORDS = [
    "add to cart",
    "add to bag"
]

# Variantes que NO quieres que disparen alerta
EXCLUDED_VARIANTS = [
    "Joker Goons",
    "Joker H",
]

# ================= CLIENTE HTTP =================

# Cliente TLS para simular navegador real
session = tls_client.Session(
    client_identifier="chrome_124",
    random_tls_extension_order=True
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.google.com/",
    "Connection": "keep-alive"
}

# ================= FUNCIONES =================

def send_discord_message(message: str) -> None:
    if not DISCORD_WEBHOOK_URL or "PON_AQUI_TU_WEBHOOK_DE_DISCORD" in DISCORD_WEBHOOK_URL:
        print("[ADVERTENCIA] No se ha configurado un webhook válido de Discord.")
        return

    data = {"content": message}
    try:
        session.post(DISCORD_WEBHOOK_URL, json=data)
        print("[OK] Notificación enviada a Discord ✔️")
    except Exception as e:
        print(f"[ERROR] No se pudo enviar mensaje a Discord: {e}")


def fetch_page(url: str) -> Optional[str]:
    try:
        resp = session.get(url, headers=HEADERS)
        if resp.status_code != 200:
            raise Exception(f"HTTP {resp.status_code}")
        return resp.text
    except Exception as e:
        print(f"[ERROR] Error al descargar {url}: {e}")
        return None


def has_any_variant_available(html: str) -> bool:
    """
    Revisa si hay alguna variante disponible (available:true)
    y se asegura de que NO sean solo variantes excluidas (Joker Goons / Joker H).
    """
    html_lower = html.lower()

    if '"available":true' not in html_lower:
        # Ninguna variante disponible
        return False

    # Si hay available:true, revisamos si TODAS las disponibles son excluidas
    def is_excluded_near(index: int) -> bool:
        # Busca hacia atrás un poco para ver el título de la variante
        start = max(0, index - 300)
        snippet = html_lower[start:index + 50]
        for variant in EXCLUDED_VARIANTS:
            pattern = f'"title":"{variant.lower()}"'
            if pattern in snippet:
                return True
        return False

    # Bandera: encontramos al menos una variante NO excluida disponible
    found_allowed = False
    found_any_available = False

    search_str = '"available":true'
    pos = 0
    while True:
        idx = html_lower.find(search_str, pos)
        if idx == -1:
            break

        found_any_available = True

        if is_excluded_near(idx):
            # Esta available:true parece ser de una variante excluida
            print("🛑 Variante excluida disponible (se ignora).")
        else:
            found_allowed = True
            break

        pos = idx + len(search_str)

    if found_allowed:
        return True

    if found_any_available and not found_allowed:
        print("⚠️ Solo variantes excluidas disponibles por ahora.")
        return False

    return False


def is_in_stock(html: str) -> bool:
    html_lower = html.lower()
    has_in = any(k in html_lower for k in IN_STOCK_KEYWORDS)
    has_out = any(k in html_lower for k in OUT_OF_STOCK_KEYWORDS)
    return has_in and not has_out


def is_out_of_stock(html: str) -> bool:
    html_lower = html.lower()
    return any(keyword in html_lower for keyword in OUT_OF_STOCK_KEYWORDS)

# ================= PROCESO PRINCIPAL =================

def main():
    print("Iniciando monitor de YoungLA 🚀...")
    print(f"Total de productos configurados: {len(PRODUCTS)}\n")

    while True:
        for product in PRODUCTS:
            print(f"Revisando: {product['name']} -> {product['url']}")
            html = fetch_page(product["url"])

            if html is None:
                print("❌ Error al obtener la página, se pasa al siguiente.\n")
                continue

            if has_any_variant_available(html):
                msg = (
                    "🔥 RESTOCK DISPONIBLE 🔥\n"
                    f"Producto: {product['name']}\n"
                    f"Link: {product['url']}"
                )
                send_discord_message(msg)
            else:
                print("Aún sin stock aceptable ❌\n")

        # Espera al final de la ronda (después de revisar TODOS los productos)
        sleep_time = CHECK_INTERVAL_SECONDS + random.randint(1, 5)
        print(f"⏱️ Esperando {sleep_time} segundos para la siguiente ronda...\n")
        time.sleep(sleep_time)


if __name__ == "__main__":
    main()