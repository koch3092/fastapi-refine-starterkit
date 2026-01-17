from fastapi import Depends
from fastapi_refine import FilterConfig, PaginationConfig, SortConfig, refine_query
from sqlmodel import SQLModel

DEFAULT_PAGINATION_CONFIG = PaginationConfig(
    default_skip=0,
    default_limit=10,
    max_limit=100,
)


def refine_query_dep(
    model: type[SQLModel],
    filter_config: FilterConfig,
    sort_config: SortConfig,
    pagination_config: PaginationConfig | None = None,
) -> Depends:
    """Build a dependency for Refine query parsing.

    Args:
        model: Model used to build the query.
        filter_config: Filter configuration for the resource.
        sort_config: Sort configuration for the resource.
        pagination_config: Optional override for pagination configuration.

    Returns:
        FastAPI dependency that yields parsed Refine query data.
    """
    if pagination_config is None:
        pagination_config = DEFAULT_PAGINATION_CONFIG
    return Depends(refine_query(model, filter_config, sort_config, pagination_config))
