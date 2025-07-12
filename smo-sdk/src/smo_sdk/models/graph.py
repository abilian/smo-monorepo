from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.graph_services_item import GraphServicesItem


T = TypeVar("T", bound="Graph")


@_attrs_define
class Graph:
    """
    Attributes:
        name (Union[Unset, str]):
        project (Union[Unset, str]):
        status (Union[Unset, str]):
        services (Union[Unset, list['GraphServicesItem']]):
    """

    name: Unset | str = UNSET
    project: Unset | str = UNSET
    status: Unset | str = UNSET
    services: Unset | list["GraphServicesItem"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        project = self.project

        status = self.status

        services: Unset | list[dict[str, Any]] = UNSET
        if not isinstance(self.services, Unset):
            services = []
            for services_item_data in self.services:
                services_item = services_item_data.to_dict()
                services.append(services_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if project is not UNSET:
            field_dict["project"] = project
        if status is not UNSET:
            field_dict["status"] = status
        if services is not UNSET:
            field_dict["services"] = services

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.graph_services_item import GraphServicesItem

        d = dict(src_dict)
        name = d.pop("name", UNSET)

        project = d.pop("project", UNSET)

        status = d.pop("status", UNSET)

        services = []
        _services = d.pop("services", UNSET)
        for services_item_data in _services or []:
            services_item = GraphServicesItem.from_dict(services_item_data)

            services.append(services_item)

        graph = cls(
            name=name,
            project=project,
            status=status,
            services=services,
        )

        graph.additional_properties = d
        return graph

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
