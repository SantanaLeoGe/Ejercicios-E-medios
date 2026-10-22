import requests
import re
from datetime import datetime, timedelta, timezone

API = "https://es-mx.wordpress.org/wp-json/wp/v2/posts?per_page=1"
TIMEOUT = 10

try:
    respuesta = requests.get(API, timeout=TIMEOUT)
    respuesta.raise_for_status()
    posts = respuesta.json()

    if not posts:
        raise ValueError("La API no devolvió publicaciones")

    post = posts[0]
    fecha = datetime.fromisoformat(
        post["modified_gmt"].replace("Z", "+00:00"))
    
    if fecha.tzinfo is None:
        fecha = fecha.replace(tzinfo=timezone.utc)

    ahora = datetime.now(timezone.utc)
    antiguedad = ahora - fecha
    api_valida = timedelta(0) <= antiguedad < timedelta(hours=24)

    print("API consultada correctamente")
    print("Última modificación:", fecha.isoformat())

    contenido = post.get("content", {}).get("rendered", "")
    urls = re.findall(r'https?://[^\s"<>]+', contenido)

    correctos = 0
    fallidos = 0

    for url in urls:
        url = url.rstrip(".,;)]}")
        try:
            r = requests.get(url, timeout=TIMEOUT)
            r.raise_for_status()

            if api_valida:
                correctos += 1
                print(f"[OK] {url}")
            else:
                fallidos += 1
                print(f"[FALLO] {url}: modificación de hace 24 horas o más")

        except requests.RequestException as e:
            fallidos += 1
            print(f"[FALLO] {url}: {e}")

    print("\n--- RESUMEN ---")
    print(f"Total de URLs: {len(urls)}")
    print(f"Correctas: {correctos}")
    print(f"Fallidas: {fallidos}")

except (requests.RequestException, ValueError, KeyError) as e:
    print(f"Error al consultar la API: {e}")