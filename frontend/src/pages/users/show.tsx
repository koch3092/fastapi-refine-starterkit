import React from "react";
import { useShow } from "@refinedev/core";
import {
    Show,
    TagField,
    EmailField,
    BooleanField,
    TextField,
} from "@refinedev/antd";
import { Typography } from "antd";

const { Title } = Typography;

export const UserShow = () => {
    const {
        result: record,
        query: { isLoading },
    } = useShow();

    return (
        <Show isLoading={isLoading}>
            <Title level={5}>Email</Title>
            <EmailField value={record?.email} />
            <Title level={5}>Is Active</Title>
            <BooleanField value={record?.is_active} />
            <Title level={5}>Is Superuser</Title>
            <BooleanField value={record?.is_superuser} />
            <Title level={5}>Id</Title>
            <TextField value={record?.id} />
        </Show>
    );
};
