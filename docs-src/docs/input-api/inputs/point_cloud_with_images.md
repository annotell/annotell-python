---
title: Point Cloud With Images (v0)
---

:::note Supported point cloud formats
Supported point cloud formats are `.csv`, `.pcd` or `.las`
:::

A `PointCloudsWithImages` input is very similar to the [`Images`](input-api/inputs/images.md) input, except that we in addition to camera images also supply lidar point clouds. In order to relate the lidar representation to the cameras a calibration is needed as well. The calibration enables projection of cuboids in the point cloud down onto the camera images, which can help guide annotators in producing annotations. For more information on how to define and create a calibration, please refer to the [Calibration](input-api/calibration.md) section.

## Single Image and Single Point Cloud Example
The first step is to produce an `Image` object for the camera image, as well as a `PointCloud` object for the lidar point cloud. It's important to specify the right source name for our image and point cloud, since these source names will need to be present in the calibration as well. In this case the source name of the image is `"RFC01"`, whereas for the point cloud we will go with the default source name of `"lidar"`.

:::info no multi-lidar support currently
Currently there is only support for supplying a single point cloud
:::

```python
import annotell.input_api.model as IAM

image1 = IAM.Image(filename="filename_image1.jpg", source="RFC01")
pc = IAM.PointCloud(filename="filename_pc.pcd")
point_clouds_with_images = IAM.PointCloudsWithImages(images=[image1],
                                                     point_clouds=[pc])
folder = Path("/home/user_name/example_path/")  # Folder to where the data is
```

### Adding metadata to the input

Next, we need to add metadata to the input. Similarly to [`Images`](input-api/inputs/images.md) inputs, we can specify the `external_id` and `source_specification`. However we are also _required_ to specify a `calibration_id` in order to create the input.

```python
scene_external_id = "Scene X collection 2020-06-16"
calibration_id = 100
metadata = IAM.CalibratedSceneMetaData(external_id=scene_external_id,
                                       calibration_id=calibration_id)
```

| Parameter            | Description                                                                                                                                                                                                                                |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| external_id          | Id which can be used to track progress of annotations with.                                                                                                                                                                                |
| source_specification | Additional information about sources, includes `source_to_pretty_name` and `source_order`. Defines which source that should be shown first, the source_order, or a mapping of source names to a prettier name version displayed in the UI. |
| calibration_id       | Which calibration to use for the input.                                                                                                                                                                                                    |

See the [Calibration](input-api/calibration.md) section for more information on how to retrieve a calibration id.

### Creating the input

The final step is to create the input.

```python
import annotell.input_api.input_api_client as IAC
client = IAC.InputApiClient()

client.create_inputs_point_cloud_with_images(folder=folder,
                                             point_clouds_with_images=point_clouds_with_images,
                                             metadata=metadata,
                                             project="my_project")
```


### Full example code

> Full example for creating an input consisting of a point cloud and one image. Also includes creation of a new calibration. 
:::tip reuse calibration
Note that you can, and should, reuse the same calibration for multiple inputs if possible.
:::


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
camera_calibration_rfc_01 = Calibration.CameraCalibrationExplicit(
    position=rfc_01_position,
    rotation_quaternion=rfc_01_rotation,
    camera_matrix=rfc_01_camera_matrix,
    distortion_coefficients=rfc_01_distortion_coefficients,
    camera_properties=rfc_01_properties,
    image_height=920,
    image_width=1244
)

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