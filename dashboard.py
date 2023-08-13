from dash import dcc, html, Dash
import dash_bootstrap_components as dbc
from spotify_data_plots import FIGS

app = Dash(__name__, external_stylesheets=[dbc.themes.MINTY])

app.layout = dbc.Container(
    [
        dbc.Row(dbc.Col(html.H2('SPOTIFY DATA OVERVIEW', className='text-center text-primary, my-3'))),  # header row
        
        dbc.Row([  
            dbc.Col([  
                dcc.Graph(id='daily_hours',
                      figure=FIGS['daily_hours'],
                      style={'height':400}),
            ], width={'size': 8, 'offset': 0, 'order': 1}),  
            dbc.Col([  
                dcc.Graph(id='total_distribution_hours_played',
                      figure = FIGS['total_distribution_hours_played'],
                      style={'height':400}),
            ], width={'size': 4, 'offset': 0, 'order': 2}),
        ]),
        
        dbc.Row([
            dbc.Col([
                dcc.Graph(id='monthly_hours',
                      figure=FIGS['monthly_hours'],
                      style={'height':400}),
            ], width={'size': 12, 'offset': 0, 'order': 1}),
        ]),

        dbc.Row([
            dbc.Col([
                dcc.Graph(id='monthly_ratio_hours_played',
                      figure=FIGS['monthly_ratio_hours_played'],
                      style={'height':400}
                   ),
            ], width={'size': 12, 'offset': 0, 'order': 1}),
        ]),

        dbc.Row([
            dbc.Col([
                dcc.Graph(id='popularity',
                      figure=FIGS['popularity'],
                      style={'height':400}
                   ),
            ], width={'size': 4, 'offset': 0, 'order': 1}),

            dbc.Col([
                dcc.Graph(id='duration',
                      figure=FIGS['duration'],
                      style={'height':400}
                   ),
            ], width={'size': 4, 'offset': 0, 'order': 1}),
            dbc.Col([
                dcc.Graph(id='features_mean',
                      figure = FIGS['features_mean'],
                      style={'height':380}),
            ], width={'size': 4, 'offset': 0, 'order': 2}),
        ]),

        dbc.Row([
            dbc.Col([
                dcc.Graph(id='tempo',
                      figure=FIGS['tempo'],
                      style={'height':400}
                   ),
            ], width={'size': 4, 'offset': 0, 'order': 1}),

        dbc.Col([
                dcc.Graph(id='features_histogram',
                      figure = FIGS['features_histogram'],
                      style={'height':400}),
            ], width={'size': 4, 'offset': 0, 'order': 2}),

        dbc.Col([
                dcc.Graph(id='pie-features_std',
                      figure = FIGS['features_std'],
                      style={'height':400}),
            ], width={'size': 4, 'offset': 0, 'order': 2}),

        ])
        
    ], fluid=True)


if __name__ == "__main__":
    app.run_server(debug=True, port=8060)
