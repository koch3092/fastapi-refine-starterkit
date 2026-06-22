import { useTable } from "@refinedev/core";
import { Plus } from "lucide-react";
import { Link } from "react-router";
import { toast } from "sonner";

import type { AssetPresignedDownloadResponse, AssetPublic } from "@/client";
import {
  DownloadButton,
  RecordActions,
} from "@/components/refine-ui/resource/record-actions";
import { ResourcePage } from "@/components/refine-ui/resource/resource-page";
import {
  ResourceTable,
  TablePagination,
  type ResourceColumn,
} from "@/components/refine-ui/resource/resource-table";
import { Button } from "@/components/ui/button";
import { apiClient } from "@/providers/data";
import { formatBytes, formatDateTime } from "@/pages/assets/utils";

export const AssetList = () => {
  const table = useTable<AssetPublic>({
    resource: "assets",
    syncWithLocation: true,
    sorters: {
      initial: [{ field: "created_at", order: "desc" }],
    },
  });

  const handleDownload = async (asset: AssetPublic) => {
    try {
      const { data } =
        await apiClient.get<AssetPresignedDownloadResponse>(
          `/assets/${asset.id}/download-url`,
        );
      window.open(data.download_url, "_blank", "noopener,noreferrer");
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : "Failed to create download URL";
      toast.error(errorMessage);
    }
  };

  const columns: ResourceColumn<AssetPublic>[] = [
    { key: "file_name", header: "File", render: (asset) => asset.file_name },
    {
      key: "content_type",
      header: "Content type",
      render: (asset) => asset.content_type,
    },
    {
      key: "size",
      header: "Size",
      render: (asset) => formatBytes(asset.size),
    },
    {
      key: "created_at",
      header: "Created",
      render: (asset) => formatDateTime(asset.created_at),
    },
    { key: "owner_id", header: "Owner Id", render: (asset) => asset.owner_id },
    {
      key: "actions",
      header: <span className="sr-only">Actions</span>,
      className: "w-36 text-right",
      render: (asset) => (
        <RecordActions
          resource="assets"
          id={asset.id}
          canEdit={false}
          extra={<DownloadButton onClick={() => handleDownload(asset)} />}
          onDeleted={() => table.tableQuery.refetch()}
        />
      ),
    },
  ];

  return (
    <ResourcePage
      title="Assets"
      description="S3/MinIO-backed file metadata with presigned upload/download URLs."
      actions={
        <Button asChild>
          <Link to="/assets/create">
            <Plus className="size-4" />
            Upload asset
          </Link>
        </Button>
      }
    >
      <ResourceTable
        columns={columns}
        data={table.result.data}
        isLoading={table.tableQuery.isLoading}
      />
      <TablePagination
        currentPage={table.currentPage}
        pageCount={table.pageCount}
        total={table.result.total}
        onPageChange={table.setCurrentPage}
      />
    </ResourcePage>
  );
};
