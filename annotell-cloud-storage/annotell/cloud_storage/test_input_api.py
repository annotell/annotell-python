import os
import json
from pathlib import Path
# from annotell.cloud_storage.input_api_client import InputApiClient

from input_api_client import InputApiClient


if __name__ == "__main__":
    c = InputApiClient(base_url="http://annotell.org:8010", api_token="DEF")

    folder = Path("/Users/markocotra/Downloads/test_input_api")
    """
    files = [
        "india_1259396926226198_1575361708215415_FC.jpg",
        "india_1259396926226198.pcd"
    ]
    """

    files = dict(
        images=["india_1259396926226198_1575361708215415_FC.jpg"],
        pointclouds=["india_1259396926226198.pcd"]
    )

    path_to_calibration = os.path.join(folder, 'annotell_sensor_config.json')

    with open(path_to_calibration, 'r') as fp:
        calibration = json.load(fp)

    input_list_id = 8

    scene_metadata = {
        "externalId": "master_skywalker_what_are_we_going_to_do_JKL",
        "sourceSpecification": {
            "imagesToSource": {
                "india_1259396926226198_1575361708215415_FC.jpg": "FC"
            },
            "sourceToPrettyName": {
                "FC": "Front Camera"
            },
            "sourceOrder": ["FC"]
        },
        "calibrationSpec": {
            "externalId": "big_boi_test:1337",
            "calibration": calibration
        }
        # "calibrationId": 419
    }
    resp = c.create_inputs_for_files(folder, files, input_list_id, scene_metadata)
    print(resp)
    """

    print()
    resp = c.list_projects()
    print(resp)

    print()
    resp = c.list_input_lists(7)
    print(resp)

    print()
    resp = c.get_calibration_data()
    print(resp)

    print()
    resp = c.get_calibration_data(id=428)
    print(resp)

    print()
    resp = c.get_calibration_data(external_id="big_boi_test:1337")
    print(resp)

    print()
    resp = c.create_calibration_data(calibration, external_id='We grant you a seat on this council')
    print(resp)
    """

    """
    print()
    resp = c.mend_input_data()
    print(resp)

    print()
    resp = c.invalidate_input()
    print(resp)

    print()
    resp = c.get_requests_for_request_ids(request_ids=[23])
    print(resp)

    print()
    resp = c.get_requests_for_input_lists(input_list_id=8)
    print(resp)

    print()
    internal_ids = ["ed8cf0da-5f5a-4b6f-bfcf-684358b0ad50", "be25e986-5be3-4bc7-8d69-321b63899942"]
    resp = c.get_input_lists_for_inputs(internal_ids=internal_ids)
    print(resp)

    print()
    internal_ids = ["ed8cf0da-5f5a-4b6f-bfcf-684358b0ad50", "be25e986-5be3-4bc7-8d69-321b63899942", "cdefdf49-ca27-464a-b29d-976f72e63556"]
    resp = c.get_input_status(internal_ids=internal_ids)
    print(resp)

    print()
    internal_ids = ["ed8cf0da-5f5a-4b6f-bfcf-684358b0ad50", "be25e986-5be3-4bc7-8d69-321b63899942", "cdefdf49-ca27-464a-b29d-976f72e63556"]
    resp = c.download_annotations(internal_ids=internal_ids, request_id=23)
    print(resp)
    """
