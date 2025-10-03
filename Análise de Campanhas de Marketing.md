# Análise de Campanhas de Marketing

## 📌 Descrição


Este projeto tem como objetivo analisar o desempenho de campanhas de marketing relacionadas a cursos de **pós-graduação em Direito**, com base em dados coletados entre **agosto de 2024 e agosto de 2025**. A partir das métricas disponíveis, foram gerados insights estratégicos para otimizar campanhas futuras e aumentar a conversão de vendas

## 🎯 Objetivo do Projeto

Avaliar os resultados das campanhas de marketing e identificar:

- Quais campanhas tiveram melhor desempenho em conversão.
- Quais produtos (cursos) geraram mais interesse/vendas.
- Quais canais e abordagens são mais eficazes.
- Oportunidades de melhoria em campanhas futuras.

O foco é fornecer informações úteis para as áreas de **marketing** e **vendas**, ajudando a **aumentar a performance comercial** dos cursos ofertados.

---

## 🗂️ Fontes de Dados

- Dados internos da empresa (não públicos).
- Informações extraídas de plataformas de disparo de campanhas e CRM.
- Dados de vendas e conversões consolidadas.

Período analisado: **Agosto de 2024 a Agosto de 2025**

---

## 🛠️ Ferramentas Utilizadas

- Python 🐍
- pandas – manipulação e análise de dados
- numpy – cálculos numéricos
- re – tratamento de strings com expressões regulares
- unidecode – padronização de textos
- datetime – manipulação de datas e tempos
- dateutil.parser – conversão inteligente de strings para datas
- Jupyter Notebook – desenvolvimento e visualização da análise


---

## 🧪 Pipeline de Tratamento e Análise

Para garantir confiabilidade na análise, os dados passaram por um **pipeline modular** de 10 etapas, inspirado em boas práticas de engenharia de dados e análises exploratórias. A função `clean_campanhas(df)` implementa todos os módulos abaixo.

### 1. Carregamento e Diagnóstico
- Detecção de encoding e delimitadores (ex: Latin-1, `;`).
- Padronização de nomes de colunas.
- Diagnóstico inicial de tipos e valores ausentes.

### 2. Tipagem e Limpeza
- Conversão de campos como `% de abertura` e `% de cliques` para `float`.
- Garantia de integridade em colunas numéricas (sem negativos, coerção de tipos).

### 3. Conversão de Datas Relativas
- Transformação de strings como “22 hrs ago” para `data_envio`.
- Cálculo de `dias_atras` para permitir análises temporais.

### 4. Validação de Métricas
- Recalculo de taxas de abertura e clique a partir de contadores brutos.
- Comparação com taxas fornecidas para detectar inconsistências (> 0,5 p.p.).

### 5. Detecção de Outliers
- Aplicação de técnica IQR para identificar campanhas fora da curva.
- Flags e limites definidos para evitar distorções em médias.

### 6. Padronização de Texto e Categorização
- Normalização textual dos nomes de campanha.
- Geração de categorias temáticas (ex: “minicurso”, “comemorativa”, etc.).
- Criação de `slugs` curtos para visualizações.

### 7. Deduplicação e Agregação
- Identificação de duplicatas por campanha e data.
- Agregação opcional por campanha, somando contadores e recalculando taxas.

### 8. Métricas Derivadas (Feature Engineering)
- `engajamento_total = abertura + cliques`
- `CTOR = cliques / abertos * 100`
- `cliques_por_1k_enviados = cliques / enviados * 1000`

### 9. Preparação Temporal
- Extração de mês, semana, dia da semana e hora da `data_envio`.
- Criação de colunas temporais para gráficos e comparações sazonais.

### 10. Empacotamento Reutilizável
- Função `clean_campanhas(df)` disponível para reuso com novos datasets.
- Retorno de DataFrame limpo, validado e enriquecido.

---

## 📈 Etapas da Análise

Após tratamento dos dados, a análise seguiu os seguintes passos:

1. **Análise descritiva**  
   - Volume de campanhas por mês  
   - Comparação de taxas por canal e categoria de campanha  
   - Identificação de campanhas com maior alcance e engajamento

2. **Geração de insights estratégicos**  
   - Correlações entre datas de envio e conversão  
   - Sazonalidade da demanda por curso  
   - Avaliação de CTOR e desempenho por tipo de campanha

3. **Visualizações**  
   - Gráficos de barras (Top N campanhas, por categoria, por canal)  
   - Séries temporais de engajamento e abertura por semana/mês  
   - Mapas de calor por dia da semana e horário de envio

---

## 🔍 Principais Insights

- Campanhas com **segmentação e personalização** tiveram CTR significativamente maior.
- **Sazonalidade clara** em campanhas comemorativas (ex: Dia dos Namorados, Black Friday).
- **Parcerias institucionais e e-mail segmentado** mostraram ROI superior a outros canais.
- O tempo entre envio e clique indica a **importância do horário de disparo**.

---

## ✅ Resultado Final

A análise resultou em um relatório estratégico contendo:

- Ajustes recomendados no **calendário de campanhas**
- Sugestões de **canais de maior retorno**
- Destaque para os cursos com **maior potencial de venda**
- Tabelas e visualizações que orientam o **time comercial e de marketing**

Esse material pode ser usado como base para o planejamento de campanhas futuras e melhoria contínua da abordagem comercial.


Conformidade com a LGPD (Lei Geral de Proteção de Dados)

⚠️ Aviso Importante:
As bases de dados utilizadas neste projeto foram totalmente anonimizadas.
Nenhum dado pessoal real (como nome, CPF, e-mail, telefone ou endereço IP) foi coletado, tratado ou publicado.

Todos os exemplos e arquivos .csv presentes ou não no repositório têm finalidade exclusivamente educacional e demonstrativa, excluindo toda e quaisquer informações sensíveis.

Este projeto segue as diretrizes da Lei nº 13.709/2018 (LGPD) e boas práticas de segurança e privacidade de dados.

