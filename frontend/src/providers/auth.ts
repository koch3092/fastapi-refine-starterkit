import type { AuthProvider } from "@refinedev/core";
import { API_URL, TOKEN_KEY } from "@/providers/constants";

const getApiErrorMessage = (
  errorData: { message?: string; detail?: string },
  fallback: string,
) => errorData.message || errorData.detail || fallback;

export const authProvider: AuthProvider = {
  login: async ({ email, password }) => {
    try {
      const formData = new URLSearchParams();
      formData.append("username", email);
      formData.append("password", password);

      const response = await fetch(`${API_URL}/login/access-token`, {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        localStorage.setItem(TOKEN_KEY, data.access_token);
        return {
          success: true,
          redirectTo: "/",
        };
      }

      const errorData = await response.json().catch(() => ({}));
      return {
        success: false,
        error: {
          name: "LoginError",
          message: getApiErrorMessage(errorData, "Invalid email or password"),
        },
      };
    } catch (error) {
      return {
        success: false,
        error: {
          name: "LoginError",
          message: "Network error occurred",
        },
      };
    }
  },

  register: async ({ email, password, fullName }) => {
    try {
      const response = await fetch(`${API_URL}/users/signup`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email,
          password,
          full_name: fullName,
        }),
      });

      if (response.ok) {
        return {
          success: true,
          redirectTo: "/login",
          successNotification: {
            message: "Registration successful",
            description: "Please login with your credentials",
          },
        };
      }

      const errorData = await response.json().catch(() => ({}));
      return {
        success: false,
        error: {
          name: "RegisterError",
          message: getApiErrorMessage(errorData, "Registration failed"),
        },
      };
    } catch (error) {
      return {
        success: false,
        error: {
          name: "RegisterError",
          message: "Network error occurred",
        },
      };
    }
  },

  forgotPassword: async ({ email }) => {
    try {
      const response = await fetch(`${API_URL}/password-recovery/${email}`, {
        method: "POST",
      });

      if (response.ok) {
        return {
          success: true,
          successNotification: {
            message: "Password recovery email sent",
            description: "Check your email for reset instructions",
          },
        };
      }

      const errorData = await response.json().catch(() => ({}));
      return {
        success: false,
        error: {
          name: "ForgotPasswordError",
          message: getApiErrorMessage(errorData, "Failed to send recovery email"),
        },
      };
    } catch (error) {
      return {
        success: false,
        error: {
          name: "ForgotPasswordError",
          message: "Network error occurred",
        },
      };
    }
  },

  updatePassword: async ({ password, token }) => {
    try {
      const response = await fetch(`${API_URL}/reset-password/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          token,
          new_password: password,
        }),
      });

      if (response.ok) {
        return {
          success: true,
          redirectTo: "/login",
          successNotification: {
            message: "Password updated",
            description: "Please login with your new password",
          },
        };
      }

      const errorData = await response.json().catch(() => ({}));
      return {
        success: false,
        error: {
          name: "UpdatePasswordError",
          message: getApiErrorMessage(errorData, "Failed to update password"),
        },
      };
    } catch (error) {
      return {
        success: false,
        error: {
          name: "UpdatePasswordError",
          message: "Network error occurred",
        },
      };
    }
  },

  logout: async () => {
    localStorage.removeItem(TOKEN_KEY);
    return {
      success: true,
      redirectTo: "/login",
    };
  },

  check: async () => {
    const token = localStorage.getItem(TOKEN_KEY);
    if (!token) {
      return {
        authenticated: false,
        redirectTo: "/login",
      };
    }

    try {
      const response = await fetch(`${API_URL}/users/me`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        return {
          authenticated: true,
        };
      }

      localStorage.removeItem(TOKEN_KEY);
      return {
        authenticated: false,
        redirectTo: "/login",
      };
    } catch (error) {
      return {
        authenticated: false,
        redirectTo: "/login",
      };
    }
  },

  getPermissions: async () => {
    const token = localStorage.getItem(TOKEN_KEY);
    if (!token) return null;

    try {
      const response = await fetch(`${API_URL}/users/me`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const user = await response.json();
        return user.is_superuser ? ["admin"] : ["user"];
      }
    } catch (error) {
      // ignore
    }
    return null;
  },

  getIdentity: async () => {
    const token = localStorage.getItem(TOKEN_KEY);
    if (!token) return null;

    try {
      const response = await fetch(`${API_URL}/users/me`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const user = await response.json();
        return {
          id: user.id,
          name: user.full_name || user.email,
          email: user.email,
          avatar: `https://ui-avatars.com/api/?name=${encodeURIComponent(user.full_name || user.email)}&background=random`,
        };
      }
    } catch (error) {
      // ignore
    }
    return null;
  },

  onError: async (error) => {
    if (error.status === 401) {
      localStorage.removeItem(TOKEN_KEY);
      return {
        logout: true,
        redirectTo: "/login",
        error,
      };
    }
    return { error };
  },
};
