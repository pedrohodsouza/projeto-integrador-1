from django.shortcuts import render, redirect, get_object_or_404
from .models import Denuncia
from .forms import DenunciaForm

def home(request):
    # Estatísticas simples para o Módulo de Inteligência (Indicadores) na Home
    total_denuncias = Denuncia.objects.count()
    total_resolvidos = Denuncia.objects.filter(status='resolvido').count()
    total_analise = Denuncia.objects.filter(status='analise').count()
    total_pendentes = Denuncia.objects.filter(status='pendente').count()

    # Ranking de categorias com mais ocorrências
    categorias_nome = dict(Denuncia.CATEGORIAS)
    ranking = []
    for cat_cod, cat_lbl in Denuncia.CATEGORIAS:
        qtd = Denuncia.objects.filter(categoria=cat_cod).count()
        if qtd > 0:
            ranking.append({'nome': cat_lbl, 'qtd': qtd})
    # Ordena pelo maior número de ocorrências
    ranking = sorted(ranking, key=lambda k: k['qtd'], reverse=True)

    # Porcentagem de resolução das demandas
    eficiencia = 0
    if total_denuncias > 0:
        eficiencia = round((total_resolvidos / total_denuncias) * 100)

    # Lógica do Feed e Filtros (Módulo 2)
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
    status_choices = [
        {'cod': cod, 'lbl': lbl, 'selected': (cod == filtro_status)}
        for cod, lbl in Denuncia.STATUS_CHOICES
    ]

    context = {
        'total_denuncias': total_denuncias,
        'total_resolvidos': total_resolvidos,
        'total_analise': total_analise,
        'total_pendentes': total_pendentes,
        'ranking': ranking[:3], # Top 3 categorias
        'eficiencia': eficiencia,
        # Variáveis do Módulo 2
        'denuncias_feed': denuncias_feed,
        'categorias_choices': categorias_choices,
        'status_choices': status_choices,
        'filtro_categoria': filtro_categoria,
        'filtro_status': filtro_status,
    }
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

def detalhe_denuncia(request, pk):
    denuncia = get_object_or_404(Denuncia, pk=pk)
    return render(request, 'denuncias/detalhe.html', {'denuncia': denuncia})
