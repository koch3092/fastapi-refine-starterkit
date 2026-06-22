import React from "react";
import { usePermissions } from "@refinedev/core";
import { Edit, useForm, useSelect } from "@refinedev/antd";
import { Form, Input, Select } from "antd";
import type { Owner } from "@/pages/items/types";

export const ItemEdit = () => {
  const { data: permissions } = usePermissions({});
  const isAdmin =
    Array.isArray(permissions) && permissions.includes("admin");
  const { formProps, saveButtonProps, query } = useForm();

  const itemsData = query?.data?.data;

  const { selectProps: ownerSelectProps } = useSelect<Owner>({
    resource: "owners",
    defaultValue: itemsData?.owner_id,
    optionLabel: (owner) => owner.full_name ?? owner.email,
    searchField: "email",
    queryOptions: {
      enabled: isAdmin,
    },
  });

  return (
    <Edit saveButtonProps={saveButtonProps}>
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
        <Form.Item
          label="Id"
          name={"id"}
          rules={[
            {
              required: true,
            },
          ]}
        >
          <Input readOnly disabled />
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
    </Edit>
  );
};
