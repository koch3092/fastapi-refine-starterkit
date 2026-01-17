import React from "react";
import { useGetIdentity, useOne, usePermissions, useShow } from "@refinedev/core";
import { Show, TextField } from "@refinedev/antd";
import { Typography } from "antd";
import type { Owner } from "@/pages/items/types";

const { Title } = Typography;

export const ItemShow = () => {
  const { data: permissions } = usePermissions({});
  const isAdmin =
    Array.isArray(permissions) && permissions.includes("admin");
  const { data: me } = useGetIdentity<{ name?: string; email?: string }>();

  const {
    result: record,
    query: { isLoading },
  } = useShow();

  const {
    result: ownerData,
    query: { isLoading: ownerIsLoading },
  } = useOne<Owner>({
    resource: "owners",
    id: record?.owner_id || "",
    queryOptions: {
      enabled: isAdmin && !!record?.owner_id,
    },
  });

  const ownerLabel = isAdmin
    ? ownerData?.full_name ?? ownerData?.email ?? record?.owner_id ?? "-"
    : me?.name ?? me?.email ?? "You";

  return (
    <Show isLoading={isLoading}>
      <Title level={5}>Title</Title>
      <TextField value={record?.title} />
      <Title level={5}>Description</Title>
      <TextField value={record?.description} />
      <Title level={5}>Id</Title>
      <TextField value={record?.id} />
      <Title level={5}>Owner</Title>
      {isAdmin && ownerIsLoading ? (
        <>Loading...</>
      ) : (
        <TextField value={ownerLabel} />
      )}
    </Show>
  );
};
