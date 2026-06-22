import type { BaseRecord } from "@refinedev/core";
import type { ReactNode } from "react";

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
} from "@/components/ui/card";
import { cn } from "@/lib/utils";

export type ResourceColumn<TRecord extends BaseRecord> = {
  key: string;
  header: ReactNode;
  className?: string;
  render: (record: TRecord) => ReactNode;
};

type ResourceTableProps<TRecord extends BaseRecord> = {
  columns: ResourceColumn<TRecord>[];
  data?: TRecord[];
  isLoading?: boolean;
  emptyText?: string;
};

export function ResourceTable<TRecord extends BaseRecord>({
  columns,
  data,
  isLoading,
  emptyText = "No records found.",
}: ResourceTableProps<TRecord>) {
  return (
    <Card className="overflow-hidden py-0">
      <CardContent className="p-0">
        <Table>
          <TableHeader>
            <TableRow>
              {columns.map((column) => (
                <TableHead key={column.key} className={column.className}>
                  {column.header}
                </TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading &&
              Array.from({ length: 5 }).map((_, rowIndex) => (
                <TableRow key={rowIndex}>
                  {columns.map((column) => (
                    <TableCell key={column.key}>
                      <Skeleton className="h-5 w-full" />
                    </TableCell>
                  ))}
                </TableRow>
              ))}

            {!isLoading &&
              data?.map((record) => (
                <TableRow key={String(record.id)}>
                  {columns.map((column) => (
                    <TableCell
                      key={column.key}
                      className={cn("max-w-[24rem] truncate", column.className)}
                    >
                      {column.render(record)}
                    </TableCell>
                  ))}
                </TableRow>
              ))}

            {!isLoading && (!data || data.length === 0) && (
              <TableRow>
                <TableCell
                  colSpan={columns.length}
                  className="h-28 text-center text-muted-foreground"
                >
                  {emptyText}
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}

export function TablePagination({
  currentPage,
  pageCount,
  total,
  onPageChange,
}: {
  currentPage: number;
  pageCount: number;
  total?: number;
  onPageChange: (page: number) => void;
}) {
  return (
    <div className="flex flex-col gap-2 text-sm text-muted-foreground sm:flex-row sm:items-center sm:justify-between">
      <div>{typeof total === "number" ? `${total} records` : null}</div>
      <div className="flex items-center gap-2">
        <Button
          type="button"
          variant="outline"
          size="sm"
          disabled={currentPage <= 1}
          onClick={() => onPageChange(currentPage - 1)}
        >
          Previous
        </Button>
        <span>
          Page {currentPage} of {Math.max(pageCount, 1)}
        </span>
        <Button
          type="button"
          variant="outline"
          size="sm"
          disabled={currentPage >= pageCount}
          onClick={() => onPageChange(currentPage + 1)}
        >
          Next
        </Button>
      </div>
    </div>
  );
}
