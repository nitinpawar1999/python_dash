import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, dcc, html, dash_table
import plotly.express as px
import pandas as pd

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


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "4rem 2rem",
    "background-color": "#f8f9fa",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

sidebar_list = [html.H2("DashBoard For Something", className="display-6"),
                html.Hr(),
                html.Div([
                    html.P('BS'),
                    dcc.Dropdown(
                        id='dynamic-dropdown-container1',
                        options=list(data_dict.keys()),
                        value='',
                        multi=False,
                        clearable=True,
                        disabled=False,)],
                style={'display': 'block'}),
                html.Hr(),
                html.Div([
                    html.P('Location'),
                    dcc.Dropdown(
                        id='dynamic-dropdown-container2',
                        options=[],
                        value='',
                        multi=False,
                        clearable=True,
                        disabled=False,)],
                style={'display': 'block'})]


sidebar = html.Div(
    sidebar_list,
    style=SIDEBAR_STYLE,
)


@app.callback(
    Output(
        component_id='dynamic-dropdown-container2',
        component_property='options'
    ),
    [Input(
        component_id='dynamic-dropdown-container1',
        component_property='value'
    )]
)
def update_dynamic_dropdown_container2(value):
    if value in data_dict:
        return sorted(list(data_dict[value]))
    return []


content = html.H3(id="output", style=CONTENT_STYLE)


@app.callback(Output("output", "children"), [Input("dynamic-dropdown-container1", "value"), Input("dynamic-dropdown-container2", "value")])
def display_value(var1, var2):
    if var1 != "" and var2 != "" and var1 != None and var2 != None:
        return f"Selected value: BS -> {var1} | Location -> {var2}"
    return


dropdown_selections = html.Div(
    id="dropdown_selections_output", style=CONTENT_STYLE)


@app.callback(Output("dropdown_selections_output", "children"), [Input("dynamic-dropdown-container1", "value"), Input("dynamic-dropdown-container2", "value")])
def display_value(var1, var2):
    if var1 != "" and var2 != "" and var1 != None and var2 != None:

        filtered_df = df[(df['Var1'] == var1) & (df['Var2'] == var2)]
        wps_list = filtered_df['var3'].drop_duplicates().to_list()
        lateral_list = filtered_df['var4'].drop_duplicates().to_list()
        quantile_list = filtered_df['var5'].drop_duplicates().to_list()

        dropdown_selections_list = [
            html.Div([
                html.P('WPS'),
                dcc.Dropdown(
                    id='dynamic-dropdown-container3',
                    options=wps_list,
                    value='',
                    multi=True,
                    clearable=True,
                    disabled=False,)],
                style={'display': 'block'}),
            html.Hr(),
            html.Div([
                html.P('Lateral'),
                dcc.Dropdown(
                    id='dynamic-dropdown-container4',
                    options=lateral_list,
                    value='',
                    multi=True,
                    clearable=True,
                    disabled=False,)],
                style={'display': 'block'}),
            html.Hr(),
            html.Div([
                html.P('Quantile'),
                dcc.Dropdown(
                    id='dynamic-dropdown-container5',
                    options=quantile_list,
                    value='',
                    multi=True,
                    clearable=True,
                    disabled=False,)],
                style={'display': 'block'})]

        return html.Div(dropdown_selections_list, style=CONTENT_STYLE,)
    return


content_table = html.Div(id="output_table", style=CONTENT_STYLE)


@app.callback(Output("output_table", "children"),
              [Input("dynamic-dropdown-container1", "value"),
               Input("dynamic-dropdown-container2", "value"),
               Input("dynamic-dropdown-container3", "value"),
               Input("dynamic-dropdown-container4", "value"),
               Input("dynamic-dropdown-container5", "value")])
def display_value(var1, var2, var3, var4, var5):
    if var1 != "" and var2 != "" and var3 != "" and var4 != "" and var5 != "" and var1 != None and var2 != None and var3 != None and var4 != None and var5 != None:
        tmp_df = df[(df['Var1'] == var1) & (df['Var2'] == var2) & (
            df['var3'].isin(var3)) & (df['var4'].isin(var4)) & (df['var5'].isin(var5))]
        tmp_df_1 = tmp_df[['var3', 'var4', 'var5', 'Z']]
        return html.Div(
            [html.Div(
                [dcc.Graph(figure=px.line(tmp_df, x='t', y='y'), id='graph-placeholder')]),
             html.Div(
                [dash_table.DataTable(
                    data=tmp_df_1.to_dict('records'), page_size=10),
                    html.Hr(),
                    html.P(f"mean of EUR - {tmp_df_1['Z'].mean()}"),
                    html.P(f"Std of EUR - {tmp_df_1['Z'].std()}")]),],
            style=CONTENT_STYLE)
    return


app.layout = html.Div(
    [dcc.Location(id="url"), sidebar, content, dropdown_selections, content_table])


if __name__ == "__main__":
    app.run_server(port=8888)
