import { useTable } from "@refinedev/core";
import { Plus } from "lucide-react";
import { Link } from "react-router";

import type { UserPublic } from "@/client";
import { RecordActions } from "@/components/refine-ui/resource/record-actions";
import { ResourcePage } from "@/components/refine-ui/resource/resource-page";
import {
  ResourceTable,
  TablePagination,
  type ResourceColumn,
} from "@/components/refine-ui/resource/resource-table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

function BooleanBadge({ value }: { value?: boolean }) {
  return (
    <Badge variant={value ? "default" : "secondary"}>
      {value ? "Yes" : "No"}
    </Badge>
  );
}

export const UserList = () => {
  const table = useTable<UserPublic>({
    resource: "users",
    syncWithLocation: true,
  });

  const columns: ResourceColumn<UserPublic>[] = [
    { key: "email", header: "Email", render: (user) => user.email },
    {
      key: "full_name",
      header: "Full name",
      render: (user) => user.full_name ?? "-",
    },
    {
      key: "is_active",
      header: "Active",
      render: (user) => <BooleanBadge value={user.is_active} />,
    },
    {
      key: "is_superuser",
      header: "Superuser",
      render: (user) => <BooleanBadge value={user.is_superuser} />,
    },
    { key: "id", header: "Id", render: (user) => user.id },
    {
      key: "actions",
      header: <span className="sr-only">Actions</span>,
      className: "w-36 text-right",
      render: (user) => (
        <RecordActions
          resource="users"
          id={user.id}
          onDeleted={() => table.tableQuery.refetch()}
        />
      ),
    },
  ];

  return (
    <ResourcePage
      title="Users"
      description="Administrative user management."
      actions={
        <Button asChild>
          <Link to="/users/create">
            <Plus className="size-4" />
            New user
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
