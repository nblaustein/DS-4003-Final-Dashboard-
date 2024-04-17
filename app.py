# %%
# import dependencies
from dash import Dash, dcc, html, Input, Output, callback, dash_table
import pandas as pd
import plotly.express as px
import io
import plotly.graph_objs as go

# %%
data = pd.read_csv("data.csv")

data.loc[data['Id'] == 1, 'Data_Type'] = 'Personal Data'
data.loc[data['Id'].isin(data['Id'].unique()[:11])& (data['Id'] != 1), 'Data_Type'] = 'Fitbit Users 1-10'
data.loc[data['Id'].isin(data['Id'].unique()[11:21])& (data['Id'] != 1), 'Data_Type'] = 'Fitbit Users 11-20'
data.loc[data['Id'].isin(data['Id'].unique()[21:31])& (data['Id'] != 1), 'Data_Type'] = 'Fitbit Users 21-30'
#rename some of the columns for better titles when graphing 
data.rename(columns={
    'TotalSteps': 'Total Steps',
    'TotalDistance': 'Total Distance (in miles)',
    'Calories': 'Calories Burned'
}, inplace=True)

#creating a df with just my personal data 
personal_df = data[data['Id'] == 1]
#creating a df of the Fitbit User data, excluding my personal data 
fitbit_df = data[data['Id'] != 1]
#creating a df without the data type column 
df = data.drop(columns=['Data_Type'])

# %%
#load in the stylesheet
stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css'] # load the CSS stylesheet
# initiate app
app = Dash(__name__, external_stylesheets=stylesheets) # initialize the app, stylesheet adds the rows 
server = app.server
######################################VISUALIZATIONS################################################
####################################################################################################
#Creating the animated bubble scatter plot 
fig2=px.scatter(data, x="Total Steps", y="Total Distance (in miles)", animation_frame="ActivityDate", animation_group="Id",
           size="VeryActiveMinutes", color="Id", hover_name="Data_Type",
        size_max=55, range_x=[0,20000], range_y=[0,15])

# Define the percentages and labels for the pie chart
total_minutes = fitbit_df[['VeryActiveMinutes', 'LightlyActiveMinutes', 'FairlyActiveMinutes']].sum() #Fitbit user data 
total_minutes2 = personal_df[['VeryActiveMinutes', 'LightlyActiveMinutes', 'FairlyActiveMinutes']].sum() #My personal data
percentages = (total_minutes / total_minutes.sum()) * 100 #Fitbit user data 
percentages2 = (total_minutes2 / total_minutes2.sum()) * 100 #My personal data 
labels = ['Very Active', 'Lightly Active', 'Fairly Active'] #pie chart labels
# Create the first pie chart trace
pie_chart_trace = go.Pie(labels=labels, values=percentages)
# Create the first figure
fig_fitbit = go.Figure(data=[pie_chart_trace], layout_title_text='Distribution of Workout Minutes for each Level of Intensity <br> for Fitbit Users')
# Create the second pie chart trace
pie_chart_trace2 = go.Pie(labels=labels, values=percentages2)
# Create the second figure
fig_personal = go.Figure(data=[pie_chart_trace2], layout_title_text='Distribution of Workout Minutes for each Level of Intensity <br> for My Personal Data')

##########################################APP LAYOUT###################################################
#######################################################################################################
app.layout = html.Div(style={'backgroundColor': '#FAF9F6', 'font-family': "Georgia"}, children=[
    html.Div(html.H1("Fitbit Analytics Dashboard"), style={'color': 'navy'}),
    html.Div(
        children="This dashboard analyzes Fitbit exercise data and allows users to easily view their workout trends and compare their data to 30 other Fitbit users (who responded to a  a survey distributed by Amazon Mechanical Turk between the dates of March 12 2016 and May 12 2016). I found this dataset on Kaggle. I then added my Fitbit data from the month of January to this dataset. Important variables included are steps taken, distance, very active minutes, fairly active minutes, lightly active minutes, sedentary minutes, total calories burned, and calories burned during activity.",
        style={'color': 'navy', 'font-family': "arial"}),
    html.Div(style={'height': '20px'}),  # adding a line of blank space
    # Tabs
    dcc.Tabs([
        # First Tab
        dcc.Tab(label='Analytics', children=[
            # first row containing radio buttons 
            html.Div([
                html.Div(
                    dcc.RadioItems(
                        options=['Fitbit Users 1-10', 'Fitbit Users 11-20', 'Fitbit Users 21-30', "Personal Data"],
                        value="Fitbit Users 1-10",
                        inline=True,
                        id='radio-buttons'
                    ),
                    className="six columns"
                ),
            ], className='row'),
            # second row containing line plot, histogram with dropdown, pie chart, and animated scatterplot
            html.Div([
                html.Div(
                    dcc.Graph(id='lineplot-with-radio-buttons'),
                    className="six columns"
                ),
                html.Div(dcc.Dropdown(
                    id = 'dropdown',
                    options = ['Total Steps', 'Total Distance (in miles)', 'Calories Burned'],
                    value =  'Total Steps'),
                         className="six columns"
                ),
                html.Div(
                    dcc.Graph(id='histogram-with-dropdown'),
                    className="six columns"
                ),
                # Radio button to select the pie chart 
                html.Div(dcc.RadioItems(
                    id='radio-buttons2',
                    options=[
                        {'label': 'Fitbit Users', 'value': 'fitbit'},
                        {'label': 'My Personal Data', 'value': 'personal'}
                    ],
                    value='fitbit',  # Default selection
                    labelStyle={'display': 'inline-block'}),
                    className="six columns"
                ),
                # container to display the selected pie chart 
                html.Div(dcc.Graph(id='pie-chart'),
                          className="six columns"
                ),
                html.Div(
                    dcc.Graph(id='animated-graph', figure=fig2),
                    className="five columns"
                ),
            ], className='row'),
            html.Div([

    html.Div([
        html.Div(children="This graph below displays the total steps and distance (in miles) the Fitbit users in the dataset and I personally took over time. The personal data was collected during the month of January 2024, while the 30 Fitbit users' data was collected during the time period of March 12 2016 to May 12 2016. This animated chart begins with the personal data and then displays a bubble for each unique user from the year 2016 to the end of the number line. The size of the bubble increases with higher amount of 'very active' minutes.", style={'align': 'right', 'color': 'navy'}),
    ], className='six columns', style={'float': 'right'}), #align on the right hand side
], className='row')
        ]),
         # Second Tab
        dcc.Tab(label='Downloadable Data Table', children=[
            # Data Table and Download Button
            html.Div([
                html.Div([
                    # Data Table creation 
                    dash_table.DataTable(
                        id='data-table',
                        columns=[{"name": i, "id": i} for i in sorted(df.columns)],
                        data=df.to_dict('records'),  # Populate table with DataFrame
                        sort_action="native",
                        page_size=10,
                        style_table={"overflowX": "auto"}
                    ),
                    # Download Button
                    html.Div([
                        html.Button("Download Filtered CSV", id="download-button", style={"marginTop": 20}),
                        dcc.Download(id="download-component")
                    ]),
                ], className="twelve columns")
            ], className='row'),
        ]),
    ]),
])
#############################################DEFINE CALLBACKS##################################################
###############################################################################################################

########################Callback to create the line plot with radio buttons #####################
@app.callback(
    Output('lineplot-with-radio-buttons', 'figure'),
    Input('radio-buttons', 'value'))
##Function updating the data frame based on the radio button selected 
def update_figure(selected_data):
    filtered_df = data[data.Data_Type == selected_data]

    color_palette = px.colors.qualitative.Plotly[:30]
    fig = px.line(filtered_df, x="ActivityDate", y="VeryActiveMinutes",
                     title="Line Plot", color='Id', color_discrete_sequence=color_palette, height=484)
      
    fig.update_layout(transition_duration=500, paper_bgcolor="#46C6C6", height=484, title="Line Plot of Very Active Exercise Minutes Over Time")

    return fig

############## Callbacks for the DATA TABLE AND DOWNLOAD BUTTON ####################
@app.callback(
    Output("download-component", "data"),
    Input("download-button", "n_clicks"),
)
def download_csv(n_clicks):
    if n_clicks is not None:
        df2 = pd.DataFrame(df)
        #convert to csv string
        csv_string = df2.to_csv(index=False, encoding='utf-8-sig')
        # Create downloaded file
        return dict(content=csv_string, filename="data.csv")
####################Callback for HISTOGRAM dropdown  ########################
@app.callback(
    Output('histogram-with-dropdown', 'figure'),
    Input('dropdown', 'value'))
#Function to update histogram based on dropdown selection
def update_figure2(selected_column):
    filtered_df2 = data.loc[:, selected_column]
    if selected_column == 'Total Distance (in miles)':
        filtered_df2 = data['Total Distance (in miles)']
    elif selected_column == 'Total Steps':
        filtered_df2 = data['Total Steps']
    elif selected_column == 'Calories Burned':
        filtered_df2 = data['Calories Burned']
    # Create the histogram based on the selected data
    fig3 = px.histogram(filtered_df2, x=selected_column, title=f'Histogram of {selected_column} for all Users in the Dataset')
    fig3.update_layout(paper_bgcolor='#CCCCFF')
    return fig3

####################Callback for PIE CHART radio button selection ########################
# Define callback to update the graph based on radio button selection
@app.callback(
    Output('pie-chart', 'figure'),
    [Input('radio-buttons2', 'value')]
)
#depending on radio button selection display one of the pie charts
def update_graph(selected_value2):
    if selected_value2 == 'fitbit':
        fig_fitbit.update_layout(paper_bgcolor='#FAF9F6')
        return fig_fitbit
    elif selected_value2 == 'personal':
        fig_personal.update_layout(paper_bgcolor='#FAF9F6')
        return fig_personal
    
#Update color and title of animated scatterplot
fig2.update_layout(paper_bgcolor='#FAF9F6', title = "Animated Bubble Scatterplot of Total Steps and Distance<br> Over Time (Size Increases with Number of Very Active Minutes)")

# run the app
if __name__ == "__main__":
 app.run_server(debug=True)


