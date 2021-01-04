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
df = df.drop(df.columns[0], axis='columns')


def busModel(numId):

    df_Bus = df[df['BusID'] == int(numId)]
    features_to_test = ['DistanceTraveled', 'TBF', 'ECPF', 'SCPF', 'DBF']
    df_Bus2 = df_Bus[features_to_test]
    train_dataset = df_Bus2 .sample(frac=0.7, random_state=0)
    test_dataset = df_Bus2.drop(train_dataset.index)
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
    if(int(numId) == 571):

        results = tpot_571.predict(
            normed_test_data[['DistanceTraveled', 'TBF', 'ECPF', 'SCPF']])

        tpot_r2 = r2_score(normed_test_data['DBF'], results)
        tpot_mae = mean_absolute_error(normed_test_data['DBF'], results)
        size_train = len(normed_train_data)
        size_test = len(normed_test_data)
        y_test = normed_test_data['DBF']
        y_pred = results
    if(int(numId) == 132):
    
        results = tpot_132.predict(
            normed_test_data[['DistanceTraveled', 'TBF', 'ECPF', 'SCPF']])

        tpot_r2 = r2_score(normed_test_data['DBF'], results)
        tpot_mae = mean_absolute_error(normed_test_data['DBF'], results)
        size_train = len(normed_train_data)
        size_test = len(normed_test_data)
        y_test = normed_test_data['DBF']
        y_pred = results

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

    # Histograma
    error = y_pred - y_test
    fig = px.histogram(x=error, nbins=25, labels={
                       'x': 'Prediction Error [DBF]', 'y': 'Count'})
    error_graph = dcc.Graph(figure=fig, style={"height": "500px"})

    # Actual vs Predicted Figure
    avp_fig = px.scatter(
        x=y_test,
        y=y_pred,
        labels={"x": "Actual", "y": "Predicted"},
        title=f"Actual vs predicted results",
    )

    avp_fig.add_shape(
        type="line", x0=y_test.min(), y0=y_test.min(), x1=y_test.max(), y1=y_test.max()
    )
    avp_graph = dcc.Graph(figure=avp_fig, style={"height": "500px"})
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

        ],
        )


    ]
    return bus
