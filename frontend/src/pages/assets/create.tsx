import { useNavigation } from "@refinedev/core";
import type { FormEvent } from "react";
import * as React from "react";
import { toast } from "sonner";

import type {
  AssetPresignedUploadRequest,
  AssetPresignedUploadResponse,
} from "@/client";
import {
  FormActions,
  FormGrid,
  ResourceCard,
  ResourcePage,
} from "@/components/refine-ui/resource/resource-page";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { apiClient } from "@/providers/data";

export const AssetCreate = () => {
  const { list } = useNavigation();
  const [file, setFile] = React.useState<File | null>(null);
  const [fileName, setFileName] = React.useState("");
  const [isUploading, setIsUploading] = React.useState(false);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (!file) {
      toast.error("Select a file first");
      return;
    }

    const payload: AssetPresignedUploadRequest = {
      file_name: fileName.trim() || file.name,
      content_type: file.type || "application/octet-stream",
      size: file.size,
    };

    setIsUploading(true);
    try {
      const { data } = await apiClient.post<AssetPresignedUploadResponse>(
        "/assets/presigned-upload",
        payload,
      );

      const uploadResponse = await fetch(data.upload_url, {
        method: data.method,
        headers: data.required_headers,
        body: file,
      });

      if (!uploadResponse.ok) {
        throw new Error(`Upload failed with status ${uploadResponse.status}`);
      }

      toast.success("Asset uploaded");
      list("assets");
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : "Asset upload failed";
      toast.error(errorMessage);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <ResourcePage title="Upload asset">
      <ResourceCard title="Asset file">
        <form onSubmit={handleSubmit}>
          <FormGrid>
            <div className="grid gap-2">
              <Label htmlFor="file">File</Label>
              <Input
                id="file"
                type="file"
                required
                onChange={(event) => {
                  const nextFile = event.target.files?.[0] ?? null;
                  setFile(nextFile);
                  if (nextFile && !fileName) {
                    setFileName(nextFile.name);
                  }
                }}
              />
              {file && (
                <p className="text-sm text-muted-foreground">
                  {file.name} · {file.type || "application/octet-stream"}
                </p>
              )}
            </div>
            <div className="grid gap-2">
              <Label htmlFor="file_name">File name</Label>
              <Input
                id="file_name"
                required
                maxLength={255}
                value={fileName}
                onChange={(event) => setFileName(event.target.value)}
              />
            </div>
            <FormActions
              submitLabel="Upload asset"
              isSubmitting={isUploading}
              onCancel={() => list("assets")}
            />
          </FormGrid>
        </form>
      </ResourceCard>
    </ResourcePage>
  );
};
