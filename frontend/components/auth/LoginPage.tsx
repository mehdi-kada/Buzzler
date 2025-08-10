"use client";

import React, { useState, FormEvent, useEffect } from "react";
import Link from "next/link";
import Image from "next/image";
import { useAuthStore } from "@/lib/store/authStore";
import api from "@/lib/axios";
import { useSearchParams, useRouter } from "next/navigation";
import { LoginFormData, SignupFormData } from "@/types/types_auth";

const loginWithGoogle = async () => {
  try {
    const result = await api.get("/auth/google/login");
    return result.data.redirect_url;
  } catch (e) {
    console.warn("failed to fetch google url");
  }
};



const LoginPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<"login" | "signup">("login");
  const [isLoading, setIsLoading] = useState(false); // local submit/loading
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const searchParams = useSearchParams();
  const oauthError = searchParams.get("error");
  // Use separate primitive selectors to avoid recreating object snapshots each render
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const isHydrated = useAuthStore((s) => s.isHydrated);
  const authChecking = useAuthStore((s) => s.isLoading);
  const login = useAuthStore((s) => s.login);
  const router = useRouter();

  useEffect(() => {
    if (oauthError) {
      setError(
        oauthError === "oauth_error"
          ? "Google login failed. Please try again."
          : "An error occurred during login."
      );
    }
  }, [oauthError]);

  // useEffect(() => {
  //   if (isHydrated && !authChecking && isAuthenticated) {
  //     router.replace("/dashboard");
  //   }
  // }, [isHydrated, authChecking, isAuthenticated, router]);

  // Login form state
  const [loginForm, setLoginForm] = useState<LoginFormData>({
    email: "",
    password: "",
    rememberMe: false,
  });

  // Signup form state
  const [signupForm, setSignupForm] = useState<SignupFormData>({
    firstName: "",
    lastName: "",
    email: "",
    password: "",
    confirmPassword: "",
    agreeToTerms: false,
  });

  const handleLoginSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    setSuccessMessage(null);

    try {
      const email = loginForm.email;
      const password = loginForm.password;
      const formData = new URLSearchParams();
      formData.append("username", email);
      formData.append("password", password);

      const response = await api.post("/auth/login", formData, {
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
      });

      const { access_token } = response.data;
      const user = { email, first_name: email.split("@")[0] };
      login(access_token, user);
      router.replace("/dashboard");
    } catch (error: any) {
      if (error.response) {
        // Handle specific error cases
        // Ensure we're always working with a string, not an object
        let errorMessage = "An unknown error occurred";
        if (typeof error.response.data.detail === "string") {
          errorMessage = error.response.data.detail;
        } else if (typeof error.response.data.detail === "object" && error.response.data.detail.msg) {
          errorMessage = error.response.data.detail.msg;
        } else if (typeof error.response.data.detail === "object") {
          // If it's an object, try to stringify it or use a generic message
          errorMessage = JSON.stringify(error.response.data.detail);
        }
        setError(errorMessage);
      } else {
        setError("Network error. Please check your connection and try again.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleSignupSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    setSuccessMessage(null);

    if (signupForm.password !== signupForm.confirmPassword) {
      setError("Passwords do not match");
      setIsLoading(false);
      return;
    }

    if (!signupForm.agreeToTerms) {
      setError("Please agree to the Terms of Service and Privacy Policy");
      setIsLoading(false);
      return;
    }

    try {
      // Prepare signup data - combine first and last name since backend only expects first_name
      const signupData = {
        email: signupForm.email,
        password: signupForm.password,
        first_name: `${signupForm.firstName} ${signupForm.lastName}`.trim(),
      };

      const response = await api.post("/auth/register", signupData);

      setSuccessMessage("Account created successfully! Please check your email for verification.");  
      setActiveTab("login");
    } catch (error: any) {
      if (error.response) {
      let errorMessage = "An error occurred during signup";
      const detail = error.response.data.detail;
      
      // Handle array of validation errors (Pydantic format)
      if (Array.isArray(detail)) {
        errorMessage = detail.map(err => err.msg).join(", ");
      } 
      // Handle string error
      else if (typeof detail === "string") {
        errorMessage = detail;
      } 
      // Handle object with msg property
      else if (typeof detail === "object" && detail.msg) {
        errorMessage = detail.msg;
      } 
      // Fallback for other object types
      else if (typeof detail === "object") {
        errorMessage = JSON.stringify(detail);
      }
      
      setError(errorMessage);
    } else {
      setError("Network error. Please check your connection and try again.");
    }
    } finally {
      setIsLoading(false);
    }
  };

  const handleSocialLogin = async (provider: "google") => {
    setIsLoading(true);
    setError(null);
    setSuccessMessage(null);
    try {
      const url = await loginWithGoogle();
      if (url) {
        router.push(url);
      }
    } catch (error: any) {
      console.error(`${provider} login error:`, error);
      setError("Failed to initiate Google login. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  if (!isHydrated || authChecking) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-black text-white">
        <div className="flex items-center space-x-2">
          <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white" />
          <span>Checking session...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-black text-white overflow-x-hidden min-h-screen">
      {/* Background */}
      <div className="fixed inset-0 gradient-bg"></div>

      {/* Main Content */}
      <main className="relative z-10 min-h-screen flex items-center justify-center px-6 py-12">
        <div className="max-w-md w-full">
          {/* Auth Card */}
          <div className="auth-card p-8 rounded-2xl">
            {/* Logo & Welcome */}
            <div className="text-center mb-8">
              <div className="w-16 h-16 bg-gradient-to-r from-pink-600 to-orange-500 rounded-2xl flex items-center justify-center mx-auto mb-4 animate-float">
                <Image
                  src={"/Logo.png"}
                  height={200}
                  width={200}
                  alt="logo"
                />
              </div>
              <h1 className="text-2xl font-bold mb-2">
                Welcome to{" "}
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-pink-600 to-orange-500 glow-effect">
                  Buzzler
                </span>
              </h1>
              <p className="text-gray-300">
                Transform your videos into viral social content
              </p>
            </div>

            {/* Tab Toggle */}
            <div className="flex bg-gray-800/50 rounded-lg p-1 mb-6">
              <button
                onClick={() => setActiveTab("login")}
                disabled={isLoading}
                className={`tab-button flex-1 font-medium text-center ${
                  activeTab === "login" ? "active" : "text-gray-300"
                } ${isLoading ? "opacity-50 cursor-not-allowed" : ""}`}
              >
                Sign In
              </button>
              <button
                onClick={() => setActiveTab("signup")}
                disabled={isLoading}
                className={`tab-button flex-1 font-medium text-center ${
                  activeTab === "signup" ? "active" : "text-gray-300"
                } ${isLoading ? "opacity-50 cursor-not-allowed" : ""}`}
              >
                Sign Up
              </button>
            </div>

            {/* Messages */}
            {error && (
              <div className="auth-error mb-4">
                {error}
              </div>
            )}
            {successMessage && (
              <div className="auth-success mb-4">
                {successMessage}
              </div>
            )}

            {/* Login Form */}
            {activeTab === "login" && (
              <form onSubmit={handleLoginSubmit} className="space-y-4">
                <div>
                  <label
                    htmlFor="login-email"
                    className="block text-sm font-medium text-gray-300 mb-2"
                  >
                    Email
                  </label>
                  <input
                    id="login-email"
                    type="email"
                    value={loginForm.email}
                    onChange={(e) =>
                      setLoginForm((prev) => ({
                        ...prev,
                        email: e.target.value,
                      }))
                    }
                    className="form-input w-full px-4 py-3 rounded-lg"
                    placeholder="Enter your email"
                    required
                    disabled={isLoading}
                  />
                </div>

                <div>
                  <label
                    htmlFor="login-password"
                    className="block text-sm font-medium text-gray-300 mb-2"
                  >
                    Password
                  </label>
                  <input
                    id="login-password"
                    type="password"
                    value={loginForm.password}
                    onChange={(e) =>
                      setLoginForm((prev) => ({
                        ...prev,
                        password: e.target.value,
                      }))
                    }
                    className="form-input w-full px-4 py-3 rounded-lg"
                    placeholder="Enter your password"
                    required
                    disabled={isLoading}
                    minLength={8}
                  />
                </div>

                <div className="flex items-center justify-between">
                  <label className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={loginForm.rememberMe}
                      onChange={(e) =>
                        setLoginForm((prev) => ({
                          ...prev,
                          rememberMe: e.target.checked,
                        }))
                      }
                      className="w-4 h-4 text-pink-600 bg-gray-800 border-gray-600 rounded focus:ring-pink-500 focus:ring-2"
                      disabled={isLoading}
                    />
                    <span className="text-sm text-gray-300">Remember me</span>
                  </label>
                  <Link
                    href="/forgot-password"
                    className="text-sm text-pink-600 hover:text-pink-500 transition-colors"
                  >
                    Forgot password?
                  </Link>
                </div>

                <button
                  type="submit"
                  disabled={isLoading}
                  className="btn-primary w-full px-6 py-3 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isLoading ? (
                    <div className="flex items-center justify-center space-x-2">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                      <span>Signing in...</span>
                    </div>
                  ) : (
                    "Sign In"
                  )}
                </button>
              </form>
            )}

            {/* Signup Form */}
            {activeTab === "signup" && (
              <form onSubmit={handleSignupSubmit} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label
                      htmlFor="signup-firstName"
                      className="block text-sm font-medium text-gray-300 mb-2"
                    >
                      First Name
                    </label>
                    <input
                      id="signup-firstName"
                      type="text"
                      value={signupForm.firstName}
                      onChange={(e) =>
                        setSignupForm((prev) => ({
                          ...prev,
                          firstName: e.target.value,
                        }))
                      }
                      className="form-input w-full px-4 py-3 rounded-lg"
                      placeholder="John"
                      required
                      disabled={isLoading}
                    />
                  </div>
                  <div>
                    <label
                      htmlFor="signup-lastName"
                      className="block text-sm font-medium text-gray-300 mb-2"
                    >
                      Last Name
                    </label>
                    <input
                      id="signup-lastName"
                      type="text"
                      value={signupForm.lastName}
                      onChange={(e) =>
                        setSignupForm((prev) => ({
                          ...prev,
                          lastName: e.target.value,
                        }))
                      }
                      className="form-input w-full px-4 py-3 rounded-lg"
                      placeholder="Doe"
                      required
                      disabled={isLoading}
                    />
                  </div>
                </div>

                <div>
                  <label
                    htmlFor="signup-email"
                    className="block text-sm font-medium text-gray-300 mb-2"
                  >
                    Email
                  </label>
                  <input
                    id="signup-email"
                    type="email"
                    value={signupForm.email}
                    onChange={(e) =>
                      setSignupForm((prev) => ({
                        ...prev,
                        email: e.target.value,
                      }))
                    }
                    className="form-input w-full px-4 py-3 rounded-lg"
                    placeholder="Enter your email"
                    required
                    disabled={isLoading}
                  />
                </div>

                <div>
                  <label
                    htmlFor="signup-password"
                    className="block text-sm font-medium text-gray-300 mb-2"
                  >
                    Password
                  </label>
                  <input
                    id="signup-password"
                    type="password"
                    value={signupForm.password}
                    onChange={(e) =>
                      setSignupForm((prev) => ({
                        ...prev,
                        password: e.target.value,
                      }))
                    }
                    className="form-input w-full px-4 py-3 rounded-lg"
                    placeholder="Create a password"
                    required
                    disabled={isLoading}
                    minLength={8}
                  />
                  <p className="text-xs text-gray-400 mt-1">
                    Must be at least 8 characters
                  </p>
                </div>

                <div>
                  <label
                    htmlFor="signup-confirmPassword"
                    className="block text-sm font-medium text-gray-300 mb-2"
                  >
                    Confirm Password
                  </label>
                  <input
                    id="signup-confirmPassword"
                    type="password"
                    value={signupForm.confirmPassword}
                    onChange={(e) =>
                      setSignupForm((prev) => ({
                        ...prev,
                        confirmPassword: e.target.value,
                      }))
                    }
                    className="form-input w-full px-4 py-3 rounded-lg"
                    placeholder="Confirm your password"
                    required
                    disabled={isLoading}
                    minLength={8}
                  />
                </div>

                <div>
                  <label className="flex items-start space-x-2">
                    <input
                      type="checkbox"
                      checked={signupForm.agreeToTerms}
                      onChange={(e) =>
                        setSignupForm((prev) => ({
                          ...prev,
                          agreeToTerms: e.target.checked,
                        }))
                      }
                      className="w-4 h-4 text-pink-600 bg-gray-800 border-gray-600 rounded focus:ring-pink-500 focus:ring-2 mt-0.5"
                      required
                      disabled={isLoading}
                    />
                    <span className="text-sm text-gray-300">
                      I agree to the{" "}
                      <Link
                        href="/terms"
                        className="text-pink-600 hover:text-pink-500 transition-colors"
                      >
                        Terms of Service
                      </Link>{" "}
                      and{" "}
                      <Link
                        href="/privacy"
                        className="text-pink-600 hover:text-pink-500 transition-colors"
                      >
                        Privacy Policy
                      </Link>
                    </span>
                  </label>
                </div>

                <button
                  type="submit"
                  disabled={isLoading}
                  className="btn-primary w-full px-6 py-3 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isLoading ? (
                    <div className="flex items-center justify-center space-x-2">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                      <span>Creating account...</span>
                    </div>
                  ) : (
                    "Create Account"
                  )}
                </button>
              </form>
            )}

            {/* Divider */}
            <div className="flex items-center my-6">
              <div className="divider flex-1"></div>
              <span className="px-4 text-sm text-gray-400">
                or continue with
              </span>
              <div className="divider flex-1"></div>
            </div>

            {/* Social Login */}
            <div className="w-ful">
              <button
                onClick={() => handleSocialLogin("google")}
                disabled={isLoading}
                className="social-btn w-full px-4 py-3 rounded-lg flex items-center justify-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <svg
                  className="w-5 h-5"
                  viewBox="0 0 24 24"
                  fill="currentColor"
                >
                  <path
                    d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                    fill="#4285F4"
                  />
                  <path
                    d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                    fill="#34A853"
                  />
                  <path
                    d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                    fill="#FBBC05"
                  />
                  <path
                    d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                    fill="#EA4335"
                  />
                </svg>
                <span className="text-sm font-medium">Google</span>
              </button>
            </div>

            {/* Footer Text */}
            <p className="text-center text-sm text-gray-400 mt-6">
              <span>
                {activeTab === "login"
                  ? "Don't have an account?"
                  : "Already have an account?"}
              </span>
              <button
                onClick={() =>
                  setActiveTab(activeTab === "login" ? "signup" : "login")
                }
                disabled={isLoading}
                className="text-pink-600 hover:text-pink-500 ml-1 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {activeTab === "login" ? "Sign up here" : "Sign in here"}
              </button>
            </p>
          </div>

          {/* Features Preview */}
          <div className="mt-8 text-center">
            <p className="text-sm text-gray-400 mb-4">
              Join thousands of creators who trust Buzzler
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center space-y-2 sm:space-y-0 sm:space-x-6 text-sm text-gray-500">
              <div className="flex items-center space-x-2">
                <svg
                  className="w-4 h-4 text-green-500 flex-shrink-0"
                  fill="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z" />
                </svg>
                <span>AI-Powered Clipping</span>
              </div>
              <div className="flex items-center space-x-2">
                <svg
                  className="w-4 h-4 text-green-500 flex-shrink-0"
                  fill="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z" />
                </svg>
                <span>Auto Social Posts</span>
              </div>
              <div className="flex items-center space-x-2">
                <svg
                  className="w-4 h-4 text-green-500 flex-shrink-0"
                  fill="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z" />
                </svg>
                <span>Analytics Dashboard</span>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Animated Background Elements */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-2 h-2 bg-pink-600 rounded-full opacity-60 animate-pulse"></div>
        <div className="absolute top-3/4 right-1/4 w-1 h-1 bg-orange-500 rounded-full opacity-40 animate-pulse animate-delay-1"></div>
        <div className="absolute top-1/2 left-3/4 w-1.5 h-1.5 bg-pink-400 rounded-full opacity-50 animate-pulse animate-delay-2"></div>
      </div>
    </div>
  );
};

export default LoginPage;
