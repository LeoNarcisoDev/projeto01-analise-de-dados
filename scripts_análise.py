# ============================================================
# 🧼 Script de Limpeza e Análise — CAMPANHAS POSESA
# ------------------------------------------------------------
# Objetivo:
# 1) Carregar "campanhas_base.csv"
# 2) Padronizar colunas (% Abertura/% Cliques, Data/Horário, Campanha)
# 3) Agrupar por campanha (envios, abertos, cliques, período)
# 4) Calcular métricas (taxas, CTR real, engajamento total)
# 5) Gerar gráficos: envios, taxas, evolução temporal e Pareto de cliques
#
# Observações:
# - Código puro Python (sem !pip). Se precisar de 'unidecode', instale previamente.
# - Compatível com Jupyter ou execução como script (.py).
# ============================================================

from __future__ import annotations

from pathlib import Path
import re
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

# Imports opcionais (gráficos)
import matplotlib.pyplot as plt
import seaborn as sns
sns.set(style="whitegrid")
plt.rcParams["figure.figsize"] = (12, 6)

# 'unidecode' é opcional: se não estiver instalado, seguimos sem ele
try:
    from unidecode import unidecode
except Exception:
    def unidecode(x: str) -> str:
        return x  # fallback neutro

# dateutil para parsing robusto de datas absolutas
try:
    from dateutil import parser as date_parser
except Exception:
    date_parser = None  # se indisponível, tratamos abaixo


# =============== 1) Leitura robusta do CSV ===================
ARQUIVO = "campanhas_base.csv"

def ler_csv_robusto(caminho: str | Path, sep: str = ";") -> pd.DataFrame:
    """Tenta encodings comuns (latin1/cp1252/utf-8-*) e retorna DataFrame."""
    caminho = Path(caminho)
    tentativas = ["latin1", "cp1252", "utf-8-sig", "utf-8"]
    ultimo_erro = None
    for enc in tentativas:
        try:
            return pd.read_csv(caminho, sep=sep, encoding=enc)
        except Exception as e:
            ultimo_erro = e
    raise RuntimeError(f"Falha ao ler {caminho}: {ultimo_erro}")

df_base = ler_csv_robusto(ARQUIVO, sep=";")

# Visual generosa (opcional)
# print(df_base.info())
# display(df_base.head())


# =============== 2) Funções utilitárias ======================

def parse_percent_br(valor) -> float | np.nan:
    """
    Converte strings como '6,46%' -> 6.46 (float).
    Aceita números, strings com '%' e vírgula.
    """
    if pd.isna(valor):
        return np.nan
    s = str(valor).strip()
    if s == "":
        return np.nan
    s = s.replace("%", "").replace(" ", "").replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return np.nan

def processar_data_horario(valor):
    """
    Interpreta:
      - Relativos em inglês: '22 hrs ago', '3 days ago', '2 weeks ago'
      - Absolutos (ex.: 'Thu, Jul 24, 2025 10:00AM')
    Retorna: Serie [data_formatada_dd/mm/aaaa, hora_HH:MM]
    """
    try:
        txt = str(valor).strip()
        agora = datetime.now()

        # Casos relativos (en)
        lower = txt.lower()
        if "ago" in lower:
            # exemplo: "22 hrs ago" | "3 days ago" | "2 weeks ago"
            partes = lower.split()
            # Busca número inteiro na string
            qtd = next((int(p) for p in partes if p.isdigit()), None)
            if qtd is None:
                return pd.Series([pd.NaT, pd.NaT])

            # Unidade
            unidade = ""
            for p in partes:
                if any(u in p for u in ["hr", "hour", "day", "week"]):
                    unidade = p
                    break

            if "hr" in unidade or "hour" in unidade:
                datahora = agora - timedelta(hours=qtd)
            elif "day" in unidade:
                datahora = agora - timedelta(days=qtd)
            elif "week" in unidade:
                datahora = agora - timedelta(weeks=qtd)
            else:
                return pd.Series([pd.NaT, pd.NaT])
        else:
            # Absoluto
            if date_parser is None:
                return pd.Series([pd.NaT, pd.NaT])
            datahora = date_parser.parse(txt)

        data_formatada = datahora.strftime("%d/%m/%Y")
        hora_formatada = datahora.strftime("%H:%M")
        return pd.Series([data_formatada, hora_formatada])

    except Exception:
        return pd.Series([pd.NaT, pd.NaT])

def padronizar_texto_campanha(texto: str) -> str:
    """
    Normaliza texto da campanha:
    - caixa baixa
    - removal de acentuação
    - reduz espaços
    - remove pontuações e ruídos comuns (ex.: '2 não enviados', '12x R$ 99,90')
    - padroniza 'POSESA'
    """
    t = str(texto)
    t = unidecode(t).lower().strip()
    t = re.sub(r"\s+", " ", t)                    # espaços repetidos
    t = re.sub(r"[^\w\s]", "", t)                 # remove pontuações
    t = re.sub(r"\|\s*\d+\s*nao enviados?", "", t)  # remove "X nao enviados"
    t = re.sub(r"\b\d{1,2}x\s*r?\$?\d+[\.,]?\d*\b", "", t)  # remove "12x R$ 99,90"
    t = t.replace("posesa", "posesa")             # mantém "posesa" padronizado (sem acento)
    t = t.strip()
    return t

def renomear_campanhas(texto: str) -> str:
    """
    Reclassifica campanhas por tema/assunto para agregação.
    Ajuste os gatilhos conforme seu catálogo real.
    """
    t = str(texto)
    # Trabalhar em versão sem acento e minúscula
    low = unidecode(t).lower()

    if "inteligencia artificial" in low or "ia" in low:
        return "MiniCurso IA"
    if "marketing juridico" in low:
        return "MiniCurso MJ"
    if "direito processual" in low or "dpcc" in low:
        return "DPCC"
    if "black friday" in low:
        return "Campanha Black Friday"
    if "imobiliaria" in low:
        return "Pós Imobiliária"
    if "empresarial" in low:
        return "Pós Empresarial"
    if "familiar" in low:
        return "Pós Familiar"
    if "namorados" in low:
        return "Campanha Namorados"
    return t.strip()


# =============== 3) Padronização de colunas ==================
# Checa colunas esperadas; se necessário, renomeie conforme sua base.
col_map_candidatos = {
    "% Abertura": "% Abertura",
    "% Cliques": "% Cliques",
    "Data/Horário": "Data/Horário",
    "Campanha": "Campanha",
    "Enviados": "Enviados",
    "Qtde Abertos": "Qtde Abertos",
    "Qtde Cliques": "Qtde Cliques",
}
# Ajuste automático se houver pequenas variações
ren_map = {}
for cand, alvo in col_map_candidatos.items():
    if cand in df_base.columns:
        ren_map[cand] = alvo
df_base = df_base.rename(columns=ren_map)

# =============== 4) Limpeza de % Abertura / % Cliques =========
if "% Abertura" in df_base.columns:
    df_base["% Abertura"] = df_base["% Abertura"].apply(parse_percent_br)

if "% Cliques" in df_base.columns:
    df_base["% Cliques"] = df_base["% Cliques"].apply(parse_percent_br)

# =============== 5) Data/Horário -> Data, Hora =================
if "Data/Horário" in df_base.columns:
    df_base[["Data", "Hora"]] = df_base["Data/Horário"].apply(processar_data_horario)
    df_base = df_base.drop(columns=["Data/Horário"])
else:
    # Se a coluna não existir, cria vazias para não quebrar fluxos seguintes
    df_base["Data"] = pd.NaT
    df_base["Hora"] = pd.NaT

# =============== 6) Padronização de "Campanha" =================
if "Campanha" in df_base.columns:
    df_base["Campanha"] = df_base["Campanha"].apply(padronizar_texto_campanha)
    df_base["Campanha"] = df_base["Campanha"].apply(renomear_campanhas)

# Visual (opcional)
# display(df_base.head())


# =============== 7) Agrupamentos =================================
# 7.1) Descarta 'Hora' (não precisamos no agrupamento)
df_group = df_base.drop(columns=[c for c in ["Hora"] if c in df_base.columns], errors="ignore")

# 7.2) Converte 'Data' (se presente) para datetime e cria período
if "Data" in df_group.columns:
    df_group["Data"] = pd.to_datetime(df_group["Data"], dayfirst=True, errors="coerce")

agr_cols = {}
for col, agg in [("Enviados", "sum"), ("Qtde Abertos", "sum"), ("Qtde Cliques", "sum")]:
    if col in df_group.columns:
        agr_cols[col] = agg

# Inclui min/max de Data se existir
usar_data = "Data" in df_group.columns
if not agr_cols:
    raise KeyError("Colunas mínimas para agrupamento não encontradas (Enviados/Qtde Abertos/Qtde Cliques).")

if usar_data:
    agrupado = df_group.groupby("Campanha").agg(
        {
            **agr_cols,
            "Data": ["min", "max"],
        }
    )
    agrupado.columns = ["Enviados", "Qtde Abertos", "Qtde Cliques", "Data_Inicial", "Data_Final"]
else:
    agrupado = df_group.groupby("Campanha").agg(agr_cols)
    agrupado.columns = ["Enviados", "Qtde Abertos", "Qtde Cliques"]
    # Cria colunas vazias para consistência
    agrupado["Data_Inicial"] = pd.NaT
    agrupado["Data_Final"] = pd.NaT

agrupado = agrupado.reset_index()

# 7.3) Percentuais recomputados no nível da campanha
agrupado["Taxa_Abertura"] = (agrupado["Qtde Abertos"] / agrupado["Enviados"]).replace([np.inf, -np.inf], np.nan) * 100
agrupado["Taxa_Cliques"]  = (agrupado["Qtde Cliques"] / agrupado["Enviados"]).replace([np.inf, -np.inf], np.nan) * 100
agrupado["Taxa_Abertura"] = agrupado["Taxa_Abertura"].round(2)
agrupado["Taxa_Cliques"]  = agrupado["Taxa_Cliques"].round(2)

# 7.4) Período (se houver datas válidas)
if usar_data:
    agrupado["Periodo"] = (
        agrupado["Data_Inicial"].dt.strftime("%d/%m/%Y").fillna("")
        + " até "
        + agrupado["Data_Final"].dt.strftime("%d/%m/%Y").fillna("")
    ).str.replace(" até ", "", regex=False).where(agrupado["Data_Inicial"].notna(), "")
else:
    agrupado["Periodo"] = ""

# 7.5) Data representativa para ordenação temporal nos gráficos de evolução
agrupado["Data"] = agrupado["Data_Inicial"]  # data de início do período


# =============== 8) Novas Métricas =============================
# CTR real: cliques sobre abertos (engajamento de quem abriu)
agrupado["CTR_real"] = np.where(
    agrupado["Qtde Abertos"] > 0,
    (agrupado["Qtde Cliques"] / agrupado["Qtde Abertos"]) * 100,
    np.nan
).round(2)

# Engajamento total: (abertos + cliques) / enviados
agrupado["Engajamento_Total"] = np.where(
    agrupado["Enviados"] > 0,
    ((agrupado["Qtde Abertos"] + agrupado["Qtde Cliques"]) / agrupado["Enviados"]) * 100,
    np.nan
).round(2)

# Colunas finais ordenadas para export/visualização
colunas_finais = [
    "Campanha", "Enviados",
    "Qtde Abertos", "Taxa_Abertura",
    "Qtde Cliques", "Taxa_Cliques",
    "CTR_real", "Engajamento_Total",
    "Periodo", "Data_Inicial", "Data_Final"
]
colunas_finais = [c for c in colunas_finais if c in agrupado.columns]
resultado = agrupado[colunas_finais].copy()

# Exibir (opcional)
# display(resultado.head())


# =============== 9) Visualizações ==============================
# Dicas:
# - Rotacione rótulos do eixo X para 45° quando necessário (plt.xticks(rotation=45, ha="right"))

# 9.1) Volume de Envios por Campanha
ax = resultado.sort_values("Enviados", ascending=True).plot.barh(
    x="Campanha", y="Enviados", figsize=(12, max(6, 0.4 * len(resultado))), legend=False
)
plt.title("Volume de Envios por Campanha")
plt.xlabel("Enviados")
plt.ylabel("Campanha")
plt.tight_layout()
plt.show()

# 9.2) Taxas de Abertura e Cliques por Campanha
taxas_cols = [c for c in ["Taxa_Abertura", "Taxa_Cliques"] if c in resultado.columns]
if taxas_cols:
    ax = resultado.plot(
        x="Campanha",
        y=taxas_cols,
        kind="bar",
        figsize=(14, max(6, 0.4 * len(resultado))),
    )
    plt.title("Taxas de Abertura e Cliques por Campanha")
    # Ajuste do limite do eixo Y com margem
    ymax = float(np.nanmax(resultado[taxas_cols].values)) if len(taxas_cols) else 0.0
    plt.ylim(0, max(10.0, (ymax * 1.1)))
    plt.xticks(rotation=45, ha="right")
    plt.ylabel("Percentual (%)")
    plt.tight_layout()
    plt.show()

# 9.3) Evolução das Taxas ao Longo do Tempo (por data inicial do período)
if "Data" in resultado.columns and resultado["Data"].notna().any() and taxas_cols:
    df_sorted = resultado.sort_values("Data")
    plt.figure(figsize=(14, 6))
    if "Taxa_Abertura" in df_sorted.columns:
        plt.plot(df_sorted["Data"], df_sorted["Taxa_Abertura"], marker="o", label="Taxa de Abertura")
    if "Taxa_Cliques" in df_sorted.columns:
        plt.plot(df_sorted["Data"], df_sorted["Taxa_Cliques"], marker="s", label="Taxa de Cliques")
    plt.title("Evolução das Taxas ao Longo do Tempo")
    plt.xlabel("Data (início do período)")
    plt.ylabel("Percentual (%)")
    plt.xticks(rotation=45, ha="right")
    plt.legend()
    plt.tight_layout()
    plt.show()

# 9.4) Ranking — CTR Real e Engajamento Total
rank_cols = [c for c in ["CTR_real", "Engajamento_Total"] if c in resultado.columns]
if rank_cols:
    resultado.set_index("Campanha")[rank_cols].plot(kind="bar", figsize=(14, max(6, 0.4 * len(resultado))))
    plt.title("Ranking: CTR Real e Engajamento Total")
    plt.xlabel("Campanha")
    plt.ylabel("Percentual (%)")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.show()

# 9.5) Pareto de Cliques
if "Qtde Cliques" in resultado.columns:
    df_sorted = resultado.sort_values("Qtde Cliques", ascending=False).copy()
    soma_cliques = df_sorted["Qtde Cliques"].sum()
    if soma_cliques > 0:
        df_sorted["% cumulativo"] = df_sorted["Qtde Cliques"].cumsum() / soma_cliques * 100

        fig, ax1 = plt.subplots(figsize=(14, max(6, 0.4 * len(df_sorted))))
        ax1.bar(df_sorted["Campanha"], df_sorted["Qtde Cliques"], color="C0")
        ax1.set_ylabel("Cliques")
        ax1.set_xlabel("Campanha")
        plt.xticks(rotation=90)

        ax2 = ax1.twinx()
        ax2.plot(df_sorted["Campanha"], df_sorted["% cumulativo"], color="C1", marker="D", ms=5)
        ax2.axhline(80, color="r", linestyle="--", linewidth=1)
        ax2.set_ylabel("% Cumulativo")
        plt.title("Pareto de Cliques")
        plt.tight_layout()
        plt.show()


# =============== 10) (Opcional) Exportar CSV ===================
# resultado.to_csv("campanhas_limpas_agrupadas.csv", index=False, encoding="utf-8-sig")
