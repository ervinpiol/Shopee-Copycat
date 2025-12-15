import { Loader2 } from "lucide-react";
import { createPortal } from "react-dom";

export const Spinner = () => {
  return createPortal(
    <div className="fixed top-0 left-0 z-999999999 w-screen h-screen bg-black/50 flex items-center justify-center">
      <Loader2 className="h-8 w-8 animate-spin text-gray-200" />
    </div>,
    document.body
  );
};
