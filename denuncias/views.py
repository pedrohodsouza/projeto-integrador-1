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

    context = {
        'total_denuncias': total_denuncias,
        'total_resolvidos': total_resolvidos,
        'total_analise': total_analise,
        'total_pendentes': total_pendentes,
        'ranking': ranking[:3], # Top 3 categorias
        'eficiencia': eficiencia,
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
