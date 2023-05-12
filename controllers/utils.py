import pandas as pd
import json


def get_json(data_path):
    with open(data_path, 'r+', encoding="utf8") as f:
        data_json = json.load(f)
    data_json = data_json['cases']
    data_dict = {data['ID']: data for data in data_json}

    return data_dict


def get_json_data(data_path):
    with open(data_path, 'r+', encoding="utf8") as f:
        data_json = json.load(f)
    data_json = data_json['cases']

    return data_json


def get_screen1_dicom_data_by_id(data, id):
    data_json = data[id]
    studyInstanceUID = data_json['StudyInstanceUID']
    data_dicom = data_json['Dicom']
    for dicom in data_dicom:
        imagePath = studyInstanceUID + '/' + dicom['ImagePath'] + '.jpg'
        dicom['FullImagePath'] = imagePath

    screen_1_data = {
        "dicoms": data_dicom
    }
    return screen_1_data


def get_screen_1_data(data_path, id):
    data_dict = get_json(data_path)
    data_json = data_dict[id]
    studyInstanceUID = data_json['StudyInstanceUID']
    data_dicom = data_json['Dicom']
    for dicom in data_dicom:
        imagePath = studyInstanceUID + '/' + dicom['ImagePath'] + '.jpg'
        dicom['FullImagePath'] = imagePath

    screen_1_data = {
        "dicoms": data_dicom
    }
    return screen_1_data


def get_screen_0_data(data_path):
    data_json = get_json_data(data_path)
    screen_0_data = []
    for data in data_json:
        data.pop('Dicom')
        screen_0_data.append(data)

    screen_0_data = {
        "cases": screen_0_data
    }
    return screen_0_data
