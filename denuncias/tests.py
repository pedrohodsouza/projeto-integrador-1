from django.test import TestCase
from django.urls import reverse
from .models import Denuncia
from .forms import DenunciaForm

class DenunciaModelTest(TestCase):
    def setUp(self):
        self.denuncia = Denuncia.objects.create(
            titulo="Buraco na pista",
            categoria="buraco",
            descricao="Um buraco muito grande perto da calçada.",
            cep="12345-678",
            endereco="Rua Principal",
            numero="123",
            bairro="Centro",
            cidade="Cidade Modelo",
            estado="SP",
            anonimo=True
        )

    def test_denuncia_creation(self):
        self.assertEqual(self.denuncia.titulo, "Buraco na pista")
        self.assertEqual(self.denuncia.categoria, "buraco")
        self.assertTrue(self.denuncia.anonimo)
        self.assertEqual(self.denuncia.status, "pendente")
        self.assertEqual(self.denuncia.cep, "12345-678")
        self.assertEqual(self.denuncia.localizacao, "Rua Principal, 123 - Centro, Cidade Modelo/SP (CEP: 12345-678)")

    def test_denuncia_string_representation(self):
        expected_str = "Buracos em vias públicas - Buraco na pista (Pendente)"
        self.assertEqual(str(self.denuncia), expected_str)


class DenunciaFormTest(TestCase):
    def test_valid_form(self):
        data = {
            'titulo': 'Lâmpada queimada',
            'categoria': 'iluminacao',
            'descricao': 'Poste em frente à praça está sem luz.',
            'cep': '12345-678',
            'endereco': 'Praça da Matriz',
            'numero': 's/n',
            'bairro': 'Centro',
            'cidade': 'Cidade Modelo',
            'estado': 'SP',
            'anonimo': False
        }
        form = DenunciaForm(data=data)
        self.assertTrue(form.is_valid())

    def test_invalid_form_missing_required(self):
        data = {
            'titulo': '',
            'categoria': 'iluminacao',
            'descricao': 'Poste em frente à praça está sem luz.',
            'cep': '12345-678',
            'endereco': 'Praça da Matriz',
            'numero': 's/n',
            'bairro': 'Centro',
            'cidade': 'Cidade Modelo',
            'estado': 'SP',
            'anonimo': False
        }
        form = DenunciaForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('titulo', form.errors)


class DenunciaViewsTest(TestCase):
    def setUp(self):
        self.denuncia = Denuncia.objects.create(
            titulo="Lixo acumulado",
            categoria="lixo",
            descricao="Grande quantidade de lixo descartada na calçada.",
            cep="12345-678",
            endereco="Avenida Secundária",
            numero="456",
            bairro="Industrial",
            cidade="Cidade Modelo",
            estado="SP",
            anonimo=False
        )

    def test_home_view_status_code(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Registro")
        # Test calculations
        self.assertEqual(response.context['total_denuncias'], 1)
        self.assertEqual(response.context['total_pendentes'], 1)
        self.assertEqual(response.context['eficiencia'], 0)

    def test_criar_denuncia_get(self):
        response = self.client.get(reverse('criar_denuncia'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Registrar Ocorrência")

    def test_criar_denuncia_post_valid(self):
        data = {
            'titulo': 'Alagamento constante',
            'categoria': 'enchente',
            'descricao': 'Toda vez que chove, a rua fica alagada devido a bueiros entupidos.',
            'cep': '12345-678',
            'endereco': 'Rua da Baixada',
            'numero': '789',
            'bairro': 'Alagados',
            'cidade': 'Cidade Modelo',
            'estado': 'SP',
            'anonimo': True
        }
        response = self.client.post(reverse('criar_denuncia'), data=data)
        new_denuncia = Denuncia.objects.get(titulo='Alagamento constante')
        self.assertRedirects(response, reverse('sucesso_denuncia', kwargs={'pk': new_denuncia.pk}))

    def test_sucesso_denuncia_view(self):
        response = self.client.get(reverse('sucesso_denuncia', kwargs={'pk': self.denuncia.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ocorrência Registrada!")
        self.assertContains(response, self.denuncia.titulo)
        self.assertContains(response, f"CL-")

    def test_acompanhar_chamado_view_get(self):
        response = self.client.get(reverse('acompanhar_chamado'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Portal de Transparência & Ocorrências")
        # Garante que a ocorrência criada no setUp está listada no feed
        self.assertContains(response, self.denuncia.titulo)

    def test_acompanhar_chamado_view_filter_search(self):
        # Filtra por texto que existe
        response = self.client.get(reverse('acompanhar_chamado'), {'busca': 'Lixo'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.denuncia.titulo)

        # Filtra por texto que não existe
        response = self.client.get(reverse('acompanhar_chamado'), {'busca': 'Inexistente'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Nenhuma ocorrência encontrada")

    def test_acompanhar_chamado_view_redirect_protocol(self):
        # Protocolo válido deve redirecionar para a página de detalhes
        protocolo = f"CL-202605-{self.denuncia.pk}"
        response = self.client.get(reverse('acompanhar_chamado'), {'busca': protocolo})
        self.assertRedirects(response, reverse('detalhe_chamado', kwargs={'pk': self.denuncia.pk}))

    def test_detalhe_chamado_view(self):
        response = self.client.get(reverse('detalhe_chamado', kwargs={'pk': self.denuncia.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.denuncia.titulo)
        self.assertContains(response, "Protocolo: CL-")

