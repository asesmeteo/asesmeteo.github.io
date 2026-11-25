"""Envía una alerta de ASES vía OneSignal.

Uso:
  export ONESIGNAL_APP_ID="..."
  export ONESIGNAL_API_KEY="..."      # clave PRIVADA, nunca en el repositorio

  python enviar_alerta.py -t "Nevadas en Agua Negra" -m "Desde las 18 h, 20 cm." \
      --zonas agua_negra alta_cordillera --tipo nevadas --url https://tuusuario.github.io
  python enviar_alerta.py -t "Prueba" -m "Mensaje de prueba" --todos
"""
import argparse
import os
import sys

import requests

API = "https://api.onesignal.com/notifications"


def construir_filtros(zonas, tipo):
    """(zona1 Y tipo) O (zona2 Y tipo) ... Dentro de un grupo, los filtros son AND."""
    filtros = []
    for i, z in enumerate(zonas):
        if i:
            filtros.append({"operator": "OR"})
        filtros.append({"field": "tag", "key": f"zona_{z}", "relation": "=", "value": "1"})
        if tipo:
            filtros.append({"field": "tag", "key": f"tipo_{tipo}", "relation": "=", "value": "1"})
    return filtros


def main():
    p = argparse.ArgumentParser()
    p.add_argument("-t", "--titulo", required=True)
    p.add_argument("-m", "--mensaje", required=True)
    p.add_argument("--zonas", nargs="*", default=[])
    p.add_argument("--tipo")
    p.add_argument("--url")
    p.add_argument("--todos", action="store_true", help="enviar a todos los suscriptos")
    a = p.parse_args()

    app_id = os.environ.get("ONESIGNAL_APP_ID")
    api_key = os.environ.get("ONESIGNAL_API_KEY")
    if not app_id or not api_key:
        sys.exit("Faltan las variables ONESIGNAL_APP_ID y ONESIGNAL_API_KEY.")

    cuerpo = {
        "app_id": app_id,
        "target_channel": "push",
        "headings": {"en": a.titulo, "es": a.titulo},
        "contents": {"en": a.mensaje, "es": a.mensaje},
    }
    if a.url:
        cuerpo["url"] = a.url
    if a.todos:
        cuerpo["included_segments"] = ["Subscribed Users"]
    else:
        if not a.zonas:
            sys.exit("Indicá --zonas o usá --todos.")
        cuerpo["filters"] = construir_filtros(a.zonas, a.tipo)

    r = requests.post(
        API,
        json=cuerpo,
        headers={"Authorization": f"Key {api_key}", "Content-Type": "application/json"},
        timeout=30,
    )
    print(r.status_code, r.text)


if __name__ == "__main__":
    main()
