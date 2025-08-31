import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px

# Download dataset from Google Drive
id = '1a93yVb9nsg6IxqIKBkOTosA2LuMgkLlD'
url = f'https://drive.google.com/uc?id={id}'

# Load dataset
df = pd.read_csv(url)

# Preprocessing
df['TotalSales'] = df['Quantity'] * df['UnitPrice']
df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])

# Initialize Dash app
app = dash.Dash(__name__)
server =app.server
app.title = "Sales Dashboard"

# Layout
app.layout = html.Div([
    html.H1("📦 Sales Dashboard", style={'textAlign': 'center'}),

    html.Div([
        html.Label("Select Date Range:"),
        dcc.DatePickerRange(
            id='date-picker',
            start_date=df['InvoiceDate'].min(),
            end_date=df['InvoiceDate'].max(),
            min_date_allowed=df['InvoiceDate'].min(),
            max_date_allowed=df['InvoiceDate'].max()
        )
    ], style={'width': '40%', 'margin': 'auto'}),

    html.Div([
        html.Div([
            dcc.Graph(id='sales-over-time')
        ], style={'width': '48%', 'display': 'inline-block', 'padding': '0 10px'}),

        html.Div([
            dcc.Graph(id='top-products')
        ], style={'width': '48%', 'display': 'inline-block', 'padding': '0 10px'})
    ], style={'display': 'flex', 'justify-content': 'center'}),

    html.Div([
        html.Div([
            dcc.Graph(id='country-distribution')
        ], style={'width': '48%', 'display': 'inline-block', 'padding': '0 10px'}),

        html.Div([
            dcc.Graph(id='top-customers')
        ], style={'width': '48%', 'display': 'inline-block', 'padding': '0 10px'})
    ], style={'display': 'flex', 'justify-content': 'center', 'paddingTop': '30px'})
])

# Callback
@app.callback(
    [Output('sales-over-time', 'figure'),
     Output('top-products', 'figure'),
     Output('country-distribution', 'figure'),
     Output('top-customers', 'figure')],
    [Input('date-picker', 'start_date'),
     Input('date-picker', 'end_date')]
)
def update_graphs(start_date, end_date):
    filtered_df = df[
        (df['InvoiceDate'] >= pd.to_datetime(start_date)) &
        (df['InvoiceDate'] <= pd.to_datetime(end_date))
    ]

    # Sales over time
    time_series = filtered_df.groupby(filtered_df['InvoiceDate'].dt.date)['TotalSales'].sum().reset_index()
    fig_time = px.line(time_series, x='InvoiceDate', y='TotalSales', title='📈 Sales Over Time')

    # Top products
    top_products = filtered_df.groupby('Description')['TotalSales'].sum().nlargest(10).reset_index()
    fig_products = px.bar(top_products, x='TotalSales', y='Description', orientation='h',
                          title='🔥 Top 10 Products', labels={'TotalSales': 'Sales', 'Description': 'Product'})

    # Country distribution
    country_sales = df.groupby('Country')['TotalSales'].sum().reset_index()
    fig_country = px.pie(country_sales, names='Country', values='TotalSales', title='🌍 Sales by Country')
    fig_country.update_layout(height=400, width=600, margin=dict(t=40, b=40, l=0, r=0))
    fig_country.update_traces(textinfo='none')

    # Top 10 customers
    top_customers = (
        filtered_df.groupby('CustomerID')['TotalSales']
        .sum()
        .nlargest(10)
        .reset_index()
    )
    top_customers['CustomerID'] = top_customers['CustomerID'].astype(str)

    fig_customers = px.bar(
        top_customers,
        x='CustomerID',
        y='TotalSales',
        title='👥 Top 10 Customers',
        labels={'CustomerID': 'Customer ID', 'TotalSales': 'Total Sales'}
    )
    fig_customers.update_layout(
        height=400,
        width=600,
        xaxis_tickangle=-45,
        xaxis=dict(type='category')
    )

    return fig_time, fig_products, fig_country, fig_customers




