import { useOne, useParsed } from "@refinedev/core";
import { toast } from "sonner";

import type { AssetPresignedDownloadResponse, AssetPublic } from "@/client";
import { DownloadButton } from "@/components/refine-ui/resource/record-actions";
import {
  Field,
  LoadingFields,
  ResourceCard,
  ResourcePage,
} from "@/components/refine-ui/resource/resource-page";
import { apiClient } from "@/providers/data";
import { formatBytes, formatDateTime } from "@/pages/assets/utils";

export const AssetShow = () => {
  const { id } = useParsed<{ id: string }>();
  const {
    result: asset,
    query: { isLoading },
  } = useOne<AssetPublic>({
    resource: "assets",
    id,
    queryOptions: { enabled: Boolean(id) },
  });

  const handleDownload = async () => {
    if (!asset?.id) return;

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

  return (
    <ResourcePage
      title="Asset details"
      actions={<DownloadButton onClick={handleDownload} />}
    >
      <ResourceCard title={asset?.file_name ?? "Asset"}>
        {isLoading ? (
          <LoadingFields count={7} />
        ) : (
          <dl className="grid gap-5 sm:grid-cols-2">
            <Field label="File" value={asset?.file_name} />
            <Field label="Content type" value={asset?.content_type} />
            <Field
              label="Size"
              value={asset ? formatBytes(asset.size) : undefined}
            />
            <Field label="Created" value={formatDateTime(asset?.created_at)} />
            <Field label="Object key" value={asset?.object_key} />
            <Field label="Owner Id" value={asset?.owner_id} />
            <Field label="Id" value={asset?.id} />
          </dl>
        )}
      </ResourceCard>
    </ResourcePage>
  );
};
