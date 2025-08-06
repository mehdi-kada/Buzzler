"use client";

import { useEffect, useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { CheckCircle, XCircle } from "lucide-react";

export default function VerifyAccountPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [status, setStatus] = useState("verifying");
  const [message, setMessage] = useState("Verifying your account...");

  useEffect(() => {
    const statusParam = searchParams.get("status")
    if (statusParam === "success"){
      setStatus("success")
      setMessage("Your account has been successfully verified! Redirecting to login...")
      setTimeout(()=>{
        router.push("/auth/login")
      }, 3000)
    }else{
      setStatus("error");
      setMessage("Invalid or expired verification token. Please try again.");
    }


    }, [searchParams, router]);

    return (
      <div className="flex min-h-screen flex-col items-center justify-center bg-gray-50 p-6">
        <div className="w-full max-w-md rounded-lg bg-white p-8 text-center shadow-md">
          {status === "verifying" && (
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          )}
          {status === "success" && (
            <CheckCircle className="mx-auto h-12 w-12 text-green-500" />
          )}
          {status === "error" && (
            <XCircle className="mx-auto h-12 w-12 text-red-500" />
          )}
          <p className="mt-4 text-lg font-medium text-gray-700">{message}</p>
        </div>
      </div>
    );
}
