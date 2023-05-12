import os
from controllers.utils import *


class PatientCaseController:
    def __init__(self, json_path=os.environ['DASHBOARD_FILE_PATH'].strip()):
        self.data = get_screen_0_data(json_path)['cases']
        self.df = pd.DataFrame(self.data)

    def get_case_id_list(self):
        return [i['ID'] for i in self.data]

    def set_selected_case(self, selected_case_data):
        self.selected_case_data = selected_case_data

    def get_selected_case(self):
        return self.selected_case_data

    def get_num_total_cases(self):
        return str(len(self.df))

    def get_doctor_list(self):
        doctors = []
        doctor_list = self.df['DoctorList'].values
        for i in doctor_list:
            doctors += i
        return sorted(list(set(doctors)))

    def get_hospital_list(self):
        return self.df['Hospital'].unique()

    def get_patient_name_list(self):
        return self.df['PatientName'].unique()

    def get_data_fields(self):
        return self.df.keys()

    def get_patient_case(self, filters=None, sort=None, filter_options=None):
        dff = self.df

        if filter_options is not None:
            if filter_options == 'done':
                ## Chưa implement vì chưa có data isdone màn 1
                # mask = dff['IsDone'].apply(lambda x: x == 'check_true')
                # dff = dff[mask]
                dff = dff
            elif filter_options == 'annotated':
                mask = dff['NumAnnotatedFrame'].apply(lambda x: x > 0)
                dff = dff[mask]

        if filters is not None and len(filters) > 0:
            for field, values in filters:
                    if isinstance(values, str):
                        mask = dff[field].apply(lambda x: values == x)
                        dff = dff[mask]
                    else:
                        for value in values:
                            mask = dff[field].apply(lambda x: value in x)
                            dff = dff[mask]
        if sort is not None:
            field, is_ascending = sort
            dff = dff.sort_values(field, ascending=is_ascending)
        return dff.to_dict('records')


if __name__ == '__main__':
    patient = PatientCaseController('../data/dashboard.json')
    print(patient.get_patient_case(filters=[["ID", "000001"]]))
