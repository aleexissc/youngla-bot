import time
import random
import tls_client
import os
import json
from typing import Optional

# ================= CONFIGURACIÓN =================

# 1) TU WEBHOOK DE DISCORD
DISCORD_WEBHOOK_URL = os.getenv(
    "DISCORD_WEBHOOK_URL",
    "https://discord.com/api/webhooks/1443365834893299832/m6R7PP-KjY00thKJosdhVIY7GpCD9hTkkZme27uhsjfLKZ10gvaSFNHtA0MnqGYSKvWW"
)

# 2) PRODUCTOS A MONITOREAR
#   - urls limpias (sin ?_pos, _sid, etc.)
#   - tallas en formato YoungLA: Small, Medium, Large, XLarge, XXLarge
#   - colores en minúsculas
PRODUCTS = [
    {
        "name": "Compresión negra Batman (4259)",
        "url": "https://www.youngla.com/products/4259",
        "sizes": ["Small", "Medium", "Large", "XLarge", "XXLarge"],
        "colors": ["black", "dark grey", "grey green", "off-white"],
        "no_size": False,
    },
    {
        "name": "Producto 8004",
        "url": "https://www.youngla.com/products/8004",
        "sizes": ["Small", "Medium", "Large", "XLarge", "XXLarge"],
        "colors": ["black", "dark grey", "grey green", "off-white"],
        "no_size": False,
    },
    {
        "name": "Producto 5174",
        "url": "https://www.youngla.com/products/5174",
        "sizes": ["Small", "Medium", "Large", "XLarge", "XXLarge"],
        "colors": ["bane h", "batman h"],
        "no_size": False,
    },
    {
        "name": "Producto 5173",
        "url": "https://www.youngla.com/products/5173",
        "sizes": ["Small", "Medium", "Large", "XLarge", "XXLarge"],
        "colors": ["black wash", "grey wash"],
        "no_size": False,
    },
    {
        "name": "Producto 2158",
        "url": "https://www.youngla.com/products/2158",
        "sizes": ["Small", "Medium", "Large", "XLarge"],
        "colors": ["action", "the battle black", "the battle grey"],
        "no_size": False,
    },
    {
        "name": "Producto 5209",
        "url": "https://www.youngla.com/products/5209",
        "sizes": ["Small", "Medium", "Large", "XLarge", "XXLarge"],
        "colors": ["black wash", "grey wash"],
        "no_size": False,
    },
    {
        "name": "Producto 2099",
        "url": "https://www.youngla.com/products/2099",
        "sizes": ["Small", "Medium", "Large", "XLarge", "XXLarge"],
        "colors": ["black wash", "grey wash"],
        "no_size": False,
    },
    {
        "name": "Producto 5218",
        "url": "https://www.youngla.com/products/5218",
        "sizes": ["Small", "Medium", "Large", "XLarge", "XXLarge"],
        "colors": ["black wash", "grey wash"],
        "no_size": False,
    },
    {
        "name": "Producto 5214",
        "url": "https://www.youngla.com/products/5214",
        "sizes": ["Small", "Medium", "Large", "XLarge", "XXLarge"],
        "colors": ["black"],
        "no_size": False,
    },
    {
        "name": "Producto 9062 (gorra)",
        "url": "https://www.youngla.com/products/9062",
        "sizes": [],
        "colors": ["black", "grey"],
        "no_size": True,  # sin talla, solo color
    },
    {
        "name": "Producto 4255",
        "url": "https://www.youngla.com/products/4255",
        "sizes": ["Small", "Medium", "Large", "XLarge", "XXLarge"],
        "colors": ["batman car p", "batman p"],
        "no_size": False,
    },
    {
        "name": "Producto 4065",
        "url": "https://www.youngla.com/products/4065",
        "sizes": ["Small", "Medium", "Large", "XLarge", "XXLarge"],
        "colors": ["black/blue", "black/red", "grey/blue"],
        "no_size": False,
    },
    {
        "name": "Producto 5079",
        "url": "https://www.youngla.com/products/5079",
        "sizes": ["Small", "Medium", "Large", "XLarge", "XXLarge"],
        "colors": ["black wash", "blue wash"],
        "no_size": False,
    },
    {
        "name": "Producto 2032",
        "url": "https://www.youngla.com/products/2032",
        "sizes": ["Small", "Medium", "Large", "XLarge"],
        "colors": ["black wash", "blue wash", "heather grey"],
        "no_size": False,
    },
    {
        "name": "Producto 5094",
        "url": "https://www.youngla.com/products/5094",
        "sizes": ["Small", "Medium", "Large", "XLarge", "XXLarge"],
        "colors": ["black wash"],
        "no_size": False,
    },
]

# 3) Intervalo entre rondas (segundos)
CHECK_INTERVAL_SECONDS = 60  # 1 minuto

# ================= CLIENTE HTTP =================

# Cliente TLS tipo navegador real
session = tls_client.Session(
    client_identifier="chrome_120",
    random_tls_extension_order=False
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json,text/javascript,*/*;q=0.01",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.youngla.com/",
    "Connection": "keep-alive",
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


def fetch_product_json(url: str) -> Optional[dict]:
    """
    Usa el endpoint oficial de Shopify:
    https://www.youngla.com/products/<handle>.js
    que regresa JSON con todas las variantes.
    """
    try:
        base = url.split("?", 1)[0].rstrip("/")
        json_url = base + ".js"
        resp = session.get(json_url, headers=HEADERS)
        if resp.status_code != 200:
            raise Exception(f"HTTP {resp.status_code}")
        return json.loads(resp.text)
    except Exception as e:
        print(f"[ERROR] Error al descargar JSON de {url}: {e}")
        return None


def variant_matches(variant: dict, product: dict) -> bool:
    """
    Verifica si la variante coincide con:
    - alguno de los colores configurados
    - y (si aplica) alguna de las tallas configuradas
    """
    colors_cfg = [c.lower() for c in product.get("colors", [])]
    sizes_cfg = [s.lower() for s in product.get("sizes", [])]
    no_size = bool(product.get("no_size"))

    # Texto combinado de la variante: título + opciones
    parts = [
        str(variant.get("title", "")),
        str(variant.get("option1", "")),
        str(variant.get("option2", "")),
        str(variant.get("option3", "")),
    ]
    text = " ".join(parts).lower()

    # Color
    if colors_cfg:
        if not any(color in text for color in colors_cfg):
            return False

    # Si no tiene talla (gorra), con color basta
    if no_size:
        return True

    # Talla
    if sizes_cfg:
        if not any(size in text for size in sizes_cfg):
            return False

    return True


def has_any_acceptable_variant(product_json: dict, product_cfg: dict) -> bool:
    """
    Revisa si existe al menos una variante:
    - disponible (available == True)
    - que coincida con tallas/colores de product_cfg
    """
    variants = product_json.get("variants", [])
    if not variants:
        return False

    found_any_available = False
    found_allowed = False

    for v in variants:
        available = bool(v.get("available"))
        if not available:
            continue

        found_any_available = True

        if variant_matches(v, product_cfg):
            found_allowed = True
            break

    if found_allowed:
        return True

    if found_any_available and not found_allowed:
        print("⚠️ Hay variantes disponibles pero ninguna coincide con tus tallas/colores.")
        return False

    return False

# ================= PROCESO PRINCIPAL =================

def main():
    print("Iniciando monitor de YoungLA (endpoint .js) 🚀...")
    print(f"Total de productos configurados: {len(PRODUCTS)}\n")

    while True:
        for product in PRODUCTS:
            print(f"Revisando: {product['name']} -> {product['url']}")
            data = fetch_product_json(product["url"])

            if data is None:
                print("❌ Error al obtener el JSON del producto, se pasa al siguiente.\n")
                continue

            if has_any_acceptable_variant(data, product):
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
