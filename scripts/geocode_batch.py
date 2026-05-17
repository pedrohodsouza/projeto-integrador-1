"""
Batch geocode script for Denuncia records missing latitude/longitude.

Usage (from project root, with venv active):
    pip install requests
    venv\Scripts\Activate.ps1
    py scripts\geocode_batch.py

Notes:
- Respects Nominatim usage policy by setting a custom User-Agent and sleeping 1s between requests.
- Review results before pushing to production.
"""
import os
import time
import urllib.parse

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

from denuncias.models import Denuncia

try:
    import requests
except Exception:
    print('The `requests` package is required. Install with: pip install requests')
    raise

USER_AGENT = 'CidadeLimpa-Geocoder/1.0 (seu-email@exemplo.com)'
BASE_URL = 'https://nominatim.openstreetmap.org/search'

qs = Denuncia.objects.filter(latitude__isnull=True, longitude__isnull=True)
count = qs.count()
print(f'Found {count} records without coordinates.')
if count == 0:
    print('Nothing to do.')
    raise SystemExit(0)

for idx, d in enumerate(qs, start=1):
    # Build a query string from structured fields (endereco, numero, bairro, cidade, estado, cep)
    parts = []
    if d.endereco:
        parts.append(d.endereco)
    if d.numero:
        parts[-1] = parts[-1] + (', ' + d.numero)
    if d.bairro:
        parts.append(d.bairro)
    if d.cidade:
        parts.append(d.cidade)
    if d.estado:
        parts.append(d.estado)
    if d.cep:
        parts.append(d.cep)
    q = ', '.join([p for p in parts if p])
    if not q:
        q = d.localizacao or d.titulo

    params = {'format': 'jsonv2', 'q': q, 'limit': 1}
    url = BASE_URL + '?' + urllib.parse.urlencode(params)
    print(f'[{idx}/{count}] Searching: {q}')
    try:
        r = requests.get(url, headers={'User-Agent': USER_AGENT}, timeout=10)
        r.raise_for_status()
        data = r.json()
        if data:
            lat = float(data[0]['lat'])
            lon = float(data[0]['lon'])
            d.latitude = lat
            d.longitude = lon
            d.save(update_fields=['latitude', 'longitude', 'atualizado_em'])
            print(f'  -> OK: {lat}, {lon} (saved)')
        else:
            print('  -> No result')
    except Exception as e:
        print('  -> Error:', e)

    # Be polite to the Nominatim service
    time.sleep(1.1)

print('Done.')
