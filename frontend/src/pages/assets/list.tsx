import React from "react";
import { DownloadOutlined } from "@ant-design/icons";
import { BaseRecord } from "@refinedev/core";
import { DeleteButton, List, ShowButton, useTable } from "@refinedev/antd";
import { App as AntdApp, Button, Space, Table } from "antd";
import type { AssetPresignedDownloadResponse, AssetPublic } from "@/client";
import { apiClient } from "@/providers/data";
import { formatBytes, formatDateTime } from "@/pages/assets/utils";

export const AssetList = () => {
  const { message } = AntdApp.useApp();
  const { tableProps } = useTable<AssetPublic>({
    syncWithLocation: true,
    sorters: {
      initial: [{ field: "created_at", order: "desc" }],
    },
  });

  const handleDownload = React.useCallback(
    async (asset: AssetPublic) => {
      try {
        const { data } =
          await apiClient.get<AssetPresignedDownloadResponse>(
            `/assets/${asset.id}/download-url`,
          );
        window.open(data.download_url, "_blank", "noopener,noreferrer");
      } catch (error) {
        const errorMessage =
          error instanceof Error ? error.message : "Failed to create download URL";
        message.error(errorMessage);
      }
    },
    [message],
  );

  return (
    <List>
      <Table {...tableProps} rowKey="id">
        <Table.Column<AssetPublic> dataIndex="file_name" title="File" />
        <Table.Column<AssetPublic>
          dataIndex="content_type"
          title="Content Type"
        />
        <Table.Column<AssetPublic>
          dataIndex="size"
          title="Size"
          render={(value: number) => formatBytes(value)}
        />
        <Table.Column<AssetPublic>
          dataIndex="created_at"
          title="Created"
          render={(value: string) => formatDateTime(value)}
        />
        <Table.Column<AssetPublic> dataIndex="owner_id" title="Owner Id" />
        <Table.Column<AssetPublic>
          title="Actions"
          dataIndex="actions"
          render={(_, record: BaseRecord) => (
            <Space>
              <Button
                aria-label="Download"
                icon={<DownloadOutlined />}
                size="small"
                onClick={() => handleDownload(record as AssetPublic)}
              />
              <ShowButton hideText size="small" recordItemId={record.id} />
              <DeleteButton hideText size="small" recordItemId={record.id} />
            </Space>
          )}
        />
      </Table>
    </List>
  );
};
