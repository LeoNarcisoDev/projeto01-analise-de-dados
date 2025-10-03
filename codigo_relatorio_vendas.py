# ============================================================
# 📦 Pipeline de Análise de Vendas — Limpeza, Métricas e Gráficos
# ------------------------------------------------------------
# Objetivo: carregar "base_de_dados.csv", padronizar colunas,
# gerar métricas (mensal, produto, Pareto, meios de pagamento,
# inadimplência) e visualizar resultados.
# Obs.: código compatível com Jupyter (células) ou script único.
# ============================================================

# === 1) Imports & Configuração ==============================================
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

from pathlib import Path
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import seaborn as sns

# Estilo visual
sns.set(style="whitegrid")
plt.rcParams["figure.figsize"] = (12, 6)
plt.rcParams["axes.titlesize"] = 14
plt.rcParams["axes.labelsize"] = 12

# Opções de exibição do pandas (útil durante o dev)
pd.set_option("display.max_columns", 50)
pd.set_option("display.width", 140)

# === 2) Utilitários =========================================================
def ler_csv_robusto(caminho: str | Path, sep: str = ";"):
    """
    Lê CSV tentando encodings comuns no Brasil (cp1252, latin1, utf-8).
    Mantém o separador padrão ';' (muitos CRMs/ERPs exportam assim).
    """
    caminho = Path(caminho)
    tentativas = ["cp1252", "latin1", "utf-8-sig", "utf-8"]
    ultimo_erro = None
    for enc in tentativas:
        try:
            return pd.read_csv(caminho, encoding=enc, sep=sep)
        except Exception as e:
            ultimo_erro = e
    raise RuntimeError(f"Falha ao ler {caminho}: {ultimo_erro}")

def normaliza_num_str_10(v):
    """
    Converte valores numéricos em string no padrão brasileiro (vírgula)
    para float padrão (ponto). Ex.: '1.234,56' -> 1234.56
    - Remove espaços
    - Remove separador de milhar (.)
    - Troca vírgula por ponto
    """
    if pd.isna(v):
        return np.nan
    s = str(v).strip()
    if s == "":
        return np.nan
    s = s.replace(".", "").replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return np.nan

def renomear_campos_pgto(texto: str):
    """
    Normaliza rótulos de meio de pagamento para categorias consistentes.
    Ajuste os mapeamentos conforme os valores reais da sua base.
    """
    if not isinstance(texto, str):
        return texto
    t = texto.lower()
    if "cartão" in t and "crédito" in t:
        return "Crédito"
    if "getnet" in t and "crédito" in t:
        return "Crédito"
    if "boleto parcelado" in t or "boleto" in t:
        return "Boleto"
    if "pix" in t:
        return "PIX"
    if "débito" in t:
        return "Débito"
    # Padrão: retorna original capitalizado
    return texto.strip().title()

def verifica_colunas(df: pd.DataFrame, cols: list[str]):
    """Garante que todas as colunas existam antes de operar."""
    faltantes = [c for c in cols if c not in df.columns]
    if faltantes:
        raise KeyError(f"Colunas faltantes: {faltantes}")

# === 3) Carregamento ========================================================
ARQUIVO = "base_de_dados.csv"
vend_df = ler_csv_robusto(ARQUIVO)  # <- ajusta sep/encoding automaticamente

# Visualização opcional do bruto (descomente se quiser inspecionar)
# display(vend_df.head())

# === 4) Limpeza & Padronização =============================================
# 4.1) Remoção de colunas desnecessárias, se existirem
colunas_para_remover = [
    "ITEM_COMPRA", "DESCONTO VOUCHERS", "CRÉDITOS DESCONTO", "CPF"
]
vend_df = vend_df.drop(columns=[c for c in colunas_para_remover if c in vend_df.columns], errors="ignore")

# 4.2) Padroniza nomes das colunas principais caso a base venha com cabeçalhos variados
# Ajuste aqui se seus cabeçalhos originais forem diferentes.
mapeamento_nomes = {
    "Aprovacao": "Aprovacao",
    "Usuarios": "Usuarios",
    "Produto": "Produto",
    "Pgto": "Pgto",
    "Valor": "Valor",
    "Pago": "Pago",
    # Exemplos de variações comuns:
    "Aprovação": "Aprovacao",
    "Usuários": "Usuarios",
    "Forma de Pagamento": "Pgto",
    "Valor Total": "Valor",
    "Valor Pago": "Pago",
}
vend_df = vend_df.rename(columns={k: v for k, v in mapeamento_nomes.items() if k in vend_df.columns})

# 4.3) Checagem de colunas mínimas exigidas
colunas_obrigatorias = ["Aprovacao", "Usuarios", "Produto", "Pgto", "Valor", "Pago"]
verifica_colunas(vend_df, colunas_obrigatorias)

# 4.4) Conversão dos campos numéricos escritos com vírgula
vend_df["Valor"] = vend_df["Valor"].apply(normaliza_num_str_10) if not np.issubdtype(vend_df["Valor"].dtype, np.number) else vend_df["Valor"]
vend_df["Pago"]  = vend_df["Pago"].apply(normaliza_num_str_10)  if not np.issubdtype(vend_df["Pago"].dtype,  np.number) else vend_df["Pago"]

# 4.5) Normalização do meio de pagamento
vend_df["Pgto"] = vend_df["Pgto"].apply(renomear_campos_pgto)

# 4.6) Conversão de data (suporta dd/mm/aaaa e dd-mm-aaaa)
vend_df["Aprovacao"] = pd.to_datetime(vend_df["Aprovacao"], dayfirst=True, errors="coerce")

# Descarta linhas sem data ou sem valores essenciais (opcional/ajuste à sua realidade)
vend_df = vend_df.dropna(subset=["Aprovacao", "Valor", "Pago"]).reset_index(drop=True)

# Cópia de trabalho
df = vend_df.copy()

# === 5) Métricas & Agregações ==============================================
# 5.1) Faturamento mensal (com período 'YYYY-MM')
df["Mes"] = df["Aprovacao"].dt.to_period("M").astype(str)
df_mensal = (
    df.groupby("Mes", as_index=False)["Pago"].sum()
    .sort_values("Mes", key=lambda s: pd.to_datetime(s, format="%Y-%m"))
    .reset_index(drop=True)
)

# 5.2) Inadimplência (Pago < Valor)
df["Inadimplente"] = df["Pago"] < df["Valor"]
inadimplentes = df["Inadimplente"].value_counts(dropna=False)

# 5.3) Faturamento por produto
df_produtos = (
    df.groupby("Produto", as_index=True)["Pago"]
    .sum()
    .sort_values(ascending=False)
)

# 5.4) Pareto por produto (80/20)
df_pareto = df_produtos.reset_index().rename(columns={"Pago": "Pago"})
df_pareto["% Acumulado"] = df_pareto["Pago"].cumsum() / df_pareto["Pago"].sum() * 100

# 5.5) Distribuição por meio de pagamento
pagamentos = df["Pgto"].value_counts()

# 5.6) Volume de vendas por produto (contagem)
vendas_por_produto = (
    df["Produto"].value_counts()
    .rename_axis("Produto")
    .reset_index(name="Quantidade")
    .sort_values("Quantidade", ascending=False)
)

# === 6) Visualizações =======================================================
# Dica: rotacionar rótulos do eixo X em 45° para evitar sobreposição

# 6.1) Faturamento Mensal
plt.figure(figsize=(14, 6))
sns.barplot(data=df_mensal, x="Mes", y="Pago", hue="Mes", palette="crest", legend=False)
plt.title("Faturamento Mensal")
plt.xlabel("Mês")
plt.ylabel("Total Pago (R$)")
plt.xticks(rotation=45, ha="right")  # eixo X em diagonal 45°
plt.tight_layout()
plt.show()

# 6.2) Status de Pagamento (Inadimplência)
status_index = inadimplentes.index.map({False: "Pagou Total", True: "Inadimplente"})
status_vals = inadimplentes.values

plt.figure(figsize=(7, 5))
sns.barplot(x=status_index, y=status_vals, hue=status_index, palette=["green", "red"], legend=False)
plt.title("Status de Pagamento")
plt.xlabel("")
plt.ylabel("Número de Vendas")
plt.tight_layout()
plt.show()

# 6.3) Faturamento por Produto (Horizontal para rótulos longos)
plt.figure(figsize=(12, max(6, 0.4 * len(df_produtos))))
sns.barplot(x=df_produtos.values, y=df_produtos.index, hue=df_produtos.index, palette="viridis", legend=False)
plt.title("Faturamento por Produto")
plt.xlabel("Total Pago (R$)")
plt.ylabel("Produto")
plt.tight_layout()
plt.show()

# 6.4) Curva de Pareto (Faturamento por Produto)
fig, ax1 = plt.subplots(figsize=(12, max(6, 0.4 * len(df_pareto))))
ax1.barh(df_pareto["Produto"], df_pareto["Pago"], color="skyblue")
ax1.set_xlabel("Faturamento (R$)")
ax1.set_ylabel("Produto")

ax2 = ax1.twiny()
ax2.plot(df_pareto["% Acumulado"], df_pareto["Produto"], marker="D", linewidth=2, color="orange")
ax2.axvline(80, color="red", linestyle="--", linewidth=1)
ax2.set_xlabel("% Acumulado")
plt.title("Pareto de Faturamento por Produto")
plt.tight_layout()
plt.show()

# 6.5) Distribuição por Meio de Pagamento (Pizza)
plt.figure(figsize=(7, 7))
pagamentos.plot(kind="pie", autopct="%1.1f%%", startangle=90, colors=sns.color_palette("Set2"))
plt.title("Distribuição por Meio de Pagamento")
plt.ylabel("")
plt.tight_layout()
plt.show()

# 6.6) Volume de Vendas por Produto (Top-N opcional)
TOP_N = 20  # ajuste conforme necessário
vpp_plot = vendas_por_produto.head(TOP_N).copy()

plt.figure(figsize=(12, max(6, 0.4 * len(vpp_plot))))
sns.barplot(data=vpp_plot, x="Quantidade", y="Produto", hue="Produto", palette="magma", legend=False)
plt.title(f"Volume de Vendas por Produto (Top {TOP_N})")
plt.xlabel("Número de Vendas")
plt.ylabel("Produto")
plt.tight_layout()
plt.show()

# === 7) Saídas opcionais ====================================================
# Salvar agregações em CSV (descomente se quiser exportar)
# df_mensal.to_csv("faturamento_mensal.csv", index=False, encoding="utf-8-sig")
# df_produtos.reset_index().rename(columns={"index": "Produto", "Pago": "Faturamento"}).to_csv(
#     "faturamento_por_produto.csv", index=False, encoding="utf-8-sig"
# )
# df_pareto.to_csv("pareto_produto.csv", index=False, encoding="utf-8-sig")
# vendas_por_produto.to_csv("volume_vendas_produto.csv", index=False, encoding="utf-8-sig")
