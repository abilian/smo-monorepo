from http import HTTPStatus
from typing import Any, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.problem import Problem
from ...models.smo_web_handlers_graph_deploy_json_body import (
    SmoWebHandlersGraphDeployJsonBody,
)
from ...types import Response


def _get_kwargs(
    project: str,
    *,
    body: SmoWebHandlersGraphDeployJsonBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/project/{project}/graphs",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | Problem | None:
    if response.status_code == 202:
        response_202 = cast(Any, None)
        return response_202
    if response.status_code == 400:
        response_400 = Problem.from_dict(response.json())

        return response_400
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Any | Problem]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    project: str,
    *,
    client: AuthenticatedClient | Client,
    body: SmoWebHandlersGraphDeployJsonBody,
) -> Response[Any | Problem]:
    """Deploy a new HDAG

     Deploys a Hyper Distributed Application Graph from a descriptor.

    Args:
        project (str):
        body (SmoWebHandlersGraphDeployJsonBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, Problem]]
    """

    kwargs = _get_kwargs(
        project=project,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    project: str,
    *,
    client: AuthenticatedClient | Client,
    body: SmoWebHandlersGraphDeployJsonBody,
) -> Any | Problem | None:
    """Deploy a new HDAG

     Deploys a Hyper Distributed Application Graph from a descriptor.

    Args:
        project (str):
        body (SmoWebHandlersGraphDeployJsonBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, Problem]
    """

    return sync_detailed(
        project=project,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    project: str,
    *,
    client: AuthenticatedClient | Client,
    body: SmoWebHandlersGraphDeployJsonBody,
) -> Response[Any | Problem]:
    """Deploy a new HDAG

     Deploys a Hyper Distributed Application Graph from a descriptor.

    Args:
        project (str):
        body (SmoWebHandlersGraphDeployJsonBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, Problem]]
    """

    kwargs = _get_kwargs(
        project=project,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    project: str,
    *,
    client: AuthenticatedClient | Client,
    body: SmoWebHandlersGraphDeployJsonBody,
) -> Any | Problem | None:
    """Deploy a new HDAG

     Deploys a Hyper Distributed Application Graph from a descriptor.

    Args:
        project (str):
        body (SmoWebHandlersGraphDeployJsonBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, Problem]
    """

    return (
        await asyncio_detailed(
            project=project,
            client=client,
            body=body,
        )
    ).parsed
