import {
  type HttpError,
  useNavigation,
  useOne,
  useParsed,
  useUpdate,
} from "@refinedev/core";
import type { FormEvent } from "react";
import * as React from "react";

import type { ItemPublic, ItemUpdate as ItemUpdateInput } from "@/client";
import {
  FormActions,
  FormGrid,
  LoadingFields,
  ResourceCard,
  ResourcePage,
} from "@/components/refine-ui/resource/resource-page";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";

export const ItemEdit = () => {
  const { id } = useParsed<{ id: string }>();
  const { list } = useNavigation();
  const { mutate, mutation } = useUpdate<ItemPublic, HttpError, ItemUpdateInput>();
  const {
    result: item,
    query: { isLoading },
  } = useOne<ItemPublic>({
    resource: "items",
    id,
    queryOptions: { enabled: Boolean(id) },
  });

  const [title, setTitle] = React.useState("");
  const [description, setDescription] = React.useState("");

  React.useEffect(() => {
    if (item) {
      setTitle(item.title);
      setDescription(item.description ?? "");
    }
  }, [item]);

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!id) return;

    mutate(
      {
        resource: "items",
        id,
        values: {
          title,
          description: description || null,
        },
      },
      {
        onSuccess: () => list("items"),
      },
    );
  };

  return (
    <ResourcePage title="Edit item">
      <ResourceCard title="Item details">
        {isLoading ? (
          <LoadingFields count={3} />
        ) : (
          <form onSubmit={handleSubmit}>
            <FormGrid>
              <div className="grid gap-2">
                <Label htmlFor="title">Title</Label>
                <Input
                  id="title"
                  name="title"
                  required
                  maxLength={255}
                  value={title}
                  onChange={(event) => setTitle(event.target.value)}
                />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="description">Description</Label>
                <Textarea
                  id="description"
                  name="description"
                  maxLength={255}
                  value={description}
                  onChange={(event) => setDescription(event.target.value)}
                />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="id">Id</Label>
                <Input id="id" value={item?.id ?? ""} readOnly disabled />
              </div>
              <FormActions
                submitLabel="Save changes"
                isSubmitting={mutation.isPending}
                onCancel={() => list("items")}
              />
            </FormGrid>
          </form>
        )}
      </ResourceCard>
    </ResourcePage>
  );
};
