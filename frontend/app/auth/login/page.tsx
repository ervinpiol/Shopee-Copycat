"use client";

import { useState, useEffect } from "react";
import axios from "axios";
import { useRouter } from "next/navigation";
import { Input } from "@/components/ui/input";
import { Spinner } from "@/components/spinner";

export default function LoginPage() {
  const router = useRouter();
  const [form, setForm] = useState({ email: "", password: "" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // ✅ Check if already logged in
  useEffect(() => {
    async function checkLoggedIn() {
      try {
        const res = await axios.get("http://localhost:8000/users/me", {
          withCredentials: true,
        });
        if (res.data) {
          router.replace("/products"); // redirect if already logged in
        }
      } catch (err) {
        // Not logged in, do nothing
        console.log(err);
      }
    }

    checkLoggedIn();
  }, [router]);

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const data = new URLSearchParams();
      data.append("username", form.email);
      data.append("password", form.password);

      await axios.post("http://localhost:8000/auth/jwt/login", data, {
        withCredentials: true,
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
      });

      router.push("/products"); // redirect after success
    } catch (err: any) {
      setError(err.response?.data?.detail || "Invalid credentials");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-50 p-4 w-full">
      {loading && <Spinner />}
      <form
        onSubmit={handleLogin}
        className="bg-white p-6 rounded-xl shadow-lg w-full max-w-sm space-y-4"
      >
        <h1 className="text-2xl font-bold text-center">Login</h1>

        {error && <p className="text-red-500 text-sm">{error}</p>}

        <div>
          <label className="block text-sm mb-1 font-medium">Email</label>
          <Input
            type="email"
            required
            value={form.email}
            onChange={(e) => setForm({ ...form, email: e.target.value })}
          />
        </div>

        <div>
          <label className="block text-sm mb-1 font-medium">Password</label>
          <Input
            type="password"
            required
            value={form.password}
            onChange={(e) => setForm({ ...form, password: e.target.value })}
          />
        </div>

        <button
          disabled={loading}
          className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? "Logging in..." : "Login"}
        </button>

        <p className="text-center text-sm">
          Don't have an account?{" "}
          <a href="/auth/signup" className="text-blue-600 underline">
            Sign up
          </a>
        </p>
      </form>
    </div>
  );
}
