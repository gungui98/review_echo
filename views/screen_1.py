# -*- coding: utf-8 -*-
"""
Module doc string
"""
import json
import random
import time
import os

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, ALL, State, MATCH
from dash.exceptions import PreventUpdate

from app import app
from controllers.screen_1_controller import DicomController
from views import screen_2
from views.view_utils import clip_long_text
from views.view_components import get_card_with_dropdown, get_card_image_field, get_card_info_field, \
    get_multi_color_card_info_field, get_filter_options_card, get_navigation_bar

controller = DicomController()
NUM_CARD_PER_PAGE = 30


def get_card_header(index, dicom_id, case_id):
    return html.A([
        dcc.Store(id={'type': 'screen-1-dicom-data',
                      'index': index},
                  data={"dicom_id": dicom_id, "case_id": case_id}),
        dbc.CardHeader([
            html.P(f'FileName:{dicom_id}'),
        ], className='case-info-card-header'),
    ], id={'type': 'screen-1-card-header',
           'index': index},
        style={'text-decoration': 'none'})


def get_dicom_card(index, data):
    # data = clip_long_text(data)

    file_name = data['FileName']
    annotated_frame = data['NumAnnotatedFrame']
    total_frame = data['NumTotalFrame']
    annotated_ef_frame = data['NumAnnotatedEFFrame']
    annotated_gls_frame = data['NumAnnotatedGLSFrame']
    annotated_ef_gls_frame = data['NumAnnotatedEFAndGLSFrame']
    is_done = data['IsDone']
    doctor_list = data['DoctorList']
    last_edit = data['LastEdit']
    label = data['Label']
    image_path = data['FullImagePath']

    label_tooltip = ""

    if is_done == 'check_true':
        color_file = '#4CAF50'
    elif is_done == 'check_false':
        color_file = 'orangered'
    else:
        color_file = 'gray'

    color_doctor = '#388e3c'
    if len(doctor_list) == 0:
        doctor_name = ''
    else:
        doctor_name = f'{list(doctor_list.keys())[0]}'
    if len(doctor_list) > 1:
        doctor_name += f", {len(doctor_list) - 1} others"

    card = dbc.Card([
        get_card_header(index, file_name, controller.id),
        dbc.CardBody([
            get_card_image_field(field_id='screen1-dicom-image', className='dicom-image', index=index,
                                 image_path=image_path),
            get_card_info_field(field_id='screen1-dicom-frame-info', index=index,
                                text=f'{annotated_frame} / {total_frame} frames',
                                icon="far fa-images",
                                tooltip=f"{annotated_frame} annotated in {total_frame} total dicoms"),
            get_card_info_field(field_id='screen1-dicom-ef-info', index=index,
                                text=f'{annotated_ef_frame} ef / {total_frame} frames',
                                icon="far fa-images",
                                tooltip=f"{annotated_ef_frame} annotated ef frames in {total_frame} total dicoms"),
            get_card_info_field(field_id='screen1-dicom-gls-info', index=index,
                                text=f'{annotated_gls_frame} gls / {total_frame} frames',
                                icon="far fa-images",
                                tooltip=f"{annotated_gls_frame} annotated gls frames in {total_frame} total dicoms"),
            get_card_info_field(field_id='screen1-dicom-ef-gls-info', index=index,
                                text=f'{annotated_ef_gls_frame} ef and gls / {total_frame} frames',
                                icon="far fa-images",
                                tooltip=f"{annotated_ef_gls_frame} annotated ef and gls frames in {total_frame} total dicoms"),

            get_card_with_dropdown(field_id='screen1-doctor-list-indicator', index=index,
                                   text=doctor_name,
                                   hidden_content=doctor_list,
                                   icon="fas fa-fw fa-user-md",
                                   tooltip=f"{doctor_name}",
                                   color=color_doctor),

            get_card_info_field(field_id='label-list-indicator', index=index,
                                text=label,
                                icon="fas fa-fw fa-tag",
                                tooltip=label_tooltip),

            get_card_info_field(field_id='last-edit-indicator', index=index,
                                text=last_edit,
                                icon="fas fa-fw fa-history",
                                tooltip=f"Last annotated: {last_edit}"),
        ], className='case-info-card-body')
    ], className='four columns case-info-card',
        style={'background-color': color_file})
    return card


def get_dicom_image_card(index, data):
    file_name = data['FileName']
    total_frame = data['NumTotalFrame']
    is_done = data['IsDone']
    doctor_list = data['DoctorList']
    image_path = data['FullImagePath']
    # image_path = 'not_found.jpg'

    if is_done == 'check_true':
        color_file = '#4CAF50'
    elif is_done == 'check_false':
        color_file = 'orangered'
    else:
        color_file = 'gray'

    if len(doctor_list) == 0:
        doctor_name = ''
    else:
        doctor_name = f'{list(doctor_list.keys())[0]}'
    if len(doctor_list) > 1:
        doctor_name += f", {len(doctor_list) - 1} others"

    card = dbc.Card([
        get_card_header(index, file_name, controller.id),
        dbc.CardBody([
            get_card_image_field(field_id='screen1-dicom-image', className='dicom-image', index=index,
                                 image_path=image_path),
            get_card_info_field(field_id='screen1-dicom-frame-info', index=index,
                                text=f'{total_frame} frames',
                                icon="far fa-images",
                                tooltip=f"dicom has {total_frame} frames"),
            dbc.Input(id="screen1-dicom-image-card-input", placeholder="Doctor comment", type="text"),

        ], className='case-info-card-body'),
    ], className='columns case-image-card',
        style={'background-color': color_file})
    return card


def get_card_grid(case_data, hide_text_data, n_columns=4):
    grid_case = []
    if not hide_text_data:
        n_row = len(case_data) // n_columns
        for i in range(n_row + 1):
            grid_case.append(
                dbc.Row([get_dicom_card(index=i * n_columns + idx, data=data) for idx, data in
                         enumerate(case_data[i * n_columns: (i * n_columns + n_columns)])
                         ])
            )
    else:
        n_columns = 3
        n_row = len(case_data) // n_columns
        for i in range(n_row + 1):
            grid_case.append(
                dbc.Row([get_dicom_image_card(index=i * n_columns + idx, data=data) for idx, data in
                         enumerate(case_data[i * n_columns: (i * n_columns + n_columns)])
                         ])
            )
    return [html.Div(grid_case)]


"""
# DICOM Review tab
"""


def get_dicom_review_filter_panel(id):
    controller.get_dicom_data(id)
    return html.Div(
        [
            html.H5('Control Panel'),
            html.P('Total case: ' + controller.get_num_total_dicoms(), id='screen1-num-dicom-indicator'),
            html.P('Hide Text', id='screen1-hide-text-button', n_clicks=0,
                   className='screen1-hide-text-button'),
            html.Hr(className="my-2"),
            html.P('Filter By Doctors:'),
            dcc.Dropdown(options=[
                {"label": i, 'value': i}
                for i in controller.get_doctor_list()
            ], multi=True, id='screen1-doctor-filter'),
            html.Hr(className="my-2"),
            html.P('Sort By Field:'),
            dcc.Dropdown(options=[
                {"label": i, 'value': i}
                for i in controller.get_data_fields()
            ], multi=False, id='screen1-sort-field'),
            dcc.Checklist(
                options=[
                    {'label': ' Ascending', 'value': 'ascending'},
                ],
                id='screen1-sort-mode',
            ),

            html.Hr(className="my-2"),
            html.P('Select By Properties:'),
            dcc.Checklist(
                options=[
                    {'label': ' 2C-3C-4C-PTS_S-PTS_L', 'value': '2C-3C-4C-PTS_S-PTS_L'},
                    {'label': ' 2C-3C-4C', 'value': '2C-3C-4C'},
                    {'label': ' 2C-4C', 'value': '2C-4C'},
                    {'label': ' 2C', 'value': '2C'},
                    {'label': ' 4C', 'value': '4C'},
                    {'label': ' 3C', 'value': '3C'},
                    {'label': ' PTS_S', 'value': 'PTS_S'},
                    {'label': ' PTS_L', 'value': 'PTS_L'},
                    {'label': ' PW', 'value': 'PW'},
                    {'label': ' CW', 'value': 'CW'},
                    {'label': ' TDI_PW', 'value': 'TDI_PW'},
                    {'label': ' CLIP_COLOR', 'value': 'CLIP_COLOR'},

                ],
                id='screen1-case-label',
                labelStyle={'margin-right': "20px", },
            ),

            html.Hr(className="my-2"),
            get_filter_options_card(filter_options_id='screen1-filter-options'),
            html.Hr(className="my-2"),
            html.Div([
                html.P('Doctor Select And Comment'),
                dcc.RadioItems(
                    options=[
                        {'label': ' kc', 'value': 'kc'},
                        {'label': ' vinif', 'value': 'vinif'},
                        {'label': ' bad', 'value': 'bad'},
                        {'label': ' other', 'value': 'other'},
                        {'label': ' not_view', 'value': 'not_view'},
                    ],
                    id='screen1-case-label',
                    labelStyle={'display': 'inline-block', 'margin-right': "20px", },
                ),
                # html.Br(),
                dcc.Textarea(
                    id='screen1-doctor-comment',
                    value='',
                    style={'width': '100%'},
                    placeholder='Doctor comment',
                ),
                html.Button('Submit', id='screen1-doctor-comment-button', n_clicks=0,
                            style={"float": "right", "padding-left": "15px", "padding-right": "15px"}),
            ]),
            html.Div(id="screen1-submit-section"),
            html.Br(),
            html.Br(),
            html.Hr(className="my-2"),

        ],
    )


def get_layout(id):
    controller.get_dicom_data(id)
    layout = html.Div(
        [
            dcc.Store(id='case_id', data=id),
            dcc.Store(id='screen1-selected_case_data'),
            dcc.Store(id='screen1-hide-text-option-data'),
            dcc.Store(id='screen1-hide-text-button-name'),

            dbc.Card(get_dicom_review_filter_panel(id),
                     className='three columns pretty_container'),
            html.Div([get_navigation_bar(screen='screen1')], className='patient-case-page-navigation'),
            html.Div(id='screen1-dicom_grid', className='eight columns dicom-grid'),
            dbc.Modal([
                # dbc.ModalHeader("Header", id='screen-2-header'),
                dbc.ModalBody(id='screen-2-body')
            ], id="screen-2", size="xl", className="screen-2-modal", )
        ],
        className="twelve columns",
        style={"marginTop": 30},
    )
    return layout


"""
# cache variables
"""

"""
# callback
"""


@app.callback(Output('screen1-page-selector', 'value'),
              [
                  Input('screen1-first-page-button', 'n_clicks'),
                  Input('screen1-next-page-button', 'n_clicks'),
                  Input('screen1-prev-page-button', 'n_clicks'),
                  Input('screen1-last-page-button', 'n_clicks'),
                  Input('screen1-num-page', 'children'),
              ],
              [
                  State('screen1-page-selector', 'value'),
              ]
              )
def on_next_prev_page(next, prev, first, last, max_page, current_page_index):
    if max_page is None:
        return current_page_index
    max_page = int(max_page)
    ctx = dash.callback_context
    if current_page_index is not None:
        current_page_index = int(current_page_index)
    if not ctx.triggered:
        button_id = 'None'
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if button_id != 'None':
        if button_id == 'screen1-next-page-button':
            current_page_index = current_page_index % max_page + 1
        elif button_id == 'screen1-prev-page-button':
            current_page_index = current_page_index - 1
            current_page_index = max_page + current_page_index if current_page_index < 1 else current_page_index
        elif button_id == 'screen1-first-page-button':
            current_page_index = 1
        elif button_id == 'screen1-last-page-button':
            current_page_index = max_page
        elif button_id == 'screen1-num-page':
            current_page_index = 1
    return current_page_index


@app.callback(Output('screen1-dicom_grid', 'children'),
              [
                  Input('screen1-page-selector', 'value'),
                  Input('screen1-num-page', 'children'),
                  Input('screen1-hide-text-option-data', 'data'),
              ],
              [State('screen1-selected_case_data', 'data')]
              )
def on_select_page(page, num_page, hide_text_data, case_data):
    if page is None or page == '':
        page = 0
    else:
        page = int(page)
    page = page - 1
    return get_card_grid(case_data[page * NUM_CARD_PER_PAGE:
                                   (page + 1) * NUM_CARD_PER_PAGE], hide_text_data)


@app.callback(
    Output('screen1-num-page', 'children'),
    [Input('screen1-selected_case_data', 'data')]
)
def update_page_selection(case_data):
    num_page = len(case_data) // NUM_CARD_PER_PAGE + 1
    return str(num_page)


@app.callback(
    Output('screen1-hide-text-option-data', 'data'),
    [Input('screen1-hide-text-button', 'n_clicks')]
)
def on_click(n_clicks):
    # hide_text_option = controller.get_hide_text_option()
    # controller.set_hide_text_option(not hide_text_option)
    hide_text_option = n_clicks % 2 == 0
    return hide_text_option


@app.callback(
    Output('screen1-hide-text-button', 'children'),
    [Input('screen1-hide-text-option-data', 'data')]
)
def on_change_name_button(data):
    if data:
        return 'Show Text'
    else:
        return 'Hide Text'


@app.callback([
    Output('screen1-selected_case_data', 'data'),
    Output('screen1-num-dicom-indicator', 'children'),
],
    [
        Input('screen1-doctor-filter', 'value'),
        Input('screen1-sort-field', 'value'),
        Input('screen1-sort-mode', 'value'),
        Input('screen1-filter-options', 'value'),
    ])
def update_selected_case(selected_doctors, sorted_field,
                         sort_mode, filter_options):
    filters = []
    if sorted_field is not None:
        if sort_mode is None:
            sort_mode = False
        else:
            sort_mode = len(sort_mode)
            if sort_mode == 1:
                sort_mode = True
            else:
                sort_mode = False
        sort_content = [sorted_field, sort_mode]

    else:
        sort_content = None
    if selected_doctors is not None and len(selected_doctors) > 0:
        filters.append(['DoctorList', selected_doctors])

    selected_cases = controller.get_dicom(filters=filters, sort_field=sort_content, filter_options=filter_options)
    return selected_cases, 'Total case: ' + str(len(selected_cases))


def get_screen_2_layout(data):
    click = dash.callback_context.triggered[0]
    if click['value'] is None:
        raise PreventUpdate
    else:
        index = json.loads(click['prop_id'].split('.')[0])["index"]
        index = int(index)
    data = data[index]
    dicom_id = data["dicom_id"]
    case_id = data["case_id"]
    screen_2_layout = screen_2.get_layout(case_id, dicom_id)
    return screen_2_layout


@app.callback(
    Output('screen-2-body', 'children'),
    [
        Input({'type': 'screen-1-card-header', 'index': ALL}, 'n_clicks'),
    ],
    [
        State({'type': 'screen-1-dicom-data', 'index': ALL}, 'data'),
    ]
)
def display_output(n_clicks, data):
    return get_screen_2_layout(data)


@app.callback(
    Output('screen-2', 'is_open'),
    [Input('screen-2-body', 'children')],
)
def open_screen_2(_):
    return [True]
