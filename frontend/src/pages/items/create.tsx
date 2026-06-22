import { type HttpError, useCreate, useNavigation } from "@refinedev/core";
import type { FormEvent } from "react";

import type { ItemCreate as ItemCreateInput, ItemPublic } from "@/client";
import {
  FormActions,
  FormGrid,
  ResourceCard,
  ResourcePage,
} from "@/components/refine-ui/resource/resource-page";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";

export const ItemCreate = () => {
  const { list } = useNavigation();
  const { mutate, mutation } = useCreate<ItemPublic, HttpError, ItemCreateInput>();

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);

    mutate(
      {
        resource: "items",
        values: {
          title: String(formData.get("title") ?? ""),
          description: String(formData.get("description") ?? "") || null,
        },
      },
      {
        onSuccess: () => list("items"),
      },
    );
  };

  return (
    <ResourcePage title="Create item">
      <ResourceCard title="Item details">
        <form onSubmit={handleSubmit}>
          <FormGrid>
            <div className="grid gap-2">
              <Label htmlFor="title">Title</Label>
              <Input id="title" name="title" required maxLength={255} />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="description">Description</Label>
              <Textarea id="description" name="description" maxLength={255} />
            </div>
            <FormActions
              submitLabel="Create item"
              isSubmitting={mutation.isPending}
              onCancel={() => list("items")}
            />
          </FormGrid>
        </form>
      </ResourceCard>
    </ResourcePage>
  );
};
