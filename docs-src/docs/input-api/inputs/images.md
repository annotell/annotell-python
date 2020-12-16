---
title: Images (v0)
---

:::note Supported image formats
Supported image formats are `.png` or `.jpg`
:::

An `Images` input consists of 1-8 different images. A common scenario might be that you have a data collection vehicle which has a front facing camera, as well as cameras facing the right and left side of the car. Often the cameras will have overlapping viewpoints, which means that the same object can be seen in several of the cameras. By including all of the cameras in the same input, it's possible to annotate each camera image while also making sure that objects don't get duplicate object ids.

:::note
Note that the `Images` input is single frame, i.e. if you have a _sequence_ of camera images that you want to annotate together, then you need to use the input type `CamerasSeq`.
:::

## Single Image Example
The first step is to produce an `Image` object. The parameters are the image name \(excluding the path to the image\) and the source of the image (i.e. camera name). In this case, we want to create a scene consisting of one image _image1_ and well go with the default source name of `"CAM"`. Next, we create a list of all our `Image` objects and create an `ImageFiles` object. Additionally, we need to include the path to where the image is located.

```python
import annotell.input_api.model as IAM
from pathlib import Path

image1 = "filename1.jpg"
images = [IAM.Image(filename=image1)]
images_files = IAM.ImagesFiles(images)
folder = Path("/home/user_name/example_path")
```

Next we can upload the images to a project

```python
# Project
project = "<external_id>"

import annotell.input_api.input_api_client as IAC
client = IAC.InputApiClient()

response = client.images.create(
    folder=folder,
    images_files=IAM.ImagesFiles(images),
    project=project)
```

If we were to use several images the process would be the same, except that we would have included more `Image` objects in the `ImageFiles` object. However, when using several images we *must* specify a unique source for each image, which means that we can't use the default `"CAM"` value. 

:::tip Use dryrun to validate input
Setting `dryrun` parameter to true in the method call, will validate the input using the Input API but not create any inputs.
:::
## Adding metadata to the input
Different types of metadata can be added to the input. For `Images` inputs, this amounts to specifying the `external_id` of the input as well as the `source_specification`:


| Property             | Description                                                                                                                                                                                                                                |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| external_id          | Id which can be used to track progress of annotations with.                                                                                                                                                                                |
| source_specification | Additional information about sources, includes `source_to_pretty_name` and `source_order`. Defines which source that should be shown first, the source_order, or a mapping of source names to a prettier name version displayed in the UI. |

If not supplied, a default metadata will be used where the `external_id` is a randomly generated UUID.

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
response = client.images.create(folder=folder,
                                images_files=images_files,
                                metadata=images_metadata,
                                project=project)
```