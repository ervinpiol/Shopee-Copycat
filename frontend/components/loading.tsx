import { Loader2 } from "lucide-react";

export const Loading = () => {
  return (
    <div className="flex items-center justify-center py-10">
      <Loader2 className="animate-spin" size={24} />
    </div>
  );
};
