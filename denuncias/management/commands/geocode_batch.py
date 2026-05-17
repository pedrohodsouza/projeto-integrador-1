from django.core.management.base import BaseCommand
import time
import urllib.parse

class Command(BaseCommand):
    help = 'Batch geocode Denuncia records missing latitude/longitude using Nominatim'

    def handle(self, *args, **options):
        try:
            import requests
        except Exception:
            self.stderr.write('The `requests` package is required. Install with: pip install requests')
            return

        from denuncias.models import Denuncia

        USER_AGENT = 'CidadeLimpa-Geocoder/1.0 (seu-email@exemplo.com)'
        BASE_URL = 'https://nominatim.openstreetmap.org/search'

        qs = Denuncia.objects.filter(latitude__isnull=True, longitude__isnull=True)
        count = qs.count()
        self.stdout.write(f'Found {count} records without coordinates.')
        if count == 0:
            return

        for idx, d in enumerate(qs, start=1):
            parts = []
            if d.endereco:
                parts.append(d.endereco)
            if d.numero:
                if parts:
                    parts[-1] = parts[-1] + (', ' + d.numero)
                else:
                    parts.append(d.numero)
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
            self.stdout.write(f'[{idx}/{count}] Searching: {q}')
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
                    self.stdout.write(f'  -> OK: {lat}, {lon} (saved)')
                else:
                    self.stdout.write('  -> No result')
            except Exception as e:
                self.stderr.write(f'  -> Error: {e}')

            time.sleep(1.1)

        self.stdout.write('Done.')
