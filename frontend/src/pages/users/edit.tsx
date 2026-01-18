import React from "react";
import { Edit, useForm } from "@refinedev/antd";
import { Form, Input, Checkbox } from "antd";

export const UserEdit = () => {
    const { formProps, saveButtonProps, query } = useForm();

    const usersData = query?.data?.data;

    return (
        <Edit saveButtonProps={saveButtonProps}>
            <Form {...formProps} layout="vertical">
                <Form.Item
                    label="Email"
                    name={["email"]}
                    rules={[
                        {
                            required: true,
                        },
                    ]}
                >
                    <Input />
                </Form.Item>
                <Form.Item
                    label="Is Active"
                    valuePropName="checked"
                    name={["is_active"]}
                    rules={[
                        {
                            required: true,
                        },
                    ]}
                >
                    <Checkbox>Is Active</Checkbox>
                </Form.Item>
                <Form.Item
                    label="Is Superuser"
                    valuePropName="checked"
                    name={["is_superuser"]}
                    rules={[
                        {
                            required: true,
                        },
                    ]}
                >
                    <Checkbox>Is Superuser</Checkbox>
                </Form.Item>
                <Form.Item
                    label="Id"
                    name={["id"]}
                    rules={[
                        {
                            required: true,
                        },
                    ]}
                >
                    <Input readOnly disabled />
                </Form.Item>
            </Form>
        </Edit>
    );
};
