import { useForgotPassword } from "@refinedev/core";
import type { FormEvent } from "react";
import { Link } from "react-router";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

type ForgotPasswordVariables = {
  email: string;
};

export const ForgotPassword = () => {
  const { mutate, isPending } = useForgotPassword<ForgotPasswordVariables>();

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    mutate({
      email: String(formData.get("email") ?? ""),
    });
  };

  return (
    <div className="flex min-h-svh items-center justify-center bg-muted/40 p-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>Recover password</CardTitle>
          <CardDescription>
            Send a recovery link to your account email.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="grid gap-4">
            <div className="grid gap-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                required
              />
            </div>
            <Button type="submit" disabled={isPending} className="w-full">
              {isPending ? "Sending..." : "Send recovery email"}
            </Button>
          </form>
        </CardContent>
        <CardFooter className="justify-center text-sm">
          <Link to="/login" className="font-medium text-primary">
            Back to sign in
          </Link>
        </CardFooter>
      </Card>
    </div>
  );
};
