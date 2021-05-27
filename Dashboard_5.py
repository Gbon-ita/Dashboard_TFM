
import dash
import dash_core_components as dcc
import dash_html_components as html

import plotly.express as px
import pandas as pd

from datetime import datetime

import dash_cytoscape as cyto

from plotly_wordcloud import plotly_wordcloud as pwc


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)
colors = {
    'background': '#222211',
    'text': '#7FABFF'
}

df_grafo=pd.read_csv('grafo.csv')

df = pd.read_csv('df_bow_final .csv')
df.drop(columns=['Unnamed: 0'], inplace=True)
df['Fecha']=pd.to_datetime(df['Fecha'])
df_mapa_filter=df[df.Fecha>=datetime.strptime('09/01/20','%m/%d/%y')]
df_mapa_filter=df_mapa_filter[df_mapa_filter.Fecha<datetime.strptime('10/01/20','%m/%d/%y')]
df_mapa_filter=df_mapa_filter[df_mapa_filter.N_like<1500]
df_mapa=df_mapa_filter.iloc[:,2:11].groupby(['TopPosition','Latitude','Longitude']).sum()
df_mapa['N_post']=df.iloc[:,2:11].groupby(['TopPosition','Latitude','Longitude']).count().Coordenadas
df_mapa.reset_index(inplace=True)
df_mapa['N_like_medio']=(df_mapa.N_like/df_mapa.N_post).apply(lambda x: int(x))
px.set_mapbox_access_token('pk.eyJ1IjoiY3J5cHRvcG90bHVjayIsImEiOiJjazhtbTN6aHEwa3lwM25taW5qNTdicHAwIn0.xFsCTDqPE_0L-OHwv21qTg')
fig = px.scatter_mapbox(df_mapa, lat="Latitude", lon="Longitude",hover_name="TopPosition",color="N_like_medio", size="N_post",width=1300, height=700,
                  color_continuous_scale=px.colors.sequential.Jet, size_max=25, zoom=12)
fig.update_layout(font_color=colors['text'])

df_1=pd.DataFrame([])
df_1['sum']=df.iloc[:,-21:].sum(axis=0)
df_1['alt']=df.columns[-21:]
fig_pie = px.pie(df_1, values='sum', names='alt')
fig_pie.update_layout(font_color=colors['text'])

df_w=pd.read_csv('df_bow_cluster.csv')

app.layout = html.Div([
    dcc.Location(id='url', refresh=True),
    html.Div(id='page-content')
])

#style={'backgroundColor': colors['background']},children=
index_page = html.Div([
    html.H1(
        children='Valencia',
        style={
            'textAlign': 'center',
            'color': 'red'
        }
    ),

    html.H2(children='Encuentras tu lugar favorito', style={
        'textAlign': 'center',
        'color': colors['text']
    }),
    dcc.Graph(
        id='example-graph-2',
        figure=fig
    ),
html.Div([
        html.Div([
            html.H3('Lugares Turisticos',style={
            'color': colors['text']
        }),dcc.Link('ajuntament-de-valencia',refresh=True, href='ajuntament-de-valencia'),
        html.Br(),dcc.Link('oceanografic-valencia',refresh=True, href='oceanografic-valencia'),
        html.Br(),dcc.Link('llotja-de-la-seda',refresh=True, href='llotja-de-la-seda')
            
        ], className="six columns"),

        html.Div([
            html.H3('Sujeto mas fotografiado',style={
            'textAlign': 'center',
            'color': colors['text']
        }),
            dcc.Graph(id='g2', figure=fig_pie)
        ], className="six columns"),
    ], className="row"),html.Div(id='page-content')
])




def grafo(pathname):
	df_tmp=df_grafo['Unnamed: 0'][df_grafo[pathname]>4].values
	elements=[{'data':{'id':pathname,'label':pathname}}]
	for i in df_tmp:
		elements.append({'data':{'id':i,'label':i}})
	for i in df_tmp:
		if i == pathname:
			continue
		elements.append({'data': {'source': pathname, 'target': i}})
	f=cyto.Cytoscape(id='cytoscape',style={'width': '100%', 'height': '400px'},layout={'name': 'circle'},elements=elements)
	return f, df_tmp

def page_1_layout(pathname):
    df_1=pd.DataFrame([])
    df_1['sum']=df[df['TopPosition']==pathname[1:]].iloc[:,-21:].sum(axis=0)
    df_1['alt']=df.columns[-21:]
    fig_pie_1 = px.pie(df_1, values='sum', names='alt')
    fig_pie_1.update_layout(font_color=colors['text'])
    f,lista = grafo(pathname[1:])
    elenco = []
    lista_words=df_w[df_w['TopPosition']==pathname[1:]]['comments'].values
    text=''
    for e in lista_words:
        for k in e:
            text+=k

    for i in lista:
        elenco.append(html.Br())
        elenco.append(dcc.Link(i, href='/{}'.format(i)))
    return html.Div([html.H1('{}'.format(pathname[1:].upper()),style={'color': 'blue'}),
    html.Div([
        html.Div([    html.H2('Lugares recomandados',style={
            'textAlign': 'center',
            'color': colors['text']
        }), f], className="six columns"),

        html.Div([
            html.H3('Palabras más usatas en los comentarios',style={
            'textAlign': 'center',
            'color': colors['text']
        }),
            dcc.Graph( figure=pwc(text))
        ], className="six columns"),
    ], className="row"),html.Div(id='page-content_3'),

        html.Div([
        html.Div([
                    html.Div([
    dcc.Link('Pagina inicial', href='/')
]+elenco)
            
        ], className="six columns"),

        html.Div([
            html.H3('Sujeto mas fotografiado',style={
            'textAlign': 'center',
            'color': colors['text']
        }),
            dcc.Graph(id='g3', figure=fig_pie_1)
        ], className="six columns"),
    ], className="row"),html.Div(id='page-content_1')
])


# Update the index
@app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
        return index_page
    else:
        return page_1_layout(pathname)
    # You could also return a 404 "URL not found" page here


if __name__ == '__main__':
    app.run_server(debug=True)

