import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, ALL, State

from app import app
from controllers.screen_1_controller import DicomController
import base64

def get_card_with_dropdown(field_id, index, text, hidden_content, icon, tooltip, color):
    line = html.Div([
        html.Hr(),
        html.Div([
            html.I(className=icon),
            html.P(text,
                   className="card-text-info",
                   style={'color': color},
                   ),
            html.Div([
                html.P(f'{key}: {len(hidden_content[key])} times') for key in hidden_content.keys()
            ], className="dropdown-content")
        ], id=f'{field_id}-{index}', className='dropdown'),
    ])
    return line


def get_card_info_field(field_id, index, text, icon, tooltip, color="black"):
    return html.Div([
        html.Hr(),
        html.Div([
            html.I(className=icon),
            html.P(text,
                   className="card-text-info",
                   style={'color': color},
                   ),
        ], id=f'{field_id}-{index}'),
        dbc.Tooltip(
            tooltip,
            target=f"{field_id}-{index}",
            style={
                "visibility": "visible",
                "position": "relative",
                "font-size": '14px',
            }
        ),
    ])


def get_card_image_field(field_id, className, index, image_path):
    path = '/screen_1/images/' + image_path
    line = html.Div([
        html.Div([
            html.Img(src=path, id=f'{field_id}', className=f'{className}'),
        ], id=f'{field_id}-{index}')
    ])
    return line

    # ## test man
    # path = image_path
    # line = html.Div([
    #     html.Div([
    #         html.Img(src=path, id=f'{field_id}', className=f'{className}'),
    #     ], id=f'{field_id}-{index}')
    # ])
    # return line


def get_multi_color_card_info_field(field_id, index, spans, icon, tooltip):
    color_text = html.Div([html.P(text, style={'color': color},
                                  className="card-text-info") for text, color in spans],
                          style={'display': 'inline'})
    line = html.Div([
        html.Hr(),
        html.Div([
            html.I(className=icon),
            color_text,
        ], id=f'{field_id}-{index}'),
        dbc.Tooltip(
            tooltip,
            target=f"{field_id}-{index}",
            style={
                "font-size": '14px',
                "background-color": "#f00"
            }
        ),
    ])
    return line


def get_filter_options_card(filter_options_id):
    return dcc.RadioItems(
        options=[
            {'label': ' Show all', 'value': 'show-all'},
            {'label': ' Done review only', 'value': 'done'},
            {'label': ' Annotated only', 'value': 'annotated'}
        ],
        id=f'{filter_options_id}'
    )


def get_navigation_bar(screen):
    PAGE_NAVIGATION = html.Div([
        html.Button([
            html.I(className='fas fa-step-backward'),
        ], id=f'{screen}-first-page-button', className='page-selector-button'),
        html.Button([
            html.I(className='fas fa-arrow-left')
        ], id=f'{screen}-prev-page-button', className='page-selector-button'),
        dcc.Input(value=0, id=f'{screen}-page-selector', className='page-selector'), html.Span(f' / '),
        html.Span(id=f'{screen}-num-page'),
        html.Button([
            html.I(className='fas fa-arrow-right')
        ], id=f'{screen}-next-page-button', className='page-selector-button'),
        html.Button([
            html.I(className='fas fa-step-forward')
        ], id=f'{screen}-last-page-button', className='page-selector-button'),
    ])

    return PAGE_NAVIGATION
