import type { NotificationProvider } from "@refinedev/core";
import { toast } from "sonner";

export function useNotificationProvider(): NotificationProvider {
  return {
    open: ({ key, type, message, description }) => {
      const options = {
        id: key,
        description,
        richColors: true,
      };

      if (type === "success") {
        toast.success(message, options);
        return;
      }

      if (type === "error") {
        toast.error(message, options);
        return;
      }

      toast(message, options);
    },
    close: (id) => {
      toast.dismiss(id);
    },
  };
}
