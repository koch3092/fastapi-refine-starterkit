import {
  type HttpError,
  useNavigation,
  useOne,
  useParsed,
  useUpdate,
} from "@refinedev/core";
import type { FormEvent } from "react";
import * as React from "react";

import type { UserPublic, UserUpdate as UserUpdateInput } from "@/client";
import {
  FormActions,
  FormGrid,
  LoadingFields,
  ResourceCard,
  ResourcePage,
} from "@/components/refine-ui/resource/resource-page";
import { Checkbox } from "@/components/ui/checkbox";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export const UserEdit = () => {
  const { id } = useParsed<{ id: string }>();
  const { list } = useNavigation();
  const { mutate, mutation } = useUpdate<UserPublic, HttpError, UserUpdateInput>();
  const {
    result: user,
    query: { isLoading },
  } = useOne<UserPublic>({
    resource: "users",
    id,
    queryOptions: { enabled: Boolean(id) },
  });

  const [email, setEmail] = React.useState("");
  const [fullName, setFullName] = React.useState("");
  const [isActive, setIsActive] = React.useState(true);
  const [isSuperuser, setIsSuperuser] = React.useState(false);

  React.useEffect(() => {
    if (user) {
      setEmail(user.email);
      setFullName(user.full_name ?? "");
      setIsActive(user.is_active ?? false);
      setIsSuperuser(user.is_superuser ?? false);
    }
  }, [user]);

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!id) return;

    mutate(
      {
        resource: "users",
        id,
        values: {
          email,
          full_name: fullName || null,
          is_active: isActive,
          is_superuser: isSuperuser,
        },
      },
      {
        onSuccess: () => list("users"),
      },
    );
  };

  return (
    <ResourcePage title="Edit user">
      <ResourceCard title="User details">
        {isLoading ? (
          <LoadingFields count={5} />
        ) : (
          <form onSubmit={handleSubmit}>
            <FormGrid>
              <div className="grid gap-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  required
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="full_name">Full name</Label>
                <Input
                  id="full_name"
                  maxLength={255}
                  value={fullName}
                  onChange={(event) => setFullName(event.target.value)}
                />
              </div>
              <div className="flex items-center gap-2">
                <Checkbox
                  id="is_active"
                  checked={isActive}
                  onCheckedChange={(checked) => setIsActive(checked === true)}
                />
                <Label htmlFor="is_active">Active</Label>
              </div>
              <div className="flex items-center gap-2">
                <Checkbox
                  id="is_superuser"
                  checked={isSuperuser}
                  onCheckedChange={(checked) =>
                    setIsSuperuser(checked === true)
                  }
                />
                <Label htmlFor="is_superuser">Superuser</Label>
              </div>
              <div className="grid gap-2">
                <Label htmlFor="id">Id</Label>
                <Input id="id" value={user?.id ?? ""} readOnly disabled />
              </div>
              <FormActions
                submitLabel="Save changes"
                isSubmitting={mutation.isPending}
                onCancel={() => list("users")}
              />
            </FormGrid>
          </form>
        )}
      </ResourceCard>
    </ResourcePage>
  );
};
