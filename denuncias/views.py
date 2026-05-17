from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from .models import Denuncia
from .forms import DenunciaForm
import json

def home(request):
    # Permite filtrar indicadores por zona via query params (remoção do filtro por município)
    zona_sel = request.GET.get('zona', '').strip()

    qs = Denuncia.objects.all()
    if zona_sel:
        qs = qs.filter(zona=zona_sel)

    # Estatísticas a partir do queryset filtrado
    total_denuncias = qs.count()
    total_resolvidos = qs.filter(status='resolvido').count()
    total_analise = qs.filter(status='analise').count()
    total_pendentes = qs.filter(status='pendente').count()

    # Ranking de categorias com mais ocorrências (no escopo filtrado)
    categorias_nome = dict(Denuncia.CATEGORIAS)
    ranking = []
    for cat_cod, cat_lbl in Denuncia.CATEGORIAS:
        qtd = qs.filter(categoria=cat_cod).count()
        if qtd > 0:
            ranking.append({'nome': cat_lbl, 'qtd': qtd})
    ranking = sorted(ranking, key=lambda k: k['qtd'], reverse=True)

    eficiencia = 0
    if total_denuncias > 0:
        eficiencia = round((total_resolvidos / total_denuncias) * 100)

    # Lista de zonas disponíveis (filtro por município removido)
    zonas = Denuncia.ZONAS

    # Contagem por zona (para o mapa simplificado)
    zone_source_qs = Denuncia.objects.all()
    zone_counts = {code: zone_source_qs.filter(zona=code).count() for code, _ in zonas}
    # Para o template, montar uma lista mais direta: [{'code','label','count'}, ...]
    zone_counts_list = []
    for code, label in zonas:
        zone_counts_list.append({'code': code, 'label': label, 'count': zone_counts.get(code, 0)})

    context = {
        'total_denuncias': total_denuncias,
        'total_resolvidos': total_resolvidos,
        'total_analise': total_analise,
        'total_pendentes': total_pendentes,
        'ranking': ranking[:3], # Top 3 categorias
        'eficiencia': eficiencia,
        'zonas': zonas,
        'zone_counts': zone_counts,
        'zone_counts_list': zone_counts_list,
        'zona_selecionada': zona_sel,
    }

    # Dados geográficos para o mapa: apenas denúncias que possuam lat/lng
    denuncias_geo_qs = qs.filter(latitude__isnull=False, longitude__isnull=False)
    denuncias_geo = []
    for d in denuncias_geo_qs:
        denuncias_geo.append({
            'pk': d.pk,
            'titulo': d.titulo,
            'categoria': d.get_categoria_display(),
            'status': d.status,
            'lat': d.latitude,
            'lng': d.longitude,
            'localizacao': d.localizacao,
            'endereco': d.endereco,
            'numero': d.numero,
            'bairro': d.bairro,
            'cidade': d.cidade,
            'estado': d.estado,
            'cep': d.cep,
        })

    # Derivar contagens por zona com base em coordenadas (Norte/Leste/Sul/Oeste/Centro/Outra)
    import math

    def haversine_km(lat1, lon1, lat2, lon2):
        R = 6371.0
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*(math.sin(dlambda/2)**2)
        return R * (2 * math.atan2(math.sqrt(a), math.sqrt(1-a)))

    def bearing_deg(lat1, lon1, lat2, lon2):
        # returns bearing from point1 to point2, degrees from North
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dlambda = math.radians(lon2 - lon1)
        x = math.sin(dlambda) * math.cos(phi2)
        y = math.cos(phi1)*math.sin(phi2) - math.sin(phi1)*math.cos(phi2)*math.cos(dlambda)
        theta = math.degrees(math.atan2(x, y))
        bearing = (theta + 360) % 360
        return bearing

    # Prepare counts
    derived_counts = {'norte': 0, 'sul': 0, 'leste': 0, 'oeste': 0, 'centro': 0, 'outra': 0}

    points = [(d['lat'], d['lng']) for d in denuncias_geo]
    # compute centroid of available points
    if points:
        mean_lat = sum(p[0] for p in points) / len(points)
        mean_lng = sum(p[1] for p in points) / len(points)
        # threshold for 'centro' in km (about ~2km)
        center_threshold_km = 2.0

        for lat, lng in points:
            dist = haversine_km(mean_lat, mean_lng, lat, lng)
            if dist <= center_threshold_km:
                derived_counts['centro'] += 1
            else:
                b = bearing_deg(mean_lat, mean_lng, lat, lng)
                # map bearing to cardinal directions
                if (b >= 315 or b < 45):
                    derived_counts['norte'] += 1
                elif 45 <= b < 135:
                    derived_counts['leste'] += 1
                elif 135 <= b < 225:
                    derived_counts['sul'] += 1
                else:
                    derived_counts['oeste'] += 1
    # missing geo points count as 'outra'
    total_with_geo = len(points)
    outra_count = total_denuncias - total_with_geo
    if outra_count > 0:
        derived_counts['outra'] += outra_count

    # Build zone_counts_list in the order expected by the template
    zone_counts_list = [
        {'code': 'norte', 'label': 'Norte', 'count': derived_counts.get('norte', 0)},
        {'code': 'sul', 'label': 'Sul', 'count': derived_counts.get('sul', 0)},
        {'code': 'leste', 'label': 'Leste', 'count': derived_counts.get('leste', 0)},
        {'code': 'oeste', 'label': 'Oeste', 'count': derived_counts.get('oeste', 0)},
        {'code': 'centro', 'label': 'Centro', 'count': derived_counts.get('centro', 0)},
        {'code': 'outra', 'label': 'Outra/Não informado', 'count': derived_counts.get('outra', 0)},
    ]

    context['denuncias_geo'] = json.dumps(denuncias_geo)
    context['zone_counts_list'] = zone_counts_list
    return render(request, 'home.html', context)

def criar_denuncia(request):
    if request.method == 'POST':
        form = DenunciaForm(request.POST, request.FILES)
        if form.is_valid():
            denuncia = form.save()
            return redirect('sucesso_denuncia', pk=denuncia.pk)
    else:
        form = DenunciaForm()
    return render(request, 'denuncias/criar_denuncia.html', {'form': form})

def sucesso_denuncia(request, pk):
    denuncia = get_object_or_404(Denuncia, pk=pk)
    return render(request, 'denuncias/sucesso.html', {'denuncia': denuncia})

def acompanhar_chamado(request):
    busca = request.GET.get('busca', '').strip()
    categoria = request.GET.get('categoria', '').strip()
    status = request.GET.get('status', '').strip()

    # Se o usuário digitou algo com cara de protocolo, ex: CL-202605-12
    # redirecionamos diretamente para os detalhes!
    if busca:
        if busca.upper().startswith('CL-') and '-' in busca:
            partes = busca.split('-')
            id_str = partes[-1]
            if id_str.isdigit():
                pk = int(id_str)
                if Denuncia.objects.filter(pk=pk).exists():
                    return redirect('detalhe_chamado', pk=pk)

    # Caso contrário, lista todas as denúncias (ordenadas por Meta: mais recentes primeiro)
    denuncias = Denuncia.objects.all()

    if busca:
        denuncias = denuncias.filter(
            Q(titulo__icontains=busca) |
            Q(descricao__icontains=busca) |
            Q(localizacao__icontains=busca) |
            Q(cep__icontains=busca)
        )

    if categoria:
        denuncias = denuncias.filter(categoria=categoria)

    if status:
        denuncias = denuncias.filter(status=status)

    context = {
        'denuncias': denuncias,
        'busca': busca,
        'categoria_selecionada': categoria,
        'status_selecionada': status,
        'categorias': Denuncia.CATEGORIAS,
        'statuses': Denuncia.STATUS_CHOICES,
    }
    return render(request, 'denuncias/acompanhar.html', context)

def detalhe_chamado(request, pk):
    denuncia = get_object_or_404(Denuncia, pk=pk)
    return render(request, 'denuncias/detalhe.html', {'denuncia': denuncia})

def detalhe_denuncia(request, pk):
    """Compatibilidade com URLs que usam `detalhe_denuncia`.

    Mantém a mesma lógica de `detalhe_chamado`.
    """
    denuncia = get_object_or_404(Denuncia, pk=pk)
    return render(request, 'denuncias/detalhe.html', {'denuncia': denuncia})
