from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponseForbidden
from .models import Denuncia
from .forms import DenunciaForm, GestaoForm

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
        'ranking': ranking[:3],
        'eficiencia': eficiencia,
        'denuncias': Denuncia.objects.all(),
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

    context = {
        'denuncia': denuncia,
        'form': form,
    }
    return render(request, 'denuncias/gestao_detalhe.html', context)


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
