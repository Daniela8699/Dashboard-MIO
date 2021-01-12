import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.express as px
from app import app
pd.options.mode.chained_assignment = None  # default='warn'
app.config.suppress_callback_exceptions = True
CONTENT_STYLE = {
    "text-align": "center",
    "margin-bottom": "2rem"
}
# Load data
datagrams = pd.read_csv(
    "./data/datagrams.csv",
    low_memory=False,
)
busesData = pd.read_csv(
    "./data/busesData.csv",
    low_memory=False,
)
linesData = pd.read_csv(
    "./data/linesData.csv",
    low_memory=False,
)


# ---------------Proccess Data------------------
df2 = datagrams[(datagrams['EventType'] == 12) |
                (datagrams['EventType'] == 23)]
df2['DatagramDate'] = pd.to_datetime(df2['DatagramDate'])
df2 = df2.sort_values(by=['DatagramDate'])

datagramsWithBusNumber = datagrams.merge(
    right=busesData, on=['BusID'], how='inner')
datagramsWithBusNumber.BusNumber = datagramsWithBusNumber.BusNumber.astype(str)

datagrams_buses_id = pd.DataFrame(
    datagrams['BusID'].unique(), columns=["BusID"])
datagrams_buses_id = datagrams_buses_id.merge(
    right=busesData, on=['BusID'], how='inner')
datagrams_buses_id = datagrams_buses_id.sort_values(by=['BusNumber'])

temp = df2.BusID.value_counts().to_frame()
BusIDCounts = temp.reset_index()
BusIDCounts.columns = ['BusID', 'Counts']

dfDuplicates = df2.drop_duplicates(["BusID", "DatagramDate"])
dfDuplicates = dfDuplicates.groupby('BusID').DatagramDate.size().to_frame()
dfDuplicates = dfDuplicates.reset_index()
dfDuplicates.columns = ['BusID', 'DateCount']
dfDuplicates = dfDuplicates.sort_values('DateCount', ascending=False)
dfDuplicates.head(10)


buses_day_event_count = df2.groupby(['BusID', 'DatagramDate']).size()
buses_day_event_count = buses_day_event_count.reset_index()
buses_day_event_count.rename(columns={0: 'Count'}, inplace=True)
buses_day_event_count.sort_values(
    by=['BusID', 'DatagramDate'], ascending=True, inplace=True)
buses_day_event_count['Month'] = buses_day_event_count.apply(
    lambda row: row['DatagramDate'].month, axis=1).astype(int)

# -----Reporteee
dfDuplicatesComplete = dfDuplicates.merge(
    right=busesData, on=['BusID'], how='inner')

# Primer Digito
# 1 --> Git Masivo
# 2 --> Blanco y Negro
# 3 --> ETM
# 4 --> UNIMETRO

# Segundo Digito
# 1 --> Articulado
# 2 --> Padrón
# 3 --> Complementario


def getConcessionaireAndTypeArray(con, tipo):
    x, y = [], []
    for index, row in busesData.iterrows():
        if str(row.BusNumber)[0] == str(con):
            if str(row.BusNumber)[1] == str(tipo):
                x.append(row.BusNumber)
                y.append(row.BusID)
    return x, y


def getConcessionaireAndTypeArrayFailure(con, tipo):
    x, y = [], []
    for index, row in dfDuplicatesComplete.iterrows():
        if str(row.BusNumber)[0] == str(con):
            if str(row.BusNumber)[1] == str(tipo):
                x.append(row.BusNumber)
                y.append(row.BusID)
    return x, y


def getConcessionaireArray(con):
    x, y = [], []
    for index, row in busesData.iterrows():
        if str(row.BusNumber)[0] == str(con):
            x.append(row.BusNumber)
            y.append(row.BusID)
    return x, y


def getNoFailureConcessionaireArray(aA, aP, aC, failure_array, concessionare_name, hist_Array):
    for value in aA:
        if failure_array.count(value) == 0:
            hist_Array.append(
                "Articulados " + concessionare_name + " Sin Falla")

    for value in aP:
        if failure_array.count(value) == 0:
            hist_Array.append("Padrones " + concessionare_name + " Sin Falla")

    for value in aP:
        if failure_array.count(value) == 0:
            hist_Array.append("Complementario " +
                              concessionare_name + " Sin Falla")


def GeneralConcessionareReport(report, totalBusesMio, totalBusesMioF, totalArticulados, totalPadrones,
                               totalComplementarios, totalArticuladosF, totalPadronesF, totalComplementariosF,
                               totalGit, totalGitF, totalBN, totalBNF, totalETM, totalETMF, totalUNI, totalUNIF):

    report += 'Flota de Buses del Mio: ' + str(totalBusesMio) + ' Buses\n'
    report += 'Conteo de Buses que envió falla de aire acondicionado: ' + \
        str(totalBusesMioF) + ' Buses\n'
    report += 'Porcentaje de flota del MIO que ha envíado la falla de aire (%): ' + str(
        round(totalBusesMioF/totalBusesMio*100, 3)) + ' %\n---\n'
    report = GeneralConcessionareReportAuxiliar(
        report, 'Git Masivo', totalBusesMio, totalBusesMioF, totalGit, totalGitF)
    report = GeneralConcessionareReportAuxiliar(
        report, 'Blanco & Negro', totalBusesMio, totalBusesMioF, totalBN, totalBNF)
    report = GeneralConcessionareReportAuxiliar(
        report, 'ETM', totalBusesMio, totalBusesMioF, totalETM, totalETMF)
    report = GeneralConcessionareReportAuxiliar(
        report, 'Unimetro', totalBusesMio, totalBusesMioF, totalUNI, totalUNIF)
    report = GeneralConcessionareReportAuxiliar(
        report, 'Articulados', totalBusesMio, totalBusesMioF, totalArticulados, totalArticuladosF)
    report = GeneralConcessionareReportAuxiliar(
        report, 'Padrones', totalBusesMio, totalBusesMioF, totalPadrones, totalPadronesF)
    report = GeneralConcessionareReportAuxiliar(
        report, 'Complementarios', totalBusesMio, totalBusesMioF, totalComplementarios, totalComplementariosF)
    return report


def GeneralConcessionareReportAuxiliar(report, name, totalBusesMio, totalBusesMioF, totalBuses, totalBusesF):
    print(name, ':', totalBuses)
    report += name + ' Informacion General\n\n'
    report += 'Flota de ' + name + ': ' + str(totalBuses) + ' Buses\n'
    report += 'Conteo de Buses que enviarón falla de aire:  ' + \
        str(totalBusesF) + ' Buses\n'
    report += 'Porcentaje de la flota ' + name + \
        ' que envió falla sobre el total de flota que envío falla (%): ' + str(
            round(totalBusesF/totalBusesMioF*100, 3)) + ' %\n'
    report += 'Porcentaje de la flota ' + name + ' que envió falla sobre el total de flota de ' + \
        name + '(%): ' + str(round(totalBusesF/totalBuses*100, 3)) + ' %\n'
    report += 'Porcentaje de la flota ' + name + \
        ' que envió falla sobre el total de flota del MIO (%): ' + str(
            round(totalBusesF/totalBusesMio*100, 3)) + ' %\n---\n'
    return report


def ByConcessionareReport(report, name, totalBusesMio, totalBusesMioF, totalBusesCo, totalBusesCoF,
                          totalBusesA, totalBusesAF, totalBusesP, totalBusesPF, totalBusesC,
                          totalBusesCF, totalTypeBusesAF, totalTypeBusesPF, totalTypeBusesCF):
    report += 'Flota de ' + name + ': ' + str(totalBusesCo) + ' Buses\n'
    report += 'Conteo de Buses que envió falla de aire acondicionado: ' + \
        str(totalBusesCoF) + ' Buses\n---\n\n'
    report = ByConcessionareReportAuxiliar(report, name, 'Articulados', totalBusesMio, totalBusesMioF, totalBusesCo, totalBusesCoF,
                                           totalBusesA, totalBusesAF, totalTypeBusesAF)
    report = ByConcessionareReportAuxiliar(report, name, 'Padrones', totalBusesMio, totalBusesMioF, totalBusesCo, totalBusesCoF,
                                           totalBusesP, totalBusesPF, totalTypeBusesPF)
    report = ByConcessionareReportAuxiliar(report, name, 'Complementarios', totalBusesMio, totalBusesMioF, totalBusesCo, totalBusesCoF,
                                           totalBusesC, totalBusesCF, totalTypeBusesCF)

    return report


def ByConcessionareReportAuxiliar(report, name, bus_type, totalBusesMio, totalBusesMioF, totalBusesC, totalBusesCF,
                                  totalBuses, totalBusesF, totalTypeBusesF):
    report += 'Informacion General ' + bus_type + ' ' + name + '\n\n'

    report += 'Flota ' + bus_type + ' ' + \
        name + ': ' + str(totalBuses) + ' Buses\n'
    report += 'Porcentaje que ocupan los ' + bus_type + ' en la flota de ' + \
        name + ' (%): ' + str(round(totalBuses/totalBusesC*100, 3)) + ' %\n'
    report += 'Conteo de Buses ' + bus_type + \
        ' que enviarón falla de aire:  ' + str(totalBusesF) + ' Buses\n'
    report += 'Porcentaje de ' + bus_type + ' que envió falla sobre el total de ' + \
        bus_type + ' de ' + name + \
        ' (%): ' + str(round(totalBusesF/totalBuses*100, 3)) + ' %\n'
    report += 'Porcentaje de ' + bus_type + ' que envió falla sobre el total de la flota ' + \
        name + ' que envió falla (%): ' + \
        str(round(totalBusesF/totalBusesCF*100, 3)) + ' %\n'
    report += 'Porcentaje de ' + bus_type + ' del ' + name + \
        ' que envió falla sobre el total de la flota del MIO que envió falla (%): ' + str(
            round(totalBusesF/totalBusesMioF*100, 3)) + ' %\n'
    report += 'Porcentaje de ' + bus_type + ' del ' + name + \
        ' que envió falla sobre el total de la flota del MIO (%): ' + str(
            round(totalBusesF/totalBusesMio*100, 3)) + ' %\n'
    report += 'Porcentaje de ' + bus_type + ' del ' + name + ' que envió falla sobre el total de ' + bus_type + \
        ' de la flota MIO que envió falla (%): ' + str(
            round(totalBusesF/totalTypeBusesF*100, 3)) + ' %\n---\n'
    return report


def getResultsReport():

    # Array Generales
    (gA, _) = getConcessionaireAndTypeArray(1, 1)
    (gP, _) = getConcessionaireAndTypeArray(1, 2)
    (gC, _) = getConcessionaireAndTypeArray(1, 3)
    (bnA, _) = getConcessionaireAndTypeArray(2, 1)
    (bnP, _) = getConcessionaireAndTypeArray(2, 2)
    (bnC, _) = getConcessionaireAndTypeArray(2, 3)
    (eA, _) = getConcessionaireAndTypeArray(3, 1)
    (eP, _) = getConcessionaireAndTypeArray(3, 2)
    (eC, _) = getConcessionaireAndTypeArray(3, 3)
    (uA, _) = getConcessionaireAndTypeArray(4, 1)
    (uP, _) = getConcessionaireAndTypeArray(4, 2)
    (uC, _) = getConcessionaireAndTypeArray(4, 3)

    # Array Dañados
    (gFA, _) = getConcessionaireAndTypeArrayFailure(1, 1)
    (gFP, _) = getConcessionaireAndTypeArrayFailure(1, 2)
    (gFC, _) = getConcessionaireAndTypeArrayFailure(1, 3)
    (bnFA, _) = getConcessionaireAndTypeArrayFailure(2, 1)
    (bnFP, _) = getConcessionaireAndTypeArrayFailure(2, 2)
    (bnFC, _) = getConcessionaireAndTypeArrayFailure(2, 3)
    (eFA, _) = getConcessionaireAndTypeArrayFailure(3, 1)
    (eFP, _) = getConcessionaireAndTypeArrayFailure(3, 2)
    (eFC, _) = getConcessionaireAndTypeArrayFailure(3, 3)
    (uFA, _) = getConcessionaireAndTypeArrayFailure(4, 1)
    (uFP, _) = getConcessionaireAndTypeArrayFailure(4, 2)
    (uFC, _) = getConcessionaireAndTypeArrayFailure(4, 3)

    # Variables Por Concesionario Completo
    articuladoGM, articuladoBN, articuladoETM, articuladoUNI = len(
        gA), len(bnA), len(eA), len(uA)
    padronGM, padronBN, padronETM, padronUNI = len(
        gP), len(bnP), len(eP), len(uP)
    complementGM, complementBN, complementETM, complementUNI = len(
        gC), len(bnC), len(eC), len(uC)

    # Variables Por Concesionario Fallas
    articuladoGMF, articuladoBNF, articuladoETMF, articuladoUNIF = len(
        gFA), len(bnFA), len(eFA), len(uFA)
    padronGMF, padronBNF, padronETMF, padronUNIF = len(
        gFP), len(bnFP), len(eFP), len(uFP)
    complementGMF, complementBNF, complementETMF, complementUNIF = len(
        gFC), len(bnFC), len(eFC), len(uFC)

    # Totales Concesionarios
    totalGit = articuladoGM + padronGM + complementGM
    totalGitF = articuladoGMF + padronGMF + complementGMF
    totalBN = articuladoBN + padronBN + complementBN
    totalBNF = articuladoBNF + padronBNF + complementBNF
    totalETM = articuladoETM + padronETM + complementETM
    totalETMF = articuladoETMF + padronETMF + complementETMF
    totalUNI = articuladoUNI + padronUNI + complementUNI
    totalUNIF = articuladoUNIF + padronUNIF + complementUNIF

    # Totales Generales
    totalBusesMio = len(busesData)
    totalBusesMioF = totalGitF + totalBNF + totalETMF + totalUNIF

    totalArticulados = articuladoGM + articuladoBN + articuladoETM + articuladoUNI
    totalPadrones = padronGM + padronBN + padronETM + padronUNI
    totalComplementarios = complementGM + \
        complementBN + complementETM + complementUNI

    totalArticuladosF = articuladoGMF + \
        articuladoBNF + articuladoETMF + articuladoUNIF
    totalPadronesF = padronGMF + padronBNF + padronETMF + padronUNIF
    totalComplementariosF = complementGMF + \
        complementBNF + complementETMF + complementUNIF

    return totalBusesMio, totalGit, totalBN, totalETM, totalUNI, totalBusesMioF, totalGitF, totalBNF, totalETMF, totalUNIF, totalArticuladosF, totalComplementariosF, totalPadronesF, articuladoGM, padronGM, complementGM, articuladoBN, padronBN, complementBN, articuladoETM, padronETM, complementETM, articuladoUNI, padronUNI, complementUNI


totalBusesMio, totalGit, totalBN, totalETM, totalUNI, totalBusesMioF, totalGitF, totalBNF, totalETMF, totalUNIF, totalArticuladosF, totalComplementariosF, totalPadronesF,  articuladoGM, padronGM, complementGM, articuladoBN, padronBN, complementBN, articuladoETM, padronETM, complementETM, articuladoUNI, padronUNI, complementUNI = getResultsReport()
df = pd.DataFrame({
    "Concesionario": ["GIT", "Blanco & Negro", "ETM", "Unimetro"],
    "# Total de Buses": [totalGit, totalBN, totalETM, totalUNI],
    "% de la Flota Total": [f"{((totalGit*100)/totalBusesMio):.0f}%", f"{((totalBN*100)/totalBusesMio):.0f}%", f"{((totalETM*100)/totalBusesMio):.0f}%", f"{((totalUNI*100)/totalBusesMio):.0f}%"]
})
df_tiposGIT = pd.DataFrame({
    "Tipo de Bus": ["Padrones", "Articulados", "Complementarios"],
    "# Total de Buses": [padronGM, articuladoGM, complementGM],
    "% de la Flota Total": [f"{((padronGM*100)/totalGit):.0f}%", f"{((articuladoGM*100)/totalGit):.0f}%",  f"{((complementGM*100)/totalGit):.0f}%"]
})
df_tiposBN = pd.DataFrame({
    "Tipo de Bus": ["Padrones", "Articulados", "Complementarios"],
    "# Total de Buses": [padronBN, articuladoBN, complementBN],
    "% de la Flota Total": [f"{((padronBN*100)/totalBN):.0f}%", f"{((articuladoBN*100)/totalBN):.0f}%",  f"{((complementBN*100)/totalBN):.0f}%"]
})
df_tiposETM = pd.DataFrame({
    "Tipo de Bus": ["Padrones", "Articulados", "Complementarios"],
    "# Total de Buses": [padronETM, articuladoETM, complementETM],
    "% de la Flota Total": [f"{((padronETM*100)/totalETM):.0f}%", f"{((articuladoETM*100)/totalETM):.0f}%",  f"{((complementETM*100)/totalETM):.0f}%"]
})
df_tiposUni = pd.DataFrame({
    "Tipo de Bus": ["Padrones", "Articulados", "Complementarios"],
    "# Total de Buses": [padronUNI, articuladoUNI, complementUNI],
    "% de la Flota Total": [f"{((padronUNI*100)/totalUNI):.0f}%", f"{((articuladoUNI*100)/totalUNI):.0f}%",  f"{((complementUNI*100)/totalUNI):.0f}%"]
})
df2 = pd.DataFrame({
    "Concesionario": ["GIT", "Blanco & Negro", "ETM", "Unimetro"],
    "# Total de Buses con Fallas": [totalGitF, totalBNF, totalETMF, totalUNIF],
})
df3 = pd.DataFrame({
    "Tipo de Bus": ["Padrones", "Articulados", "Complementarios"],
    "# Total de Tipos Buses con Fallas": [totalPadronesF, totalArticuladosF, totalComplementariosF],
})
select = dcc.Dropdown(
    id='demo-dropdown',

    options=[{'value': x, 'label': x}
             for x in ['Todos los Buses', 'GIT', 'Blanco & Negro', 'ETM', 'Unimetro']],
    value='Todos los Buses',
    clearable=False
)


fig = px.pie(df2, values='# Total de Buses con Fallas', names='Concesionario', color='Concesionario',  title=f"No. de Buses de MetroCali que Han Reportado Fallas (Total = {totalBusesMioF})",
             color_discrete_map={'GIT': 'dodgerblue',
                                 'Blanco & Negro': 'white',
                                 'ETM': 'limegreen',
                                 'Unimetro': 'gold'})
fig.update_traces(marker=dict(line=dict(color='#000000', width=0.5)))
pie_graph = dcc.Graph(figure=fig, style={"height": "500px"})


pie_graph2 = dcc.Loading(dcc.Graph(id="pie-graph", style={"height": "500px"}))

BusIDCounts["Counts"] = BusIDCounts["Counts"].astype(int)
BusIDCounts["BusID"] = BusIDCounts["BusID"].astype(str)

bar_graph = dcc.Loading(dcc.Graph(id="bar-graph", style={"height": "500px"}))


dfDuplicates["BusID"] = dfDuplicates["BusID"].astype(str)


bar_graph2 = dcc.Loading(dcc.Graph(id="bar-graph2", style={"height": "500px"}))


bar_graph3 = dcc.Loading(dcc.Graph(id="bar-lines", style={"height": "500px"}))

test_sample = buses_day_event_count.loc[buses_day_event_count['BusID'].isin(
    BusIDCounts['BusID'].head())]
fig6 = px.line(test_sample, x='DatagramDate', y='Count',
               title="No. de Eventos por día (Buses con mayor Numero Eventos Enviados)", color='BusID')
line_graph = dcc.Loading(
    dcc.Graph(id="line-graph", figure=fig6, style={"height": "500px"}))

test_sample2 = buses_day_event_count.loc[buses_day_event_count['BusID'].isin(
    dfDuplicates['BusID'].head())]
fig7 = px.line(test_sample2, x='DatagramDate', y='Count',
               title="No. de Eventos por día (Buses con mayor Numero Dias Enviados)", color='BusID')
line_graph2 = dcc.Loading(
    dcc.Graph(id="line-graph2", figure=fig7, style={"height": "500px"}))

# Tabs
tab1_content = dbc.Card(
    dbc.CardBody(
        [

            bar_graph
        ]
    ),
    className="mt-3",
)

tab2_content = dbc.Card(
    dbc.CardBody(
        [

            bar_graph2,
        ]
    ),
    className="mt-3",
)


tab3_content = dbc.Card(
    dbc.CardBody(
        [

            bar_graph3,
        ]
    ),
    className="mt-3",
)


def reportBuses():
    report = [
        html.Div(
            [
                html.Div(
                    [
                        html.H2(
                            "Reporte General",
                            style={"margin-bottom": "0px",
                                   "color": "darkslategrey"},
                        ),
                    ]
                )
            ],

            id="title",
            style=CONTENT_STYLE
        ), html.Br(), html.Div(
            [
                dbc.Row(
                    [
                        dbc.Col(html.Div(children=[
                            dbc.Row(
                                [
                                    dbc.Col(select, width=3),

                                ],
                            ), html.Br(), dcc.Loading(html.Div(id="table"))
                        ])),
                        dbc.Col(dbc.Card(
                            dbc.CardBody(
                                [

                                    pie_graph,
                                ]
                            ),
                            className="mt-3",
                        )),
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(html.Div(
                            [
                                dbc.Tabs(
                                    [
                                        dbc.Tab(tab1_content,
                                                label="Buses vs Total Fallas", id="tab-1"),
                                        dbc.Tab(tab2_content,
                                                label="Buses vs Total Dias", id="tab-2"),
                                        dbc.Tab(tab3_content,
                                                label="Lineas vs  Buses Reportados", id="tab-3"),
                                    ],
                                    id="tabs",

                                ),
                                html.Div(id="content"),
                            ]
                        )),

                        dbc.Col(dbc.Card(dbc.CardBody([

                            pie_graph2,
                        ]
                        ),
                            id="card-1",
                            className="mt-3"
                        )),
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(dbc.Card(
                            dbc.CardBody(
                                [

                                    line_graph,
                                ]
                            ),
                            className="mt-3",
                        )),
                        dbc.Col(dbc.Card(
                            dbc.CardBody(
                                [

                                    line_graph2,
                                ]
                            ),
                            className="mt-3",
                        )),

                    ]
                ),
            ]
        )

    ]
    return report


@app.callback(
    [
        Output("table", "children"),
        Output("bar-graph", "figure"),
        Output("bar-graph2", "figure"),
        Output("bar-lines", "figure"),
        Output("pie-graph", "figure"),
        Output("line-graph", "figure"),
        Output("line-graph2", "figure"),
    ],
    [
        Input("demo-dropdown", "value")
    ])
def update_table(value):
    if value == "Todos los Buses":
        fig3 = px.bar(BusIDCounts.head(15).sort_values(
            'Counts', ascending=True), x="Counts", y="BusID", title="Buses vs Total de Fallas Enviadas", color='Counts', orientation='h')

        fig = px.pie(df3, values='# Total de Tipos Buses con Fallas', names='Tipo de Bus', color='Tipo de Bus',  title=f"No. de Buses que Han Reportado Fallas (Total = {totalBusesMioF})",
                     color_discrete_map={'Padrones': 'dodgerblue',
                                         'Articulados': 'gainsboro',
                                         'Complementarios': 'greenyellow'})
        fig.update_traces(marker=dict(line=dict(color='#000000', width=0.5)))

        fig4 = px.bar(dfDuplicates.head(15).sort_values(
            'DateCount', ascending=True), x="DateCount", y="BusID", title="Buses vs Total de Enviando Dias", color='DateCount', orientation='h')

        df2 = datagrams[(datagrams['EventType'] == 12) |
                        (datagrams['EventType'] == 23)]
        df2['DatagramDate'] = pd.to_datetime(df2['DatagramDate'])
        df2 = df2.sort_values(by=['DatagramDate'])
        df2["BusID"] = df2["BusID"].astype(str)

        line_event_count = df2.groupby(
            'LineID')['BusID'].unique().iloc[:].reset_index()
        line_event_count['Buses_Count'] = line_event_count.apply(
            lambda row: len(row['BusID']), axis=1).astype(int)
        line_event_count.drop(['BusID'], axis=1, inplace=True)
        line_event_count.sort_values(
            by='Buses_Count', ascending=False, inplace=True)
        line_event_count = line_event_count.merge(
            right=linesData, on=['LineID'], how='inner')
        line_event_count = line_event_count[[
            'LineID', 'Shortname', 'Buses_Count']]

        fig5 = px.bar(line_event_count.head(15).sort_values(
            'Buses_Count', ascending=True), x="Buses_Count",
            y="Shortname", title="Lineas vs Buses Reportados", orientation='h', color='Buses_Count', color_continuous_scale=px.colors.sequential.Viridis)

        test_sample = buses_day_event_count.loc[buses_day_event_count['BusID'].isin(
            BusIDCounts['BusID'].head())]
        fig6 = px.line(test_sample, x='DatagramDate', y='Count',
                       title="No. de Eventos por día (Buses con mayor Numero Eventos Enviados)", color='BusID')
        fig6.update_xaxes(rangeslider_visible=True)
        fig6.update_traces(mode="markers+lines")

        test_sample2 = buses_day_event_count.loc[buses_day_event_count['BusID'].isin(
            dfDuplicates['BusID'].head())]
        fig7 = px.line(test_sample2, x='DatagramDate', y='Count',
                       title="No. de Eventos por día (Buses con mayor Numero Dias Enviados)", color='BusID')
        fig7.update_xaxes(rangeslider_visible=True)
        fig7.update_traces(mode="markers+lines")

        return [dbc.Row(
                [
                    dbc.Col(dbc.Table.from_dataframe(df, bordered=True, dark=False,
                                                     hover=True, responsive=True, striped=True)),
                ], align="end"
                )
                ], fig3, fig4, fig5, fig, fig6, fig7
    elif value == "GIT":
        gitA_x, gitA_y = getConcessionaireAndTypeArray(1, 1)
        gitP_x, gitP_y = getConcessionaireAndTypeArray(1, 2)
        gitC_x, gitC_y = getConcessionaireAndTypeArray(1, 3)

        gitA_x1, gitA_y1 = getConcessionaireAndTypeArrayFailure(1, 1)
        gitP_x1, gitP_y1 = getConcessionaireAndTypeArrayFailure(1, 2)
        gitC_x1, gitC_y1 = getConcessionaireAndTypeArrayFailure(1, 3)

        gitBusID = gitA_y + gitP_y + gitC_y
        df5 = pd.DataFrame({"BusID": gitBusID})
        df5['BusID'] = df5['BusID'].astype(str)
        int_df = pd.merge(BusIDCounts, df5, how='inner', on='BusID')
        int_df2 = pd.merge(dfDuplicates, df5, how='inner', on='BusID')
        dfGIT = pd.DataFrame({
            "Tipo de Bus": ["Padrones", "Articulados", "Complementarios"],
            "# Total de Tipos Buses con Fallas": [len(gitP_y1), len(gitA_y1), len(gitC_y1)],
        })

        df2 = datagrams[(datagrams['EventType'] == 12) |
                        (datagrams['EventType'] == 23)]
        df2['DatagramDate'] = pd.to_datetime(df2['DatagramDate'])
        df2 = df2.sort_values(by=['DatagramDate'])
        df2["BusID"] = df2["BusID"].astype(str)

        int_df3 = pd.merge(df2, df5, how='inner', on='BusID')

        line_event_count = int_df3.groupby(
            'LineID')['BusID'].unique().iloc[:].reset_index()
        line_event_count['Buses_Count'] = line_event_count.apply(
            lambda row: len(row['BusID']), axis=1).astype(int)
        line_event_count.drop(['BusID'], axis=1, inplace=True)
        line_event_count.sort_values(
            by='Buses_Count', ascending=False, inplace=True)
        line_event_count = line_event_count.merge(
            right=linesData, on=['LineID'], how='inner')
        line_event_count = line_event_count[[
            'LineID', 'Shortname', 'Buses_Count']]

        fig5 = px.bar(line_event_count.head(15).sort_values(
            'Buses_Count', ascending=True), x="Buses_Count",
            y="Shortname", title="Lineas vs Buses Reportados", orientation='h', color='Buses_Count', color_continuous_scale=px.colors.sequential.Viridis)

        fig = px.pie(dfGIT, values='# Total de Tipos Buses con Fallas', names='Tipo de Bus', color='Tipo de Bus',  title=f"No. de Tipos Buses que Han Reportado Fallas (Total = {totalGitF})",
                     color_discrete_map={'Padrones': 'dodgerblue',
                                         'Articulados': 'gainsboro',
                                         'Complementarios': 'greenyellow'})
        fig.update_traces(marker=dict(line=dict(color='#000000', width=0.5)))
        fig3 = px.bar(int_df.head(15).sort_values(
            'Counts', ascending=True), x="Counts", y="BusID", title="Buses vs Total de Fallas Enviadas (GIT)", color='Counts', orientation='h')

        fig4 = px.bar(int_df2.head(15).sort_values(
            'DateCount', ascending=True), x="DateCount", y="BusID", title="Buses vs Total de Enviando Dias", color='DateCount', orientation='h')

        test_sample = buses_day_event_count.loc[buses_day_event_count['BusID'].isin(
            int_df['BusID'].head())]
        fig6 = px.line(test_sample, x='DatagramDate', y='Count',
                       title="No. de Eventos por día (Buses con mayor Numero Eventos Enviados)", color='BusID')
        fig6.update_xaxes(rangeslider_visible=True)
        fig6.update_traces(mode="markers+lines")
        test_sample2 = buses_day_event_count.loc[buses_day_event_count['BusID'].isin(
            int_df2['BusID'].head())]
        fig7 = px.line(test_sample2, x='DatagramDate', y='Count',
                       title="No. de Eventos por día (Buses con mayor Numero Dias Enviados)", color='BusID')
        fig7.update_xaxes(rangeslider_visible=True)
        fig7.update_traces(mode="markers+lines")
        return [dbc.Row(
            [
                dbc.Col(dbc.Table.from_dataframe(df_tiposGIT, bordered=True, dark=False,
                                                 hover=True, responsive=True, striped=True,)),
            ], align="end"
        )
        ], fig3, fig4, fig5, fig, fig6, fig7
    elif value == "Blanco & Negro":
        gitA_x, gitA_y = getConcessionaireAndTypeArray(2, 1)
        gitP_x, gitP_y = getConcessionaireAndTypeArray(2, 2)
        gitC_x, gitC_y = getConcessionaireAndTypeArray(2, 3)

        gitA_x1, gitA_y1 = getConcessionaireAndTypeArrayFailure(2, 1)
        gitP_x1, gitP_y1 = getConcessionaireAndTypeArrayFailure(2, 2)
        gitC_x1, gitC_y1 = getConcessionaireAndTypeArrayFailure(2, 3)

        dfGIT = pd.DataFrame({
            "Tipo de Bus": ["Padrones", "Articulados", "Complementarios"],
            "# Total de Tipos Buses con Fallas": [len(gitP_y1), len(gitA_y1), len(gitC_y1)],
        })

        fig = px.pie(dfGIT, values='# Total de Tipos Buses con Fallas', names='Tipo de Bus', color='Tipo de Bus',  title=f"No. de Tipos Buses que Han Reportado Fallas (Total = {totalBNF})",
                     color_discrete_map={'Padrones': 'dodgerblue',
                                         'Articulados': 'gainsboro',
                                         'Complementarios': 'greenyellow'})
        fig.update_traces(marker=dict(line=dict(color='#000000', width=0.5)))

        gitBusID = gitA_y + gitP_y + gitC_y
        df5 = pd.DataFrame({"BusID": gitBusID})
        df5['BusID'] = df5['BusID'].astype(str)
        int_df = pd.merge(BusIDCounts, df5, how='inner', on='BusID')
        int_df2 = pd.merge(dfDuplicates, df5, how='inner', on='BusID')

        df2 = datagrams[(datagrams['EventType'] == 12) |
                        (datagrams['EventType'] == 23)]
        df2['DatagramDate'] = pd.to_datetime(df2['DatagramDate'])
        df2 = df2.sort_values(by=['DatagramDate'])
        df2["BusID"] = df2["BusID"].astype(str)

        int_df3 = pd.merge(df2, df5, how='inner', on='BusID')

        line_event_count = int_df3.groupby(
            'LineID')['BusID'].unique().iloc[:].reset_index()
        line_event_count['Buses_Count'] = line_event_count.apply(
            lambda row: len(row['BusID']), axis=1).astype(int)
        line_event_count.drop(['BusID'], axis=1, inplace=True)
        line_event_count.sort_values(
            by='Buses_Count', ascending=False, inplace=True)
        line_event_count = line_event_count.merge(
            right=linesData, on=['LineID'], how='inner')
        line_event_count = line_event_count[[
            'LineID', 'Shortname', 'Buses_Count']]

        fig5 = px.bar(line_event_count.head(15).sort_values(
            'Buses_Count', ascending=True), x="Buses_Count",
            y="Shortname", title="Lineas vs Buses Reportados", orientation='h', color='Buses_Count', color_continuous_scale=px.colors.sequential.Viridis)

        fig3 = px.bar(int_df.head(15).sort_values(
            'Counts', ascending=True), x="Counts", y="BusID", title="Buses vs Total de Fallas Enviadas (Blanco & Negro)", color='Counts', orientation='h')

        fig4 = px.bar(int_df2.head(15).sort_values(
            'DateCount', ascending=True), x="DateCount", y="BusID", title="Buses vs Total de Enviando Dias", color='DateCount', orientation='h')
        test_sample = buses_day_event_count.loc[buses_day_event_count['BusID'].isin(
            int_df['BusID'].head())]
        fig6 = px.line(test_sample, x='DatagramDate', y='Count',
                       title="No. de Eventos por día (Buses con mayor Numero Eventos Enviados)", color='BusID')
        fig6.update_xaxes(rangeslider_visible=True)
        fig6.update_traces(mode="markers+lines")
        test_sample2 = buses_day_event_count.loc[buses_day_event_count['BusID'].isin(
            int_df2['BusID'].head())]
        fig7 = px.line(test_sample2, x='DatagramDate', y='Count',
                       title="No. de Eventos por día (Buses con mayor Numero Dias Enviados)", color='BusID')
        fig7.update_xaxes(rangeslider_visible=True)
        fig7.update_traces(mode="markers+lines")
        return [dbc.Row(
                [
                    dbc.Col(dbc.Table.from_dataframe(df_tiposBN, bordered=True, dark=False,
                                                     hover=True, responsive=True, striped=True,)),
                ], align="end"
                )
                ], fig3, fig4, fig5, fig, fig6, fig7
    elif value == "ETM":
        gitA_x, gitA_y = getConcessionaireAndTypeArray(3, 1)
        gitP_x, gitP_y = getConcessionaireAndTypeArray(3, 2)
        gitC_x, gitC_y = getConcessionaireAndTypeArray(3, 3)

        gitA_x1, gitA_y1 = getConcessionaireAndTypeArrayFailure(3, 1)
        gitP_x1, gitP_y1 = getConcessionaireAndTypeArrayFailure(3, 2)
        gitC_x1, gitC_y1 = getConcessionaireAndTypeArrayFailure(3, 3)

        dfGIT = pd.DataFrame({
            "Tipo de Bus": ["Padrones", "Articulados", "Complementarios"],
            "# Total de Tipos Buses con Fallas": [len(gitP_y1), len(gitA_y1), len(gitC_y1)],
        })

        fig = px.pie(dfGIT, values='# Total de Tipos Buses con Fallas', names='Tipo de Bus', color='Tipo de Bus',  title=f"No. de Tipos Buses que Han Reportado Fallas (Total = {totalETMF})",
                     color_discrete_map={'Padrones': 'dodgerblue',
                                         'Articulados': 'gainsboro',
                                         'Complementarios': 'greenyellow'})
        fig.update_traces(marker=dict(line=dict(color='#000000', width=0.5)))

        gitBusID = gitA_y + gitP_y + gitC_y
        df5 = pd.DataFrame({"BusID": gitBusID})
        df5['BusID'] = df5['BusID'].astype(str)
        int_df = pd.merge(BusIDCounts, df5, how='inner', on='BusID')
        int_df2 = pd.merge(dfDuplicates, df5, how='inner', on='BusID')

        df2 = datagrams[(datagrams['EventType'] == 12) |
                        (datagrams['EventType'] == 23)]
        df2['DatagramDate'] = pd.to_datetime(df2['DatagramDate'])
        df2 = df2.sort_values(by=['DatagramDate'])
        df2["BusID"] = df2["BusID"].astype(str)

        int_df3 = pd.merge(df2, df5, how='inner', on='BusID')

        line_event_count = int_df3.groupby(
            'LineID')['BusID'].unique().iloc[:].reset_index()
        line_event_count['Buses_Count'] = line_event_count.apply(
            lambda row: len(row['BusID']), axis=1).astype(int)
        line_event_count.drop(['BusID'], axis=1, inplace=True)
        line_event_count.sort_values(
            by='Buses_Count', ascending=False, inplace=True)
        line_event_count = line_event_count.merge(
            right=linesData, on=['LineID'], how='inner')
        line_event_count = line_event_count[[
            'LineID', 'Shortname', 'Buses_Count']]

        fig5 = px.bar(line_event_count.head(15).sort_values(
            'Buses_Count', ascending=True), x="Buses_Count",
            y="Shortname", title="Lineas vs Buses Reportados", orientation='h', color='Buses_Count', color_continuous_scale=px.colors.sequential.Viridis)

        fig3 = px.bar(int_df.head(15).sort_values(
            'Counts', ascending=True), x="Counts", y="BusID", title="Buses vs Total de Fallas Enviadas (ETM)", color='Counts', orientation='h')

        fig4 = px.bar(int_df2.head(15).sort_values(
            'DateCount', ascending=True), x="DateCount", y="BusID", title="Buses vs Total de Enviando Dias", color='DateCount', orientation='h')
        test_sample = buses_day_event_count.loc[buses_day_event_count['BusID'].isin(
            int_df['BusID'].head())]
        fig6 = px.line(test_sample, x='DatagramDate', y='Count',
                       title="No. de Eventos por día (Buses con mayor Numero Eventos Enviados)", color='BusID')
        fig6.update_xaxes(rangeslider_visible=True)
        fig6.update_traces(mode="markers+lines")
        test_sample2 = buses_day_event_count.loc[buses_day_event_count['BusID'].isin(
            int_df2['BusID'].head())]
        fig7 = px.line(test_sample2, x='DatagramDate', y='Count',
                       title="No. de Eventos por día (Buses con mayor Numero Dias Enviados)", color='BusID')
        fig7.update_xaxes(rangeslider_visible=True)
        fig7.update_traces(mode="markers+lines")
        return [dbc.Row(
                [
                    dbc.Col(dbc.Table.from_dataframe(df_tiposBN, bordered=True, dark=False,
                                                     hover=True, responsive=True, striped=True,)),
                ], align="end"
                )
                ], fig3, fig4, fig5, fig, fig6, fig7
    elif value == "Unimetro":
        gitA_x, gitA_y = getConcessionaireAndTypeArray(4, 1)
        gitP_x, gitP_y = getConcessionaireAndTypeArray(4, 2)
        gitC_x, gitC_y = getConcessionaireAndTypeArray(4, 3)

        gitA_x1, gitA_y1 = getConcessionaireAndTypeArrayFailure(4, 1)
        gitP_x1, gitP_y1 = getConcessionaireAndTypeArrayFailure(4, 2)
        gitC_x1, gitC_y1 = getConcessionaireAndTypeArrayFailure(4, 3)

        dfGIT = pd.DataFrame({
            "Tipo de Bus": ["Padrones", "Articulados", "Complementarios"],
            "# Total de Tipos Buses con Fallas": [len(gitP_y1), len(gitA_y1), len(gitC_y1)],
        })

        fig = px.pie(dfGIT, values='# Total de Tipos Buses con Fallas', names='Tipo de Bus', color='Tipo de Bus',  title=f"No. de Tipos Buses que Han Reportado Fallas (Total = {totalUNIF})",
                     color_discrete_map={'Padrones': 'dodgerblue',
                                         'Articulados': 'gainsboro',
                                         'Complementarios': 'greenyellow'})
        fig.update_traces(marker=dict(line=dict(color='#000000', width=0.5)))

        gitBusID = gitA_y + gitP_y + gitC_y
        df5 = pd.DataFrame({"BusID": gitBusID})
        df5['BusID'] = df5['BusID'].astype(str)
        int_df = pd.merge(BusIDCounts, df5, how='inner', on='BusID')
        int_df2 = pd.merge(dfDuplicates, df5, how='inner', on='BusID')

        df2 = datagrams[(datagrams['EventType'] == 12) |
                        (datagrams['EventType'] == 23)]
        df2['DatagramDate'] = pd.to_datetime(df2['DatagramDate'])
        df2 = df2.sort_values(by=['DatagramDate'])
        df2["BusID"] = df2["BusID"].astype(str)

        int_df3 = pd.merge(df2, df5, how='inner', on='BusID')

        line_event_count = int_df3.groupby(
            'LineID')['BusID'].unique().iloc[:].reset_index()
        line_event_count['Buses_Count'] = line_event_count.apply(
            lambda row: len(row['BusID']), axis=1).astype(int)
        line_event_count.drop(['BusID'], axis=1, inplace=True)
        line_event_count.sort_values(
            by='Buses_Count', ascending=False, inplace=True)
        line_event_count = line_event_count.merge(
            right=linesData, on=['LineID'], how='inner')
        line_event_count = line_event_count[[
            'LineID', 'Shortname', 'Buses_Count']]

        fig5 = px.bar(line_event_count.head(15).sort_values(
            'Buses_Count', ascending=True), x="Buses_Count",
            y="Shortname", title="Lineas vs Buses Reportados", orientation='h', color='Buses_Count', color_continuous_scale=px.colors.sequential.Viridis)

        fig3 = px.bar(int_df.head(15).sort_values(
            'Counts', ascending=True), x="Counts", y="BusID", title="Buses vs Total de Fallas Enviadas (Unimetro)", color='Counts', orientation='h')

        fig4 = px.bar(int_df2.head(15).sort_values(
            'DateCount', ascending=True), x="DateCount", y="BusID", title="Buses vs Total de Enviando Dias", color='DateCount', orientation='h')
        test_sample = buses_day_event_count.loc[buses_day_event_count['BusID'].isin(
            int_df['BusID'].head())]
        fig6 = px.line(test_sample, x='DatagramDate', y='Count',
                       title="No. de Eventos por día (Buses con mayor Numero Eventos Enviados)", color='BusID')
        fig6.update_xaxes(rangeslider_visible=True)
        fig6.update_traces(mode="markers+lines")
        test_sample2 = buses_day_event_count.loc[buses_day_event_count['BusID'].isin(
            int_df2['BusID'].head())]
        fig7 = px.line(test_sample2, x='DatagramDate', y='Count',
                       title="No. de Eventos por día (Buses con mayor Numero Dias Enviados)", color='BusID')
        fig7.update_xaxes(rangeslider_visible=True)
        fig7.update_traces(mode="markers+lines")
        return [dbc.Row(
                [
                    dbc.Col(dbc.Table.from_dataframe(df_tiposBN, bordered=True, dark=False,
                                                     hover=True, responsive=True, striped=True,)),
                ], align="end"
                )
                ], fig3, fig4, fig5, fig, fig6, fig7

    return html.P("This shouldn't ever be displayed...")
