import { AuthPage } from "@refinedev/antd";

export const Login = () => {
  return (
    <AuthPage
      type="login"
      formProps={{
        initialValues: { email: "admin@example.com", password: "changethis" },
      }}
    />
  );
};
