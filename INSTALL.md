# Guia de Instalação e Configuração Inicial

Este tutorial descreve o passo a passo de como preparar o seu ambiente para rodar o **Sistema Web para Registro de Denúncias Anônimas** localmente na sua máquina.

## 1. Pré-requisitos

Antes de começar, certifique-se de ter os seguintes programas instalados no seu computador:

- **[Git](https://git-scm.com/downloads)**: Ferramenta para controle de versão e download do código.
- **[Python (versão 3.10 ou superior)](https://www.python.org/downloads/)**: Linguagem de programação do backend.
  - *Atenção (Windows):* Durante a instalação do Python, certifique-se de marcar a caixa **"Add Python to PATH"** na primeira tela do instalador.

Para verificar se estão instalados corretamente, abra seu terminal (PowerShell ou CMD) e digite:
```powershell
git --version
python --version
```

## 2. Clonando o Repositório

Abra o terminal na pasta onde você deseja salvar o projeto e execute o comando abaixo para baixar o código:

```powershell
git clone https://github.com/pedrohodsouza/projeto-integrador-1.git
```

Em seguida, entre na pasta do projeto:
```powershell
cd projeto-integrador-1
```

## 3. Criando o Ambiente Virtual

O ambiente virtual serve para isolar as dependências deste projeto de outros projetos no seu computador. Dentro da pasta do projeto, execute:

**No Windows (PowerShell/CMD):**
```powershell
python -m venv venv
```

Após criar, você precisa **ativar** o ambiente virtual:
```powershell
.\venv\Scripts\activate
```
*(Quando o ambiente virtual estiver ativado, você verá `(venv)` escrito no início da linha do seu terminal).*

**Nota para Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

## 4. Instalando as Dependências

Com o ambiente virtual ativado, instale as bibliotecas necessárias para o projeto funcionar (como o Django e o Pillow para manipulação de imagens):

```powershell
pip install django pillow
```

*(No futuro, conforme o projeto evoluir, usaremos um arquivo `requirements.txt`. Por enquanto, instalamos diretamente).*

## 5. Configurando o Banco de Dados (Migrações)

O Django já vem pré-configurado para usar o SQLite, que é um banco de dados leve ideal para desenvolvimento. Precisamos criar as tabelas básicas do sistema executando as migrações:

```powershell
python manage.py migrate
```

## 6. Subindo o Servidor

Tudo pronto! Agora é só rodar o servidor local de desenvolvimento do Django:

```powershell
python manage.py runserver
```

Acesse o seu navegador de internet e digite:
**`http://127.0.0.1:8000`**

Você deverá ver a tela inicial padrão do Django, confirmando que a instalação foi um sucesso!

---
> ⚠️ **Lembrete:** Toda vez que você fechar o terminal e for trabalhar no projeto novamente, lembre-se de navegar até a pasta do projeto e ativar o ambiente virtual (`.\venv\Scripts\activate`) antes de rodar o servidor.
