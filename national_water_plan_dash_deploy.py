# Deployed Version of National Water Plan Dashapp

import pandas as pd
import numpy as np
from dash import Dash, html, dcc
from dash.dependencies import Input, Output, State
import plotly_express as px
import dash_bootstrap_components as dbc
# import warnings
import gunicorn

# warnings.simplefilter("ignore")

github_path = 'https://raw.githubusercontent.com/twrighta/national-water-plan-dashapp/main/national_water_plan.csv'

df = pd.read_csv(github_path)  # Read csv from github

# Define categorical lists - filtering options within the dashapp - e.g., dropdowns
COMPANIES = np.unique(df["Water company"])  # 9
SITES = np.unique(df["Site name"])  # 12683
BASIN_DISTRICTS = np.unique(df["River Basin District"])  # 10
CATCHMENTS = np.unique(df["Management Catchment"])  # 209
LOCAL_AUTHORITIES = np.unique(df["Local Authority"])  # 288
WATER_BODIES = np.unique(df["Water Body"])  # 2534
RECEIVING_ENVIRONMENTS = np.unique(df["Receiving Environment"])  # 3
YEAR_OPTIONS = [2020, 2021, 2022, 'All']  # For selecting years to filter to.
OVERFLOW_LOC_FLAGS = ["Bathing Water Discharge Flag",
                      "Ecological High Priority Site Flag",
                      "Non-bathing Priority Site Flag",
                      "Shellfish Water Discharge Flag"]
FUTURES_GEOGRAPHIES = ["Water company", "Receiving Environment", "River Basin District", "Management Catchment",
                       "Local Authority", "Water Body"]

AVG_SPILLS_2020 = np.nanmedian(df["Spill Events 2020"])
AVG_SPILLS_2021 = np.nanmedian(df["Spill Events 2021"])
AVG_SPILLS_2022 = np.nanmedian(df["Spill Events 2022"])

AVG_SPILLS_DICT = {2020: np.nanmedian(df["Spill Events 2020"]),
                   2021: np.nanmedian(df["Spill Events 2021"]),
                   2022: np.nanmedian(df["Spill Events 2022"]),
                   "All": np.nanmedian(df["All Spill Events"])}

PCT_UNDER_BASELINE = (len(df[df["Baseline Less than Target Flag"] == "Yes"]) / len(df)) * 100

# STRUCTURE
# Page 1: Overall Sites / Homepage
# Page 2: Water Company
# Page 3: River Basin District
# Page 4: Futures


# SETUP
plot_palette = ["#003f5c", "#2f4b7c", "#665191", "#a05195", "#d45087", "#f95d6a", "#ff7c43", "#ffa600"]
graduated_palette = ["#004c6d", "#256081", "#3e7695", "#558ca9", "#6da2be", "#84b9d3", "#9cd1e9", "#b5e9ff"]

specific_colours = {"sidebar_background": "#97deff",
                    "content_background": "#d2f1ff",
                    "page_heading": "#003f5c",
                    "text_heading": "#003F3F"}

# Object styles
# Sidebar - for page navigation
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": specific_colours["sidebar_background"]
}
# Content - for displaying graphs/information on, to right of sidebar
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem"
}

PAGE_HEADINGS_STYLE = {"textAlign": "center",
                       "font-weight": "bold",
                       "color": specific_colours["page_heading"]}

TEXT_HEADINGS_STYLE = {"textAlign": "center",
                       "font-weight": "bold",
                       "color": specific_colours["text_heading"]}

# Define sidebar structure outside of layout
sidebar = html.Div([
    html.H2("Pages",
            style={"font-weight": "bold"}),
    html.Hr(),
    html.P("Select a page to visit:",
           style={"font-weight": "bold"}),
    dbc.Nav([
        dbc.NavLink("Home",
                    href="/home",
                    active="exact"),
        dbc.NavLink("Water Companies",
                    href="/water-companies",
                    active="exact"),
        dbc.NavLink("River Basin Districts",
                    href="/river-basin-districts",
                    active="exact"),
        dbc.NavLink("Futures",
                    href="/futures",
                    active="exact")
    ],
        vertical=True,
        pills=True)],
    style=SIDEBAR_STYLE,
    id="sidebar-nav")

# Instantiate Dashapp
app = Dash(__name__,
           suppress_callback_exceptions=True,
           external_stylesheets=[dbc.themes.BOOTSTRAP])

server = app.server

# Define App Layout
content = html.Div(id="page-content", style=CONTENT_STYLE)
app.layout = html.Div([dcc.Location(id="url"), sidebar, content])

# HOMEPAGE CONTENT
homepage_content = html.Div(children=[
    html.H1("National Water Plan 2020-2022 - Home",
            style=PAGE_HEADINGS_STYLE),
    html.Hr(),
    html.Div(children=[
        dbc.Row([
            html.H2(f"Sites below Target: {str(round(PCT_UNDER_BASELINE, 1))}%",
                    style=PAGE_HEADINGS_STYLE),
            dbc.Col([
                html.Div(children=[
                    dcc.RadioItems(options=YEAR_OPTIONS,
                                   value="All",
                                   id="hp-year-radio",
                                   labelStyle={"padding": "5px",
                                               "display": "inline-block"}
                                   ),
                    dcc.Graph(id="hp-map")
                ])
            ],
                width=6),
            dbc.Col([
                html.Div(children=[
                    dcc.Graph(id="hp-basin-bar")
                ])
            ],
                width=6)
        ]),
        dbc.Row([
            dbc.Col([
                html.Div(children=[
                    dcc.Dropdown(options=OVERFLOW_LOC_FLAGS,
                                 multi=True,
                                 value=["Bathing Water Discharge Flag", "Ecological High Priority Site Flag"],
                                 id="flags-dropdown"),
                    dcc.Graph(id="total-spills_flagged-bar")
                ])
            ],
                width=5),
            dbc.Col([
                html.Div(children=[
                    dcc.Graph("hp-pie")

                ])
            ],
                width=2),
            dbc.Col([
                html.Div(children=[
                    dcc.RadioItems(options=RECEIVING_ENVIRONMENTS,
                                   value=RECEIVING_ENVIRONMENTS[0],
                                   id="hp-receiving-environment",
                                   labelStyle={"padding": "5px",
                                               "display": "inline-block"}),
                    dcc.Graph("home-improvements-bar")
                ])
            ],
                width=5)
        ])
    ])
])

# WATER COMPANIES CONTENT
companies_page = html.Div(children=[
    html.H1("National Water Plan 2020-2022 - Water Companies",
            style=PAGE_HEADINGS_STYLE),
    html.Hr(),
    html.Div(children=[
        html.Div(children=[
            dcc.Dropdown(options=COMPANIES,
                         value="Yorkshire Water",
                         id="wc-dropdown",
                         placeholder="Select a water company"),
            html.H2(id="chosen-company",
                    style={"textAlign": "center",
                           "fontWeight": "bold"})
        ]),
        html.Div(children=[
            dbc.Row([
                dbc.Col([
                    html.H3("Sites Below Target (%):"),
                    html.H4(id="company-underperforming")
                ]),
                dbc.Col([
                    html.H3("Total Sites:"),
                    html.H4(id="company-sites")
                ]),
                dbc.Col([
                    html.H3("Local Authority Districts:"),
                    html.H4(id="company-lads")
                ]),
                dbc.Col([
                    html.H3("Management Catchments:"),
                    html.H4(id="company-catchments")
                ]),
                dbc.Col([
                    html.H3("River Basins:"),
                    html.H4(id="company-basins")
                ])
            ])
        ]),
    ]),
    html.Div(children=[
        dbc.Row([
            dbc.Col([
                html.Div(children=[
                    dcc.RadioItems(options=YEAR_OPTIONS,
                                   value=2020,
                                   id="company-year-radio",
                                   labelStyle={"padding": "5px",
                                               "display": "inline-block"}),
                    dcc.Graph(id="company-map-fig")
                ])
            ],
                width=6),
            dbc.Col([
                html.Div([
                    dcc.Graph(id="wc-line-fig")
                ])
            ],
                width=6)
        ]),
        dbc.Row([
            dbc.Col([
                html.Div(children=[
                    dcc.Graph(id="wc-projected-spills")
                ])
            ],
                width=6),
            dbc.Col([
                html.Div(children=[
                    dcc.Graph(id="wc-pie-fig")
                ])
            ],
                width=6)
        ])
    ])
])

# WATER BASINS CONTENT
basin_content = html.Div(children=[
    html.H1("National Water Plan 2020-2022 - River Basin Districts",
            style=PAGE_HEADINGS_STYLE),
    html.Hr(),
    html.Div(children=[
        html.Div(children=[
            dcc.Dropdown(options=BASIN_DISTRICTS,
                         value=BASIN_DISTRICTS[0],
                         multi=False,
                         id="basin-dropdown"),
            html.H2(id="chosen-basin",
                    style={"textAlign": "center",
                           "fontWeight": "bold"})
        ]),
        html.Div(children=[
            dbc.Row([
                dbc.Col([
                    html.H3("Sites Below Target (%):"),
                    html.H4(id="basin-sites-below-target")
                ]),
                dbc.Col([
                    html.H3("Number of Sites:"),
                    html.H4(id="basin-num-sites")
                ]),
                dbc.Col([
                    html.H3("Local Authority Districts:"),
                    html.H4(id="basin-num-lads")
                ]),
                dbc.Col([
                    html.H3("Water Bodies:"),
                    html.H4(id="basin-num-water-bodies")
                ]),
                dbc.Col([
                    html.H3("Sites Requiring Improvements (%):"),
                    html.H4(id="basin-sites-needing-improvements")
                ])
            ])
        ]),
        html.Div(children=[
            dbc.Row([
                dbc.Col([
                    html.Div(children=[
                        dcc.RadioItems(options=YEAR_OPTIONS,
                                       value=YEAR_OPTIONS[0],
                                       id="basin-year-radio",
                                       labelStyle={'display': 'inline-block',
                                                   "padding": "5px"}),
                        dcc.Graph(id="basin-map-fig")
                    ])
                ],
                    width=6),
                dbc.Col([
                    html.Div(children=[
                        dcc.RadioItems(options=["Best", "Worst"],
                                       value="Best",
                                       id="basin-authority-best-flag",
                                       labelStyle={'display': 'inline-block',
                                                   "padding": "5px"}),
                        dcc.Input(placeholder="Please enter a number of sites to filter check:",
                                  value=3,
                                  type="number",
                                  id="basin-authority-input"),
                        dcc.Graph(id="basin-authority-bar-fig")

                    ])
                ],
                    width=6)

            ]),
            dbc.Row([
                dbc.Col([
                    # Lower left plot
                    html.Div(children=[
                        dcc.Graph(id="projected-spills-line")
                    ])
                ],
                    width=6),
                dbc.Col([
                    # Lower right plot
                    html.Div(children=[
                        dcc.Dropdown(options=OVERFLOW_LOC_FLAGS,
                                     value="",
                                     id="basin-flags-dropdown",
                                     multi=False,
                                     placeholder="Select a flag to filter sites by"),
                        dcc.Input(id="water-bodies-count",
                                  placeholder="Please enter a number of water bodies to filter to",
                                  type="number",
                                  value=3),
                        dcc.Graph(id="basin-water-bodies-bar")
                    ])
                ],
                    width=6)
            ])
        ])
    ])
])

# FUTURES CONTENT
futures_content = html.Div(children=[
    html.H1("National Water Plan - Futures",
            style=PAGE_HEADINGS_STYLE),
    html.Hr(),
    html.Div(children=[
        html.Div(children=[
            dcc.Dropdown(options=FUTURES_GEOGRAPHIES,
                         value=FUTURES_GEOGRAPHIES[0],
                         multi=False,
                         id="geography-dropdown"),
            html.H2(id="grwg",
                    style={"textAlign": "center",
                           "fontWeight": "bold"})
        ]),
        html.Div(children=[
            dcc.Dropdown(id="geography-member-dropdown",
                         placeholder="Please select a geography to populate the charts:"),
            html.H2(id="vg",
                    style={"textAlign": "center",
                           "fontWeight": "bold"})
        ]),
        html.Div(children=[
            dbc.Row([
                dbc.Col([
                    html.H3("Number of Sites:"),
                    html.H4(id="futures-total-sites")
                ]),
                dbc.Col([
                    html.H3("Sites Below Target (%):"),
                    html.H4(id="futures-pct-below-target")
                ]),
                dbc.Col([
                    html.H3("Total Improvements Planned:"),
                    html.H4(id="futures-improvements-planned")
                ]),
                dbc.Col([
                    html.H3("Average Required Improvements per Site:"),
                    html.H4(id="futures-improvements-ratio")
                ]),
                dbc.Col([
                    html.H3("Sites Meeting 2050 Target (%)"),
                    html.H4(id="futures-meeting-2050")
                ])

            ])
        ]),
        html.Div(children=[
            dbc.Row([
                dbc.Col([
                    html.Div(children=[
                        dcc.RadioItems(options=YEAR_OPTIONS,
                                       value=YEAR_OPTIONS[0],
                                       id="futures-year-radio",
                                       labelStyle={"display": "inline-block",
                                                   "padding": "5px"}
                                       ),
                        dcc.Graph(id="futures-map")
                    ]),
                ],
                    width=6),
                dbc.Col([
                    html.Div(children=[
                        dcc.Graph(id="futures-projected-line-fig")
                    ])
                ],
                    width=6)
            ]),
            dbc.Row([
                dbc.Col([
                    html.Div(children=[
                        dcc.Graph(id="futures-meeting-req-line")
                    ])
                ],
                    width=6),
                dbc.Col([
                    html.Div(children=[
                        dcc.RadioItems(options=[2025, 2030, 2035, 2040, 2045, 2050],
                                       value=2025,
                                       id="futures-proj-year-radio",
                                       labelStyle={"display": "inline-block",
                                                   "padding": "5px"}
                                       ),
                        dcc.Graph(id="futures-box-fig")
                    ])
                ],
                    width=6)
            ])
        ])
    ])
])


# CREATE CALLBACKS
# Page navigation - navigate to the page by url. Error if another page is tried to be reached.
@app.callback(Output("page-content", "children"),
              [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/home":
        return homepage_content
    elif pathname == "/water-companies":
        return companies_page
    elif pathname == "/river-basin-districts":
        return basin_content
    elif pathname == "/futures":
        return futures_content
    return html.Div(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
            html.P("Please navigate to one of the tabs")
        ],
        className="p-3 bg-light rounded-3",
    )


# Homepage - Map of all sites points, coloured by water company and sized by spill count.
# Filterable by whether they are bathing water/shellfish/ecoloical/marine protected/priority flag
@app.callback(
    Output("hp-map", "figure"),
    Input("hp-year-radio", "value"))
def update_hp_map(year):
    if df.empty:
        failed_fig = px.scatter_geo(title=f"Failed for your selection")
        failed_fig.update_layout(margin=dict(l=10, r=10, t=30, b=10))
        return failed_fig

    year_column_map = {
        2020: "Spill Events 2020",
        2021: "Spill Events 2021",
        2022: "Spill Events 2022",
        'All': "All Spill Events"
    }

    spill_column = year_column_map.get(year)

    # Filter and aggregate data based on the selected year
    filtered_year_agg_df = df[["Site name", "Latitude", "Longitude", "Water company", spill_column]].groupby(
        by=["Site name", "Water company"], as_index=False).sum().reset_index(drop=True)

    # Create scatter:
    map_fig = px.scatter_geo(filtered_year_agg_df,
                             lat="Latitude",
                             lon="Longitude",
                             color="Water company",
                             size=spill_column,
                             color_discrete_sequence=plot_palette,
                             title=f"<b>Sewage Spill Events by Site - {str(year)}<b>",
                             scope="europe",
                             basemap_visible=True,
                             center=dict(lat=52.43, lon=-1.22),
                             template="seaborn")
    map_fig.update_layout(transition_duration=500,
                          geo=dict(projection_scale=5),
                          margin=dict(l=10, r=10, t=30, b=10))
    map_fig.update_geos(resolution=50,
                        showland=True, landcolor="LightGreen",
                        showocean=True, oceancolor="LightBlue",
                        showlakes=True, lakecolor="Blue",
                        showrivers=True, rivercolor="Blue",
                        showcountries=True)
    return map_fig


# Pie chart of count of all releases by Receiving environment. Filterable by year the type flags.
@app.callback(
    Output("hp-pie", "figure"),
    Input("hp-year-radio", "value"))
def update_hp_pie(year):
    if df.empty:
        return px.pie(title=f"<b>Your selection failed<b>")

    if year != "All":
        year_col = f"Spill Events {str(year)}"
        year_title = f"<b>Sewage Spill Events - {str(year)}<b>"
    else:
        year_col = "All Spill Events"
        year_title = f"<b>All Sewage Spill Events<b>"

    filtered_df = df[["Receiving Environment", year_col]].groupby(by="Receiving Environment", as_index=False).sum()

    pie_fig = px.pie(filtered_df,
                     values=year_col,
                     color="Receiving Environment",
                     names="Receiving Environment",
                     title=f"{year_title}",
                     template="seaborn")
    pie_fig.update_layout(transition_duration=200,
                          margin=dict(l=10, r=10, t=30, b=10))
    return pie_fig


# Home page - Bar chart of counts of each type of improvements by receiving environment
@app.callback(Output("home-improvements-bar", "figure"),
              Input("hp-receiving-environment", "value"))
def improvements_bar_count(receiving_environment):
    filtered_df = df[df["Receiving Environment"] == receiving_environment]
    reshaped_df = pd.DataFrame({"Improvement": ["Storage", "Mew Screen", "Other Unconfirmed Improvements",
                                                "Nature-Based", "Increased pass forward flow", "Bespoke solution",
                                                "Sealing of sewers", "Operational Improvement", "Smart sewers",
                                                "Spill treatment"],
                                "Count": [np.sum(filtered_df["Storage"]),
                                          np.sum(filtered_df["Mew screen"]),
                                          np.sum(filtered_df["Other improvements to be confirmed"]),
                                          np.sum(filtered_df["Nature-Based"]),
                                          np.sum(filtered_df["Increased pass forward flow"]),
                                          np.sum(filtered_df["Bespoke solution"]),
                                          np.sum(filtered_df["Sealing of sewers"]),
                                          np.sum(filtered_df["Operational"]),
                                          np.sum(filtered_df["Smart sewers"]),
                                          np.sum(filtered_df["Spill treatment"])]
                                })
    bar_fig = px.histogram(data_frame=reshaped_df.sort_values(by="Improvement", ascending=True),
                           x="Improvement",
                           y="Count",
                           barmode="group",
                           title=f"<b>Number of Improvements Planned - {receiving_environment}<b>",
                           template="seaborn")

    bar_fig.update_layout(margin=dict(l=10, r=10, t=30, b=10))
    return bar_fig


# Barchart total spills per year by Basin district. Filterable by year.
@app.callback(Output("hp-basin-bar", "figure"),
              Input("hp-year-radio", "value"))
def update_hp_basin_bar(year):
    if year == "All":
        filtered_df = (df[["River Basin District", "All Spill Events"]].groupby
                       (by="River Basin District", as_index=False).sum().reset_index(drop=True).sort_values
                       (by="River Basin District", ascending=False))

        bar_fig = px.histogram(data_frame=filtered_df,
                               x="River Basin District",
                               y="All Spill Events",
                               title=f"<b>Sewage Spill Events - 2020-2022<b>",
                               barmode="group",
                               template="seaborn")
        bar_fig.update_layout(margin=dict(l=10, r=10, t=30, b=10),
                              yaxis_title="Sewage Spill Events")
        return bar_fig

    if year == 2020:
        filtered_df = df[["River Basin District", "Spill Events 2020"]].groupby(by="River Basin District",
                                                                                as_index=False).sum().reset_index(
            drop=True).sort_values(by="River Basin District", ascending=False)

        bar_fig = px.histogram(data_frame=filtered_df,
                               x="River Basin District",
                               y="Spill Events 2020",
                               title=f"<b>Sewage Spill Events - 2020<b>",
                               barmode="group",
                               template="seaborn")
        bar_fig.update_layout(margin=dict(l=10, r=10, t=30, b=10),
                              yaxis_title="Sewage Spill Events")
        return bar_fig

    if year == 2021:
        filtered_df = df[["River Basin District", "Spill Events 2021"]].groupby(by="River Basin District",
                                                                                as_index=False).sum().reset_index(
            drop=True).sort_values(by="River Basin District", ascending=False)
        bar_fig = px.histogram(data_frame=filtered_df,
                               x="River Basin District",
                               y="Spill Events 2021",
                               title=f"<b>Sewage Spill Events - 2021<b>",
                               barmode="group",
                               template="seaborn")
        bar_fig.update_layout(margin=dict(l=10, r=10, t=30, b=10),
                              yaxis_title="Sewage Spill Events")
        return bar_fig

    if year == 2022:
        filtered_df = df[["River Basin District", "Spill Events 2022"]].groupby(by="River Basin District",
                                                                                as_index=False).sum().reset_index(
            drop=True).sort_values(by="River Basin District", ascending=False)

        bar_fig = px.histogram(data_frame=filtered_df,
                               x="River Basin District",
                               y="Spill Events 2022",
                               barmode="group",
                               title=f"<b>Sewage Spill Events - 2022<b>",
                               template="seaborn")
        bar_fig.update_layout(margin=dict(l=10, r=10, t=30, b=10),
                              yaxis_title="Sewage Spill Events")
        return bar_fig


# 2020, 2021, 2022 Total Spills barchart. Filterable by each flag or all flags
@app.callback(Output("total-spills_flagged-bar", "figure"),
              Input("flags-dropdown", "value"))
def hp_spills_flag_bar(flags):
    num_flags = len(flags)
    if num_flags == 0:
        filtered_df = df  # All sites included
    if num_flags == 1:
        filtered_df = df[(df[flags[0]] == "Yes")]
    if num_flags == 2:
        filtered_df = df[(df[flags[0]] == "Yes") & (df[flags[1]] == "Yes")]
    if num_flags == 3:
        filtered_df = df[(df[flags[0]] == "Yes") & (df[flags[1]] == "Yes") & (df[flags[2]] == "Yes")]
    if num_flags == 4:
        filtered_df = df[
            (df[flags[0]] == "Yes") & (df[flags[1]] == "Yes") & (df[flags[2]] == "Yes") & (df[flags[3]] == "Yes")]

    title_flags = str(flags).strip("[\'").strip("\']").strip("\'").strip()
    summed_df = filtered_df[["Spill Events 2020", "Spill Events 2021", "Spill Events 2022"]].groupby(
        by=["Spill Events 2020", "Spill Events 2021", "Spill Events 2022"], as_index=False).sum()
    year_summed_df = pd.DataFrame({"Year": ["2020", "2021", "2022"],
                                   "Events": [np.sum(summed_df["Spill Events 2020"]),
                                              np.sum(summed_df["Spill Events 2021"]),
                                              np.sum(summed_df["Spill Events 2022"])]})
    if 0 < num_flags < 4:
        bar_fig = px.histogram(year_summed_df,
                               x="Year",
                               y="Events",
                               barmode="group",
                               title=f"<b>Sewage Spill Events by: {title_flags.strip("\'").strip("[\'").strip("\']")} \
                               <b>",
                               nbins=3,
                               template="seaborn")
        bar_fig.update_layout(margin=dict(l=10, r=10, t=30, b=10),
                              yaxis_title="Sewage Spill Events")
        return bar_fig
    if num_flags == 0:
        bar_fig = px.histogram(year_summed_df,
                               x="Year",
                               y="Events",
                               barmode="group",
                               title="<b>All Sewage Spill Events",
                               nbins=3,
                               template="seaborn")
        bar_fig.update_layout(margin=dict(l=10, r=10, t=30, b=10),
                              yaxis_title="Sewage Spill Events")
        return bar_fig


# Water companies - calculate and return water company metrics
@app.callback(
    [Output("company-sites", "children"),
     Output("company-lads", "children"),
     Output("company-catchments", "children"),
     Output("company-basins", "children"),
     Output("company-underperforming", "children"),
     Output("chosen-company", "children")],
    Input("wc-dropdown", "value"))
def calculate_company_stats(company):
    filtered_df = df[df["Water company"] == str(company)]

    site_count = len(filtered_df)
    unique_local_authorities = len(np.unique(filtered_df["Local Authority"]))
    unique_catchments = len(np.unique(filtered_df["Management Catchment"]))
    unique_basins = len(np.unique(filtered_df["River Basin District"]))
    underperforming_sites = round(
        (len(filtered_df[filtered_df["Baseline Less than Target Flag"] == "Yes"]) / (len(filtered_df) + 1)) * 100, 2)

    return site_count, unique_local_authorities, unique_catchments, unique_basins, underperforming_sites, company


# Water Companies - Map of all sites, sized by spill count. Coloured by whether less than or greater than average
# or by improvement counts needed. Filterable by year, and down to water company
@app.callback(
    Output("company-map-fig", "figure"),
    Input("company-year-radio", "value"),
    Input("wc-dropdown", "value")
)
def company_map(year, company):
    # Filter the DataFrame for the selected company
    filtered_df = df[df["Water company"] == str(company)]

    # Select the correct column based on the year
    if year in [2020, 2021, 2022]:
        spill_col = f"Spill Events {year}"
        filtered_df["nat_avg"] = AVG_SPILLS_DICT[year]
    else:
        spill_col = "All Spill Events"
        filtered_df["nat_avg"] = AVG_SPILLS_DICT["All"]
        year = "All Spill Events"

    filtered_df["Difference from National Average"] = filtered_df[spill_col] - filtered_df["nat_avg"]

    # Generate the figure
    map_fig = px.scatter_geo(filtered_df,
                             lat="Latitude",
                             lon="Longitude",
                             color="Difference from National Average",
                             size=spill_col,
                             color_continuous_scale=graduated_palette,
                             title=f"<b>{company} - Sewage Spill Events - {year}<b>",
                             scope="europe",
                             basemap_visible=True,
                             center=dict(lat=52.43, lon=-1.22),
                             template="seaborn"
                             )
    map_fig.update_layout(transition_duration=500,
                          geo=dict(projection_scale=7),
                          legend_title_text="Difference from National Average",
                          margin=dict(l=10, r=10, t=30, b=10))
    map_fig.update_geos(resolution=50,
                        showland=True, landcolor="LightGreen",
                        showocean=True, oceancolor="LightBlue",
                        showlakes=True, lakecolor="Blue",
                        showrivers=True, rivercolor="Blue",
                        showcountries=True)

    return map_fig


# - Water Companies - Line chart of all releases coloured by Receiving Environment, by year.
# Compared to average for all water companies (dotted line)
@app.callback(
    Output("wc-line-fig", "figure"),
    Input("wc-dropdown", "value"))
def company_release_line(company):
    filtered_df = df[df["Water company"] == company]

    avg_releases = {"2020_company": np.nanmean(filtered_df["Spill Events 2020"]),
                    "2021_company": np.nanmean(filtered_df["Spill Events 2021"]),
                    "2022_company": np.nanmean(filtered_df["Spill Events 2022"]),
                    "2020_all": np.nanmean(df["Spill Events 2020"]),
                    "2021_all": np.nanmean(df["Spill Events 2021"]),
                    "2022_all": np.nanmean(df["Spill Events 2022"])
                    }
    # Line plot of average company releases, and average national releases dotted.
    company_spill_df = pd.DataFrame(
        {"All": [avg_releases["2020_all"], avg_releases["2021_all"], avg_releases["2022_all"]],
         "Sewage Spill Events": [avg_releases["2020_company"], avg_releases["2021_company"],
                                 avg_releases["2022_company"]],
         "Year": ["2020", "2021", "2022"]})

    line_fig = px.line(company_spill_df,
                       x="Year",
                       y="Sewage Spill Events",
                       title=f"<b>{company} - Average Sewage Spill Events vs. National Average - 2020-2022<b>",
                       template="seaborn")
    line_fig.add_scatter(x=company_spill_df["Year"],
                         y=company_spill_df["All"],
                         mode="lines",
                         name="All Companies Average",
                         line=dict(dash="dash"))
    line_fig.update_layout(margin=dict(l=10, r=10, t=30, b=10),
                           yaxis_title="Sewage Spill Events")
    return line_fig


# Water companies - Line chart of projected spills 2025-2050 - vs average of other water companies
# 2025 Projected Spills
@app.callback(Output("wc-projected-spills", "figure"),
              Input("wc-dropdown", "value"))
def company_projected_line(input_company):
    filtered_df = df[df["Water company"] == input_company]

    projected_spill_dict = {"2025_all": np.nanmean(df["2025 Projected Spills"]),
                            "2030_all": np.nanmean(df["2030 Projected Spills"]),
                            "2035_all": np.nanmean(df["2035 Projected Spills"]),
                            "2040_all": np.nanmean(df["2040 Projected Spills"]),
                            "2045_all": np.nanmean(df["2045 Projected Spills"]),
                            "2050_all": np.nanmean(df["2050 Projected Spills"]),
                            "2025_company": np.nanmean(filtered_df["2025 Projected Spills"]),
                            "2030_company": np.nanmean(filtered_df["2030 Projected Spills"]),
                            "2035_company": np.nanmean(filtered_df["2035 Projected Spills"]),
                            "2040_company": np.nanmean(filtered_df["2040 Projected Spills"]),
                            "2045_company": np.nanmean(filtered_df["2045 Projected Spills"]),
                            "2050_company": np.nanmean(filtered_df["2050 Projected Spills"])
                            }
    projected_spill_df = pd.DataFrame({"Year": ["2025", "2030", "2035", "2040", "2045", "2050"],
                                       "All": list(projected_spill_dict.values())[:6],
                                       "Company": list(projected_spill_dict.values())[6:]})

    line_fig = px.line(projected_spill_df,
                       x="Year",
                       y="Company",
                       title=f"<b>{input_company} - Average Projected Sewage Spill Events per Site",
                       template="seaborn")
    line_fig.add_scatter(x=projected_spill_df["Year"],
                         y=projected_spill_df["All"],
                         mode="lines",
                         name="All Companies Average",
                         line=dict(dash="dash")
                         )
    line_fig.update_layout(margin=dict(l=10, r=10, t=30, b=10),
                           yaxis_title="Projected Sewage Spill Events")
    return line_fig


# Water companies - Pie chart of counts of each improvement required
@app.callback(Output("wc-pie-fig", "figure"),
              Input("wc-dropdown", "value"))
def company_improvement_count_pie(company):
    filtered_df = df[df["Water company"] == company]

    summed_df = pd.DataFrame({"Storage": np.sum(filtered_df["Storage"]),
                              "Mew Screen": np.sum(filtered_df["Mew screen"]),
                              "Other unconfirmed improvements ": np.sum(
                                  filtered_df["Other improvements to be confirmed"]),
                              "Nature-Based": np.sum(filtered_df["Nature-Based"]),
                              "Increased pass forward flow": np.sum(filtered_df["Increased pass forward flow"]),
                              "Bespoke Solution": np.sum(filtered_df["Bespoke solution"]),
                              "Sewer Sealing": np.sum(filtered_df["Sealing of sewers"]),
                              "Operational improvements": np.sum(filtered_df["Operational"]),
                              "Smart Sewers": np.sum(filtered_df["Smart sewers"]),
                              "Spill treatment": np.sum(filtered_df["Spill treatment"])},
                             index=["Total"]).T.reset_index()
    summed_df.rename(columns={"index": "Method"},
                     inplace=True)

    pie_fig = px.pie(data_frame=summed_df,
                     names="Method",
                     values="Total",
                     color="Method",
                     title=f"<b>{company} - Number of Improvements Planned<b>",
                     template="seaborn")
    pie_fig.update_layout(margin=dict(l=10, r=10, t=30, b=10),
                          legend=dict(title="Improvement Type"))
    return pie_fig


# River Basin Statistics for top of page
@app.callback([Output("basin-sites-below-target", "children"),
               Output("basin-num-sites", "children"),
               Output("basin-num-lads", "children"),
               Output("basin-num-water-bodies", "children"),
               Output("basin-sites-needing-improvements", "children"),
               Output("chosen-basin", "children")],
              Input("basin-dropdown", "value")
              )
def calculate_river_basin_statistics(basin_district):
    filtered_df = df[df["River Basin District"] == basin_district]

    # Sites within that are baseline less than target
    sites_below_target = round(
        (len(filtered_df[filtered_df["Baseline Less than Target Flag"] == "Yes"]) / (len(filtered_df) + 1)) * 100, 2)

    # Total number of sites within
    num_sites = len(filtered_df)

    # Local authority districts within
    num_lads = len(np.unique(filtered_df["Local Authority"]))

    # Water bodies within
    num_water_bodies = len(np.unique(filtered_df["Water Body"]))

    # Proportion of sites with some kind of improvement required/planned
    sites_needing_improvement_df = filtered_df[filtered_df["Improvement Count Needed"] > 0]
    sites_needing_improvement = round(len(sites_needing_improvement_df) / (len(filtered_df)) * 100, 0)

    # Chosen water company
    chosen_company = str(basin_district)

    return sites_below_target, num_sites, num_lads, num_water_bodies, sites_needing_improvement, chosen_company


# Map of all sites points. Coloured by Water Company, sized by total spills
@app.callback(
    Output("basin-map-fig", "figure"),
    Input("basin-dropdown", "value"),
    Input("basin-year-radio", "value")
)
def river_basin_map(basin, year):
    filtered_df = df[df["River Basin District"] == basin]

    # Coords to centralise to
    avg_x = np.median(filtered_df["Longitude"])
    avg_y = np.median(filtered_df["Latitude"])

    # Select the correct column based on the year
    if year in [2020, 2021, 2022]:
        spill_col = f"Spill Events {year}"
    else:
        spill_col = "All Spill Events"

    # Use precomputed average
    filtered_df["avg"] = AVG_SPILLS_DICT[year]

    # Generate the figure
    map_fig = px.scatter_geo(filtered_df,
                             lat="Latitude",
                             lon="Longitude",
                             color="Water company",
                             size=spill_col,
                             color_continuous_scale=graduated_palette,
                             title=f"<b>{basin} - Sewage Spill Events - {year}<b>",
                             scope="europe",
                             basemap_visible=True,
                             center=dict(lat=avg_y, lon=avg_x),
                             template="seaborn"
                             )
    map_fig.update_layout(transition_duration=500,
                          geo=dict(projection_scale=8),
                          legend_title_text="Water Company",
                          margin=dict(l=10, r=10, t=30, b=10))

    map_fig.update_geos(resolution=50,
                        showland=True, landcolor="LightGreen",
                        showocean=True, oceancolor="LightBlue",
                        showlakes=True, lakecolor="Blue",
                        showrivers=True, rivercolor="Blue",
                        showcountries=True)

    return map_fig


# - River Basins - Barchart of top n local authorities by total average spill count in the river basin.
# Option to filter by best or worst, and year.
@app.callback(
    Output("basin-authority-bar-fig", "figure"),
    Input("basin-dropdown", "value"),
    Input("basin-authority-input", "value"),
    Input("basin-authority-best-flag", "value"),
    Input("basin-year-radio", "value")
)
def basin_authority_spills(basin, n_authorities, best_worst, year):
    num_authorities = len(np.unique(
        df[df["River Basin District"] == basin]["Local Authority"]))  # Number of local authorities the District has

    grouped_cols = ["Local Authority", "Spill Events 2020", "Spill Events 2021",
                    "Spill Events 2022", "All Spill Events"]

    if int(num_authorities) >= n_authorities > 0:  # Number of local authorities chosen to list by user

        grouped_df = df[df["River Basin District"] == basin][grouped_cols].groupby(by="Local Authority",
                                                                                   as_index=False).mean()

        if year in [2020, 2021, 2022]:
            spill_col = f"Spill Events {year}"
        else:
            spill_col = "All Spill Events"

        if best_worst == "Best":
            result_df = grouped_df.sort_values(by=spill_col, ascending=True).iloc[:n_authorities + 1]
        if best_worst == "Worst":
            result_df = grouped_df.sort_values(by=spill_col, ascending=False).iloc[:n_authorities]

        bar_fig = px.histogram(data_frame=result_df,
                               x="Local Authority",
                               y=spill_col,
                               title=f"<b>{basin} - Top {str(n_authorities)} {str(best_worst)} \
                                     Local Authorities - {str(year)}<b>",
                               barmode="group",
                               template="seaborn")

        bar_fig.update_layout(margin=dict(l=5, r=5, t=30, b=10),
                              yaxis_title="Sewage Spill Events")
        return bar_fig

    else:
        n_authorities = num_authorities
        grouped_df = (df[df["River Basin District"] == basin][grouped_cols].groupby
                      (by="Local Authority", as_index=False).mean())

        if year in [2020, 2021, 2022]:
            spill_col = f"Spill Events {year}"
        else:
            spill_col = "All Spill Events"

        if best_worst == "Best":
            result_df = grouped_df.sort_values(by=spill_col, ascending=True).iloc[:n_authorities + 1]
        if best_worst == "Worst":
            result_df = grouped_df.sort_values(by=spill_col, ascending=False).iloc[:n_authorities]

        bar_fig = px.histogram(data_frame=result_df,
                               x="Local Authority",
                               y=spill_col,
                               title=f"<b>{basin} - Top {str(n_authorities)} {str(best_worst)} \
                                     Local Authorities - {str(year)}<b>",
                               barmode="group",
                               template="seaborn")

        bar_fig.update_layout(margin=dict(l=5, r=5, t=30, b=10),
                              yaxis_title="Sewage Spill Events")
        return bar_fig


# Basin - Projected spills by receiving environment - with average across all catchments as well
# option to switch to sum of meeting YYYY requirements as a line chart too
@app.callback(
    Output("projected-spills-line", "figure"),
    Input("basin-dropdown", "value")
)
def projected_spill_line(basin):
    projected_cols = ["Receiving Environment", "River Basin District", "2025 Projected Spills", "2030 Projected Spills",
                      "2035 Projected Spills", "2040 Projected Spills",
                      "2045 Projected Spills", "2050 Projected Spills"]

    grouped_df = df[df["River Basin District"] == basin][projected_cols].groupby(by="Receiving Environment",
                                                                                 as_index=False).sum()

    try:
        proj_coastal_25 = float(
            grouped_df[grouped_df["Receiving Environment"] == "Coastal"]["2025 Projected Spills"].values[0])
        proj_coastal_30 = float(
            grouped_df[grouped_df["Receiving Environment"] == "Coastal"]["2030 Projected Spills"].values[0])
        proj_coastal_35 = float(
            grouped_df[grouped_df["Receiving Environment"] == "Coastal"]["2035 Projected Spills"].values[0])
        proj_coastal_40 = float(
            grouped_df[grouped_df["Receiving Environment"] == "Coastal"]["2040 Projected Spills"].values[0])
        proj_coastal_45 = float(
            grouped_df[grouped_df["Receiving Environment"] == "Coastal"]["2045 Projected Spills"].values[0])
        proj_coastal_50 = float(
            grouped_df[grouped_df["Receiving Environment"] == "Coastal"]["2050 Projected Spills"].values[0])
    except:
        proj_coastal_25 = proj_coastal_30 = proj_coastal_35 = proj_coastal_40 = proj_coastal_45 = proj_coastal_50 = 0

    try:
        proj_est_25 = float(
            grouped_df[grouped_df["Receiving Environment"] == "Estuarine"]["2025 Projected Spills"].values[0])
        proj_est_30 = float(
            grouped_df[grouped_df["Receiving Environment"] == "Estuarine"]["2030 Projected Spills"].values[0])
        proj_est_35 = float(
            grouped_df[grouped_df["Receiving Environment"] == "Estuarine"]["2035 Projected Spills"].values[0])
        proj_est_40 = float(
            grouped_df[grouped_df["Receiving Environment"] == "Estuarine"]["2040 Projected Spills"].values[0])
        proj_est_45 = float(
            grouped_df[grouped_df["Receiving Environment"] == "Estuarine"]["2045 Projected Spills"].values[0])
        proj_est_50 = float(
            grouped_df[grouped_df["Receiving Environment"] == "Estuarine"]["2050 Projected Spills"].values[0])
    except:
        proj_est_25 = proj_est_30 = proj_est_35 = proj_est_40 = proj_est_45 = proj_est_50 = 0

    try:
        proj_in_25 = float(
            grouped_df[grouped_df["Receiving Environment"] == "Inland"]["2025 Projected Spills"].values[0])
        proj_in_30 = float(
            grouped_df[grouped_df["Receiving Environment"] == "Inland"]["2030 Projected Spills"].values[0])
        proj_in_35 = float(
            grouped_df[grouped_df["Receiving Environment"] == "Inland"]["2035 Projected Spills"].values[0])
        proj_in_40 = float(
            grouped_df[grouped_df["Receiving Environment"] == "Inland"]["2040 Projected Spills"].values[0])
        proj_in_45 = float(
            grouped_df[grouped_df["Receiving Environment"] == "Inland"]["2045 Projected Spills"].values[0])
        proj_in_50 = float(
            grouped_df[grouped_df["Receiving Environment"] == "Inland"]["2050 Projected Spills"].values[0])
    except:
        proj_in_25 = proj_in_30 = proj_in_35 = proj_in_40 = proj_in_45 = proj_in_50 = 0

    output_df = pd.DataFrame({"Year": ["2025", "2025", "2025",
                                       "2030", "2030", "2030",
                                       "2035", "2035", "2035",
                                       "2040", "2040", "2040",
                                       "2045", "2045", "2045",
                                       "2050", "2050", "2050"],
                              "Spills": [proj_coastal_25, proj_est_25, proj_in_25,
                                         proj_coastal_30, proj_est_30, proj_in_30,
                                         proj_coastal_35, proj_est_35, proj_in_35,
                                         proj_coastal_40, proj_est_40, proj_in_40,
                                         proj_coastal_45, proj_est_45, proj_in_45,
                                         proj_coastal_50, proj_est_50, proj_in_50],
                              "Receiving Environment": ["Coastal", "Estuarine", "Inland",
                                                        "Coastal", "Estuarine", "Inland",
                                                        "Coastal", "Estuarine", "Inland",
                                                        "Coastal", "Estuarine", "Inland",
                                                        "Coastal", "Estuarine", "Inland",
                                                        "Coastal", "Estuarine", "Inland"]
                              })

    projected_spills_fig = px.line(data_frame=output_df,
                                   x="Year",
                                   y="Spills",
                                   color="Receiving Environment",
                                   title=f"<b>{basin} - Projected Spills by Receiving Environment<b>",
                                   template="seaborn")

    projected_spills_fig.update_layout(margin=dict(l=10, r=10, t=30, b=10),
                                       yaxis_title="Projected Sewage Spill Events")
    return projected_spills_fig


# River Basin - worst/best water bodies by spill count - selectable by year, and can check the issue flags
@app.callback(
    Output("basin-water-bodies-bar", "figure"),
    Input("basin-dropdown", "value"),
    Input("basin-year-radio", "value"),
    Input("basin-flags-dropdown", "value"),
    Input("water-bodies-count", "value")
)
def basin_water_bodies(basin, year, flag, num_water_bodies):
    filtered_df = df[df["River Basin District"] == basin]
    max_water_bodies = len(np.unique(filtered_df["Water Body"]))

    # If less than or equal to max water bodies and greater than 0
    if max_water_bodies >= num_water_bodies > 0:

        # Get the Spill events column to measure by
        if year in [2020, 2021, 2022]:
            spill_col = f"Spill Events {year}"
        else:
            spill_col = "All Spill Events"

        # Filter by flag
        if flag in OVERFLOW_LOC_FLAGS:
            df2 = filtered_df[filtered_df[flag] == "Yes"]
            flag_title = f"{flag} Filtering"
        else:
            df2 = filtered_df
            flag_title = "No Flag filtering"

        # Organize columns and group by water body
        if len(df2) >= 1:
            grouped = df2[["Water Body", spill_col]].groupby("Water Body", as_index=False).sum().reset_index \
                          (drop=True).sort_values(by=spill_col, ascending=False).iloc[: int(num_water_bodies)].copy()

            # Plot
            waterbody_bar_fig = px.histogram(data_frame=grouped,
                                             x="Water Body",
                                             y=spill_col,
                                             title=f"<b>{basin} - Top {str(num_water_bodies)} \
                                                   Worst Water Bodies with {flag_title} - {str(year)}<b>",
                                             barmode="group",
                                             log_y=True,
                                             template="seaborn")
            waterbody_bar_fig.update_layout(margin=dict(l=10, r=10, t=30, b=70),
                                            yaxis_title="Sewage Spill Events")
            return waterbody_bar_fig
    else:
        num_water_bodies = max_water_bodies

        # Get the Spill events column to measure by
        if year in [2020, 2021, 2022]:
            spill_col = f"Spill Events {year}"
        else:
            spill_col = "All Spill Events"

        # Filter by flag
        if flag in OVERFLOW_LOC_FLAGS:
            df2 = filtered_df[filtered_df[flag] == "Yes"]
            flag_title = f"{flag} Filtering"
        else:
            df2 = filtered_df
            flag_title = "No Flag filtering"

        # Organize columns and group by water body
        if len(df2) >= 1:
            grouped = df2[["Water Body", spill_col]].groupby("Water Body", as_index=False).sum().reset_index \
                          (drop=True).sort_values(by=spill_col, ascending=False).iloc[: int(num_water_bodies)].copy()

            # Plot
            waterbody_bar_fig = px.histogram(data_frame=grouped,
                                             x="Water Body",
                                             y=spill_col,
                                             title=f"<b>{basin} - Top {str(num_water_bodies)} Worst Water Bodies with \
                                                   {flag_title} - {str(year)}<b>",
                                             barmode="group",
                                             log_y=True,
                                             template="seaborn")
            waterbody_bar_fig.update_layout(margin=dict(l=10, r=10, t=30, b=70),
                                            yaxis_title="Sewage Spill Events")
            return waterbody_bar_fig


# Page 4: Futures
@app.callback(
    Output("geography-member-dropdown", "options"),
    Input("geography-dropdown", "value")
)
def update_geography_members(selected_geography):
    if selected_geography is None:
        return []
    else:
        return [{"label": member, "value": member} for member in df[selected_geography].unique()]


# Futures - Callback to populate geography dropdown
@app.callback(
    Output("geography-dropdown", "options"),
    Input("geography-dropdown", "search_value")
)
def update_geography_dropdown(search_value):
    return [{"label": geo, "value": geo} for geo in FUTURES_GEOGRAPHIES]


# Futures - Stats by chosen geography for top of page
@app.callback(
    [Output("futures-total-sites", "children"),
     Output("futures-pct-below-target", "children"),
     Output("futures-improvements-planned", "children"),
     Output("futures-improvements-ratio", "children"),
     Output("futures-meeting-2050", "children")],
    Input("geography-member-dropdown", "value"),
    State("geography-dropdown", "value")
)
def futures_stats(geography_member, selected_geography):
    # If a specific geography member is selected
    if geography_member != "All":
        filtered_df = df[df[selected_geography] == geography_member]

        total_sites = int(len(filtered_df["Site name"].unique()))
        pct_sites_currently_below_target = round(
            (len(filtered_df[filtered_df["Baseline Less than Target Flag"] == "Yes"]) + 1) / (total_sites + 1) * 100, 2)

        total_improvements_planned = np.sum(filtered_df[["Storage", "Mew screen", "Other improvements to be confirmed",
                                                         "Nature-Based", "Increased pass forward flow",
                                                         "Bespoke solution", "Sealing of sewers", "Operational",
                                                         "Smart sewers", "Spill treatment"]].fillna(0).values)

        total_improvements_planned_ratio = round(total_improvements_planned / total_sites, 2)

        try:
            sites_meeting_2050_target = (len(filtered_df[filtered_df["Meets 2050 Requirements"] == 1]) / len(
                filtered_df)) * 100
        except ZeroDivisionError:
            sites_meeting_2050_target = "N/A"  # Filtered_df has no length - not populated at the moment in time.

        return (total_sites, pct_sites_currently_below_target, total_improvements_planned,
                total_improvements_planned_ratio, sites_meeting_2050_target)

    # If "All" geography members are selected, return aggregated statistics for the entire geography
    else:
        grouped_df = df.groupby(by=selected_geography, as_index=False).agg({
            "Site name": pd.Series.nunique,
            "All Spill Events": 'mean',
            "Improvement Count Needed": 'mean',
            "Baseline Less than Target Flag": lambda x: round((x == "Yes").mean() * 100, 2),
            "Meets 2050 Requirements": 'sum'
        })

        grouped_sum_df = df.groupby(by=selected_geography, as_index=False).sum()

        grouped_sites = grouped_df["Site name"].sum()  # Total unique sites
        average_spill_count = grouped_df["All Spill Events"].mean()
        average_improvement_count = grouped_sum_df["Improvement Count Needed"].mean()
        average_baseline_less_than_target_pct = grouped_df["Baseline Less than Target Flag"].mean()
        sites_meeting_2050_target = grouped_df["Meets 2050 Requirements"].sum()

        return (grouped_sites, average_baseline_less_than_target_pct, average_spill_count, average_improvement_count,
                sites_meeting_2050_target)


# Futures - map of all points in the chosen geography. Coloured by improvement count, filterable by year
@app.callback(Output("futures-map", "figure"),
              State("geography-dropdown", "value"),
              Input("geography-member-dropdown", "value"),
              Input("futures-year-radio", "value")
              )
def futures_map(geography, geography_member, year):
    # If not 'All', then focus on a single component of that geography and just group by whole geography
    if str(year) != 'All':
        hover_year = "Spill Events " + str(year)
        geog_filtered = df[df[geography] == geography_member]
        # Coordinates to centralise to
        avg_x = np.nanmedian(geog_filtered["Longitude"])
        avg_y = np.nanmedian(geog_filtered["Latitude"])
        scatter_filtered = px.scatter_geo(data_frame=geog_filtered,
                                          lat="Latitude",
                                          lon="Longitude",
                                          scope="europe",
                                          basemap_visible=True,
                                          title=f"<b>{geography_member} - Sewage Spill Events - {str(year)}<b>",
                                          hover_name="Site name",
                                          hover_data=["Improvement Count Needed"],
                                          color="Improvement Count Needed",
                                          size=hover_year,
                                          center=dict(lat=avg_y, lon=avg_x),
                                          template="seaborn")
        scatter_filtered.update_layout(geo=dict(projection_scale=8),
                                       legend_title_text="Improvements Required",
                                       margin=dict(l=10, r=10, t=30, b=10))
        scatter_filtered.update_geos(resolution=50,
                                     showland=True, landcolor="LightGreen",
                                     showocean=True, oceancolor="LightBlue",
                                     showlakes=True, lakecolor="Blue",
                                     showrivers=True, rivercolor="Blue",
                                     showcountries=True)
        return scatter_filtered
    elif str(year) == "All":
        geog_filtered = df[df[geography] == geography_member]

        avg_x = np.nanmedian(geog_filtered["Longitude"])
        avg_y = np.nanmedian(geog_filtered["Latitude"])
        scatter_unfiltered = px.scatter_geo(data_frame=geog_filtered,
                                            lat="Latitude",
                                            lon="Longitude",
                                            scope="europe",
                                            basemap_visible=True,
                                            title=f"<b>{geography_member} - Sewage Spill Events - {str(year)} Years<b>",
                                            hover_name="Site name",
                                            color="Improvement Count Needed",
                                            hover_data=["All Spill Events", "Improvement Count Needed"],
                                            size="All Spill Events",
                                            center=dict(lat=avg_y, lon=avg_x),
                                            template="seaborn"
                                            )
        scatter_unfiltered.update_layout(geo=dict(projection_scale=8),
                                         legend=dict(title="Improvements Required"),
                                         margin=dict(l=10, r=10, t=30, b=10))
        scatter_unfiltered.update_geos(resolution=50,
                                       showland=True, landcolor="LightGreen",
                                       showocean=True, oceancolor="LightBlue",
                                       showlakes=True, lakecolor="Blue",
                                       showrivers=True, rivercolor="Blue",
                                       showcountries=True)
        return scatter_unfiltered


# Futures - Line graph of sum of projected spills each 5 year - Can do whole geography or an individual unit within
@app.callback(Output("futures-projected-line-fig", "figure"),
              Input("geography-dropdown", "value"),
              Input("geography-member-dropdown", "value"))
def futures_projected_line(geography, geography_member):
    x_years = ["2025", "2030", "2035", "2040", "2045", "2050"]
    if geography_member != "All":
        filtered_df = df[df[geography] == geography_member].copy()
        proj_2025 = np.sum(filtered_df["2025 Projected Spills"])
        proj_2030 = np.sum(filtered_df["2030 Projected Spills"])
        proj_2035 = np.sum(filtered_df["2035 Projected Spills"])
        proj_2040 = np.sum(filtered_df["2040 Projected Spills"])
        proj_2045 = np.sum(filtered_df["2045 Projected Spills"])
        proj_2050 = np.sum(filtered_df["2050 Projected Spills"])

        plot_df = pd.DataFrame({"Year": x_years,
                                "Projected Spills": [proj_2025, proj_2030, proj_2035, proj_2040, proj_2045, proj_2050]})
        line_fig = px.line(plot_df,
                           x="Year",
                           y="Projected Spills",
                           title=f"<b>{geography_member} - Projected Sewage Spill Events 2025-2050<b>",
                           template="seaborn")
        line_fig.update_layout(margin=dict(l=10, r=10, t=30, b=10),
                               yaxis_title="Projected Sewage Spill Events")
        return line_fig

    if geography_member == "All":
        filtered_df = df.groupby(by=geography, as_index=False).copy()
        proj_2025 = filtered_df["2025 Projected Spills"]
        proj_2030 = filtered_df["2030 Projected Spills"]
        proj_2035 = filtered_df["2035 Projected Spills"]
        proj_2040 = filtered_df["2040 Projected Spills"]
        proj_2045 = filtered_df["2045 Projected Spills"]
        proj_2050 = filtered_df["2050 Projected Spills"]

        plot_df = pd.DataFrame({"Year": x_years,
                                "Projected Spills": [proj_2025, proj_2030, proj_2035, proj_2040, proj_2045,
                                                     proj_2050]
                                })
        line_fig = px.line(plot_df,
                           x="Year",
                           y="Projected Spills",
                           title=f"<b>{geography} - Projected Sewage Spills 2025-2050<b>",
                           template="seaborn")
        line_fig.update_layout(margin=dict(l=10, r=10, t=30, b=10),
                               yaxis_title="Projected Sewage Spill Events")
        return line_fig


# - Futures - Line graph of count of sites meeting requirements each 5 year
@app.callback(Output("futures-meeting-req-line", "figure"),
              Input("geography-dropdown", "value"),
              Input("geography-member-dropdown", "value"))
def futures_meeting_requirements(geography, geography_member):
    x_years = ["2025", "2030", "2035", "2040", "2045", "2050"]
    if geography_member != "All":
        filtered_df = df[df[geography] == geography_member].copy()
        req_2025 = round((np.sum(filtered_df["Meets 2025 Requirements"]) / len(filtered_df)) * 100, 2)
        req_2030 = round((np.sum(filtered_df["Meets 2030 Requirements"]) / len(filtered_df)) * 100, 2)
        req_2035 = round((np.sum(filtered_df["Meets 2035 Requirements"]) / len(filtered_df)) * 100, 2)
        req_2040 = round((np.sum(filtered_df["Meets 2040 Requirements"]) / len(filtered_df)) * 100, 2)
        req_2045 = round((np.sum(filtered_df["Meets 2045 Requirements"]) / len(filtered_df)) * 100, 2)
        req_2050 = round((np.sum(filtered_df["Meets 2050 Requirements"]) / len(filtered_df)) * 100, 2)

        plot_df = pd.DataFrame({"Year": x_years,
                                "Pct Meeting Requirements": [req_2025, req_2030, req_2035,
                                                             req_2040, req_2045, req_2050]})
        line_fig = px.line(plot_df,
                           x="Year",
                           y="Pct Meeting Requirements",
                           title=f"<b>{geography_member} - Percentage of Sites Meeting Requirements 2025-2050",
                           template="seaborn")
        line_fig.update_layout(margin=dict(l=10, r=10, t=30, b=10),
                               yaxis_title="Sites Meeting Requirements (%)")
        return line_fig

    if geography_member == "All":
        filtered_df = df.groupby(by=geography, as_index=False).copy()
        req_2025 = round((np.sum(filtered_df["Meets 2025 Requirements"]) / len(filtered_df)) * 100, 2)
        req_2030 = round((np.sum(filtered_df["Meets 2030 Requirements"]) / len(filtered_df)) * 100, 2)
        req_2035 = round((np.sum(filtered_df["Meets 2035 Requirements"]) / len(filtered_df)) * 100, 2)
        req_2040 = round((np.sum(filtered_df["Meets 2040 Requirements"]) / len(filtered_df)) * 100, 2)
        req_2045 = round((np.sum(filtered_df["Meets 2045 Requirements"]) / len(filtered_df)) * 100, 2)
        req_2050 = round((np.sum(filtered_df["Meets 2050 Requirements"]) / len(filtered_df)) * 100, 2)

        plot_df = pd.DataFrame({"Year": x_years,
                                "Pct Meeting Requirements": [req_2025, req_2030, req_2035, req_2040, req_2045,
                                                             req_2050]
                                })
        line_fig = px.line(plot_df,
                           x="Year",
                           y="Pct Meeting Requirements",
                           title=f"<b>{geography} - Percentage of Sites Meeting Requirements 2025-2050<b>",
                           template="seaborn")
        line_fig.update_layout(margin=dict(l=10, r=10, t=30, b=10),
                               yaxis_title="Sites Meeting Requirements (%)")
        return line_fig


# Futures - Boxplot of Predicted Annual Spill Frequency Post Scheme
@app.callback(Output("futures-box-fig", "figure"),
              Input("geography-dropdown", "value"),
              Input("geography-member-dropdown", "value"),
              Input("futures-proj-year-radio", "value"))
def projected_spills_year_box(geography, geography_member, year):
    selected_year_col = str(str(year) + " Projected Spills")
    # If it is a geography with many individual geography members, just show the whole geography boxplot
    # and add the mark for the individual geography member if selected
    if geography not in ["Water Body", "Local Authority", "Management Catchment"]:

        box_fig = px.box(data_frame=df,
                         x=geography,
                         y=selected_year_col,
                         title=f"<b>{geography_member} - Projected Sewage Spill Events Distribution - {str(year)}<b>",
                         template="seaborn")
        box_fig.update_layout(margin=dict(l=10, r=10, t=30, b=10))

        return box_fig

    # Geographies with only a few individual geography members
    else:
        filtered_df = df[df[geography] == geography_member]
        box_fig = px.box(data_frame=filtered_df,
                         x=geography,
                         y=selected_year_col,
                         title=f"<b>{geography_member} - Projected Sewage Spill Events Distribution - {str(year)}<b>",
                         template="seaborn")
        box_fig.update_layout(margin=dict(l=10, r=10, t=30, b=10))
        return box_fig


# Run the application
if __name__ == '__main__':
    app.run(debug=True)
