# Input API

## Project

In order to create inputs via the Input API, an Annotell project needs to exist.
Projects are configured by the Annotell Professional Services team, during the Guideline Agreement Process (GAP) of a new client engagement.

### List Projects

```python
projects = client.list_projects()
```

> Or via `annoutil` CLI

```shell
annoutil projects
```

Returns all projects.

## Batch

Input batches allow further grouping of inputs into smaller batches within a project. Specifying input batch during input creation is optional, and will otherwise default to the latest open batch.

Ongoing projects can benefit from using batches in two ways

- Group inputs collected at the same time
- Perform guideline or task definition changes without the need for retroactive changes.

### Batch Status

| Status      | Description                                                                                                            |
| ----------- | ---------------------------------------------------------------------------------------------------------------------- |
| pending     | Batch has been created but is still not fully configured by Annotell. Either during project setup or requested changes |
| open        | Batch is open for new inputs                                                                                           |
| ready       | Batch has been published and no longer open for new inputs.                                                            |
| in-progress | Annotell has started annotation of inputs within the batch.                                                            |
| completed   | Annotations has been completed.                                                                                        |

### Listing Batches

```python
projects = client.list_project_batches("project_external_id")
```

> Or via `annoutil` CLI

```shell
annoutil batches <project-external-id>
```

Returns all batches for the project

### Publish Batch

```python
projects = client.publish_batch("project_external_id", "batch_external_id")
```

Publishes the input batch. Published batches are not open for new inputs.

## Input

### Invalidate Inputs

```python
invalid_ids = ["0edb8f59-a8ea-4c9b-aebb-a3caaa6f2ba3", "37d9dda4-3a29-4fcb-8a71-6bf16d5a9c36"]
reason = IAM.InvalidatedReasonInput.BAD_CONTENT
client.invalidate_inputs(invalid_ids, reason)
```

If issues are detected upstream related to inputs created, it is possible to invalidate inputs.
Invalidated inputs will not produce annotations and any completed annotations of the input will be invalidated.


| Reason              | Description                                                                |
| ------------------- | -------------------------------------------------------------------------- |
| bad-content         | Input does not load, or has erroneous metadata such as invalid calibration |
| duplicate           | If same input has been created several times                               |
| incorrectly-created | If the input was unintentionally created.                                  |


### List Invalidated Inputs
<aside class="warning">
List using project id and not external identifier
</aside>
```python
project = 10
client.get_inputs(project_id= project, invalidated= True)
```

If errors are detected by Annotell, inputs will be invalidated and a reason will be supplied. 

## Images

### Single Image

> We start out by creating a representation of our image.

```python
image1 = "filename1.jpg"
images = [IAM.Image(filename=image1)]
images_files = IAM.ImagesFiles(images)
folder = Path("/home/user_name/example_path")
```

> Next we can upload the images to a project

```python
# Project
project = "<external_id>"

response = client.upload_and_create_images_input_job(folder=folder,
                                                     images_files=iam.ImagesFiles(images),
                                                     project=project)
```

Images inputs can be created from python via the _upload_and_create_images_input_job_ method.

The representation consists of the image name \(excluding the path to the image\) and the source of the image. In this case, we want to create a scene consisting of one image _image1_. We also specify a folder where the image is located.

<aside class="notice">
Setting dryrun parameter to true in the method call, will validate the input using the Input API but not create any inputs.
</aside>

### Image with Source Specification

> Scene with several images and custom source names

```python
# Create objects representing the images and the scene
image1 = "filename1.jpg"
image2 = "filename2.jpg"
images = [IAM.Image(filename=image1, source="CAM1"),
          IAM.Image(filename=image2, source="CAM2")]
images_files = IAM.ImagesFiles(images)
folder = Path("/home/user_name/example_path")

# Project
project = "<external_id>"

# Create Scene meta data
source_spec = IAM.SourceSpecification(source_to_pretty_name={"CAM1": "FC", "CAM2": "BC"},
                                      source_order=["CAM1", "CAM2"])
images_metadata = IAM.SceneMetaData(external_id="2020-06-16",
                                    source_specification=source_spec)
# Create Input
response = client.upload_and_create_images_input_job(folder=folder,
                                                     images_files=iam.ImagesFiles(images),
                                                     metadata=images_metadata,
                                                     project=project)
```

Optionally, we can also add _**SceneMetaData**_ to the input, with the following properties.

| Property             | Description                                                                                                                                                                                                                                |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| external_id          | Id which can be used to track progress of annotations with.                                                                                                                                                                                |
| source_specification | Additional information about sources, includes `source_to_pretty_name` and `source_order`. Defines which source that should be shown first, the source_order, or a mapping of source names to a prettier name version displayed in the UI. |

## Point Clouds

<aside class="notice">
Supported point cloud formats are .csv, .pcd or .npy
</aside>

## Point Clouds with Images

> Create representation of images and point clouds + source specification images

```python
image1 = IAM.Image(filename="filename_image1.jpg", source="RFC01")
pc = IAM.PointCloud(filename="filename_pc.pcd")
point_clouds_with_images = IAM.PointCloudsWithImages(images=[image1],
                                                     point_clouds=[pc])
folder = Path("/home/user_name/example_path/")  # Folder to where the data is
```

### PointCloudsWithImages

We start off by creating a representation of the images and the point cloud that make up the scene along with a SourceSpecification for the images.

| Parameter    | Description                                                             |
| ------------ | ----------------------------------------------------------------------- |
| images       | 2D Images                                                               |
| point_clouds | LiDAR point clouds in any of the supported formats (.csv, .pcd or .npy) |

<aside class="warning">
Currently there is only support for supplying a single point cloud
</aside>

### Scene metadata

> Add Scene metadata

```python
scene_external_id = "Scene X collection 2020-06-16"
calibration_id = 100
metadata = IAM.CalibratedSceneMetaData(external_id=scene_external_id,
                                       source_specification=source_specification,
                                       calibration_id=calibration_id)
```

| Parameter            | Description                                                                                                                                                                                                                                |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| external_id          | Id which can be used to track progress of annotations with.                                                                                                                                                                                |
| source_specification | Additional information about sources, includes `source_to_pretty_name` and `source_order`. Defines which source that should be shown first, the source_order, or a mapping of source names to a prettier name version displayed in the UI. |
| calibration_id       | Which calibration to use for the input.                                                                                                                                                                                                    |

See calibration section for more information on how to retrieve a calibration_id.

### Creating the input

> Create input

```python
client.create_inputs_point_cloud_with_images(folder=folder,
                                             point_clouds_with_images=point_clouds_with_images,
                                             metadata=metadata,
                                             project="my_project")
```

Now everything required is prepared in order to use `create_inputs_point_cloud_with_images`.

### Full example code

> Full example for creating an input consisting of a point cloud and one images. Including creating a new calibration for the input.

```python
import annotell.input_api.input_api_model as IAM
import annotell.input_api.model.calibration as Calibration
import annotell.input_api.input_api_client as IAC
from pathlib import Path
client = IAC.InputApiClient()
# Create representation of images and point clouds + source specification images
image1 = IAM.Image(filename="filename_image1.jpg", source="RFC01")
pc = IAM.PointCloud(filename="filename_pc.pcd")
point_clouds_with_images = IAM.PointCloudsWithImages(images=[image1],
                                                     point_clouds=[pc])
folder = Path("/home/user_name/example_path/")  # Folder to where the data is
# Create lidar calibration
lidar_position = Calibration.Position(x=0.0, y=0.0, z=0.0)
lidar_rotation = Calibration.RotationQuaternion(w=1.0, x=0.0, y=0.0, z=0.0)
lidar_calibration = Calibration.LidarCalibrationExplicit(position=lidar_position,
                                                         rotation_quaternion=lidar_rotation)
# Create a camera calibration
rfc_01_camera_type = Calibration.CameraType.PINHOLE
rfc_01_position = Calibration.Position(x=0.0, y=0.0, z=0.0)  # similar to Lidar
rfc_01_rotation = Calibration.RotationQuaternion(w=1.0, x=0.0, y=0.0, z=0.0)  # similar to Lidar
rfc_01_camera_matrix = Calibration.CameraMatrix(fx=3450, fy=3250, cx=622, cy=400)
rfc_01_distortion_coefficients = Calibration.DistortionCoefficients(k1=0.0, k2=0.0, p1=0.0, p2=0.0, k3=0.0)
rfc_01_properties = Calibration.CameraProperty(camera_type=rfc_01_camera_type)
camera_calibration_rfc_01 = Calibration.CameraCalibrationExplicit(position=rfc_01_position,
                                                                  rotation_quaternion=rfc_01_rotation,
                                                                  camera_matrix=rfc_01_camera_matrix,
                                                                  distortion_coefficients=rfc_01_distortion_coefficients,
                                                                  camera_properties=rfc_01_properties,
                                                                  image_height=920,
                                                                  image_width=1244)

# Create calibration for the scene
calibration_dict = dict(RFC01=camera_calibration_rfc_01,
                        lidar=lidar_calibration)
calibration = IAM.Calibration(calibration_dict=calibration_dict)
calibration_external_id = "Collection 2020-06-16"
calibration_spec = IAM.CalibrationSpec(external_id=calibration_external_id,
                                       calibration=calibration)
# Create the calibration using the Input API client
created_calibration = client.create_calibration_data(calibration_spec=calibration_spec)

# Create metadata
scene_external_id = "Scene X collection 2020-06-16"
metadata = IAM.CalibratedSceneMetaData(external_id=scene_external_id,
                                       calibration_id=created_calibration.id)

# Add input
client.create_inputs_point_cloud_with_images(folder=folder,
                                             point_clouds_with_images=point_clouds_with_images,
                                             metadata=metadata,
                                             project="my_project")
```

Putting this together, we first create a representation of the input and its metadata, create or reuse calibration and then uploads the input.

## Calibration

Inputs including both a 2D and 3D representation such as **point cloud with images** require a calibration relating the camera sensors with the lidar sensors in terms of location and rotation. The calibration file should also contain the required information for projecting 3D points into the image plane of the camera.

A Calibration object consists of a set of key-value pairs where the key is the name of the source and the value is either a _LidarCalibrationExplicit_ object or a _CameraCalibrationExplicit_ object depending on the sensor.

### Listing existing calibrations

> Get calibrations matching an external identifier

```python
client.get_calibration_data(external_id="Collection 2020-06-16")
```

Previously created calibrations are available through either client or `annoutil calibration`

### Creating a lidar calibration

<aside class="notice">
Note that you can, and should, reuse the same calibration for multiple scenes if possible.
</aside>

```python
import annotell.input_api.model.calibration as Calibration
# Create lidar calibration
lidar_position = Calibration.Position(x=0.0, y=0.0, z=0.0)
lidar_rotation = Calibration.RotationQuaternion(w=1.0, x=0.0, y=0.0, z=0.0)
lidar_calibration = Calibration.LidarCalibrationExplicit(position=lidar_position,
                                                         rotation_quaternion=lidar_rotation)
```

A lidar calibration is represented as a _LidarCalibrationExplicit_ object and consists of a position expressed with three coordinates and a rotation in the form of a [Quaternion](https://en.wikipedia.org/wiki/Quaternions_and_spatial_rotation). See the code example below for creating a basic _LidarCalibrationExplicit_ object.

### Creating a camera calibration

```python
rfc_01_camera_type = Calibration.CameraType.PINHOLE
rfc_01_position = Calibration.Position(x=0.0, y=0.0, z=0.0)  # similar to Lidar
rfc_01_rotation = Calibration.RotationQuaternion(w=1.0, x=0.0, y=0.0, z=0.0)  # similar to Lidar
rfc_01_camera_matrix = Calibration.CameraMatrix(fx=3450, fy=3250, cx=622, cy=400)
rfc_01_distortion_coefficients = Calibration.DistortionCoefficients(k1=0.0, k2=0.0, p1=0.0, p2=0.0, k3=0.0)
rfc_01_properties = Calibration.CameraProperty(camera_type=rfc_01_camera_type)
camera_calibration_rfc_01 = Calibration.CameraCalibrationExplicit(position=rfc_01_position,
                                                                  rotation_quaternion=rfc_01_rotation,
                                                                  camera_matrix=rfc_01_camera_matrix,
                                                                  distortion_coefficients=rfc_01_distortion_coefficients,
                                                                  camera_properties=rfc_01_properties,
                                                                  image_height=920,
                                                                  image_width=1244)
```

A camera calibration is represented as a CameraCalibrationExplicit object. The Camera calibration format is based on [OpenCVs](https://docs.opencv.org/3.4/d4/d94/tutorial_camera_calibration.htm) format and this [paper](http://www.robots.ox.ac.uk/~cmei/articles/single_viewpoint_calib_mei_07.pdf). The camera calibration consists of the following set of key-value pairs.

| Key                       | Value                                                                                                                               |
| :------------------------ | :---------------------------------------------------------------------------------------------------------------------------------- |
| rotation_quaternion       | A RotationQuaternion object                                                                                                         |
| position                  | A Position object                                                                                                                   |
| camera_matrix             | A CameraMatrix object                                                                                                               |
| camera_properties         | A CameraProperty object                                                                                                             |
| distortion_coefficients   | A DistortionCoefficients object. Please note that the coefficient _k3_ should be equal to None if the camera type is _Kannala_**.** |
| image_height              | Integer                                                                                                                             |
| image_width               | Integer                                                                                                                             |
| undistortion_coefficients | \(**Optional\)** An UndistortionCoefficients object. This is only used for _Kannala_ cameras.                                       |

```python
# Create calibration for the scene
calibration_dict = dict(RFC01=camera_calibration_rfc_01,
                        lidar=lidar_calibration)
calibration = IAM.Calibration(calibration_dict=calibration_dict)
calibration_external_id = "Collection 2020-06-16"
calibration_spec = IAM.CalibrationSpec(external_id=calibration_external_id,
                                       calibration=calibration)
# Create the calibration using the Input API client
created_calibration = client.create_calibration_data(calibration_spec=calibration_spec)
```

We tie the calibration together by creating a dictionary mapping the source name to the corresponding calibration. We then create a _Calibration_ object and a _CalibrationSpecification_ object which we then use to create a calibration in the Annotell platform. The external id can be used for querying for the calibration file and also for relating the calibration in our system to how the client refers to it.

## Dealing with errors

When the client sends a http request to the Input API and waits until it receives a response. If the response code is 2xx \(the status code for a successful call\) the client converts the received message into a python object which can be viewed or used. However if the Input API responds with an error code \(4xx or 5xx\) the python client will raise an error. It's up to the user to decide if and how the want to handle this error.
