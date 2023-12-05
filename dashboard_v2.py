import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, dcc, html, dash_table
import pandas as pd
import plotly.graph_objs as go

df = pd.read_csv("df.csv")

temp_df = df[['Var1', 'Var2']]
temp_df = temp_df.drop_duplicates()
data_dict = {}

for ele in temp_df.values.tolist():
    if ele[0] in data_dict:
        data_dict[ele[0]].add(ele[1])
    else:
        data_dict[ele[0]] = set()
        data_dict[ele[0]].add(ele[1])

radioItems_lst = []

for key in data_dict:
    for value in data_dict[key]:
        radioItems_lst.append(
            {"label": f"{key} - {value}", "value": f"{key}|&|{value}"})


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "width": "20rem",
    "padding": "1rem 2rem",
    "background-color": "#f8f9fa",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "1rem",
    "margin-right": "2rem",
    "padding": "1rem",
}

DROPDOWN_WRAPPER = {
    "margin-right": "2rem",
    "padding": "1rem",
}

BODY_LAYOUT = {
    "height": "120vh",
    "display": "flex",
}

TABLE_CHART_STYLE = {
    "display": "flex",
    "margin-left": "1rem",
    "margin-right": "2rem",
    "padding": "1rem",
}

sidebar_list = [html.H2("Dashboard", className="display-6"),
                html.Hr(),
                html.Div([
                    html.H6('var1 var2 list', style=CONTENT_STYLE),
                    dbc.RadioItems(
                        id="radios",
                        className="btn-group",
                        inputClassName="btn-check",
                        labelClassName="btn btn-outline-primary",
                        labelCheckedClassName="active",
                        options=radioItems_lst,
                        value=radioItems_lst[0]["value"],)],
                style={'display': 'block', 'margin-bottom': '0.75rem'}),
                ]


sidebar = html.Div(
    sidebar_list,
    style=SIDEBAR_STYLE,
)


heading = html.H3(id="output", style=CONTENT_STYLE)


@app.callback(Output("output", "children"), [Input("radios", "value")])
def display_value(val):
    if val != "" and val != None:
        return "Factors"
    return


dropdown_selections = html.Div(
    id="dropdown_selections_output", style=DROPDOWN_WRAPPER)


@app.callback(Output("dropdown_selections_output", "children"), [Input("radios", "value")])
def display_value(val:str):
    if val != "" and val != None:

        filtered_df = df[(df['Var1'] == val.split('|&|')[0]) & (df['Var2'] == val.split('|&|')[1])]
        var3_list = filtered_df['var3'].drop_duplicates().to_list()
        var4_list = filtered_df['var4'].drop_duplicates().to_list()
        var5_list = filtered_df['var5'].drop_duplicates().to_list()

        dropdown_selections_list = [
            html.Div([
                html.P('Var3', style={'margin-bottom': 0}),
                dcc.Dropdown(
                    id='dynamic-dropdown-container3',
                    options=var3_list,
                    value=[var3_list[0]],
                    multi=True,
                    clearable=True,
                    disabled=False,)],
                style={'display': 'block', 'margin-bottom': '0.75rem'}),

            html.Div([
                html.P('Var4', style={'margin-bottom': 0}),
                dcc.Dropdown(
                    id='dynamic-dropdown-container4',
                    options=var4_list,
                    value=[var4_list[0]],
                    multi=True,
                    clearable=True,
                    disabled=False,)],
                style={'display': 'block', 'margin-bottom': '0.75rem'}),

            html.Div([
                html.P('Var5', style={'margin-bottom': 0}),
                dcc.Dropdown(
                    id='dynamic-dropdown-container5',
                    options=var5_list,
                    value=[var5_list[0]],
                    multi=True,
                    clearable=True,
                    disabled=False,)],
                style={'display': 'block', 'margin-bottom': '0.75rem'})]

        return html.Div(dropdown_selections_list, style=CONTENT_STYLE,)
    return


content_table = html.Div(id="output_table", style=CONTENT_STYLE)


@app.callback(Output("output_table", "children"),
              [Input("radios", "value"),
               Input("dynamic-dropdown-container3", "value"),
               Input("dynamic-dropdown-container4", "value"),
               Input("dynamic-dropdown-container5", "value")])
def display_value(val, var3, var4, var5):
    if val.split('|&|')[0] != "" and val.split('|&|')[1] != "" and var3 != "" and var4 != "" and var5 != "" and val.split('|&|')[0] != None and val.split('|&|')[1] != None and var3 != None and var4 != None and var5 != None:
        tmp_df = df[(df['Var1'] == val.split('|&|')[0]) & (df['Var2'] == val.split('|&|')[1]) & (
            df['var3'].isin(var3)) & (df['var4'].isin(var4)) & (df['var5'].isin(var5))]
        tmp_df_1 = tmp_df[['var3', 'var4', 'var5', 'Z']]
        fig = go.Figure()
        for i in range(len(tmp_df)):
            fig = fig.add_trace(go.Scatter(
                x=list(tmp_df['t'].iloc[i]), y=list(tmp_df['y'].iloc[i])))
        return html.Div(
            [html.Div(
                [dcc.Graph(figure=fig, id='graph-placeholder')]),
             html.Div(
                [dash_table.DataTable(
                    data=tmp_df_1.to_dict('records'), page_size=10,
                    style_header={
                        'backgroundColor': '#f8f9fa',
                        'fontWeight': 'bold'
                    },),
                    html.Hr(),
                    html.P(f"mean of Z - {tmp_df_1['Z'].mean()}"),
                    html.P(f"Std of Z - {tmp_df_1['Z'].std()}")],
                style={"margin-top": "6.4rem"}),],
            style=TABLE_CHART_STYLE)
    return


content = html.Div([heading, dropdown_selections, content_table], style={
                   "flex-basis": "100%"})

app.layout = html.Div(
    [dcc.Location(id="url"), sidebar, content], style=BODY_LAYOUT)

if __name__ == "__main__":
    app.run_server(port=8080)
