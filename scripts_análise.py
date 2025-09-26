'''
Script de Limpeza de Dados CAMPANHAS POSESA

'''

!pip install pandas
!pip install unidecode

import pandas as pd
from pandas import DataFrame
import numpy as np
import re
from unidecode import unidecode

# Setando o DataFrame e iniciando a limdeza de dados

dataframe_base = pd.read_csv("campanhas_base.csv", encoding='latin1', sep=';')
dataframe_base.info()


#Alterando o tipo dos dados de Colunas do DataFrame

dataframe_base['% Abertura'] = (
    dataframe_base['% Abertura']
    .astype(str)
    .str.replace('%', ' ', regex=False)
    .str.replace(',', '.', regex=False)
    .astype(float)
)


dataframe_base['% Cliques'] = (
    dataframe_base['% Cliques']
    .astype(str)
    .str.replace('%', '', regex=-False)
    .str.replace(',', '.', regex=False)
    .astype(float)
)

dataframe_base.info()

#Ajustando a data e hora com a função DateTime

from dateutil import parser
from datetime import datetime, timedelta

# Vamos criar uma função para tratar cada valor da coluna
def processar_data_horario(valor):
    try:
        valor = str(valor).strip()
        agora = datetime.now()

        if 'ago' in valor.lower():
            # Tratar valores relativos como '22 hrs ago', '3 weeks ago'
            partes = valor.lower().split()
            quantidade = int(partes[0])
            unidade = partes[1]

            if 'hr' in unidade:
                datahora = agora - timedelta(hours=quantidade)
            elif 'day' in unidade:
                datahora = agora - timedelta(days=quantidade)
            elif 'week' in unidade:
                datahora = agora - timedelta(weeks=quantidade)
            else:
                return pd.NaT, pd.NaT
        else:
            # Tratar datas absolutas como 'Thu, Jul 24, 2025 10:00AM'
            datahora = parser.parse(valor)

        data_formatada = datahora.strftime('%d/%m/%Y')
        hora_formatada = datahora.strftime('%H:%M')
        return pd.Series([data_formatada, hora_formatada])

    except Exception:
        return pd.Series([pd.NaT, pd.NaT])

# Aplica a função à coluna 'Data/Horário'
dataframe_base[['Data', 'Hora']] = dataframe_base['Data/Horário'].apply(processar_data_horario)

#Excluindo colunas desnecessárias

dataframe_base.drop('Data/Horário', axis=1, inplace=True)
pd.set_option('display.max_colwidth', None)

#Padronizando o texto da coluna "Campanha"

#CRIANDO UMA FUNÇÃO PARA PADRONIZAR O NOME DAS CAMPANHAS
def padronizar_texto(texto):
    texto = str(texto).lower()
    texto = texto.strip()
    texto = re.sub(r'\s+', ' ', texto)  # espaços múltiplos para 1
    texto = re.sub(r'[^\w\s]', '', texto)  # remover pontuações
    texto = re.sub(r'\|\s*\d+\s*[^a-zA-Z]*n[aã]o enviados?', '', texto)  # remove '2 não enviados'
    texto = re.sub(r'\b\d{1,2}x\s*r?\$?\d+[\.,]?\d*\b', '', texto)  # remove valores tipo 12x R$ 99,90
    texto = texto.replace('pose(sa)', 'posesa')  # padronizar "POSESA"
    texto = texto.strip()
    return texto

dataframe_base['Campanha'] = dataframe_base['Campanha'].apply(padronizar_texto)

#Agrupando campanhas semelhantes

# Criando uma função para renomear as camapnhas com dados a serem analisados juntos !!!!

def renomear_campanhas(texto):
    if 'inteligência artificial' in texto:
        return "MiniCurso IA"
    elif 'marketing jurídico' in texto:
        return "MiniCurso MJ"
    elif 'direito processual' in texto:
        return "DPCC"
    elif 'black friday' in texto:
        return "Campanha Black Friday"
    elif 'imobiliária' in texto:
        return "Pós Imobiliária"
    elif 'empresarial' in texto:
        return "Pós Empresarial"
    elif 'familiar' in texto:
        return "Pós Familiar"
    elif 'namorados' in texto:
        return 'Campanha Namorados'
    else:
        return texto

dataframe_base['Campanha'] = dataframe_base['Campanha'].apply(renomear_campanhas)

"""Agrupando as campanhas:
Descartar a coluna Hora e reescrever Data como período;
Calcular os percentuais em grupos;"""


# 1. Descartar 'Hora'
dataframe_grouped = dataframe_base.drop(columns=['Hora'])

# 2. Converter 'Data' para datetime
dataframe_grouped['Data'] = pd.to_datetime(dataframe_grouped['Data'], dayfirst=True)

# 3. Agrupar os dados
agrupado = dataframe_grouped.groupby('Campanha').agg({
    'Enviados': 'sum',
    'Qtde Abertos': 'sum',
    'Qtde Cliques': 'sum',
    'Data': ['min', 'max']  # para gerar o período
})

# 4. Ajustar colunas após o groupby com múltiplos níveis(necessário re-cálculo devido à união das percentagens de abertura e cliques)

agrupado.columns = ['Enviados', 'Qtde Abertos', 'Qtde Cliques', 'Data_Inicial', 'Data_Final']
agrupado = agrupado.reset_index()

# 5. Calcular percentuais
agrupado['% Abertura'] = (agrupado['Qtde Abertos'] / agrupado['Enviados']) * 100
agrupado['% Cliques'] = (agrupado['Qtde Cliques'] / agrupado['Enviados']) * 100

# 6. Arredondar os percentuais
agrupado['% Abertura'] = agrupado['% Abertura'].round(2)
agrupado['% Cliques'] = agrupado['% Cliques'].round(2)

# 7. Criar coluna de período no formato desejado
agrupado['Período'] = agrupado['Data_Inicial'].dt.strftime('%d/%m/%Y') + ' até ' + agrupado['Data_Final'].dt.strftime('%d/%m/%Y')

# 8. Organizar colunas finais
resultado = agrupado[[
    'Campanha', 'Enviados', '% Abertura', 'Qtde Abertos',
    '% Cliques', 'Qtde Cliques', 'Período'
]]


# Deletando colunas indesejadas

agrupado.drop('Data_Final', axis=1, inplace=True)
agrupado.drop(index=5, inplace=True)


# Renomenando colunas

agrupado.columns = [
    "Campanha", "Enviados", "Abertos", "Cliques",
    "Data", "Taxa_Abertura", "Taxa_Cliques", "Periodo"
]



# Resultados Gráficos:


df = agrupado
import matplotlib.pyplot as plt
from IPython.display import display


#Volume de Envios por Campanha
df.sort_values("Enviados", ascending=True).plot.barh(
    x="Campanha", y="Enviados", figsize=(10,6), legend=False)
plt.title("Volume de Envios por Campanha")
plt.show()



#Taxas de Abertura e Cliques por Campanha
import matplotlib.pyplot as plt

ax = df.plot(
    x="Campanha",
    y=["Taxa_Abertura", "Taxa_Cliques"],
    kind="bar",
    figsize=(12,6)
)

plt.title("Taxas de Abertura e Cliques por Campanha")

# Força o eixo X (valores numéricos) a ir de 0 até 20
plt.ylim(0, 12)

plt.show()


#Evolução das Taxas ao Longo do Tempo
df_sorted = df.sort_values("Data")
plt.figure(figsize=(12,6))
plt.plot(df_sorted["Data"], df_sorted["Taxa_Abertura"], marker="o", label="Tx Abertura")
plt.plot(df_sorted["Data"], df_sorted["Taxa_Cliques"], marker="s", label="Tx Cliques")
plt.legend()
plt.title("Evolução das Taxas ao Longo do Tempo")
plt.xticks(rotation=45)
plt.show()


#Novas Métricas Derivadas
1.  CTR real (cliques / abertos)
→ mede engajamento de quem abriu.
df["CTR_real"] = (df["Cliques"]/df["Abertos"])*100
2.  Engajamento Total (abertos + cliques / enviados)
→ visão consolidada.
df["Engajamento_Total"] = ((df["Abertos"]+df["Cliques"])/df["Enviados"])*100
3.  Plotar ranking dessas métricas:
df.set_index("Campanha")[["CTR_real","Engajamento_Total"]].plot(kind="bar", figsize=(12,6))


#Pareto de Cliques
df_sorted = df.sort_values("Cliques", ascending=False)
df_sorted["% cumulativo"] = df_sorted["Cliques"].cumsum()/df_sorted["Cliques"].sum()*100

fig, ax1 = plt.subplots(figsize=(12,6))
ax1.bar(df_sorted["Campanha"], df_sorted["Cliques"], color="C0")
ax2 = ax1.twinx()
ax2.plot(df_sorted["Campanha"], df_sorted["% cumulativo"], color="C1", marker="D", ms=5)
ax2.axhline(80, color="r", linestyle="--")
plt.title("Pareto de Cliques")
plt.xticks(rotation=90)
plt.show()
