import {
  useGetIdentity,
  useLogout,
  useMenu,
  type TreeMenuItem,
} from "@refinedev/core";
import { Archive, Boxes, FileText, LogOut, UserRound } from "lucide-react";
import type { ReactNode } from "react";
import { NavLink, Outlet } from "react-router";

import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { cn } from "@/lib/utils";

const fallbackIcons: Record<string, ReactNode> = {
  items: <Boxes />,
  assets: <Archive />,
  users: <UserRound />,
};

function MenuLink({ item, selectedKey }: { item: TreeMenuItem; selectedKey: string }) {
  if (!item.route) return null;

  const isSelected = item.key === selectedKey;
  const icon = item.icon ?? fallbackIcons[item.name ?? ""];

  return (
    <NavLink
      to={item.route}
      className={({ isActive }) =>
        cn(
          "flex h-9 items-center gap-3 rounded-md px-3 text-sm font-medium text-sidebar-foreground/80 transition-colors hover:bg-sidebar-accent hover:text-sidebar-accent-foreground",
          (isActive || isSelected) &&
            "bg-sidebar-accent text-sidebar-accent-foreground",
        )
      }
    >
      <span className="[&_svg]:size-4">{icon ?? <FileText />}</span>
      <span>{item.label ?? item.name}</span>
    </NavLink>
  );
}

export function AppLayout() {
  const { menuItems, selectedKey } = useMenu();
  const { data: identity } = useGetIdentity<{ name?: string; email?: string }>();
  const { mutate: logout, isPending: isLoggingOut } = useLogout();

  return (
    <div className="min-h-svh bg-background">
      <aside className="fixed inset-y-0 left-0 hidden w-64 flex-col border-r border-sidebar-border bg-sidebar text-sidebar-foreground md:flex">
        <div className="flex h-16 items-center px-5">
          <div className="flex items-center gap-3">
            <div className="flex size-9 items-center justify-center rounded-md bg-sidebar-foreground text-sidebar">
              <Boxes className="size-4" />
            </div>
            <div>
              <div className="text-sm font-semibold">Starterkit</div>
              <div className="text-xs text-sidebar-foreground/60">
                FastAPI + Refine
              </div>
            </div>
          </div>
        </div>
        <Separator className="bg-sidebar-border" />
        <nav className="flex flex-1 flex-col gap-1 p-3">
          {menuItems.map((item) => (
            <MenuLink key={item.key} item={item} selectedKey={selectedKey} />
          ))}
        </nav>
      </aside>

      <div className="md:pl-64">
        <header className="sticky top-0 z-20 flex h-16 items-center justify-between border-b bg-background/95 px-4 backdrop-blur md:px-6">
          <div>
            <div className="text-sm font-semibold md:hidden">Starterkit</div>
            <div className="hidden text-sm text-muted-foreground md:block">
              Admin console
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="hidden text-right text-sm md:block">
              <div className="font-medium">{identity?.name ?? "User"}</div>
              <div className="text-xs text-muted-foreground">
                {identity?.email}
              </div>
            </div>
            <Button
              type="button"
              variant="outline"
              size="sm"
              disabled={isLoggingOut}
              onClick={() => logout({})}
            >
              <LogOut className="size-4" />
              Logout
            </Button>
          </div>
        </header>

        <main className="mx-auto flex w-full max-w-7xl flex-col gap-6 p-4 md:p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
