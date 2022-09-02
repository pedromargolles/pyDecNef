############################################################################
# AUTHORS: Pedro Margolles & David Soto
# EMAIL: pmargolles@bcbl.eu, dsoto@bcbl.eu
# COPYRIGHT: Copyright (C) 2021, Python fMRI-Neurofeedback
# INSTITUTION: Basque Center on Cognition, Brain and Language (BCBL), Spain
# LICENCE: 
############################################################################

#############################################################################################
# IMPORT DEPENDENCIES
#############################################################################################

import dash
from dash.dependencies import Output, Input
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import webbrowser
import numpy as np
import pandas as pd
from pathlib import Path
from colorama import init, Fore # For colouring outputs in the terminal
init() # Initialize Colorama

#############################################################################################
# PARTICIPANT, SESSION, RUN
#############################################################################################

print(Fore.YELLOW + 'Specify participant, session and run numbers to load logs file')
subject = input(Fore.YELLOW + '\nSubject number: ')
session = input(Fore.YELLOW + 'Session number: ')
run = input(Fore.YELLOW + 'Run number: ')
print('\n')

#############################################################################################
# PLOTTING PARAMETERS
#############################################################################################

port = 9000 # Plot an interactive figure in http://127.0.0.1/9000
chance_level = 0.5 # Decoding chance level
refresh_interval = 1000 # Refresh plot each 1000ms

#############################################################################################
# OPEN LOGS DIRECTORY
#############################################################################################

# Decoding logs dir
logs_dir = Path(__file__).absolute().parent.glob(f'outputs/sub-{subject}_session-{session}/run-{run}*')

# Get last run folder
logs_dir = sorted(list(logs_dir), key = lambda folder: str(folder).split('_')[-1])[-1]
print('Processing:', logs_dir)

#############################################################################################
# PLOT DECODING ACROSS TRIALS
#############################################################################################

# Generate a Dash layout
app = dash.Dash(__name__)
app.layout = html.Div([
                        dcc.Graph(id = 'live-graph', animate = True),
                        dcc.Interval(id = 'graph-update', interval = refresh_interval),
                      ])

# Update plot function
@app.callback(Output('live-graph', 'figure'), [Input('graph-update', 'n_intervals')])
def update_scatter(n):
    global trial_idxs
    global decoding_probs

    #############################################################################################
    # LOAD LOGS FILE
    #############################################################################################

    # Load participant's corresponding log file
    df = pd.read_csv(logs_dir / 'logs_dir/logs.csv')

    # Get decoding accuracy of each trial
    trials = [trial[0] for trial in df.groupby(['decoding_prob', 'trial_idx'], as_index = False)]
    trials = sorted(trials, key=lambda x: x[1]) # Sort by trial_idx
    decoding_probs, trial_idxs = list(zip(*trials))

    # Generate a scatter plot
    data = go.Scatter(x = trial_idxs, 
                      y = decoding_probs, 
                      name='Scatter', 
                      mode='lines+markers')
    
    return {'data': [data], 
            'layout': go.Layout(
                                xaxis = dict(tickmode = 'array', 
                                             tickvals = np.array(trial_idxs), 
                                             range = [min(trial_idxs), max(trial_idxs)]
                                            ),
                                yaxis = dict(range=[0, 1]),
                                xaxis_title = 'Trial number',
                                yaxis_title = 'Decoding probability (%)',
                                title='Probability of decoding target category by trial',
                                shapes = [dict(type = 'line',
                                               name = 'chance_level',
                                               xref = 'paper', 
                                               x0 = 0, 
                                               x1 = 1, 
                                               yref = 'y', 
                                               y0 = chance_level, 
                                               y1 = chance_level,
                                               line = {'dash': 'dash', 
                                                       'color': 'red'})],
                                )}

if __name__ == "__main__":
  webbrowser.open('http://127.0.0.1:9000', new = 0, autoraise = True) # Automatically opens a new browser window (default browser)
  app.run_server(host = '127.0.0.1', port = port, debug = False, use_reloader = False) # Run a localserver on port 9000
