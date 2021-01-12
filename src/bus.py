import pickle
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_core_components as dcc
from sklearn.metrics import mean_absolute_error, r2_score, median_absolute_error
import pandas as pd
import plotly.express as px
CONTENT_STYLE = {
    "text-align": "center",
    "margin-bottom": "2rem"
}
# Load data
df = pd.read_csv(
    "./data/busesT31.csv",
    low_memory=False,
)

# load model
tpot_571 = pickle.load(open('./src/models/tpot_571.pkl', 'rb'))
tpot_132 = pickle.load(open('./src/models/tpot_132.pkl', 'rb'))
randomForest_571 = pickle.load(open('./src/models/randomForest_571.pkl', 'rb'))
randomForest_132 = pickle.load(open('./src/models/randomForest_132.pkl', 'rb'))
df = df.drop(df.columns[0], axis='columns')


def busModel(numId):

    df_Bus = df[df['BusID'] == int(numId)]
    features_to_test = ['DistanceTraveled', 'TBF', 'ECPF', 'SCPF', 'DBF']
    df_Bus2 = df_Bus[features_to_test]
    train_dataset = df_Bus2 .sample(frac=0.7, random_state=0)
    test_dataset = df_Bus2.drop(train_dataset.index)
    X = df_Bus[['DistanceTraveled', 'TBF', 'ECPF', 'SCPF']]
    y = df_Bus['DBF']
    X2 = df_Bus[['TBF', 'ECPF', 'SCPF']]
    y2 = df_Bus['DBF']
    # Normalizar---------------------------
    train_stats = train_dataset.describe()
    train_stats.pop("DBF")
    train_stats = train_stats.transpose()

    def norm(x):
        return (x - train_stats['mean']) / train_stats['std']
    normed_train_data = norm(
        train_dataset[['DistanceTraveled', 'TBF', 'ECPF', 'SCPF']])
    normed_test_data = norm(
        test_dataset[['DistanceTraveled', 'TBF', 'ECPF', 'SCPF']])
    normed_train_data['DBF'] = train_dataset['DBF']
    normed_test_data['DBF'] = test_dataset['DBF']
    # ------------------------------------
    # ---- Desarrollo de graficas del Modelo y Resultados de metricas
    if(int(numId) == 306):
        results = tpot_571.predict(
        normed_test_data[['DistanceTraveled', 'TBF', 'ECPF', 'SCPF']])

        tpot_r2 = r2_score(normed_test_data['DBF'], results)
        tpot_mae = mean_absolute_error(normed_test_data['DBF'], results)
        size_train = len(normed_train_data)
        size_test = len(normed_test_data)
        y_test = normed_test_data['DBF']
        y_pred = results




        bus = [
            html.Div(
                [
                    html.Div(
                        [
                            html.H2(
                                "Modelos del",
                                style={"margin-bottom": "0px",
                                    "color": "darkslategrey"},
                            ),
                            html.H4(
                                "Bus "+numId, style={"margin-top": "0px", "color": "darkslategrey"}
                            ),
                        ]
                    )
                ],

                id="title",
                style=CONTENT_STYLE
            ), html.H5("Red Deep Learning (H2O)"), html.Hr(),
            
        ]
           
    else:


        if(int(numId) == 571):

            results = tpot_571.predict(
                normed_test_data[['DistanceTraveled', 'TBF', 'ECPF', 'SCPF']])

            tpot_r2 = r2_score(normed_test_data['DBF'], results)
            tpot_mae = mean_absolute_error(normed_test_data['DBF'], results)
            size_train = len(normed_train_data)
            size_test = len(normed_test_data)
            y_test = normed_test_data['DBF']
            y_pred = results

            
            train_index = range(102,507)
            test_index = range(0,101)
            X_train, X_test2 = X.iloc[train_index], X.iloc[test_index]
            y_test2 = y.iloc[test_index]
            results2 = randomForest_571.predict(X_test2)
            randomF_r2 = r2_score(y_test2, results2)
            randomF_mae = mean_absolute_error(y_test2, results2)
            size_trainRandom = len(X_train)
            size_testRandom = len(y_test2)
        if(int(numId) == 132):

            results = tpot_132.predict(
                normed_test_data[['DistanceTraveled', 'TBF', 'ECPF', 'SCPF']])

            tpot_r2 = r2_score(normed_test_data['DBF'], results)
            tpot_mae = mean_absolute_error(normed_test_data['DBF'], results)
            size_train = len(normed_train_data)
            size_test = len(normed_test_data)
            y_test = normed_test_data['DBF']
            y_pred = results

            train_index = list(range(0,162)) + list(range(217,270))
            test_index = range(163,216)
            X_train, X_test2 = X2.iloc[train_index], X2.iloc[test_index]
            y_test2 = y2.iloc[test_index]
            results2 = randomForest_132.predict(X_test2)
            randomF_r2 = r2_score(y_test2, results2)
            randomF_mae = mean_absolute_error(y_test2, results2)
            size_trainRandom = len(X_train)
            size_testRandom = len(y_test2)

        # ----Parte Visual
        cards = html.Div(
            [
                dbc.Row(
                    [
                        dbc.Col(dbc.Card(dbc.CardBody(
                            [
                                html.H4(f"{tpot_r2*100:.2f}%",
                                        className="card-title"),
                                html.P(
                                    "R2 del Modelo",
                                    className="card-text",
                                ),
                            ]
                        ), color="light")),
                        dbc.Col(
                            dbc.Card(dbc.CardBody(
                                [
                                    html.H4(f"{tpot_mae/1000:.2f} km",
                                            className="card-title"),
                                    html.P(
                                        "MAE del Modelo",
                                        className="card-text",
                                    ),
                                ]
                            ), color="info", inverse=True)
                        ),
                        dbc.Col(dbc.Card(dbc.CardBody(
                            [
                                html.H4(f"{size_train}/{size_test}",
                                        className="card-title"),
                                html.P(
                                    "Partición Entrenamiento/Pruebas ",
                                    className="card-text",
                                ),
                            ]
                        ), color="light")),
                    ],
                    className="mb-5",
                    style={"margin-right": "10rem",
                        "margin-left": "10rem", "margin-top": "1.5rem"}
                )

            ]

        )
        cards2 = html.Div(
            [
                dbc.Row(
                    [
                        dbc.Col(dbc.Card(dbc.CardBody(
                            [
                                html.H4(f"{randomF_r2*100:.2f}%",
                                        className="card-title"),
                                html.P(
                                    "R2 del Modelo",
                                    className="card-text",
                                ),
                            ]
                        ), color="light")),
                        dbc.Col(
                            dbc.Card(dbc.CardBody(
                                [
                                    html.H4(f"{randomF_mae/1000:.2f} km",
                                            className="card-title"),
                                    html.P(
                                        "MAE del Modelo",
                                        className="card-text",
                                    ),
                                ]
                            ), color="info", inverse=True)
                        ),
                        dbc.Col(dbc.Card(dbc.CardBody(
                            [
                                html.H4(f"{size_trainRandom}/{size_testRandom}",
                                        className="card-title"),
                                html.P(
                                    "Partición Entrenamiento/Pruebas ",
                                    className="card-text",
                                ),
                            ]
                        ), color="light")),
                    ],
                    className="mb-5",
                    style={"margin-right": "10rem",
                        "margin-left": "10rem", "margin-top": "1.5rem"}
                )

            ]

        )
        cards3 = html.Div(
            [
                dbc.Row(
                    [
                        dbc.Col(dbc.Card(dbc.CardBody(
                            [
                                html.H4(f"{0*100:.2f}%",
                                        className="card-title"),
                                html.P(
                                    "R2 del Modelo",
                                    className="card-text",
                                ),
                            ]
                        ), color="light")),
                        dbc.Col(
                            dbc.Card(dbc.CardBody(
                                [
                                    html.H4(f"{0/1000:.2f} km",
                                            className="card-title"),
                                    html.P(
                                        "MAE del Modelo",
                                        className="card-text",
                                    ),
                                ]
                            ), color="info", inverse=True)
                        ),
                        dbc.Col(dbc.Card(dbc.CardBody(
                            [
                                html.H4(f"{0}/{0}",
                                        className="card-title"),
                                html.P(
                                    "Partición Entrenamiento/Pruebas ",
                                    className="card-text",
                                ),
                            ]
                        ), color="light")),
                    ],
                    className="mb-5",
                    style={"margin-right": "10rem",
                        "margin-left": "10rem", "margin-top": "1.5rem"}
                )

            ]

        )

        # Histograma
        error = y_pred - y_test
        fig = px.histogram(x=error, nbins=25, labels={
                        'x': 'Error de Predicción [DBF]', 'y': 'Total'}, title=f"Distribución del Error de Predicción")
        error_graph = dcc.Graph(figure=fig, style={"height": "500px"})

        # Histograma
        error2 = results2 - y_test2
        fig2 = px.histogram(x=error2, nbins=25, labels={
                        'x': 'Error de Predicción [DBF]', 'y': 'Total'}, title=f"Distribución del Error de Predicción")
        error_graph2 = dcc.Graph(figure=fig2, style={"height": "500px"})

        # Actual vs Predicted Figure
        avp_fig = px.scatter(
            x=y_test,
            y=y_pred,
            labels={"x": "Actual", "y": "Predicción"},
            title=f"Resultados Reales vs Predicciones",
        )

        avp_fig.add_shape(
            type="line", x0=y_test.min(), y0=y_test.min(), x1=y_test.max(), y1=y_test.max()
        )
        avp_graph = dcc.Graph(figure=avp_fig, style={"height": "500px"})
         # Actual vs Predicted Figure
        avp_fig2 = px.scatter(
            x=y_test2,
            y=results2,
            labels={"x": "Actual", "y": "Predicción"},
            title=f"Resultados Reales vs Predicciones",
        )

        avp_fig2.add_shape(
            type="line", x0=y_test2.min(), y0=y_test2.min(), x1=y_test2.max(), y1=y_test2.max()
        )
        avp_graph2 = dcc.Graph(figure=avp_fig2, style={"height": "500px"})
        bus = [
            html.Div(
                [
                    html.Div(
                        [
                            html.H2(
                                "Modelos del",
                                style={"margin-bottom": "0px",
                                    "color": "darkslategrey"},
                            ),
                            html.H4(
                                "Bus "+numId, style={"margin-top": "0px", "color": "darkslategrey"}
                            ),
                        ]
                    )
                ],

                id="title",
                style=CONTENT_STYLE
            ), html.H5("Modelo Árbol de Decisión (TPOT)"), html.Hr(),
            cards, dbc.Row([

                dbc.Col([avp_graph], md=4),
                dbc.Col([error_graph], md=4),

            ],), html.Br(), html.H5("Random Forest"), html.Hr(), cards2,dbc.Row([

                dbc.Col([avp_graph2], md=4),
                dbc.Col([error_graph2], md=4),

            ],),  html.Br(), html.H5("Red Deep Learning (H2O)"), html.Hr(), cards3


        ]
    return bus
