"use client";

import { useState } from "react";
import axios from "axios";
import { useRouter } from "next/navigation";
import { Input } from "@/components/ui/input";

export default function SignupPage() {
  const router = useRouter();
  const [form, setForm] = useState({
    name: "",
    email: "",
    password: "",
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSignup(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      await axios.post("http://localhost:8000/auth/register", form, {
        withCredentials: true,
      });

      router.push("/auth/login");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-50 p-4">
      <form
        onSubmit={handleSignup}
        className="bg-white p-6 rounded-xl shadow-lg w-full max-w-sm space-y-4"
      >
        <h1 className="text-2xl font-bold text-center">Create an Account</h1>

        {error && <p className="text-red-500 text-sm">{error}</p>}

        <div>
          <label className="block text-sm mb-1 font-medium">Name</label>
          <Input
            type="name"
            required
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
          />
        </div>

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
          {loading ? "Creating account..." : "Sign Up"}
        </button>

        <p className="text-center text-sm">
          Already have an account?{" "}
          <a href="/auth/login" className="text-blue-600 underline">
            Login
          </a>
        </p>
      </form>
    </div>
  );
}
