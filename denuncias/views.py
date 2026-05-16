from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
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
