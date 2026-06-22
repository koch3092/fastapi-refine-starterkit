import {
  useGetIdentity,
  useOne,
  useParsed,
  usePermissions,
} from "@refinedev/core";

import type { ItemPublic } from "@/client";
import {
  Field,
  LoadingFields,
  ResourceCard,
  ResourcePage,
} from "@/components/refine-ui/resource/resource-page";
import type { Owner } from "@/pages/items/types";

export const ItemShow = () => {
  const { id } = useParsed<{ id: string }>();
  const { data: permissions } = usePermissions({});
  const isAdmin =
    Array.isArray(permissions) && permissions.includes("admin");
  const { data: me } = useGetIdentity<{ name?: string; email?: string }>();

  const {
    result: item,
    query: { isLoading },
  } = useOne<ItemPublic>({
    resource: "items",
    id,
    queryOptions: { enabled: Boolean(id) },
  });

  const {
    result: owner,
    query: { isLoading: ownerIsLoading },
  } = useOne<Owner>({
    resource: "owners",
    id: item?.owner_id,
    queryOptions: {
      enabled: isAdmin && Boolean(item?.owner_id),
    },
  });

  const ownerLabel = isAdmin
    ? owner?.full_name ?? owner?.email ?? item?.owner_id ?? "-"
    : me?.name ?? me?.email ?? "You";

  return (
    <ResourcePage title="Item details">
      <ResourceCard title={item?.title ?? "Item"}>
        {isLoading ? (
          <LoadingFields count={4} />
        ) : (
          <dl className="grid gap-5 sm:grid-cols-2">
            <Field label="Title" value={item?.title} />
            <Field label="Description" value={item?.description} />
            <Field label="Id" value={item?.id} />
            <Field
              label="Owner"
              value={isAdmin && ownerIsLoading ? "Loading..." : ownerLabel}
            />
          </dl>
        )}
      </ResourceCard>
    </ResourcePage>
  );
};
