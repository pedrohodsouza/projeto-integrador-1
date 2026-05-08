from django.db import models

class Denuncia(models.Model):
    CATEGORIAS = [
        ('buraco', 'Buracos em vias públicas'),
        ('iluminacao', 'Falha na iluminação pública'),
        ('lixo', 'Descarte irregular de lixo / entulho'),
        ('enchente', 'Alagamento / Enchente'),
        ('outros', 'Outros problemas urbanos'),
    ]

    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('analise', 'Em Análise'),
        ('resolvido', 'Resolvido'),
    ]

    titulo = models.CharField(max_length=100, verbose_name="Título")
    categoria = models.CharField(max_length=50, choices=CATEGORIAS, verbose_name="Categoria")
    descricao = models.TextField(verbose_name="Descrição do Problema")
    
    # Novos campos de endereço detalhados
    cep = models.CharField(max_length=9, verbose_name="CEP", default="")
    endereco = models.CharField(max_length=255, verbose_name="Endereço", default="")
    numero = models.CharField(max_length=20, verbose_name="Número", default="", blank=True)
    bairro = models.CharField(max_length=100, verbose_name="Bairro", default="")
    cidade = models.CharField(max_length=100, verbose_name="Cidade", default="")
    estado = models.CharField(max_length=2, verbose_name="Estado", default="")
    
    localizacao = models.CharField(max_length=255, verbose_name="Endereço / Localização", blank=True)
    foto = models.ImageField(upload_to='denuncias/', null=True, blank=True, verbose_name="Fotografia de Evidência")
    anonimo = models.BooleanField(default=False, verbose_name="Denunciar de forma anônima")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente', verbose_name="Status")
    resposta_gestor = models.TextField(null=True, blank=True, verbose_name="Resposta da Administração")
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        ordering = ['-criado_em']
        verbose_name = "Denúncia"
        verbose_name_plural = "Denúncias"

    def __str__(self):
        return f"{self.get_categoria_display()} - {self.titulo} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        # Concatena os campos estruturados de endereço para gerar a localização unificada
        num_str = f", {self.numero}" if self.numero else ""
        self.localizacao = f"{self.endereco}{num_str} - {self.bairro}, {self.cidade}/{self.estado} (CEP: {self.cep})"
        super().save(*args, **kwargs)

