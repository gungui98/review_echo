import pathlib

import dash
import dash_bootstrap_components as dbc

PATH = pathlib.Path(__file__).parent.resolve()
DATA_PATH = PATH.joinpath("data").resolve()

EXTERNAL_STYLESHEETS = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
FONT_AWESOME = "https://use.fontawesome.com/releases/v5.10.2/css/all.css"
VIDEO_FRAME = "https://rawgit.com/allensarkisyan/VideoFrame/master/VideoFrame.min.js"
JQUERY = "https://ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js"
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, FONT_AWESOME],
                external_scripts=[VIDEO_FRAME, JQUERY],
                suppress_callback_exceptions=True)
