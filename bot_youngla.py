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
#    Aquí ya van TODAS tus tallas/colores normalizados
PRODUCTS = [
    {
        "name": "Compresión negra Batman (4259)",
        "url": "https://www.youngla.com/products/4259?hcUrl=%2Fes-ES",
        "sizes": ["Small", "Medium", "Large", "XLarge", "XXLarge"],
        "colors": ["black", "dark grey", "grey green", "off-white"],
        "no_size": False,
    },
    {
        "name": "Producto 8004",
        "url": "https://www.youngla.com/products/8004?hcUrl=%2Fes-ES",
        "sizes": ["Small", "Medium", "Large", "XLarge", "XXLarge"],
        "colors": ["black", "dark grey", "grey green", "off-white"],
        "no_size": False,
    },
    {
        "name": "Producto 5174",
        "url": "https://www.youngla.com/products/5174?_pos=3&_sid=7412087b5&_ss=r&variant=45034422927548&hcUrl=%2Fes-ES",
        "sizes": ["Small", "Medium", "Large", "XLarge", "XXLarge"],
        "colors": ["bane h", "batman h"],
        "no_size": False,
    },
    {
        "name": "Producto 5173",
        "url": "https://www.youngla.com/products/5173?_pos=10&_sid=7412087b5&_ss=r&hcUrl=%2Fes-ES",
        "sizes": ["Small", "Medium", "Large", "XLarge", "XXLarge"],
        "colors": ["black wash", "grey wash"],
        "no_size": False,
    },
    {
        "name": "Producto 2158",
        "url": "https://www.youngla.com/products/2158?_pos=11&_sid=7412087b5&_ss=r&hcUrl=%2Fes-ES",
        "sizes": ["Small", "Medium", "Large", "XLarge"],
        "colors": ["action", "the battle black", "the battle grey"],
        "no_size": False,
    },
    {
        "name": "Producto 5209",
        "url": "https://www.youngla.com/products/5209?_pos=14&_sid=7412087b5&_ss=r&hcUrl=%2Fes-ES",
        "sizes": ["Small", "Medium", "Large", "XLarge", "XXLarge"],
        "colors": ["black wash", "grey wash"],
        "no_size": False,
    },
    {
        "name": "Producto 2099",
        "url": "https://www.youngla.com/products/2099?_pos=25&_sid=7412087b5&_ss=r&hcUrl=%2Fes-ES",
        "sizes": ["Small", "Medium", "Large", "XLarge", "XXLarge"],
        "colors": ["black wash", "grey wash"],
        "no_size": False,
    },
    {
        "name": "Producto 5218",
        "url": "https://www.youngla.com/products/5218?_pos=26&_sid=7412087b5&_ss=r",
        "sizes": ["Small", "Medium", "Large", "XLarge", "XXLarge"],
        "colors": ["black wash", "grey wash"],
        "no_size": False,
    },
    {
        "name": "Producto 5214",
        "url": "https://www.youngla.com/products/5214?_pos=17&_sid=7412087b5&_ss=r&hcUrl=%2Fes-ES",
        "sizes": ["Small", "Medium", "Large", "XLarge", "XXLarge"],
        "colors": ["black"],
        "no_size": False,
    },
    {
        "name": "Producto 9062 (gorra)",
        "url": "https://www.youngla.com/products/9062?_pos=20&_sid=7412087b5&_ss=r&hcUrl=%2Fes-ES",
        "sizes": [],
        "colors": ["black", "grey"],
        "no_size": True,  # sin tallas, solo colores
    },
    {
        "name": "Producto 4255",
        "url": "https://www.youngla.com/products/4255?_pos=7&_sid=7412087b5&_ss=r&variant=45034407723196&hcUrl=%2Fes-ES",
        "sizes": ["Small", "Medium", "Large", "XLarge", "XXLarge"],
        "colors": ["batman car p", "batman p"],
        "no_size": False,
    },
    {
        "name": "Producto 4065",
        "url": "https://www.youngla.com/products/4065?_pos=3&_sid=1ef06ab16&_ss=r&hcUrl=%2Fes-ES",
        "sizes": ["Small", "Medium", "Large", "XLarge", "XXLarge"],
        "colors": ["black/blue", "black/red", "grey/blue"],
        "no_size": False,
    },
    {
        "name": "Producto 5079",
        "url": "https://www.youngla.com/products/5079?_pos=2&_sid=28b770262&_ss=r&hcUrl=%2Fes-ES",
        "sizes": ["Small", "Medium", "Large", "XLarge", "XXLarge"],
        "colors": ["black wash", "blue wash"],
        "no_size": False,
    },
    {
        "name": "Producto 2032",
        "url": "https://www.youngla.com/products/2032?_pos=13&_sid=28b770262&_ss=r&hcUrl=%2Fes-ES",
        "sizes": ["Small", "Medium", "Large", "XLarge"],
        "colors": ["black wash", "blue wash", "heather grey"],
        "no_size": False,
    },
    {
        "name": "Producto 5094",
        "url": "https://www.youngla.com/products/5094?_pos=12&_sid=28b770262&_ss=r&hcUrl=%2Fes-ES",
        "sizes": ["Small", "Medium", "Large", "XLarge", "XXLarge"],
        "colors": ["black wash"],
        "no_size": False,
    },
]

# 3) Intervalo entre rondas (segundos)
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

# ================= CLIENTE HTTP =================

session = tls_client.Session(
    client_identifier="chrome_124",
    random_tls_extension_order=True
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.youngla.com/",
    "Connection": "keep-alive",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Dest": "document",
    "Upgrade-Insecure-Requests": "1"
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


def variant_matches(snippet_lower: str, product: dict) -> bool:
    """
    Verifica si el bloque de variante (alrededor de '\"available\":true')
    coincide con las tallas/colores configurados para ese producto.
    """
    colors_cfg = [c.lower() for c in product.get("colors", [])]
    sizes_cfg = [s.lower() for s in product.get("sizes", [])]
    no_size = bool(product.get("no_size"))

    # Colores: si se configuraron, se exige que aparezca al menos uno
    if colors_cfg:
        if not any(color in snippet_lower for color in colors_cfg):
            return False

    # Si es producto sin talla (gorra), sólo nos importa el color
    if no_size:
        return True

    # Tallas: si se configuraron, se exige que aparezca al menos una
    if sizes_cfg:
        if not any(size in snippet_lower for size in sizes_cfg):
            return False

    return True


def has_any_variant_available(html: str, product: dict) -> bool:
    """
    Revisa si hay alguna variante disponible (\"available\":true)
    que además coincida con tallas y colores permitidos para ese producto.
    """
    html_lower = html.lower()

    if '"available":true' not in html_lower:
        # Ninguna variante disponible
        return False

    found_any_available = False
    found_allowed = False

    search_str = '"available":true'
    pos = 0

    while True:
        idx = html_lower.find(search_str, pos)
        if idx == -1:
            break

        found_any_available = True

        # Tomamos un bloque alrededor de la marca "available":true
        # para capturar el título, opciones, etc. de esa variante.
        start = max(0, idx - 400)
        end = idx + 200
        snippet_lower = html_lower[start:end]

        if variant_matches(snippet_lower, product):
            found_allowed = True
            break

        pos = idx + len(search_str)

    if found_allowed:
        return True

    if found_any_available and not found_allowed:
        print("⚠️ Sólo hay variantes disponibles que NO cumplen con tallas/colores configurados.")
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

            if has_any_variant_available(html, product):
                msg = (
                    "🔥 RESTOCK DISPONIBLE 🔥\n"
                    f"Producto: {product['name']}\n"
                    f"Link: {product['url']}"
                )
                send_discord_message(msg)
            else:
                print("Aún sin stock aceptable ❌\n")

        sleep_time = CHECK_INTERVAL_SECONDS + random.randint(1, 5)
        print(f"⏱️ Esperando {sleep_time} segundos para la siguiente ronda...\n")
        time.sleep(sleep_time)


if __name__ == "__main__":
    main()
