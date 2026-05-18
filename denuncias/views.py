from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponseForbidden
from .models import Denuncia
from .forms import DenunciaForm, GestaoForm
import json
import urllib.request
import urllib.parse

def _geocode(endereco, numero, bairro, cidade, estado, cep):
    parts = [p for p in [endereco, numero, bairro, cidade, estado, cep] if p]
    if not parts:
        return None, None
    query = urllib.parse.urlencode({'q': ', '.join(parts), 'format': 'json', 'limit': 1})
    url = f'https://nominatim.openstreetmap.org/search?{query}'
    req = urllib.request.Request(url, headers={'User-Agent': 'VozUrbana/1.0 (projeto-integrador)'})
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            data = json.loads(r.read())
            if data:
                return float(data[0]['lat']), float(data[0]['lon'])
    except Exception:
        pass
    return None, None

def home(request):
    zona_sel = request.GET.get('zona', '').strip()

    qs = Denuncia.objects.all()
    if zona_sel:
        qs = qs.filter(zona=zona_sel)

    total_denuncias = qs.count()
    total_resolvidos = qs.filter(status='resolvido').count()
    total_analise = qs.filter(status='analise').count()
    total_pendentes = qs.filter(status='pendente').count()

    ranking = []
    for cat_cod, cat_lbl in Denuncia.CATEGORIAS:
        qtd = qs.filter(categoria=cat_cod).count()
        if qtd > 0:
            ranking.append({'nome': cat_lbl, 'qtd': qtd})
    ranking = sorted(ranking, key=lambda k: k['qtd'], reverse=True)

    eficiencia = 0
    if total_denuncias > 0:
        eficiencia = round((total_resolvidos / total_denuncias) * 100)

    # Módulo 2 — Consulta: feed com filtros
    denuncias_feed = Denuncia.objects.all()
    filtro_categoria = request.GET.get('categoria', '')
    filtro_status = request.GET.get('status', '')

    if filtro_categoria:
        denuncias_feed = denuncias_feed.filter(categoria=filtro_categoria)
    if filtro_status:
        denuncias_feed = denuncias_feed.filter(status=filtro_status)

    categorias_choices = [
        {'cod': cod, 'lbl': lbl, 'selected': (cod == filtro_categoria)}
        for cod, lbl in Denuncia.CATEGORIAS
    ]
    status_choices_home = [
        {'cod': cod, 'lbl': lbl, 'selected': (cod == filtro_status)}
        for cod, lbl in Denuncia.STATUS_CHOICES
    ]

    # Módulo 4 — Indicadores: dados geográficos e zonas
    zonas = Denuncia.ZONAS

    # Contagem por zona direto do campo zona (confiável, independe de coordenadas)
    zone_counts_list = [
        {'code': code, 'label': label, 'count': qs.filter(zona=code).count()}
        for code, label in Denuncia.ZONAS
    ]

    # Dados geográficos para o mapa Leaflet (apenas denúncias com coordenadas)
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

    context = {
        'total_denuncias': total_denuncias,
        'total_resolvidos': total_resolvidos,
        'total_analise': total_analise,
        'total_pendentes': total_pendentes,
        'ranking': ranking[:3],
        'eficiencia': eficiencia,
        # Módulo 2 — Consulta
        'denuncias_feed': denuncias_feed,
        # Módulo 3 — Gestão (feed inline)
        'denuncias': Denuncia.objects.all(),
        'categorias_choices': categorias_choices,
        'status_choices': status_choices_home,
        'filtro_categoria': filtro_categoria,
        'filtro_status': filtro_status,
        # Módulo 4 — Indicadores
        'zonas': zonas,
        'zona_selecionada': zona_sel,
        'zone_counts_list': zone_counts_list,
        'denuncias_geo': json.dumps(denuncias_geo),
    }
    return render(request, 'home.html', context)

def criar_denuncia(request):
    if request.method == 'POST':
        form = DenunciaForm(request.POST, request.FILES)
        if form.is_valid():
            denuncia = form.save(commit=False)
            if not denuncia.latitude or not denuncia.longitude:
                lat, lng = _geocode(
                    denuncia.endereco, denuncia.numero, denuncia.bairro,
                    denuncia.cidade, denuncia.estado, denuncia.cep
                )
                if lat and lng:
                    denuncia.latitude = lat
                    denuncia.longitude = lng
            denuncia.save()
            return redirect('sucesso_denuncia', pk=denuncia.pk)
    else:
        form = DenunciaForm()
    return render(request, 'denuncias/criar_denuncia.html', {'form': form})

def sucesso_denuncia(request, pk):
    denuncia = get_object_or_404(Denuncia, pk=pk)
    return render(request, 'denuncias/sucesso.html', {'denuncia': denuncia})

def detalhe_denuncia(request, pk):
    denuncia = get_object_or_404(Denuncia, pk=pk)
    return render(request, 'denuncias/detalhe.html', {'denuncia': denuncia})

def acompanhar_chamado(request):
    busca = request.GET.get('busca', '').strip()
    categoria = request.GET.get('categoria', '').strip()
    status = request.GET.get('status', '').strip()

    if busca:
        if busca.upper().startswith('CL-') and '-' in busca:
            partes = busca.split('-')
            id_str = partes[-1]
            if id_str.isdigit():
                pk = int(id_str)
                if Denuncia.objects.filter(pk=pk).exists():
                    return redirect('detalhe_chamado', pk=pk)

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


# ── Módulo de Gestão ────────────────────────────────────────────────────────

@login_required
def gestao_lista(request):
    if not request.user.is_staff:
        return HttpResponseForbidden('Acesso restrito a administradores.')

    denuncias = Denuncia.objects.all()
    status_filter = request.GET.get('status', '')
    categoria_filter = request.GET.get('categoria', '')
    busca = request.GET.get('busca', '')

    if status_filter:
        denuncias = denuncias.filter(status=status_filter)
    if categoria_filter:
        denuncias = denuncias.filter(categoria=categoria_filter)
    if busca:
        denuncias = denuncias.filter(Q(titulo__icontains=busca) | Q(descricao__icontains=busca))

    context = {
        'denuncias': denuncias,
        'status_filter': status_filter,
        'categoria_filter': categoria_filter,
        'busca': busca,
        'status_choices': Denuncia.STATUS_CHOICES,
        'categorias': Denuncia.CATEGORIAS,
        'total': Denuncia.objects.count(),
        'total_pendentes': Denuncia.objects.filter(status='pendente').count(),
        'total_analise': Denuncia.objects.filter(status='analise').count(),
        'total_resolvidos': Denuncia.objects.filter(status='resolvido').count(),
    }
    return render(request, 'denuncias/gestao_lista.html', context)


@login_required
def gestao_detalhe(request, pk):
    if not request.user.is_staff:
        return HttpResponseForbidden('Acesso restrito a administradores.')

    denuncia = get_object_or_404(Denuncia, pk=pk)

    if request.method == 'POST':
        form = GestaoForm(request.POST, instance=denuncia)
        if form.is_valid():
            form.save()
            messages.success(request, 'Denúncia atualizada com sucesso.')
            return redirect('gestao_detalhe', pk=pk)
    else:
        form = GestaoForm(instance=denuncia)

    return render(request, 'denuncias/gestao_detalhe.html', {'denuncia': denuncia, 'form': form})


@login_required
def gestao_excluir(request, pk):
    if not request.user.is_staff:
        return HttpResponseForbidden('Acesso restrito a administradores.')

    denuncia = get_object_or_404(Denuncia, pk=pk)
    if request.method == 'POST':
        titulo = denuncia.titulo
        denuncia.delete()
        messages.success(request, f'Denúncia "{titulo}" excluída com sucesso.')
        return redirect('gestao_lista')
    return redirect('gestao_detalhe', pk=pk)
