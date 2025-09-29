# === 📦 Imports & Configuração ===
# Cell #1
import pandas as pd

# Cell #2
import numpy as np

# === 🧪 Cálculos & Análises Pontuais ===
# Cell #3
from pandas import DataFrame

# Cell #5
vend_df

# Cell #6
vend_df.drop('ITEM_COMPRA', axis=1, inplace=True)
vend_df.drop('DESCONTO VOUCHERS', axis=1, inplace=True)
vend_df.drop('CRÉDITOS DESCONTO', axis=1, inplace=True)
vend_df.drop('CPF', axis=1, inplace=True)

# Cell #7
vend_df

# Cell #8
vend_df.columns = [
    'Aprovacao', 'Usuarios', 'Produto', 'Pgto', 'Valor', 'Pago'    
]

vend_df

# Cell #13
vend_df

# Cell #21
df

# === 🗂️ Carregamento de Dados (CSV/SQL/Excel) ===
# Cell #4
vend_df = pd.read_csv("base_de_dados.csv", encoding='cp1252', sep=';')

# === 🧹 Limpeza & Padronização ===
# Cell #9
vend_df['Valor'] = (
    vend_df['Valor']
    .astype(str)
    .str.replace(',', '.', regex=False)
    .astype(float)
)

# Cell #10
vend_df['Pago'] = (
    vend_df['Pago']
    .astype(str)
    .str.replace(',', '.',  regex=False)
    .astype(float)
)

# Cell #12
vend_df['Pgto'] = vend_df['Pgto'].apply(renomear_campos)

# Cell #17
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

# Cell #19
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

# === 🧠 Funções Utilitárias ===
# Cell #11
def renomear_campos(texto):
    if 'Cartão de Crédito' in texto:
        return 'Crédito'
    elif 'Boleto Parcelado' in texto:
        return 'Boleto'
    elif 'GetNet - Cartão de Crédito' in texto:
        return 'Crédito'
    else:
        return texto

# === 📈 Visualizações (Gráficos) ===
# Cell #14
df = vend_df
import matplotlib.pyplot as plt
from IPython.display import display
import seaborn as sns

# Cell #15
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

# === 📊 Agregações & Métricas ===
# Cell #16
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

# Cell #18
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

# Cell #20
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
