import { useOne, useParsed } from "@refinedev/core";

import type { UserPublic } from "@/client";
import {
  Field,
  LoadingFields,
  ResourceCard,
  ResourcePage,
} from "@/components/refine-ui/resource/resource-page";
import { Badge } from "@/components/ui/badge";

function BooleanBadge({ value }: { value?: boolean }) {
  return (
    <Badge variant={value ? "default" : "secondary"}>
      {value ? "Yes" : "No"}
    </Badge>
  );
}

export const UserShow = () => {
  const { id } = useParsed<{ id: string }>();
  const {
    result: user,
    query: { isLoading },
  } = useOne<UserPublic>({
    resource: "users",
    id,
    queryOptions: { enabled: Boolean(id) },
  });

  return (
    <ResourcePage title="User details">
      <ResourceCard title={user?.email ?? "User"}>
        {isLoading ? (
          <LoadingFields count={5} />
        ) : (
          <dl className="grid gap-5 sm:grid-cols-2">
            <Field label="Email" value={user?.email} />
            <Field label="Full name" value={user?.full_name} />
            <Field label="Active" value={<BooleanBadge value={user?.is_active} />} />
            <Field
              label="Superuser"
              value={<BooleanBadge value={user?.is_superuser} />}
            />
            <Field label="Id" value={user?.id} />
          </dl>
        )}
      </ResourceCard>
    </ResourcePage>
  );
};
