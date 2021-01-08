---
title: FAQ
description: FAQ
---


### Receiving `requests.exceptions.HTTPError: 403 Client Error: Forbidden for url: ...` when trying to create inputs

This implies that the authenticated user does not have access to the endpoint being called. Make sure you're [authenticating](../annotell-auth) correctly. If an Annotell user, make sure `client_organization_id` is specified on the `InputApiClient`.