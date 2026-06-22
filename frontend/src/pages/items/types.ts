import type { BaseKey } from "@refinedev/core";

export type Owner = {
  id: BaseKey;
  email: string;
  full_name?: string | null;
};
