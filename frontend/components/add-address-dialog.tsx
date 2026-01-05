"use client";

import { useState } from "react";
import axios from "axios";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { toast } from "sonner";

interface AddAddressDialogProps {
  onSuccess: () => void;
}

export function AddAddressDialog({ onSuccess }: AddAddressDialogProps) {
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);

  const [form, setForm] = useState({
    label: "",
    recipient_name: "",
    phone: "",
    address_line1: "",
    address_line2: "",
    city: "",
    province: "",
    postal_code: "",
    country: "PH",
    is_default: false,
  });

  const handleChange = (key: string, value: any) => {
    setForm((prev) => ({ ...prev, [key]: value }));
  };

  const handleSubmit = async () => {
    setLoading(true);
    try {
      await axios.post(
        "http://localhost:8000/users/me/addresses",
        {
          ...form,
          phone: Number(form.phone),
          postal_code: Number(form.postal_code),
        },
        { withCredentials: true }
      );

      toast.success("Address added successfully");
      setOpen(false);
      onSuccess();
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Failed to add address");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button size="sm" variant="outline">
          Add
        </Button>
      </DialogTrigger>

      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle>Add New Address</DialogTitle>
        </DialogHeader>

        <div className="grid grid-cols-2 gap-4">
          <div className="col-span-2">
            <Label>Label</Label>
            <Input
              placeholder="Home, Office"
              value={form.label}
              onChange={(e) => handleChange("label", e.target.value)}
            />
          </div>

          <div className="col-span-2">
            <Label>Recipient Name</Label>
            <Input
              value={form.recipient_name}
              onChange={(e) => handleChange("recipient_name", e.target.value)}
            />
          </div>

          <div className="col-span-2">
            <Label>Phone</Label>
            <Input
              type="number"
              value={form.phone}
              onChange={(e) => handleChange("phone", e.target.value)}
            />
          </div>

          <div className="col-span-2">
            <Label>Address Line 1</Label>
            <Input
              value={form.address_line1}
              onChange={(e) => handleChange("address_line1", e.target.value)}
            />
          </div>

          <div className="col-span-2">
            <Label>Address Line 2</Label>
            <Input
              value={form.address_line2}
              onChange={(e) => handleChange("address_line2", e.target.value)}
            />
          </div>

          <div>
            <Label>City</Label>
            <Input
              value={form.city}
              onChange={(e) => handleChange("city", e.target.value)}
            />
          </div>

          <div>
            <Label>Province</Label>
            <Input
              value={form.province}
              onChange={(e) => handleChange("province", e.target.value)}
            />
          </div>

          <div>
            <Label>Postal Code</Label>
            <Input
              type="number"
              value={form.postal_code}
              onChange={(e) => handleChange("postal_code", e.target.value)}
            />
          </div>

          <div className="flex items-center gap-2 mt-2 col-span-2">
            <Checkbox
              checked={form.is_default}
              onCheckedChange={(v) => handleChange("is_default", Boolean(v))}
            />
            <Label>Set as default address</Label>
          </div>
        </div>

        <Button
          className="w-full mt-4"
          onClick={handleSubmit}
          disabled={loading}
        >
          {loading ? "Saving..." : "Save Address"}
        </Button>
      </DialogContent>
    </Dialog>
  );
}
