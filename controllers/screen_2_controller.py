import glob
import json
import os
from datetime import datetime

import cv2
import requests

from controllers.utils import get_json

ROOT_DICOM_MP4 = os.environ["ROOT_DICOM_MP4"]
ANNOTATION_JSON_PATH = os.environ["ANNOTATION_JSON_PATH"]
SERVER_API_VERIFY = os.environ["SERVER_API_VERIFY"]


class DicomVideosController:
    def __init__(self, json_path=os.environ['DASHBOARD_FILE_PATH'].strip()):
        self.data = get_json(json_path)
        self.__dicom_list_to_dict()
        self.RelativePath = None
        self.annotation_review = None
        self.quality_review = None
        self.study_instance_uid = None

    def __dicom_list_to_dict(self):
        for case_id in self.data.keys():
            dicom_data = self.data[case_id]['Dicom']
            dicom_data_dict = {}
            for dicom in dicom_data:
                dicom_data_dict[dicom['FileName']] = dicom
            self.data[case_id]['Dicom'] = dicom_data_dict

    def get_video_path(self, case_id, dicom_id):
        data_json = self.data[case_id]
        study_instance_uid = data_json['StudyInstanceUID']
        dicom_data = data_json["Dicom"][dicom_id]
        video_path = study_instance_uid + '/' + dicom_data['ImagePath'] + '.mp4'
        return video_path

    def get_history_from_dicom_id(self, case_id, dicom_id):
        self.study_instance_uid = self.data[case_id]['StudyInstanceUID']
        image_path = self.data[case_id]['Dicom'][dicom_id]["ImagePath"]
        self.RelativePath = image_path

        history = dict()
        pattern = f"{self.study_instance_uid}____{image_path}"
        files = sorted(glob.glob(os.path.join(ANNOTATION_JSON_PATH, "**", f'*{pattern}*')), reverse=True)
        mp4_file = os.path.join(f"{self.study_instance_uid}/{image_path}" + ".mp4")
        for f in files:
            lastFile = f
            phone_number = os.path.basename(os.path.dirname(lastFile))
            timeLastFile = lastFile.split("____")[-1][:-5]
            dtLastFile = datetime.strptime(timeLastFile, "%Y%m%d%H%M%S.%f").strftime("%Y/%m/%d ")
            data_json = json.load(open(lastFile, 'r'))
            history[dtLastFile + " " + phone_number] = {"mp4": mp4_file,
                                                        "checked": data_json.get("checked", "not_check"),
                                                        "json_path": lastFile
                                                        }
        return mp4_file, history

    def get_annotated_index(self, json_data):
        annotated_frame = []
        for idx, annotation in enumerate(json_data["dicomAnnotation"]):
            if len(annotation["ef_boundary"]) > 0:
                annotated_frame.append(idx + 1)
        return len(json_data["dicomAnnotation"]), annotated_frame

    def get_frame_rate_and_width_height(self, video_url):
        video = cv2.VideoCapture(os.path.join(ROOT_DICOM_MP4, video_url))

        # Find OpenCV version
        (major_ver, minor_ver, subminor_ver) = (cv2.__version__).split('.')

        if int(major_ver) < 3:
            fps = video.get(cv2.cv.CV_CAP_PROP_FPS)
        else:
            fps = video.get(cv2.CAP_PROP_FPS)
        ret, frame = video.read()
        height, width = frame.shape[:2]
        video.release()
        return fps, height, width

    def annotation_submit(self, json_path, is_accepted, comment):
        print(f"[API] {json_path} is_accepted: {is_accepted} reason:{self.annotation_review}")
        json_path = json_path[len(ANNOTATION_JSON_PATH) + 1:]
        return_status = requests.post(SERVER_API_VERIFY,
                                      json={"relative_path": json_path,
                                            "checked": "check_true" if is_accepted else "check_false",
                                            "note": comment,
                                            })
        return return_status.status_code == 200

    def quality_submit(self, rating, comment):
        print(f"[API]  {self.RelativePath} rating {rating} comment:{comment}")
        return True


if __name__ == '__main__':
    controller = DicomVideosController("/root/tuannm/AICardio-Server/Stat_Dashboard/src/dashboard.json")
    print(controller.get_history_from_dicom_id(case_id='000010', dicom_id='IM_0126'))
