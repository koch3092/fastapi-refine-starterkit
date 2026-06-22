import { type HttpError, useCreate, useNavigation } from "@refinedev/core";
import type { FormEvent } from "react";
import * as React from "react";

import type { UserCreate as UserCreateInput, UserPublic } from "@/client";
import {
  FormActions,
  FormGrid,
  ResourceCard,
  ResourcePage,
} from "@/components/refine-ui/resource/resource-page";
import { Checkbox } from "@/components/ui/checkbox";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export const UserCreate = () => {
  const { list } = useNavigation();
  const { mutate, mutation } = useCreate<UserPublic, HttpError, UserCreateInput>();
  const [isActive, setIsActive] = React.useState(true);
  const [isSuperuser, setIsSuperuser] = React.useState(false);

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);

    mutate(
      {
        resource: "users",
        values: {
          email: String(formData.get("email") ?? ""),
          full_name: String(formData.get("full_name") ?? "") || null,
          password: String(formData.get("password") ?? ""),
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
    <ResourcePage title="Create user">
      <ResourceCard title="User details">
        <form onSubmit={handleSubmit}>
          <FormGrid>
            <div className="grid gap-2">
              <Label htmlFor="email">Email</Label>
              <Input id="email" name="email" type="email" required />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="full_name">Full name</Label>
              <Input id="full_name" name="full_name" maxLength={255} />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                name="password"
                type="password"
                required
                minLength={8}
                maxLength={128}
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
                onCheckedChange={(checked) => setIsSuperuser(checked === true)}
              />
              <Label htmlFor="is_superuser">Superuser</Label>
            </div>
            <FormActions
              submitLabel="Create user"
              isSubmitting={mutation.isPending}
              onCancel={() => list("users")}
            />
          </FormGrid>
        </form>
      </ResourceCard>
    </ResourcePage>
  );
};
