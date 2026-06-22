import React from "react";
import { DownloadOutlined } from "@ant-design/icons";
import { Show, TextField } from "@refinedev/antd";
import { App as AntdApp, Button, Space, Typography } from "antd";
import { useShow } from "@refinedev/core";
import type { AssetPresignedDownloadResponse, AssetPublic } from "@/client";
import { apiClient } from "@/providers/data";
import { formatBytes, formatDateTime } from "@/pages/assets/utils";

const { Title } = Typography;

export const AssetShow = () => {
  const { message } = AntdApp.useApp();
  const {
    result: record,
    query: { isLoading },
  } = useShow<AssetPublic>();

  const handleDownload = React.useCallback(async () => {
    if (!record?.id) return;

    try {
      const { data } =
        await apiClient.get<AssetPresignedDownloadResponse>(
          `/assets/${record.id}/download-url`,
        );
      window.open(data.download_url, "_blank", "noopener,noreferrer");
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : "Failed to create download URL";
      message.error(errorMessage);
    }
  }, [message, record?.id]);

  return (
    <Show
      isLoading={isLoading}
      headerButtons={({ defaultButtons }) => (
        <Space>
          {defaultButtons}
          <Button icon={<DownloadOutlined />} onClick={handleDownload}>
            Download
          </Button>
        </Space>
      )}
    >
      <Title level={5}>File</Title>
      <TextField value={record?.file_name} />
      <Title level={5}>Content Type</Title>
      <TextField value={record?.content_type} />
      <Title level={5}>Size</Title>
      <TextField value={record ? formatBytes(record.size) : undefined} />
      <Title level={5}>Created</Title>
      <TextField value={formatDateTime(record?.created_at)} />
      <Title level={5}>Object Key</Title>
      <TextField value={record?.object_key} />
      <Title level={5}>Owner Id</Title>
      <TextField value={record?.owner_id} />
      <Title level={5}>Id</Title>
      <TextField value={record?.id} />
    </Show>
  );
};
