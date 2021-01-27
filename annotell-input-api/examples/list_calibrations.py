from typing import List

from annotell.input_api.input_api_client import InputApiClient

if __name__ == "__main__":
    print("Listing Calibration...")

    client = InputApiClient()

    calibrations = client.calibration.get_calibration()
    print(calibrations)
