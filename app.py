# %%
# import dependencies
from dash import Dash, dcc, html, Input, Output, callback, dash_table
import pandas as pd
import plotly.express as px
import io
import plotly.graph_objs as go
import plotly.io as pio

# %%
data = pd.read_csv("C:/Users/nblau\Documents/Ds 4003/data.csv") #read in the cleaned data 
#Create new column called Data_Type that will be utilized in the line plot with radio buttons 
data.loc[data['Id'] == 1, 'Data_Type'] = 'Personal Data' 
data.loc[data['Id'].isin(data['Id'].unique()[:11])& (data['Id'] != 1), 'Data_Type'] = 'Fitbit Users 1-10'
data.loc[data['Id'].isin(data['Id'].unique()[11:21])& (data['Id'] != 1), 'Data_Type'] = 'Fitbit Users 11-20'
data.loc[data['Id'].isin(data['Id'].unique()[21:37])& (data['Id'] != 1), 'Data_Type'] = 'Fitbit Users 21-35'
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
# Define the percentages and labels for the pie chart
total_minutes = fitbit_df[['VeryActiveMinutes', 'LightlyActiveMinutes', 'FairlyActiveMinutes']].sum() #Fitbit user data 
total_minutes2 = personal_df[['VeryActiveMinutes', 'LightlyActiveMinutes', 'FairlyActiveMinutes']].sum() #My personal data
percentages = (total_minutes / total_minutes.sum()) * 100 #Fitbit user data 
percentages2 = (total_minutes2 / total_minutes2.sum()) * 100 #My personal data 
labels = ['Very Active', 'Lightly Active', 'Fairly Active'] #pie chart labels
colors = ['#ffb3ba','#96ead7', '#bae1ff'] #pie chart colors 
# Create the first pie chart trace
pie_chart_trace = go.Pie(labels=labels, values=percentages, marker=dict(colors=colors))
# Create the first figure
fig_fitbit = go.Figure(data=[pie_chart_trace], layout_title_text='Distribution of Workout Minutes for each Level of Intensity for Fitbit Users')
# Create the second pie chart trace
pie_chart_trace2 = go.Pie(labels=labels, values=percentages2, marker=dict(colors=colors))
# Create the second figure
fig_personal = go.Figure(data=[pie_chart_trace2], layout_title_text='Distribution of Workout Minutes for each Level of Intensity for My Personal Data')

###############################Animated plotly line chart number 1 (will all the ids except 1)##############################################
df = data.copy() #make copy of data so the original data is not changed 
df = df[df['Id'] != 1] #remove the first Id (my personal data)

# Set the range of the x-axis
april_16_2016 = pd.to_datetime('2016-04-16')
x_axis_range = [df['ActivityDate'].min(), april_16_2016]

#Create the figure 
fig5 = go.Figure(
    layout=go.Layout(
        updatemenus=[
            dict(
                type="buttons",
                buttons=[
                    dict(
                        label="Play",
                        method="animate",
                        args=[None, {"frame": {"duration": 500, "redraw": True}, "fromcurrent": True}],
                    ),
                    dict(
                        label="Pause",
                        method="animate",
                        args=[[None], {"frame": {"duration": 0, "redraw": True}, "mode": "immediate", "transition": {"duration": 0}}],
                    ),
                ],
                direction="right",
                x=0.9,
                y=1.16,
            ),
        ],
        xaxis=dict(range=x_axis_range,
                   autorange=False, tickwidth=2,
                   title_text="Time"),
        yaxis=dict(range=[0, 30],
                   autorange=False,
                   title_text="Total Distance (in miles)")
    )
)
# Add traces for each unique ID
for unique_id in df['Id'].unique():
    df_id = df[df['Id'] == unique_id]
    fig5.add_trace(
        go.Scatter(x=df_id['ActivityDate'],
                   y=df_id['Total Distance (in miles)'],
                   name=f"ID {unique_id}",
                   visible=True,
                   line=dict(dash="dash")
                 )
    )
#Animation frames
frames = [go.Frame(
    data=[
        go.Scatter(x=df[df['Id'] == unique_id]['ActivityDate'][:k],
                   y=df[df['Id'] == unique_id]['Total Distance (in miles)'][:k],
                   name=f"ID {unique_id}") for unique_id in df['Id'].unique()]
) for k in range(1, len(df['ActivityDate']) + 1)]

#Add ID annotation so the ID number can be seen when hovering on the line 
if df_id['ActivityDate'].iloc[-1] != df['ActivityDate'].iloc[-1]:  #exclude the last id so it doesn't print out on the graph (previous issue)
    fig5.add_annotation(
            x=df_id['ActivityDate'].iloc[-1],
            y=df_id['Total Distance (in miles)'].iloc[-1],
            text=f"ID {unique_id}",
            showarrow=True,
            arrowhead=1
        )

fig5.update(frames=frames, layout=dict(sliders=[dict(steps=[])]))
# Update layout
fig5.update_xaxes(ticks="outside", tickwidth=2, tickcolor='white', ticklen=10)
fig5.update_yaxes(ticks="outside", tickwidth=2, tickcolor='white', ticklen=1)
fig5.update_layout(yaxis_tickformat=',')
fig5.update_layout(legend=dict(x=0, y=1.1), legend_orientation="h")
###############################Animated plotly line chart number 2 (will only Id "1")##############################################
df = data.copy() #make a copy of the data
#create a new df subsetting for Id=1 (personal data) and the correct dates
df_id_1 = df[(df['Id'] == 1) & (df['ActivityDate'] >= '2024-01-01') & (df['ActivityDate'] <= '2024-01-30')]
# Set the range of the x-axis
jan_1_2024 = pd.to_datetime('2024-01-01')
jan_30_2024 = pd.to_datetime('2024-01-30')
x_axis_range = [jan_1_2024, jan_30_2024]

#Create the figure 
fig4 = go.Figure(
    layout=go.Layout(
        updatemenus=[
            dict(
                type="buttons",
                buttons=[
                    dict(
                        label="Play",
                        method="animate",
                        args=[None, {"frame": {"duration": 500, "redraw": True}, "fromcurrent": True}],
                    ),
                    dict(
                        label="Pause",
                        method="animate",
                        args=[[None], {"frame": {"duration": 0, "redraw": True}, "mode": "immediate", "transition": {"duration": 0}}],
                    ),
                ],
                direction="right",
                x=0.9,
                y=1.16,
            ),
        ],
        xaxis=dict(range= [df_id_1['ActivityDate'].min(), jan_30_2024],
                   autorange=False, tickwidth=2,
                   title_text="Time"),
        yaxis=dict(range=[0, 30],
                   autorange=False,
                   title_text="Total Distance (in miles)")
    )
)
# Add traces for each ID (just one in this case)
for unique_id in df_id_1['Id'].unique():
    df_id = df_id_1[df_id_1['Id'] == unique_id]
    fig4.add_trace(
        go.Scatter(x=df_id['ActivityDate'],
                   y=df_id['Total Distance (in miles)'],
                   name=f"ID {unique_id}",
                   visible=True,
                   line=dict(dash="dash", color="darkblue"))
    )
#Animation frames
frames = [go.Frame(
    data=[
        go.Scatter(x=df_id_1[df_id_1['Id'] == unique_id]['ActivityDate'][:k],
                   y=df_id_1[df_id_1['Id'] == unique_id]['Total Distance (in miles)'][:k],
                   name=f"ID {unique_id}") for unique_id in df_id_1['Id'].unique()]
) for k in range(1, len(df_id_1['ActivityDate']) + 1)]
fig4.update(frames=frames, layout=dict(sliders=[dict(steps=[])]))

#Update layout
fig4.update_xaxes(ticks="outside", tickwidth=2, tickcolor='white', ticklen=10)
fig4.update_yaxes(ticks="outside", tickwidth=2, tickcolor='white', ticklen=1)
fig4.update_layout(yaxis_tickformat=',')
fig4.update_layout(legend=dict(x=0, y=1.1), legend_orientation="h")

###To make these animated line plots I used code very similar to this source and fit the code to work with my data:
# https://www.shedloadofcode.com/blog/how-to-create-animated-charts-with-python-and-plotly

##########################################APP LAYOUT###################################################
#######################################################################################################
app.layout = html.Div(style={'backgroundColor': '#FAF9F6', 'font-family': "Georgia"}, children=[
    html.Div(html.H1("Fitbit Analytics Dashboard"), style={'color': 'navy'}), #Title
    html.Div(
        children="This dashboard analyzes Fitbit exercise data and allows users to easily view their workout metrics and compare their data to 35 other Fitbit users (who responded to a survey distributed by Amazon Mechanical Turk between the dates of March 12, 2016 and May 12, 2016). The collected Fibit data ranges from the dates March 12 to April 12, 2016. This dataset was found on Kaggle and merged with my personal Fitbit exported data from January 1 to January 30, 2024. The interactivity allows users to view personal data, Fitbit user data, and compare the two. Important variables included are steps taken, total distance (in miles), very active minutes, and calories burned. Very active minutes are a metric defined by Fitbit and are the highest level of intensity for the categorization of workout minutes (involves the highest heart rate). On the second tab, the data that populated this dashboard can be viewed and the csv file can be downloaded.",
        style={'color': 'navy', 'font-family': "arial"}),
    html.Div(style={'height': '20px'}),  # adding a line of blank space
    #Creating Tabs
    dcc.Tabs([
        # First Tab
        dcc.Tab(label='Analytics', children=[
            #first row containing radio buttons 
            html.Div([
                html.Div(
                    dcc.RadioItems(
                        options=['Fitbit Users 1-10', 'Fitbit Users 11-20', 'Fitbit Users 21-35', "Personal Data"],
                        value="Fitbit Users 1-10",
                        inline=True,
                        id='radio-buttons'
                    ),
                    className="six columns"
                ),
            ], className='row'),
            #second row containing line plot, histogram with dropdown, pie chart, and animated lineplot description text
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
                #Radio button to select the pie chart 
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
                #container to display the selected pie chart 
                html.Div(dcc.Graph(id='pie-chart'),
                          className="seven columns"
                ),
                #Animated line plots description 
                html.Div(children="These animated line charts below display Total Distance in miles over time. The top graph displays this information for each Fitbit User in the dataset (each user is a different line, hover to view Id) and the time period is from March 12, 2016 to April 12, 2016 (when the Fitbit data was collected). The bottom graph displays Total Distance over time for personal user data, which is why only one user Id is shown. These dates are from January 1 to January 30, 2024, when my Fitbit data was collected. Note: My Fitbit was only worn during workouts, so the mileage reflects distance traveled during workouts.", style={'margin-top': '160px','align': 'right', 'color': 'navy'},
                      className="four columns"), 
                  ], className='row'),
            #Div for the two animated line plots (stacked one on top of the other)
            html.Div([
                html.Div(
                    dcc.Graph(id='animated-graph', figure=fig5),
                    className="twelve columns"
                ),
                html.Div(
                    dcc.Graph(id='animated-graph2', figure=fig4),
                    className="twelve columns"
                ),
            ], className='row')
        ]),
         #Second Tab
        dcc.Tab(label='Downloadable Data Table',children=[
            #Data Table and Download Button
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
                    #Download Button
                    html.Div([
                        html.Button("Download Filtered CSV", id="download-button", style={"marginTop": 20}),
                        dcc.Download(id="download-component")
                    ]),
                ], className="twelve columns"),
                #Colored div below the data table
                html.Div(style={'backgroundColor': '#FAF9F6', 'height': '1000px'}),
            ], className='row'),
        ]),
]),
])
###################################################DEFINE CALLBACKS################################################################
###################################################################################################################################

########################Callback to create the LINE PLOT with radio buttons #####################
@app.callback(
    Output('lineplot-with-radio-buttons', 'figure'),
    Input('radio-buttons', 'value'))
#Function updating the data frame based on the radio button selected 
def update_figure(selected_data):
    filtered_df = data[data.Data_Type == selected_data]

    color_palette = px.colors.qualitative.Plotly[:30] #selecting the colors 
    fig = px.line(filtered_df, x="ActivityDate", y="VeryActiveMinutes",
                     title="Line Plot", color='Id', color_discrete_sequence=color_palette, height=484)
      
    fig.update_layout(transition_duration=500, paper_bgcolor="#46C6C6", height=484, title="Line Plot of Very Active Exercise Minutes Over Time", template="plotly_white")

    return fig
##################Callbacks for the DATA TABLE AND DOWNLOAD BUTTON ####################
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
####################Callback for HISTOGRAM dropdown #########################
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
    #Update figure with background color and template of plot 
    fig3.update_layout(paper_bgcolor='#CCCCFF', template="plotly_white")
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
    
#Update color and title of animated line plots
fig5.update_layout(paper_bgcolor='#FAF9F6', title = "Animated Line Plot of Total Distance (in miles) Over Time for all Fitbit Users", template="plotly_white")
fig4.update_layout(paper_bgcolor='#FAF9F6', title = "Animated Line Plot of Total Distance (in miles) Over Time for My Personal Data", template="plotly_white")

# run the app
if __name__ == "__main__":
 app.run_server(debug=True)



