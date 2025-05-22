import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
from dash import dash_table

# --- Configurações Iniciais ---
app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
server = app.server

# --- Carregamento e Limpeza dos Dados ---
def carregar_dados():
    try:
        df = pd.read_csv('Relatorio.csv', sep=';', encoding='latin1')
        df.columns = ['Entidade', 'Credor', 'Cargo', 'Especie', 'Empenho', 'Emissao', 
                      'Valor_Transporte', 'Valor_Diarias']

        for col in ['Valor_Diarias', 'Valor_Transporte']:
            df[col] = df[col].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        df['Emissao'] = pd.to_datetime(df['Emissao'], format='%d/%m/%Y', errors='coerce')
        df['Mes'] = df['Emissao'].dt.month
        df['Ano'] = df['Emissao'].dt.year
        df['Cargo'] = df['Cargo'].fillna('Não Especificado')
        return df
    except Exception as e:
        print(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

df = carregar_dados()

# --- Cores e Estilos Personalizados ---
COLORS = {
    'background': '#222222',
    'text': '#FFFFFF',
    'primary': '#375a7f',
    'secondary': '#444',
    'accent': '#3498db'
}

CARD_STYLE = {
    'border': '1px solid ' + COLORS['secondary'],
    'boxShadow': '0 4px 8px 0 rgba(0,0,0,0.2)',
    'borderRadius': '5px'
}

GRAPH_CONFIG = {
    'displayModeBar': False,
    'staticPlot': False
}

# --- Layout ---
app.layout = dbc.Container([
    # Cabeçalho com título e descrição
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H1("Dashboard de Diárias", className="display-4 text-center mb-3", 
                       style={'color': COLORS['accent'], 'fontWeight': 'bold'}),
                html.P("Análise de despesas com diárias em São José/SC", 
                      className="lead text-center mb-4",
                      style={'color': COLORS['text']}),
                html.Hr(style={'borderTop': f"1px solid {COLORS['secondary']}", 'width': '80%'})
            ], className="my-4")
        ])
    ]),
    
    # Linha de filtros e resumo
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Filtros", className="text-white", 
                              style={'backgroundColor': COLORS['primary'], 'fontWeight': 'bold'}),
                dbc.CardBody([
                    html.Label("Selecione a Entidade:", className="mb-2 font-weight-bold"),
                    dcc.Dropdown(
                        id='filtro-entidade',
                        options=[{'label': 'Todas as Entidades', 'value': 'Todas'}] +
                                [{'label': i, 'value': i} for i in sorted(df['Entidade'].unique())],
                        value='Todas',
                        className="mb-4",
                        style={'color': '#333'}
                    ),
                    html.Label("Intervalo de Meses:", className="mb-2 font-weight-bold"),
                    dcc.RangeSlider(
                        id='filtro-mes',
                        min=1, max=12, step=1,
                        value=[1, 12],
                        marks={i: ['Jan','Fev','Mar','Abr','Mai','Jun',
                                  'Jul','Ago','Set','Out','Nov','Dez'][i-1] for i in range(1, 13)},
                        className="mb-2"
                    )
                ], style={'padding': '20px'})
            ], style=CARD_STYLE)
        ], md=4, className="mb-4"),
        
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Resumo Financeiro", className="text-white", 
                              style={'backgroundColor': COLORS['primary'], 'fontWeight': 'bold'}),
                dbc.CardBody(id='resumo', style={'padding': '25px'})
            ], style=CARD_STYLE)
        ], md=8, className="mb-4")
    ], className="mb-4"),
    
    # Primeira linha de gráficos
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Distribuição por Entidade", className="text-white", 
                              style={'backgroundColor': COLORS['primary'], 'fontWeight': 'bold'}),
                dbc.CardBody(dcc.Graph(id='grafico-entidade', config=GRAPH_CONFIG))
            ], style=CARD_STYLE)
        ], md=6, className="mb-4"),
        
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Top 10 Beneficiários", className="text-white", 
                              style={'backgroundColor': COLORS['primary'], 'fontWeight': 'bold'}),
                dbc.CardBody(dcc.Graph(id='grafico-credores', config=GRAPH_CONFIG))
            ], style=CARD_STYLE)
        ], md=6, className="mb-4")
    ]),
    
    # Segundo linha de gráficos
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Distribuição por Cargo", className="text-white", 
                              style={'backgroundColor': COLORS['primary'], 'fontWeight': 'bold'}),
                dbc.CardBody(dcc.Graph(id='grafico-cargo', config=GRAPH_CONFIG))
            ], style=CARD_STYLE)
        ], className="mb-4")
    ]),
    
    # Tabela de dados
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Detalhamento das Diárias", className="text-white", 
                              style={'backgroundColor': COLORS['primary'], 'fontWeight': 'bold'}),
                dbc.CardBody(html.Div(id='tabela', style={'overflowX': 'auto'}))
            ], style=CARD_STYLE)
        ], className="mb-4")
    ]),
    
    # Rodapé
    dbc.Row([
        dbc.Col([
            html.Div([
                html.Hr(style={'borderTop': f"1px solid {COLORS['secondary']}", 'width': '80%'}),
                html.P("© 2023 Prefeitura de São José/SC - Dados atualizados em " + 
                       pd.to_datetime('today').strftime('%d/%m/%Y'),
                      className="text-center mt-3",
                      style={'color': COLORS['text'], 'fontSize': '0.9em'})
            ], className="my-4")
        ])
    ])
], fluid=True, style={'backgroundColor': COLORS['background'], 'padding': '20px'})

# --- Callback ---
@app.callback(
    Output('resumo', 'children'),
    Output('grafico-entidade', 'figure'),
    Output('grafico-credores', 'figure'),
    Output('grafico-cargo', 'figure'),
    Output('tabela', 'children'),
    Input('filtro-entidade', 'value'),
    Input('filtro-mes', 'value')
)
def atualizar_dashboard(entidade, meses):
    dff = df.copy()

    if entidade != 'Todas':
        dff = dff[dff['Entidade'] == entidade]

    dff = dff[(dff['Mes'] >= meses[0]) & (dff['Mes'] <= meses[1])]

    if dff.empty:
        return ["Nenhum dado encontrado."], go.Figure(), go.Figure(), go.Figure(), ""

    total = f"R$ {dff['Valor_Diarias'].sum():,.2f}".replace('.', '#').replace(',', '.').replace('#', ',')
    media = f"R$ {dff['Valor_Diarias'].mean():,.2f}".replace('.', '#').replace(',', '.').replace('#', ',')
    maximo = f"R$ {dff['Valor_Diarias'].max():,.2f}".replace('.', '#').replace(',', '.').replace('#', ',')

    resumo = dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Total em Diárias", className="card-title"),
                    html.P(total, className="card-text h3", 
                          style={'color': COLORS['accent'], 'fontWeight': 'bold'})
                ])
            ], style={'backgroundColor': COLORS['secondary'], 'height': '100%'})
        ], md=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Média das Diárias", className="card-title"),
                    html.P(media, className="card-text h3",
                          style={'color': COLORS['accent'], 'fontWeight': 'bold'})
                ])
            ], style={'backgroundColor': COLORS['secondary'], 'height': '100%'})
        ], md=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Maior Diária", className="card-title"),
                    html.P(maximo, className="card-text h3",
                          style={'color': COLORS['accent'], 'fontWeight': 'bold'})
                ])
            ], style={'backgroundColor': COLORS['secondary'], 'height': '100%'})
        ], md=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Beneficiários", className="card-title"),
                    html.P(f"{dff['Credor'].nunique()}", className="card-text h3",
                          style={'color': COLORS['accent'], 'fontWeight': 'bold'})
                ])
            ], style={'backgroundColor': COLORS['secondary'], 'height': '100%'})
        ], md=3)
    ])

    # Gráfico de Entidades
    entidade_data = dff.groupby('Entidade')['Valor_Diarias'].sum().reset_index()
    fig_ent = px.bar(entidade_data, x='Entidade', y='Valor_Diarias', 
                     color='Entidade', template='plotly_dark',
                     title='<b>Diárias por Entidade</b>',
                     labels={'Valor_Diarias': 'Valor Total (R$)', 'Entidade': ''})
    fig_ent.update_layout(
        plot_bgcolor=COLORS['background'],
        paper_bgcolor=COLORS['background'],
        font_color=COLORS['text'],
        showlegend=False,
        hovermode='x'
    )
    
    # Gráfico de Credores
    credores_data = dff.groupby('Credor')['Valor_Diarias'].sum().reset_index().nlargest(10, 'Valor_Diarias')
    fig_cred = px.bar(credores_data, x='Valor_Diarias', y='Credor', 
                      orientation='h', color='Valor_Diarias',
                      template='plotly_dark',
                      title='<b>Top 10 Beneficiários</b>',
                      labels={'Valor_Diarias': 'Valor Total (R$)', 'Credor': ''},
                      color_continuous_scale='Blues')
    fig_cred.update_layout(
        plot_bgcolor=COLORS['background'],
        paper_bgcolor=COLORS['background'],
        font_color=COLORS['text'],
        showlegend=False,
        yaxis={'categoryorder': 'total ascending'}
    )
    
    # Gráfico de Cargos
    cargo_data = dff.groupby('Cargo')['Valor_Diarias'].sum().reset_index().nlargest(15, 'Valor_Diarias')
    fig_cargo = px.treemap(cargo_data, path=['Cargo'], values='Valor_Diarias',
                           title='<b>Distribuição por Cargo</b>',
                           color='Valor_Diarias', hover_data=['Valor_Diarias'],
                           color_continuous_scale='Blues',
                           template='plotly_dark')
    fig_cargo.update_layout(
        plot_bgcolor=COLORS['background'],
        paper_bgcolor=COLORS['background'],
        font_color=COLORS['text'],
        margin=dict(t=50, l=25, r=25, b=25)
    )
    fig_cargo.update_traces(
        textinfo="label+value",
        texttemplate="<b>%{label}</b><br>R$ %{value:,.2f}",
        hovertemplate="<b>%{label}</b><br>Total: R$ %{value:,.2f}<extra></extra>"
    )

    # Tabela de dados
    tabela_df = dff[['Entidade', 'Credor', 'Cargo', 'Emissao', 'Valor_Diarias']].sort_values('Valor_Diarias', ascending=False).head(20)
    tabela_df['Valor_Diarias'] = tabela_df['Valor_Diarias'].apply(lambda x: f"R$ {x:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','))
    tabela_df['Emissao'] = tabela_df['Emissao'].dt.strftime('%d/%m/%Y')
    tabela_df.columns = ['Entidade', 'Beneficiário', 'Cargo', 'Data', 'Valor']
    
    tabela = dash_table.DataTable(
        data=tabela_df.to_dict('records'),
        columns=[{'name': i, 'id': i} for i in tabela_df.columns],
        style_table={'overflowX': 'auto'},
        style_header={
            'backgroundColor': COLORS['primary'],
            'color': 'white',
            'fontWeight': 'bold'
        },
        style_cell={
            'backgroundColor': COLORS['secondary'],
            'color': 'white',
            'padding': '10px',
            'textAlign': 'left'
        },
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': '#444'
            }
        ],
        page_size=10,
        filter_action='native',
        sort_action='native'
        
    )
    

    return resumo, fig_ent, fig_cred, fig_cargo, tabela

# --- Run ---
if __name__ == '__main__':
    app.run(debug=True)
