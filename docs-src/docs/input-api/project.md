---
title: Projects
---

## Project

In order to create inputs via the Input API, an Annotell project needs to exist.
Projects are configured by the Annotell Professional Services team, during the Guideline Agreement Process (GAP) of a new client engagement.

### List Projects

```python
projects = client.project.list_projects()
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
projects = client.project.list_project_batches("project_external_id")
```

> Or via `annoutil` CLI

```shell
annoutil batches <project-external-id>
```

Returns all batches for the project

### Publish Batch

```python
projects = client.project.publish_batch("project_external_id", "batch_external_id")
```

Publishes the input batch. Published batches are not open for new inputs.
