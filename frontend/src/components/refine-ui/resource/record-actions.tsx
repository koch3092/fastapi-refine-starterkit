import { type BaseKey, useDelete, useNavigation } from "@refinedev/core";
import { Download, Eye, Pencil, Trash2 } from "lucide-react";
import * as React from "react";

import { Button } from "@/components/ui/button";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";

export function RecordActions({
  resource,
  id,
  onDeleted,
  extra,
  canEdit = true,
  canDelete = true,
  canShow = true,
}: {
  resource: string;
  id?: BaseKey;
  onDeleted?: () => void;
  extra?: React.ReactNode;
  canEdit?: boolean;
  canDelete?: boolean;
  canShow?: boolean;
}) {
  const { show, edit } = useNavigation();
  const { mutate, mutation } = useDelete();
  const [confirmOpen, setConfirmOpen] = React.useState(false);

  if (!id) return null;

  return (
    <div className="flex items-center justify-end gap-1">
      {extra}
      {canShow && (
        <Button
          type="button"
          variant="ghost"
          size="icon"
          aria-label="Show"
          onClick={() => show(resource, id)}
        >
          <Eye className="size-4" />
        </Button>
      )}
      {canEdit && (
        <Button
          type="button"
          variant="ghost"
          size="icon"
          aria-label="Edit"
          onClick={() => edit(resource, id)}
        >
          <Pencil className="size-4" />
        </Button>
      )}
      {canDelete && (
        <Popover open={confirmOpen} onOpenChange={setConfirmOpen}>
          <PopoverTrigger asChild>
            <Button
              type="button"
              variant="ghost"
              size="icon"
              aria-label="Delete"
            >
              <Trash2 className="size-4 text-destructive" />
            </Button>
          </PopoverTrigger>
          <PopoverContent align="end" className="w-72">
            <div className="grid gap-3">
              <div>
                <div className="text-sm font-medium">Delete record?</div>
                <p className="text-sm text-muted-foreground">
                  This action cannot be undone.
                </p>
              </div>
              <div className="flex justify-end gap-2">
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => setConfirmOpen(false)}
                >
                  Cancel
                </Button>
                <Button
                  type="button"
                  variant="destructive"
                  size="sm"
                  disabled={mutation.isPending}
                  onClick={() => {
                    mutate(
                      { resource, id, invalidates: ["list"] },
                      {
                        onSuccess: () => {
                          setConfirmOpen(false);
                          onDeleted?.();
                        },
                      },
                    );
                  }}
                >
                  Delete
                </Button>
              </div>
            </div>
          </PopoverContent>
        </Popover>
      )}
    </div>
  );
}

export function DownloadButton({ onClick }: { onClick: () => void }) {
  return (
    <Button
      type="button"
      variant="ghost"
      size="icon"
      aria-label="Download"
      onClick={onClick}
    >
      <Download className="size-4" />
    </Button>
  );
}
