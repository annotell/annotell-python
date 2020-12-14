---
title: General
---

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
If errors are detected by Annotell, inputs will be invalidated and a reason will be supplied. 

```python
project = 10
client.get_inputs(project_id= project, invalidated= True)
```

:::caution
List using project id and not external identifier
:::