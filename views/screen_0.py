# -*- coding: utf-8 -*-
"""
Module doc string
"""
import json
import random
import time

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, ALL, State, ClientsideFunction
from dash.exceptions import PreventUpdate

from app import app
from controllers.screen_0_controller import PatientCaseController
from views.view_utils import clip_long_text
from views.view_components import get_card_info_field, get_filter_options_card, get_multi_color_card_info_field, \
    get_navigation_bar

controller = PatientCaseController()
NUM_CARD_PER_PAGE = 8


def get_patient_case_card(index, data):
    id = data['ID']
    approved = data['NumApproved']
    rejected = data['NumRejected']
    annotated_dicom = data['NumAnnotatedDicom']
    total_dicom = data['NumTotalDicom']
    annotated_frame = data['NumAnnotatedFrame']
    total_frame = data['NumTotalFrame']
    doctor_list = data['DoctorList']
    last_edit = data['LastEdit']
    last_review = data['LastReview']
    hospital = data['Hospital']
    patient_name = data['PatientName']
    label = data['Label']
    # is_done = random.choice([True, False])
    is_done = data.get('IsDone', "not_check")
    if is_done == 'check_true':
        color_file = '#4CAF50'
    elif is_done == 'check_false':
        color_file = 'orangered'
    else:
        color_file = 'gray'

    label_tooltip = ""
    label_text = ""
    label_keys = sorted(list(label.keys()))
    if len(label.keys()) != 0:
        label_text = f"{label_keys[0]} - {label[label_keys[0]]} dicoms"
        for k in label_keys:
            label_tooltip += f"{k} - {label[k]} dicoms, "
    if len(label.keys()) > 1:
        label_text += ", ..."

    if len(doctor_list) != 0:
        doctor_name = f'{doctor_list[0]}'
    else:
        doctor_name = ''
    if len(doctor_list) > 1:
        doctor_name += f", {len(doctor_list) - 1} others"
    card = dbc.Card([
        html.A([
            dbc.CardHeader([
                html.P(f'Case {id}'),
            ], className='case-info-card-header'),
        ], href=f'case_id={id}', style={'text-decoration': 'none'}),
        dbc.CardBody([
            get_card_info_field(field_id='dicom-info', index=index,
                                text=f'{annotated_dicom} / {total_dicom} dicoms',
                                icon="fas fa-pencil-ruler",
                                tooltip=f"{annotated_dicom} annotated in {total_dicom} total dicoms"),
            get_multi_color_card_info_field(
                field_id='review-status-indicator', index=index,
                spans=[
                    [f'{approved} / ', 'green'],
                    [f'{rejected} / ', 'red'],
                    [f'{total_dicom}', 'default'],
                ],
                icon="fa fa-tasks",
                tooltip=f"{approved} approved {rejected} rejected in {total_dicom} total dicom"),
            get_card_info_field(field_id='annotated-frame-indicator', index=index,
                                text=f'{annotated_frame} / {total_frame} frames',
                                icon="fa fa-pen",
                                tooltip=f"{annotated_frame} annotated {total_frame} total frames"),
            get_card_info_field(field_id='doctor-list-indicator', index=index,
                                text=doctor_name,
                                icon="fas fa-fw fa-user-md",
                                tooltip=", ".join(doctor_list)),

            get_card_info_field(field_id='label-list-indicator', index=index,
                                text=label_text,
                                icon="fas fa-fw fa-tag",
                                tooltip=label_tooltip),

            get_card_info_field(field_id='hospital-indicator', index=index,
                                text=clip_long_text(hospital),
                                icon="fas fa-fw fa-hospital",
                                tooltip=hospital),
            get_card_info_field(field_id='patient-name-indicator', index=index,
                                text=clip_long_text(patient_name),
                                icon="fas fa-fw fa-procedures",
                                tooltip=patient_name),
            get_card_info_field(field_id='last-edit-indicator', index=index,
                                text=last_edit,
                                icon="fas fa-fw fa-history",
                                tooltip=f"annotated: {last_edit}, review: {last_review}"),
        ], className='case-info-card-body')
    ], className='four columns case-info-card',
        style={'background-color': color_file})
    return card


def get_card_grid(case_data, n_columns=4):
    n_row = len(case_data) // n_columns
    grid_case = []
    for i in range(n_row + 1):
        grid_case.append(
            dbc.Row([get_patient_case_card(index=i * n_columns + idx, data=data) for idx, data in
                     enumerate(case_data[i * n_columns: (i * n_columns + n_columns)])
                     ])
        )
    return [html.Div(grid_case)]


"""
# DICOM Review tab
"""
DICOM_REVIEW_FILTER_PANEL = html.Div(
    [
        html.H5('Control Panel'),
        html.P('Total cases: ' + controller.get_num_total_cases(), id='num-case-indicator'),
        html.Hr(className="my-2"),
        html.P('Search for Case:'),
        dcc.Dropdown(options=[
            {"label": i, 'value': i}
            for i in controller.get_case_id_list()
        ], multi=False, id='case-id-filter'),
        html.Hr(className="my-2"),
        html.P('Filter By Doctors:'),
        dcc.Dropdown(options=[
            {"label": i, 'value': i}
            for i in controller.get_doctor_list()
        ], multi=True, id='doctor-filter'),
        html.Hr(className="my-2"),
        html.P('Filter By Hospital:'),
        dcc.Dropdown(options=[
            {"label": i, 'value': i}
            for i in controller.get_hospital_list()
        ], multi=True, id='hospital-filter'),

        html.Hr(className="my-2"),
        html.P('Filter By PatientName:'),
        dcc.Dropdown(options=[
            {"label": i, 'value': i}
            for i in controller.get_patient_name_list()

        ], multi=True, id='patient-filter'),

        html.Hr(className="my-2"),
        html.P('Sort By Field:'),
        dcc.Dropdown(options=[
            {"label": i, 'value': i}
            for i in controller.get_data_fields()
        ], id='sort-field'),
        dcc.Checklist(
            options=[
                {'label': ' Ascending', 'value': 'ascending'},
            ],
            id='sort-mode',
        ),
        html.Hr(className="my-2"),
        get_filter_options_card(filter_options_id='screen0-filter-options'),
    ],
)

layout = html.Div(
    [
        dcc.Store(id='selected_case_data'),
        html.Div(id='fade-in'),
        dbc.Card(DICOM_REVIEW_FILTER_PANEL,
                 className='three columns pretty_container'),
        html.Div([get_navigation_bar(screen='screen0')], className='patient-case-page-navigation'),
        html.Div(id='patient-case-grid', className='eight columns patient-case-grid', ),

    ],
    className="twelve columns",
    style={"marginTop": 30},
)

"""
# cache variables
"""

"""
# callback
"""


@app.callback(Output('screen0-page-selector', 'value'),
              [
                  Input('screen0-first-page-button', 'n_clicks'),
                  Input('screen0-next-page-button', 'n_clicks'),
                  Input('screen0-prev-page-button', 'n_clicks'),
                  Input('screen0-last-page-button', 'n_clicks'),
                  Input('screen0-num-page', 'children'),
              ],
              [
                  State('screen0-page-selector', 'value'),
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
        if button_id == 'screen0-next-page-button':
            current_page_index = current_page_index % max_page + 1
        elif button_id == 'screen0-prev-page-button':
            current_page_index = current_page_index - 1
            current_page_index = max_page + current_page_index if current_page_index < 1 else current_page_index
        elif button_id == 'screen0-first-page-button':
            current_page_index = 1
        elif button_id == 'screen0-last-page-button':
            current_page_index = max_page
        elif button_id == 'screen0-num-page':
            current_page_index = 1
    return current_page_index


@app.callback(Output('patient-case-grid', 'children'),
              [
                  Input('screen0-page-selector', 'value'),
                  Input('screen0-num-page', 'children'),
              ],
              [State('selected_case_data', 'data')]
              )
def on_select_page(page, num_page, case_data):
    case_data = controller.get_selected_case()
    if page is None or page == '':
        page = 0
    else:
        page = int(page)
    page = page - 1
    return get_card_grid(case_data[page * NUM_CARD_PER_PAGE:
                                   (page + 1) * NUM_CARD_PER_PAGE])


@app.callback(
    Output('screen0-num-page', 'children'),
    [Input('selected_case_data', 'data')]
)
def update_page_selection(case_data):
    case_data = controller.get_selected_case()
    num_page = len(case_data) // NUM_CARD_PER_PAGE + 1
    return str(num_page)


@app.callback([
    Output('selected_case_data', 'data'),
    Output('num-case-indicator', 'children'),
],
    [
        Input('case-id-filter', 'value'),
        Input('doctor-filter', 'value'),
        Input('hospital-filter', 'value'),
        Input('patient-filter', 'value'),
        Input('sort-field', 'value'),
        Input('sort-mode', 'value'),
        Input('screen0-filter-options', 'value'),
    ])
def update_selected_case(selected_case, selected_doctors, selected_hospitals,
                         selected_patients, sorted_field,
                         sort_mode, filter_options):
    filters = []
    print(selected_case)
    if selected_case is not None:
        filters.append(['ID', selected_case])
    if selected_doctors is not None and len(selected_doctors) > 0:
        filters.append(['DoctorList', selected_doctors])
    if selected_hospitals is not None and len(selected_hospitals) > 0:
        filters.append(['Hospital', selected_hospitals])
    if selected_patients is not None and len(selected_patients) > 0:
        filters.append(['PatientName', selected_patients])
    sort = None
    if sorted_field is not None:
        if sort_mode is None:
            sort_mode = False
        elif len(sort_mode) > 0:
            sort_mode = True
        else:
            sort_mode = False
        sort = [sorted_field, sort_mode]

    selected_cases = controller.get_patient_case(filters=filters, sort=sort, filter_options=filter_options)
    total_case_title = 'Total cases: ' + str(len(selected_cases))
    controller.set_selected_case(selected_cases)
    return 'updated', total_case_title


app.clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='fade_in'
    ),
    Output('fade-in', 'children'),
    [
     Input('screen0-page-selector', 'value'),
     Input('screen0-num-page', 'children'),
     ],
)
