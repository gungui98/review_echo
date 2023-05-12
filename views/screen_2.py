import json

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import ClientsideFunction, Output, Input, State
from dash.exceptions import PreventUpdate

from app import app
from controllers.screen_2_controller import DicomVideosController

controller = DicomVideosController()


def get_history_review_panel(history):
    DICOM_HISTORY_PANEL = dbc.Jumbotron(
        [
            html.H5(children="Control Panel", className="display-5"),
            html.Hr(className="my-2"),
            dcc.Dropdown(options=[{
                "label": k,
                "value": json.dumps(history[k])} for k in history.keys()],
                id="video-selector",
                className="video-selector",
                clearable=False,
            ),
            html.Hr(className="my-2"),
            html.Div(id="history-submit-section"),
        ],
    )
    return DICOM_HISTORY_PANEL


def get_rating(div_id):
    rating = html.Div([
        html.Div(id=f"{div_id}-rating-init-output"),
        dcc.RadioItems(
            options=[
                {'label': '', 'value': '1'},
                {'label': '', 'value': '2'},
                {'label': '', 'value': '3'},
                {'label': '', 'value': '4'},
                {'label': '', 'value': '5'},
            ],
            labelStyle={'display': 'inline-block'},
            className="star-rating",
            labelClassName="fa fa-star",
            id=f"{div_id}-star-rating",
        ),
    ])
    return rating


def get_dicom_quality_panel():
    QUALITY_PANEL = dbc.Jumbotron(
        [
            html.H5(children="Image Quality Review", className="display-5"),
            html.Hr(className="my-2"),
            get_rating('quality'),
            html.Div(
                [
                    dcc.Textarea(id="quality-comment"),
                    html.P(id="quality-submit-status"),
                    html.Button("Submit", id="quality-submit-button"),
                ], id="quality-submit-section", hidden=True,
            ),
            html.Hr(className="my-2"),
        ],
    )
    return QUALITY_PANEL


VIDEO_CONTROL_BUTTON = html.Div(
    dbc.Row(
        [
            dbc.Col([html.Button("previous", className="previous-frame-button", id="previous-frame-button"), ]),
            dbc.Col([  # html.P("0", className="frame-idx-indicator", id="idx-indicator"),
                html.Button("play/pause", id="play-pause-button", className="play-pause-button")
            ]),
            dbc.Col([html.Button("next", className="next-frame-button", id="next-frame-button"), ]),
        ])
)
VIDEO_CONTROL_BAR = [
    html.Div(
        [
            VIDEO_CONTROL_BUTTON,
            html.Hr(className="video-control-divider"),
            html.Div(id="slider-placeholder"),
        ],
        style={"margin": "1%"},
    ),
]


def get_video_viewer(video_url, height, width):
    VIDEO_VIEWER_WINDOW = [
        html.Div(
            [
                html.Video(
                    id='video-player',
                    src=f'/screen_2/video/{video_url}',
                    controls=False,
                    autoPlay=True,
                    loop=True,
                ),
                html.Canvas(id='annotation-canvas', height=height, width=width),
            ], className='video-player', id="video-player-placeholder"
        ),
    ]
    return VIDEO_VIEWER_WINDOW


def get_layout(case_id, dicom_id):
    mp4_file, history = controller.get_history_from_dicom_id(case_id, dicom_id)
    DICOM_REVIEW = html.Div(
        [
            html.Div(id="init-output"),
            html.Div(id="temp"),
            html.Div(id="temp2"),
            html.Div(id="current-frame-index"),
            dcc.Store(id='annotation-json'),
            dcc.Store(id='frame-rate'),
            dcc.Store(id="json-path", data=dicom_id),
            html.Div([
                get_history_review_panel(history),
                get_dicom_quality_panel(),
            ], className="three columns left-column"),
            html.Div(
                [
                    html.Div([html.Video(
                        id='video-player',
                        src=f'/screen_2/video/{mp4_file}',
                        controls=False,
                        autoPlay=True,
                        loop=True,
                    )]),
                ]
                , id="dicom-viewer-placeholder", className="seven columns"
            ),
        ],
        className="eleven columns center",
        style={"marginTop": "1%"},
    )
    return DICOM_REVIEW


@app.callback(
    [
        Output('frame-rate', 'data'),
        Output('annotation-json', "data"),
        Output('json-path', "data"),
        Output('dicom-viewer-placeholder', "children"),

    ],
    [Input("video-selector", "value")]
)
def on_choose_dicom_history(data):
    if data is None:
        raise PreventUpdate
    data = json.loads(data)
    video_url = data["mp4"]
    annotation_data = json.load(open(data["json_path"], 'r'))
    json_path = data["json_path"]
    fps, height, width = controller.get_frame_rate_and_width_height(video_url)
    video_viewer = dcc.Loading([
        dbc.Card(get_video_viewer(video_url, height, width),
                 className="video_viewer_section"),
        dbc.Card(VIDEO_CONTROL_BAR, className="video_control_section"),
    ])
    return fps, annotation_data, json_path, video_viewer


@app.callback(
    [
        Output("history-submit-section", "children"),
        Output("slider-placeholder", "children"),
    ],
    [Input("annotation-json", "data")],
)
def on_update_dicom(annotation_data):
    if annotation_data is None:
        raise PreventUpdate
    total_frame, annotated_frame = controller.get_annotated_index(annotation_data)
    SUBMIT_SECTION = [
        get_rating("annotation"),
        html.Div(
            [
                dcc.Textarea(id="annotation-comment"),
                html.Hr(className="my-2"),
                html.P(children="", id="annotation-submit-status"),
                html.Div([
                    dbc.Col([html.Button("Accept", className="accept-button", id="accept-button", ), ],
                            className="one columns accept-button-holder"),
                    dbc.Col([html.Button("Reject", className="reject-button", id="reject-button"), ],
                            className="one columns reject-button-holder"),
                ], className="row"),

            ], id="annotation-accept-rejected", hidden=True,
        )
    ]

    SLIDER = dcc.Slider(
        id="frame-index", min=1, max=total_frame, step=1, value=1,
        marks={i: str(i) for i in annotated_frame},
    )
    return SUBMIT_SECTION, SLIDER


@app.callback(
    Output("annotation-accept-rejected", "hidden"),
    [
        Input("annotation-star-rating", "value"),
    ])
def select_reject_reasons(rating_value):
    hide_accept_reject_button = False
    if rating_value is None:
        hide_accept_reject_button = True
    return hide_accept_reject_button


@app.callback(
    Output("quality-submit-section", "hidden"),
    [
        Input("quality-star-rating", "value"),
    ])
def select_reject_reasons(rating_value):
    hide_submit = False
    if rating_value is None:
        hide_submit = True
    return hide_submit


@app.callback(
    Output("annotation-submit-status", "children"),
    [
        Input('reject-button', "n_clicks"),
        Input('accept-button', "n_clicks")
    ],
    [
        State("json-path", 'data'),
        State("annotation-comment", 'data'),
    ]
)
def on_reject_accept_click(reject_click, accept_click, json_path, comment):
    ctx = dash.callback_context
    if not ctx.triggered:
        button_id = 'No clicks yet'
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == "reject-button":
        return_status = controller.annotation_submit(json_path=json_path, is_accepted=False, comment=comment)
        if return_status:
            return ["Submit to server successfully! status: Rejected"]
        else:
            return html.Div(["Server error"], style={
                "color": "red"
            })
    elif button_id == "accept-button":
        return_status = controller.annotation_submit(json_path=json_path, is_accepted=True, comment=comment)
        if return_status:
            return ["Submit to server successfully! status: Accept"]
        else:
            return html.Div(["Server error"], style={
                "color": "red"
            })


@app.callback(
    Output("quality-submit-status", "children"),
    [
        Input('quality-submit-button', "n_clicks")
    ], [
        State('quality-star-rating', "value"),
        State('quality-comment', "value"),
    ]
)
def on_quality_submit(n_clicks, rating, comment):
    if n_clicks is None:
        raise PreventUpdate
    rating = 6 - int(rating)
    return_status = controller.quality_submit(rating=rating, comment=comment)
    if return_status:
        return ["Submit to server successfully!"]
    else:
        return html.Div(["Server error"], style={
            "color": "red"
        })


app.clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='quality_star_init_callback'
    ),
    Output("quality-rating-init-output", 'children'),
    [Input('quality-star-rating', 'value')],
)

app.clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='annotations_star_init_callback'
    ),
    Output("annotation-rating-init-output", 'children'),
    [Input('annotation-star-rating', 'value')],
)

app.clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='init_callback_annotation_review'
    ),
    Output('temp', 'children'),
    [Input('annotation-json', 'data')],
    [State('frame-rate', 'data')]
)
app.clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='select_slider'
    ),
    Output('temp2', 'children'),
    [Input('frame-index', 'value')],
)
