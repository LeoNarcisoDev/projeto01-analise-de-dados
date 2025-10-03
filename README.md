# 🧠 Projeto: Análise e Limpeza de Dados com Python  


⚠️ Aviso Importante:
As bases de dados utilizadas neste projeto foram totalmente anonimizadas.
Nenhum dado pessoal real (como nome, CPF, e-mail, telefone ou endereço IP) foi coletado, tratado ou publicado.

Todos os exemplos e arquivos .csv presentes ou não no repositório têm finalidade exclusivamente educacional e demonstrativa, excluindo toda e quaisquer informações sensíveis.

Este projeto segue as diretrizes da Lei nº 13.709/2018 (LGPD) e boas práticas de segurança e privacidade de dados.


### Campanhas de Marketing & Relatórios de Vendas
📊 **Resumo**  
Este repositório contém dois pipelines completos em **Python** desenvolvidos para automatizar a **limpeza, padronização e análise de dados** de campanhas de marketing (e-mail) e relatórios de vendas, transformando bases brutas em **insights estratégicos e gráficos de performance**.

Foram criados dois scripts independentes, otimizados para performance, clareza e reuso em diferentes bases de dados:

- `vendas_analysis.py` → Análise de faturamento e Pareto de produtos  
- `campanhas.py` → Limpeza e análise de campanhas de e-mail marketing  

---

## 🚀 Tecnologias Utilizadas

| Categoria | Ferramentas |
|------------|-------------|
| 🐍 Linguagem | **Python 3.12** |
| 📦 Bibliotecas | `pandas`, `numpy`, `matplotlib`, `seaborn`, `regex`, `unidecode`, `dateutil` |
| 📄 Entrada | Arquivos `.csv` (separador `;`, encoding `latin1` / `cp1252`) |
| 💾 Saída | Relatórios `.csv` + gráficos `.png` e dashboards interativos |

---

## 📈 1️⃣ Análise de Vendas — Produtos & Faturamento

### ⚙️ Funcionalidades
- Leitura robusta de bases CSV (autoajuste de encoding e separador)  
- Conversão e padronização de colunas numéricas e datas  
- Cálculo de:
  - 💰 **Faturamento Mensal**
  - 📉 **Inadimplência (Pago < Valor Total)**
  - 🔍 **Pareto de Produtos (80/20)**
- Agrupamento por produto e período
- Visualizações automáticas com `matplotlib` e `seaborn`:
  - Faturamento Mensal  
  - Status de Pagamento  
  - Distribuição por Meio de Pagamento  
  - Volume de Vendas por Produto  

### 💡 Insights
- Identificação dos produtos responsáveis por **80% da receita**  
- Visualização da **sazonalidade de faturamento**  
- Diagnóstico rápido de **inadimplência** e gargalos de conversão  

---

## 💌 2️⃣ Campanhas POSESA — E-mail Marketing Analytics

### 🧩 Pipeline de Limpeza e Agrupamento
1. **Padronização textual** com `regex` + `unidecode`  
   - Normalização de acentos, ruídos e duplicidades.  
   - Agrupamento automático de campanhas semelhantes:
     > Exemplo: “MiniCurso IA”, “Pós Empresarial”, “Campanha Black Friday” etc.
2. **Interpretação de datas relativas e absolutas**  
   - Ex.: “22 hrs ago”, “3 weeks ago”, “Thu, Jul 24, 2025”.
3. **Agrupamento e cálculo de métricas:**
   - `% Abertura`, `% Cliques`, `CTR Real`, `Engajamento Total`
4. **Visualizações:**
   - Volume de Envios  
   - Taxas de Abertura e Cliques  
   - Evolução Temporal  
   - Pareto de Cliques  

### 📊 Métricas Derivadas
| Métrica | Descrição |
|----------|------------|
| **CTR Real** | Cliques ÷ Abertos × 100 — mede engajamento de quem abriu |
| **Engajamento Total** | (Abertos + Cliques) ÷ Enviados × 100 |
| **Taxa de Abertura** | Abertos ÷ Enviados × 100 |
| **Taxa de Cliques** | Cliques ÷ Enviados × 100 |

### 💡 Insights Estratégicos
- Ranking automático das campanhas mais engajadas  
- Detecção de **quedas sazonais** nas taxas de clique  
- Base sólida para otimizar futuras campanhas  

---


