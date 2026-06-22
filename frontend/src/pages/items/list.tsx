import { Link } from "react-router";
import {
  useGetIdentity,
  useMany,
  usePermissions,
  useTable,
} from "@refinedev/core";
import { Plus } from "lucide-react";
import * as React from "react";

import type { ItemPublic } from "@/client";
import { RecordActions } from "@/components/refine-ui/resource/record-actions";
import {
  ResourceTable,
  TablePagination,
  type ResourceColumn,
} from "@/components/refine-ui/resource/resource-table";
import { ResourcePage } from "@/components/refine-ui/resource/resource-page";
import { Button } from "@/components/ui/button";
import type { Owner } from "@/pages/items/types";

export const ItemList = () => {
  const { data: permissions } = usePermissions({});
  const isAdmin =
    Array.isArray(permissions) && permissions.includes("admin");
  const { data: me } = useGetIdentity<{ name?: string; email?: string }>();

  const table = useTable<ItemPublic>({
    resource: "items",
    syncWithLocation: true,
  });

  const ownerIds = React.useMemo(() => {
    const ids =
      table.result.data
        ?.map((item) => item.owner_id)
        .filter((id): id is string => Boolean(id)) ?? [];

    return Array.from(new Set(ids));
  }, [table.result.data]);

  const {
    result: ownerData,
    query: { isLoading: ownerIsLoading },
  } = useMany<Owner>({
    resource: "owners",
    ids: ownerIds,
    queryOptions: {
      enabled: isAdmin && ownerIds.length > 0,
    },
  });

  const ownersById = React.useMemo(() => {
    return new Map(ownerData?.data?.map((owner) => [owner.id, owner]) ?? []);
  }, [ownerData?.data]);

  const columns: ResourceColumn<ItemPublic>[] = [
    { key: "title", header: "Title", render: (item) => item.title },
    {
      key: "description",
      header: "Description",
      render: (item) => item.description ?? "-",
    },
    {
      key: "owner",
      header: "Owner",
      render: (item) => {
        if (!isAdmin) return me?.name ?? me?.email ?? "You";
        if (ownerIsLoading) return "Loading...";
        const owner = ownersById.get(item.owner_id);
        return owner?.full_name ?? owner?.email ?? item.owner_id ?? "-";
      },
    },
    { key: "id", header: "Id", render: (item) => item.id },
    {
      key: "actions",
      header: <span className="sr-only">Actions</span>,
      className: "w-36 text-right",
      render: (item) => (
        <RecordActions
          resource="items"
          id={item.id}
          onDeleted={() => table.tableQuery.refetch()}
        />
      ),
    },
  ];

  return (
    <ResourcePage
      title="Items"
      description="Baseline CRUD resource for project-specific data models."
      actions={
        <Button asChild>
          <Link to="/items/create">
            <Plus className="size-4" />
            New item
          </Link>
        </Button>
      }
    >
      <ResourceTable
        columns={columns}
        data={table.result.data}
        isLoading={table.tableQuery.isLoading}
      />
      <TablePagination
        currentPage={table.currentPage}
        pageCount={table.pageCount}
        total={table.result.total}
        onPageChange={table.setCurrentPage}
      />
    </ResourcePage>
  );
};
