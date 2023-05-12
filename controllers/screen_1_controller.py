import os
from controllers.utils import *
import copy


class DicomController(object):
    def __init__(self, dicoms_path=os.environ['DASHBOARD_FILE_PATH'].strip()):
        self.data = get_json(dicoms_path)
        self.hide_text = False


    def get_dicom_data(self, id):
        self.id = id
        self.dicom_data = get_screen1_dicom_data_by_id(self.data, id)['dicoms']
        self.df = pd.DataFrame(self.dicom_data)

    def get_num_total_dicoms(self):
        return str(len(self.df))

    def get_data_fields(self):
        return self.df.keys().drop('DoctorList')

    def get_doctor_list(self):
        doctors = []
        doctor_list = self.df['DoctorList'].values
        for i in doctor_list:
            doctors += i
        return sorted(list(set(doctors)))

    def get_group_case(self):
        return ['kc', 'vinif', 'bad', 'other', 'not_view']

    def get_hide_text_option(self):
        return self.hide_text

    def set_hide_text_option(self, hide_text):
        self.hide_text = hide_text

    def get_list_properties_case(self):
        return ['2C-3C-4C-PTS_S-PTS_L', '2C-3C-4C', '2C-4C', '2C', '4C', '3C', 'PTS_S', 'PTS_L', 'PW', 'CW', 'TDI_PW', 'CLIP_COLOR']

    def get_dicom(self, filters=None, sort_field=None, filter_options=None):
        dff = self.df
        if filter_options is not None:
            if filter_options == 'done':
                mask = dff['IsDone'].apply(lambda x: x == 'check_true')
                dff = dff[mask]
            elif filter_options == 'annotated':
                mask = dff['NumAnnotatedFrame'].apply(lambda x: x > 0)
                dff = dff[mask]

        if filters is not None and len(filters) > 0:
            for field, values in filters:
                for value in values:
                    mask = dff[field].apply(lambda x: value in x)
                    dff = dff[mask]

        if sort_field is not None:
            field, is_ascending = sort_field
            dff = dff.sort_values(field, ascending=is_ascending, axis=0)
        return dff.to_dict('records')
