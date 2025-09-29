# Scripts extraídos e anotados – Relatório de Vendas (POSESA)

> Código consolidado a partir do notebook `relatório_vendas_posesa.ipynb`, com comentários e insights sobre a função de cada bloco.

## 📦 Imports & Configuração

**Objetivo do bloco:**
- Preparar ambiente de execução e dependências.

**Código:**

<details><summary>Cell #1</summary>

```python
import pandas as pd
```

</details>


<details><summary>Cell #2</summary>

```python
import numpy as np
```

</details>

**Insights práticos:**
- Centralizar imports facilita replicabilidade e evita conflitos de versão.
- Defina seeds e estilos de plot (quando usados) no início para reprodutibilidade.


## 🧪 Cálculos & Análises Pontuais

**Objetivo do bloco:**
- Executar análises pontuais específicas.

**Código:**

<details><summary>Cell #3</summary>

```python
from pandas import DataFrame
```

</details>


<details><summary>Cell #5</summary>

```python
vend_df
```

</details>


<details><summary>Cell #6</summary>

```python
vend_df.drop('ITEM_COMPRA', axis=1, inplace=True)
vend_df.drop('DESCONTO VOUCHERS', axis=1, inplace=True)
vend_df.drop('CRÉDITOS DESCONTO', axis=1, inplace=True)
vend_df.drop('CPF', axis=1, inplace=True)
```

</details>


<details><summary>Cell #7</summary>

```python
vend_df
```

</details>


<details><summary>Cell #8</summary>

```python
vend_df.columns = [
    'Aprovacao', 'Usuarios', 'Produto', 'Pgto', 'Valor', 'Pago'    
]

vend_df
```

</details>


<details><summary>Cell #13</summary>

```python
vend_df
```

</details>


<details><summary>Cell #21</summary>

```python
df
```

</details>

**Insights práticos:**
- Registre hipóteses próximas ao código para contextualizar resultados.
- Compare sempre métricas relativas (percentuais) para neutralizar efeito de volume.


## 🗂️ Carregamento de Dados (CSV/SQL/Excel)

**Objetivo do bloco:**
- Conectar às fontes e materializar dados de trabalho.

**Código:**

<details><summary>Cell #4</summary>

```python
vend_df = pd.read_csv("base_de_dados.csv", encoding='cp1252', sep=';')
```

</details>

**Insights práticos:**
- Prefira conexões via `SQLAlchemy` para melhor gestão de credenciais e performance.
- Valide schema/colunas logo após carregar para detectar quebras precocemente.


## 🧹 Limpeza & Padronização

**Objetivo do bloco:**
- Tratar tipos, padronizar campos e garantir integridade.

**Código:**

<details><summary>Cell #9</summary>

```python
vend_df['Valor'] = (
    vend_df['Valor']
    .astype(str)
    .str.replace(',', '.', regex=False)
    .astype(float)
)
```

</details>


<details><summary>Cell #10</summary>

```python
vend_df['Pago'] = (
    vend_df['Pago']
    .astype(str)
    .str.replace(',', '.',  regex=False)
    .astype(float)
)
```

</details>


<details><summary>Cell #12</summary>

```python
vend_df['Pgto'] = vend_df['Pgto'].apply(renomear_campos)
```

</details>


<details><summary>Cell #17</summary>

```python
# Converte a coluna de datas corretamente
df["Aprovacao"] = pd.to_datetime(df["Aprovacao"], dayfirst=True)
df["Mes"] = df["Aprovacao"].dt.to_period("M").astype(str)

# Agrupamento mensal
df_mensal = df.groupby("Mes")["Pago"].sum().reset_index()

# Gráfico atualizado
plt.figure(figsize=(14,6))
sns.barplot(
    x="Mes", y="Pago", data=df_mensal,
    hue="Mes", palette="crest", legend=False
)
plt.title("Faturamento Mensal")
plt.ylabel("Total Pago (R$)")
plt.xlabel("Mês")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
```

</details>


<details><summary>Cell #19</summary>

```python
df["Inadimplente"] = df["Pago"] < df["Valor"]
inadimplentes = df["Inadimplente"].value_counts()

plt.figure(figsize=(6,4))
sns.barplot(
    x= inadimplentes.index.map({False: "Pagou Total", True: "Inadimplente"}),
    y= inadimplentes.values,
    hue= inadimplentes.index.map({False: "Pagou Total", True: "Inadimplente"}),
    palette=["green", "red"],
    legend=False
)
plt.title("Status de Pagamento")
plt.ylabel("Número de Vendas")
plt.tight_layout()
plt.show()
```

</details>

**Insights práticos:**
- Padronização de datas e categorias reduz ruído e melhora qualidade das métricas.
- Deduplicação antes de agregações evita inflação de indicadores.


## 🧠 Funções Utilitárias

**Objetivo do bloco:**
- Encapsular lógica reutilizável e pipelines.

**Código:**

<details><summary>Cell #11</summary>

```python
def renomear_campos(texto):
    if 'Cartão de Crédito' in texto:
        return 'Crédito'
    elif 'Boleto Parcelado' in texto:
        return 'Boleto'
    elif 'GetNet - Cartão de Crédito' in texto:
        return 'Crédito'
    else:
        return texto
```

</details>

**Insights práticos:**
- Encapsular rotinas em funções permite reuso (ex.: `clean_campanhas(df)` para pipeline de higienização).
- Documente com docstrings e valide entradas para reduzir erros em produção.


## 📈 Visualizações (Gráficos)

**Objetivo do bloco:**
- Gerar gráficos para leitura executiva e validação exploratória.

**Código:**

<details><summary>Cell #14</summary>

```python
df = vend_df
import matplotlib.pyplot as plt
from IPython.display import display
import seaborn as sns
```

</details>


<details><summary>Cell #15</summary>

```python
plt.figure(figsize=(12,6))
sns.barplot(
    x=df_produtos.values,
    y=df_produtos.index,
    hue=df_produtos.index,   # usa o próprio índice como hue
    palette="viridis",
    legend=False             # esconde a legenda repetitiva
)
plt.title("Faturamento por Produto")
plt.xlabel("Total Pago (R$)")
plt.ylabel("Produto")
plt.tight_layout()
plt.show()
```

</details>

**Insights práticos:**
- Escolha o gráfico pelo tipo de pergunta: linha para séries temporais, barras para comparação de categorias, heatmap para horários/dias.
- Evite eixos duplos e prefira rótulos percentuais quando o foco não é valor absoluto.


## 📊 Agregações & Métricas

**Objetivo do bloco:**
- Calcular métricas, consolidar e comparar dimensões.

**Código:**

<details><summary>Cell #16</summary>

```python
df_pareto = df.groupby("Produto")["Pago"].sum().sort_values(ascending=False).reset_index()
df_pareto["% Acumulado"] = df_pareto["Pago"].cumsum() / df_pareto["Pago"].sum() * 100

fig, ax1 = plt.subplots(figsize=(12, 8))
ax1.barh(df_pareto["Produto"], df_pareto["Pago"], color="skyblue")
ax2 = ax1.twiny()
ax2.plot(df_pareto["% Acumulado"], df_pareto["Produto"], color="orange", marker="D", linewidth=2)
ax2.axvline(80, color="red", linestyle="--")
ax2.set_xlabel("% Acumulado")
ax1.set_xlabel("Faturamento (R$)")
plt.title("Pareto de Faturamento por Produto")
plt.tight_layout()
plt.show()
```

</details>


<details><summary>Cell #18</summary>

```python
pagamentos = df["Pgto"].value_counts()

plt.figure(figsize=(6,6))
pagamentos.plot(
    kind="pie",
    autopct='%1.1f%%',
    startangle=90,
    colors=sns.color_palette("Set2")
)
plt.title("Distribuição por Meio de Pagamento")
plt.ylabel("")
plt.tight_layout()
plt.show()
```

</details>


<details><summary>Cell #20</summary>

```python
vendas_por_produto = df["Produto"].value_counts().reset_index()
vendas_por_produto.columns = ["Produto", "Quantidade"]

plt.figure(figsize=(12,6))
sns.barplot(
    x="Quantidade", y="Produto", data=vendas_por_produto,
    hue="Produto", palette="magma", legend=False
)
plt.title("Volume de Vendas por Produto")
plt.xlabel("Número de Vendas")
plt.tight_layout()
plt.show()
```

</details>

**Insights práticos:**
- Crie métricas derivadas (CTR real, CTOR, participação %) para interpretação executiva.
- Use `pivot_table` para análises comparativas (produto × mês × canal).
