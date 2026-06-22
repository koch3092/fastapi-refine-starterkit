import React from "react";
import { UploadOutlined } from "@ant-design/icons";
import { useNavigation } from "@refinedev/core";
import { Create } from "@refinedev/antd";
import { App as AntdApp, Form, Input, Upload } from "antd";
import type { UploadFile } from "antd/es/upload/interface";
import type {
  AssetPresignedUploadRequest,
  AssetPresignedUploadResponse,
} from "@/client";
import { apiClient } from "@/providers/data";

const { Dragger } = Upload;

type AssetUploadFormValues = {
  file_name?: string;
};

export const AssetCreate = () => {
  const [form] = Form.useForm<AssetUploadFormValues>();
  const { message } = AntdApp.useApp();
  const { list } = useNavigation();
  const [fileList, setFileList] = React.useState<UploadFile[]>([]);
  const [isUploading, setIsUploading] = React.useState(false);

  const handleSubmit = React.useCallback(async () => {
    const file = fileList[0]?.originFileObj;
    if (!file) {
      message.error("Select a file first");
      return;
    }

    const values = await form.validateFields();
    const payload: AssetPresignedUploadRequest = {
      file_name: values.file_name?.trim() || file.name,
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

      message.success("Asset uploaded");
      list("assets");
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : "Asset upload failed";
      message.error(errorMessage);
    } finally {
      setIsUploading(false);
    }
  }, [fileList, form, list, message]);

  return (
    <Create saveButtonProps={{ loading: isUploading, onClick: handleSubmit }}>
      <Form form={form} layout="vertical">
        <Form.Item label="File" required>
          <Dragger
            beforeUpload={() => false}
            fileList={fileList}
            maxCount={1}
            multiple={false}
            onChange={({ fileList: nextFileList }) => {
              const nextFile = nextFileList.slice(-1);
              setFileList(nextFile);

              const selectedName = nextFile[0]?.name;
              if (selectedName && !form.getFieldValue("file_name")) {
                form.setFieldValue("file_name", selectedName);
              }
            }}
            onRemove={() => {
              setFileList([]);
              return true;
            }}
          >
            <p className="ant-upload-drag-icon">
              <UploadOutlined />
            </p>
            <p className="ant-upload-text">Select or drop a file</p>
          </Dragger>
        </Form.Item>
        <Form.Item
          label="File Name"
          name="file_name"
          rules={[{ required: true, message: "File name is required" }]}
        >
          <Input maxLength={255} />
        </Form.Item>
      </Form>
    </Create>
  );
};
