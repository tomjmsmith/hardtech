import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objects as go
import numpy as np

df = pd.read_csv('/Users/tom/Desktop/Hardtech/val_company_data.csv')

investors_list = set()
df['Investors'].dropna().str.split(',').apply(lambda investors: [investors_list.add(investor.strip()) for investor in investors])
investor_options = [{'label': investor, 'value': investor} for investor in sorted(list(investors_list))]

app = dash.Dash(__name__)

app.layout = html.Div([
    html.Div([
        html.Div([
            "Company Name:",
            dcc.Input(id='company-name-input', type='text', placeholder='Enter a company name', style={'width': '100%'}),
        ], style={'padding': '10px', 'width': '20%'}),
        html.Div([
            "Investor Name:",
            dcc.Dropdown(id='investor-name-dropdown', options=investor_options, placeholder='Select an investor', style={'width': '100%'}),
        ], style={'padding': '10px', 'width': '20%'}),
        html.Div([
            "Category:",
            dcc.Dropdown(
                id='category-dropdown',
                options=[{'label': i, 'value': i} for i in df['Category'].unique()],
                placeholder='Select a category',
                style={'width': '100%'}
            ),
        ], style={'padding': '10px', 'width': '20%'}),
        html.Div([
            dcc.Checklist(
                id='exclude-public-companies-checkbox',
                options=[{'label': 'Exclude Public Companies', 'value': 'Yes'}],
                value=[],
                inline=True
            )
        ], style={'padding': '10px', 'width': '40%'}),
    ], style={'display': 'flex', 'flex-wrap': 'wrap'}),
    dcc.Graph(id='company-graph')
])

@app.callback(
    Output('company-graph', 'figure'),
    [Input('company-name-input', 'value'),
     Input('investor-name-dropdown', 'value'),
     Input('category-dropdown', 'value'),
     Input('exclude-public-companies-checkbox', 'value')]
)
def update_graph(company_name, investor_name, category_name, exclude_public):
    filtered_df = df

    if company_name:
        filtered_df = filtered_df[filtered_df['Company Name'].str.contains(company_name, case=False, na=False)]
    if investor_name:
        filtered_df = filtered_df[filtered_df['Investors'].str.contains(investor_name, case=False, na=False)]
    if category_name:
        filtered_df = filtered_df[filtered_df['Category'] == category_name]
    if 'Yes' in exclude_public:
        filtered_df = filtered_df[filtered_df['Public / Private'] != 'Public']
    
    if filtered_df.empty:
        return go.Figure()

    fig = go.Figure()

    y_ticks_values = list(range(500, 50500, 500))

    for company in filtered_df['Company Name'].unique():
        company_df = filtered_df[filtered_df['Company Name'] == company]
        company_df['Investors'] = company_df['Investors'].apply(lambda x: ', '.join(str(x).split(',')[:5]) + ('...' if len(str(x).split(',')) > 5 else ''))
        hover_text = company_df['Company Name'] + '<br>Investors: ' + company_df['Investors'].astype(str)

        fig.add_trace(go.Scatter(x=company_df['Year'], y=company_df['Post Money Valuation'],
                                 mode='lines+markers',
                                 name=company,
                                 text=hover_text,
                                 hoverinfo='text+x+y'))

    current_year = pd.to_datetime('now').year
    fig.update_xaxes(tickvals=list(range(2000, current_year + 1)),
                     ticktext=[str(year) for year in range(2000, current_year + 1)])

    fig.update_yaxes(tickvals=y_ticks_values, ticktext=[str(value) for value in y_ticks_values],
                     type='linear', autorange=True)

    fig.update_layout(xaxis_title="Year", yaxis_title="Post Money Valuation (million USD)")

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)

