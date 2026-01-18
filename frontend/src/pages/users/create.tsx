import React from "react";
import { Create, useForm } from "@refinedev/antd";
import { Form, Input, Checkbox } from "antd";

export const UserCreate = () => {
    const { formProps, saveButtonProps, query } = useForm();

    return (
        <Create saveButtonProps={saveButtonProps}>
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
                    label="Password"
                    name={["password"]}
                    rules={[
                        {
                            required: true,
                        },
                    ]}
                >
                    <Input.Password placeholder="input password"  />
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
                            required: false,
                        },
                    ]}
                >
                    <Checkbox>Is Superuser</Checkbox>
                </Form.Item>
            </Form>
        </Create>
    );
};
