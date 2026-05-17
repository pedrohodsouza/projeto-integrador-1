# 📑 Especificação de Módulos e Funcionalidades

Este documento serve como o roteiro de desenvolvimento do Sistema de Denúncias Urbanas. Utilize os checklists abaixo para marcar o progresso conforme avançarmos.

---

## 🏗️ 1. Módulo de Registro (Interface do Cidadão)
**Objetivo:** Permitir que qualquer morador registre um problema de forma rápida e intuitiva.

- [x] **Formulário de Cadastro**: Criar campos para Título, Categoria, Descrição e Localização.
- [x] **Seleção de Categoria**: Menu suspenso com opções (Buracos, Lixo, Iluminação, Enchentes, etc.).
- [x] **Upload de Evidência**: Campo para envio de 1 fotografia da ocorrência.
- [x] **Sistema de Anonimato**: Checkbox "Denunciar anonimamente" que oculta o autor no feed público.
- [x] **Validação de Dados**: Garantir que campos obrigatórios não sejam enviados vazios.
- [x] **Confirmação de Envio**: Mensagem de sucesso amigável após o salvamento.

---

## 🔍 2. Módulo de Consulta (Portal de Transparência)
**Objetivo:** Exibir as demandas da comunidade de forma organizada para evitar duplicidade.

- [x] **Feed Cronológico**: Listagem de denúncias da mais recente para a mais antiga.
- [x] **Cards de Visualização**: Exibir miniatura da foto, título, categoria e selo de status.
- [x] **Filtros de Pesquisa**: Permitir filtrar o feed por Categoria ou por Status (Ex: "Somente Resolvidos").
- [x] **Página de Detalhes**: Visualização completa da denúncia, incluindo a descrição e a foto ampliada.
- [x] **Identificação de Status**: Cores diferentes para cada estado (Pendente = Amarelo, Resolvido = Verde, etc.).

---

## 🛠️ 3. Módulo de Gestão (Painel Administrativo)
**Objetivo:** Ferramenta interna para que os responsáveis gerenciem as ordens de serviço.

- [ ] **Lista Geral de Gestão**: Tabela administrativa com todas as denúncias e datas de recebimento.
- [ ] **Fluxo de Status**: Capacidade de alterar o status de "Pendente" para "Em Análise" ou "Resolvido".
- [ ] **Resposta Administrativa**: Campo para o gestor escrever uma breve nota sobre a resolução.
- [ ] **Moderação de Conteúdo**: Ferramenta para excluir ou editar denúncias com termos impróprios.
- [ ] **Segurança**: Acesso restrito apenas para usuários administradores (Login/Senha).

---

## 📊 4. Módulo de Inteligência (Indicadores)
**Objetivo:** Gerar visão macro dos problemas urbanos (Requisito do Relatório Técnico).

- [ ] **Contadores de Impacto**: Exibição do total de denúncias recebidas e total de problemas resolvidos.
- [ ] **Ranking de Problemas**: Identificar qual categoria possui mais ocorrências (Ex: Top 1 = Buracos).
- [ ] **Resumo de Eficiência**: Mostrar a porcentagem de resolução das demandas.
- [ ] **Exportação Simples**: (Opcional) Capacidade de imprimir um resumo das ocorrências.
