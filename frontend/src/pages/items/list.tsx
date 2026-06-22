import React from "react";
import {
  BaseKey,
  BaseRecord,
  useGetIdentity,
  useMany,
  usePermissions,
} from "@refinedev/core";
import {
  useTable,
  List,
  EditButton,
  ShowButton,
  DeleteButton,
} from "@refinedev/antd";
import { Table, Space } from "antd";
import type { Owner } from "@/pages/items/types";

export const ItemList = () => {
  const { data: permissions } = usePermissions({});
  const isAdmin =
    Array.isArray(permissions) && permissions.includes("admin");
  const { data: me } = useGetIdentity<{ name?: string; email?: string }>();

  const { tableProps } = useTable({
    syncWithLocation: true,
  });

  const ownerIds = React.useMemo(() => {
    const ids =
      tableProps?.dataSource
        ?.map((item) => item?.owner_id)
        .filter((id): id is BaseKey => Boolean(id)) ?? [];

    return Array.from(new Set(ids));
  }, [tableProps?.dataSource]);

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

  return (
    <List>
      <Table {...tableProps} rowKey="id">
        <Table.Column dataIndex="id" title="Id" />
        <Table.Column dataIndex="title" title="Title" />
        <Table.Column dataIndex="description" title="Description" />
        <Table.Column
          dataIndex={"owner_id"}
          title="Owner"
          render={(value) => {
            if (!isAdmin) return me?.name ?? me?.email ?? "You";
            if (ownerIsLoading) return <>Loading...</>;
            const owner = ownersById.get(value);
            return owner?.full_name ?? owner?.email ?? value ?? "-";
          }}
        />
        <Table.Column
          title="Actions"
          dataIndex="actions"
          render={(_, record: BaseRecord) => (
            <Space>
              <EditButton hideText size="small" recordItemId={record.id} />
              <ShowButton hideText size="small" recordItemId={record.id} />
              <DeleteButton hideText size="small" recordItemId={record.id} />
            </Space>
          )}
        />
      </Table>
    </List>
  );
};
