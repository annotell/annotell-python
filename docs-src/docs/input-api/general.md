---
title: General
---

## Creating Inputs

:::note
For detailed information about different input modalities, check [images](inputs/images), [point cloud with images](inputs/point_cloud_with_images) or [LidarsAndCamerasSeq](inputs/lidars_and_cameras_seq).
:::

:::tip Annotell Users
As an Annotell user, it is possible to specify `client_organization_id` to `InputApiClient` constructor to create inputs on behalf of a client organization
:::

In order to create inputs, they need to be associated with a [project](project) and an [input batch](project#batch). Consider the following project setup:

```
organization # root for projects
└── projects
   ├── project-a
       ├── batch-1 - completed
       ├── batch-2 - open
           ├── input 0edb8f59-a8ea-4c9b-aebb-a3caaa6f2ba3
           ├── input 37d9dda4-3a29-4fcb-8a71-6bf16d5a9c36
           └── ...
       └── batch-3 - pending
   └── project-b
       ├── batch-1
       └── ...
```

There are 3 ways in order to create inputs

- Adding inputs to latest open batch for a project
- Adding inputs to specified batchfor a project
- Adding inputs to an input list (deprecated)

The following examples all use an input of type `IMAGES`, however the interface applies to all input types.

### Adding inputs to latest open batch for a project

```python
client.create_inputs_images(
    ...,
    project="project-a")
```

Will add inputs to `project-a` `batch-2` because it's the latest open batch.

### Adding inputs to specified batchfor a project

```python
client.create_inputs_images(
    ...,
    project="project-a",
    batch="batch-3")
```

Will add inputs to `project-a` `batch-3`.

### Adding inputs to an input list (deprecated)

```python
client.create_inputs_images(
    ...,
    input_list_id=500)
```

Will add inputs to input list `500`.

:::caution deprecated input_list_id
Using input lists is deprecated and will be removed in future releases
:::

## Input Status

Once an input has been created, it might be preprocessed before being made available for annotation. Also, postprocessing such as conversion to the client-specific format might take place after annotation has been performed. During this process, the status property of an input can be used to keep track of progress.

| Status                          | Description                                                                                                             |
| ------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| processing                      | Input has been received and currently processed by Annotell Platform, potentially performing conversion of file formats |
| created                         | Input is created and available for annotation                                                                           |
| failed                          | Conversion of input failed                                                                                              |
| invalidated:broken-input        | Input was invalidated since it did not load                                                                             |
| invalidated:duplicate           | Input was invalidated due to being uploaded several times                                                               |
| invalidated:incorrectly-created | Input was invalidated because it was incorrectly created1                                                               |

## List Inputs

```python
project = "project-identifier"
client.input.get_inputs(project=project)
```

Inputs can be retrieved via the API by specifying project. Additional filter parameters are also available (see below) for querying inputs.

| Parameter           | Description                                               |
| ------------------- | --------------------------------------------------------- |
| project             | Project identifier to filter by                           |
| batch               | Which batch in the project to return inputs for           |
| external_ids        | Return inputs matching the `external_ids` supplied        |
| include_invalidated | Filters inputs based on their status, defaults to `False` |

### Response

| Property    | Description                                                |
| ----------- | ---------------------------------------------------------- |
| internal_id | ID used to identify the input within the Annotell Platform |
| external_id | External ID supplied during input creation                 |
| batch_id    | Which batch does the input belong to                       |
| input_type  | Type of input (see [Input Types](../key_concepts.md))      |
| status      | Input status (see [Input Statuses](#input-status))         |

## Invalidate Inputs

```python
invalid_ids = ["0edb8f59-a8ea-4c9b-aebb-a3caaa6f2ba3", "37d9dda4-3a29-4fcb-8a71-6bf16d5a9c36"]
reason = IAM.InvalidatedReasonInput.BAD_CONTENT
client.input.invalidate_inputs(invalid_ids, reason)
```

If issues are detected upstream related to inputs created, it is possible to invalidate inputs.
Invalidated inputs will not produce annotations and any completed annotations of the input will be invalidated.

| Reason              | Description                                                                |
| ------------------- | -------------------------------------------------------------------------- |
| bad-content         | Input does not load, or has erroneous metadata such as invalid calibration |
| duplicate           | If same input has been created several times                               |
| incorrectly-created | If the input was unintentionally created.                                  |

## List Invalidated Inputs

If errors are detected by Annotell, inputs will be invalidated and a reason will be supplied.

```python
project = "project-identifier"
client.input.get_inputs(project= project, include_invalidated= True)
```
