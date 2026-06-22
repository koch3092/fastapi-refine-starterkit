import React from "react";
import { usePermissions } from "@refinedev/core";
import { Create, useForm, useSelect } from "@refinedev/antd";
import { Form, Input, Select } from "antd";
import type { Owner } from "@/pages/items/types";

export const ItemCreate = () => {
  const { data: permissions } = usePermissions({});
  const isAdmin =
    Array.isArray(permissions) && permissions.includes("admin");
  const { formProps, saveButtonProps } = useForm();

  const { selectProps: ownerSelectProps } = useSelect<Owner>({
    resource: "owners",
    optionLabel: (owner) => owner.full_name ?? owner.email,
    searchField: "email",
    queryOptions: {
      enabled: isAdmin,
    },
  });

  return (
    <Create saveButtonProps={saveButtonProps}>
      <Form {...formProps} layout="vertical">
        <Form.Item
          label="Title"
          name={"title"}
          rules={[
            {
              required: true,
            },
          ]}
        >
          <Input />
        </Form.Item>
        <Form.Item
          label="Description"
          name={"description"}
          rules={[
            {
              required: true,
            },
          ]}
        >
          <Input />
        </Form.Item>
        {isAdmin && (
          <Form.Item
            label="Owner"
            name={"owner_id"}
            rules={[
              {
                required: true,
              },
            ]}
          >
            <Select {...ownerSelectProps} />
          </Form.Item>
        )}
      </Form>
    </Create>
  );
};
