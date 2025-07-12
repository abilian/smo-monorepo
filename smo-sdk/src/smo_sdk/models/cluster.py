from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Cluster")


@_attrs_define
class Cluster:
    """
    Attributes:
        name (Union[Unset, str]):
        available_cpu (Union[Unset, float]):
        available_ram (Union[Unset, str]):
        availability (Union[Unset, bool]):
    """

    name: Union[Unset, str] = UNSET
    available_cpu: Union[Unset, float] = UNSET
    available_ram: Union[Unset, str] = UNSET
    availability: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        available_cpu = self.available_cpu

        available_ram = self.available_ram

        availability = self.availability

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if available_cpu is not UNSET:
            field_dict["available_cpu"] = available_cpu
        if available_ram is not UNSET:
            field_dict["available_ram"] = available_ram
        if availability is not UNSET:
            field_dict["availability"] = availability

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name", UNSET)

        available_cpu = d.pop("available_cpu", UNSET)

        available_ram = d.pop("available_ram", UNSET)

        availability = d.pop("availability", UNSET)

        cluster = cls(
            name=name,
            available_cpu=available_cpu,
            available_ram=available_ram,
            availability=availability,
        )

        cluster.additional_properties = d
        return cluster

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
