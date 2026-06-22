import { Authenticated, Refine } from "@refinedev/core";
import routerProvider, {
  CatchAllNavigate,
  DocumentTitleHandler,
  NavigateToResource,
  UnsavedChangesNotifier,
} from "@refinedev/react-router";
import { Archive, Boxes, Users } from "lucide-react";
import { BrowserRouter, Outlet, Route, Routes } from "react-router";

import "@/App.css";
import { AppLayout } from "@/components/refine-ui/layout/app-layout";
import { ErrorComponent } from "@/components/refine-ui/layout/error-component";
import { useNotificationProvider } from "@/components/refine-ui/notification/use-notification-provider";
import { Toaster } from "@/components/ui/sonner";
import { ForgotPassword } from "@/pages/forgotPassword";
import { Login } from "@/pages/login";
import { Register } from "@/pages/register";
import { authProvider } from "@/providers/auth";
import { dataProvider } from "@/providers/data";
import { AssetCreate, AssetList, AssetShow } from "@/pages/assets";
import { ItemCreate, ItemEdit, ItemList, ItemShow } from "@/pages/items";
import { UserCreate, UserEdit, UserList, UserShow } from "@/pages/users";

function App() {
  const isAdmin = true;

  return (
    <BrowserRouter>
      <Refine
        dataProvider={dataProvider}
        notificationProvider={useNotificationProvider()}
        routerProvider={routerProvider}
        authProvider={authProvider}
        resources={[
          {
            name: "items",
            list: "/items",
            create: "/items/create",
            edit: "/items/edit/:id",
            show: "/items/show/:id",
            meta: {
              canDelete: true,
              icon: <Boxes />,
            },
          },
          {
            name: "assets",
            list: "/assets",
            create: "/assets/create",
            show: "/assets/show/:id",
            meta: {
              canDelete: true,
              icon: <Archive />,
            },
          },
          {
            name: "users",
            list: "/users",
            create: "/users/create",
            edit: "/users/edit/:id",
            show: "/users/show/:id",
            meta: {
              canDelete: true,
              hide: !isAdmin,
              icon: <Users />,
            },
          },
        ]}
        options={{
          syncWithLocation: true,
          warnWhenUnsavedChanges: true,
          title: {
            text: "FastAPI Refine Starterkit",
          },
        }}
      >
        <Routes>
          <Route
            element={
              <Authenticated
                key="authenticated-inner"
                fallback={<CatchAllNavigate to="/login" />}
              >
                <AppLayout />
              </Authenticated>
            }
          >
            <Route index element={<NavigateToResource resource="items" />} />
            <Route path="/items">
              <Route index element={<ItemList />} />
              <Route path="create" element={<ItemCreate />} />
              <Route path="edit/:id" element={<ItemEdit />} />
              <Route path="show/:id" element={<ItemShow />} />
            </Route>
            <Route path="/assets">
              <Route index element={<AssetList />} />
              <Route path="create" element={<AssetCreate />} />
              <Route path="show/:id" element={<AssetShow />} />
            </Route>
            {isAdmin && (
              <Route path="/users">
                <Route index element={<UserList />} />
                <Route path="create" element={<UserCreate />} />
                <Route path="edit/:id" element={<UserEdit />} />
                <Route path="show/:id" element={<UserShow />} />
              </Route>
            )}
            <Route path="*" element={<ErrorComponent />} />
          </Route>
          <Route
            element={
              <Authenticated key="authenticated-outer" fallback={<Outlet />}>
                <NavigateToResource />
              </Authenticated>
            }
          >
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/forgot-password" element={<ForgotPassword />} />
          </Route>
        </Routes>

        <Toaster position="top-right" />
        <UnsavedChangesNotifier />
        <DocumentTitleHandler />
      </Refine>
    </BrowserRouter>
  );
}

export default App;
