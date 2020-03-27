import os
import json
from pathlib import Path
# from annotell.cloud_storage.input_api_client import InputApiClient

from input_api_client import InputApiClient
import input_api_model as IAM


if __name__ == "__main__":
    c = InputApiClient(
        host="http://annotell.org:8010",
        api_token="DEF",
        auth_host="http://annotell.org:8001"
    )

    folder = Path("/Users/markocotra/Downloads/test_input_api")
    """
    files = [
        "india_1259396926226198_1575361708215415_FC.jpg",
        "india_1259396926226198.pcd" 
    ]
    """

    files = IAM.FilesPointCloudWithImages(
        images=["india_1259396926226198_1575361708215415_FC.jpg"],
        pointclouds=["india_1238861697022498.csv"]
    )

    path_to_calibration = os.path.join(folder, 'annotell_sensor_config.json')

    with open(path_to_calibration, 'r') as fp:
        calibration = json.load(fp)

    input_list_id = 8

    scene_metadata = {
        "externalId": "beta",
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


    metadata = IAM.Metadata(
        external_id="beta",
        source_specification=IAM.SourceSpecification(
            images_to_source={
                "india_1259396926226198_1575361708215415_FC.jpg": "FC"
            },
            source_to_pretty_name={
                "FC": "Front Camera"
            },
            source_order=["FC"]
        ),
#        calibration_id= 419,
        calibration_spec=IAM.CalibrationSpec(
            external_id="big_boi_test:1337",
            calibration=calibration
        )
    )

    m = metadata.to_dict()
    print(m)
    print(m == scene_metadata)
    raise
    print()
    print("get_view_links")
    resp = c.get_view_links(internal_ids=["ed8cf0da-5f5a-4b6f-bfcf-684358b0ad50", "be25e986-5be3-4bc7-8d69-321b63899942"])
    print(resp)

    print()
    print("get_internal_ids_for_external_ids")
    resp = c.get_internal_ids_for_external_ids(
        external_ids=["alpha", "master_skywalker_what_are_we_going_to_do"]
    )
    print(resp)

    print()
    print("get_input_jobs_status")
    resp = c.get_input_jobs_status(
        external_id="alpha"
    )
    print(resp)

    print()
    print("get_input_jobs_status")
    resp = c.get_input_jobs_status(
        external_id="beta"
    )
    print(resp)

    raise
    print()
    print("create_inputs_point_cloud_with_images")
    resp = c.create_inputs_point_cloud_with_images(folder, files, input_list_id, scene_metadata)
    print(resp)

    print()
    print("list_projects")
    resp = c.list_projects()
    print(resp)

    print()
    print("list_input_lists")
    resp = c.list_input_lists(7)
    print(resp)

    print()
    print("get_calibration_data")
    resp = c.get_calibration_data()
    print(resp)

    print()
    print("get_calibration_data")
    resp = c.get_calibration_data(id=428)
    print(resp)

    print()
    print("get_calibration_data")
    resp = c.get_calibration_data(external_id="big_boi_test:1337")
    print(resp)

    print()
    print("create_calibration_data")
    resp = c.create_calibration_data(calibration, external_id='We grant you a seat on this council')
    print(resp)

    """
    print()
    resp = c.mend_input_data()
    print(resp)

    print()
    resp = c.invalidate_input()
    print(resp)
    """
    print()
    print("get_requests_for_request_ids")
    resp = c.get_requests_for_request_ids(request_ids=[23])
    print(resp)

    print()
    print("get_requests_for_input_lists")
    resp = c.get_requests_for_input_lists(input_list_id=8)
    print(resp)

    print()
    print("get_input_lists_for_inputs")
    internal_ids = ["ed8cf0da-5f5a-4b6f-bfcf-684358b0ad50", "be25e986-5be3-4bc7-8d69-321b63899942"]
    resp = c.get_input_lists_for_inputs(internal_ids=internal_ids)
    print(resp)

    print()
    print("get_input_status")
    internal_ids = ["ed8cf0da-5f5a-4b6f-bfcf-684358b0ad50", "be25e986-5be3-4bc7-8d69-321b63899942", "cdefdf49-ca27-464a-b29d-976f72e63556"]
    resp = c.get_input_status(internal_ids=internal_ids)
    print(resp)

    print()
    print("download_annotations")
    internal_ids = ["ed8cf0da-5f5a-4b6f-bfcf-684358b0ad50", "be25e986-5be3-4bc7-8d69-321b63899942", "cdefdf49-ca27-464a-b29d-976f72e63556"]
    resp = c.download_annotations(internal_ids=internal_ids, request_id=23)
    print(resp)
