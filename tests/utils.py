from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from odata.query import QuerySpec


def build_query_params(spec: "QuerySpec") -> dict:
    params = {}

    if spec.select:
        params["$select"] = ",".join(spec.select)

    if spec.expand:
        params["$expand"] = ",".join(spec.expand)

    if spec.filter:
        params["$filter"] = spec.filter

    if spec.orderby:
        params["$orderby"] = ",".join(spec.orderby)

    if spec.top is not None:
        params["$top"] = str(spec.top)

    if spec.skip is not None:
        params["$skip"] = str(spec.skip)

    if spec.count:
        params["$count"] = "true"

    return params