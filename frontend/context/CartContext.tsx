"use client";

import {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from "react";
import axios from "axios";
import { useAuth } from "@/context/AuthContext";

interface Product {
  id: string;
  price: number;
  name: string;
  image?: string;
}

interface CartItem {
  id: string;
  quantity: number;
  product: Product;
}

interface CartContextType {
  cartItems: CartItem[];
  itemCount: number;
  subtotal: number;
  isFetching: boolean;
  isProcessing: boolean;
  refreshCart: () => void;
  addToCart: (productId: string, quantity?: number) => Promise<void>;
  updateQuantity: (
    cartItemId: string,
    productId: string,
    quantity: number
  ) => Promise<void>;
  removeItem: (cartItemId: string, productId: string) => Promise<void>;
  clearCart: () => void;
}

const CartContext = createContext<CartContextType | undefined>(undefined);

export function CartProvider({ children }: { children: ReactNode }) {
  const { user, loading } = useAuth();
  const [cartItems, setCartItems] = useState<CartItem[]>([]);
  const [isFetching, setIsFetching] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);

  const fetchCartItems = async () => {
    if (!user) return;

    setIsFetching(true);
    try {
      const { data } = await axios.get("http://localhost:8000/cart/items", {
        withCredentials: true,
      });
      setCartItems(data);
    } catch (err) {
      console.error("Failed to fetch cart items", err);
    } finally {
      setIsFetching(false);
    }
  };

  useEffect(() => {
    if (!loading) {
      fetchCartItems();
    }
  }, [user, loading]);

  const addToCart = async (productId: string, quantity = 1) => {
    if (!user) {
      alert("Please login first.");
      return;
    }

    setIsProcessing(true);
    try {
      const existingItem = cartItems.find(
        (item) => item.product.id === productId
      );

      if (existingItem) {
        const newQuantity = existingItem.quantity + quantity;

        const { data } = await axios.put(
          `http://localhost:8000/cart/items/${existingItem.id}`,
          { product_id: productId, quantity: newQuantity },
          { withCredentials: true }
        );

        setCartItems((prev) =>
          prev.map((item) =>
            item.id === data.id ? { ...item, quantity: data.quantity } : item
          )
        );
      } else {
        const { data } = await axios.post(
          "http://localhost:8000/cart/items",
          { product_id: productId, quantity },
          { withCredentials: true }
        );

        setCartItems((prev) => [...prev, data]);
      }
    } catch (err: any) {
      console.error("Failed to add item", err);
      alert(err.response?.data?.detail || err.message);
    } finally {
      setIsProcessing(false);
    }
  };

  const updateQuantity = async (
    cartItemId: string,
    productId: string,
    quantity: number
  ) => {
    if (!user) return;

    setIsProcessing(true);
    try {
      const { data } = await axios.put(
        `http://localhost:8000/cart/items/${cartItemId}`,
        { product_id: productId, quantity },
        { withCredentials: true }
      );
      setCartItems((prev) =>
        prev.map((item) =>
          item.id === data.id ? { ...item, quantity: data.quantity } : item
        )
      );
    } catch (err: any) {
      console.error("Failed to update quantity", err);
      alert(err.response?.data?.detail || err.message);
    } finally {
      setIsProcessing(false);
    }
  };

  const removeItem = async (cartItemId: string, productId: string) => {
    if (!user) return;

    setIsProcessing(true);
    try {
      await axios.delete(`http://localhost:8000/cart/items/${cartItemId}`, {
        data: { product_id: productId },
        withCredentials: true,
      });
      setCartItems((prev) => prev.filter((item) => item.id !== cartItemId));
    } catch (err: any) {
      console.error("Failed to remove item", err);
      alert(err.response?.data?.detail || err.message);
    } finally {
      setIsProcessing(false);
    }
  };

  const clearCart = () => {
    setCartItems([]);
  };

  const itemCount = cartItems.reduce((acc, item) => acc + item.quantity, 0);
  const subtotal = cartItems.reduce(
    (acc, item) => acc + item.quantity * item.product.price,
    0
  );

  return (
    <CartContext.Provider
      value={{
        cartItems,
        itemCount,
        subtotal,
        isFetching,
        isProcessing,
        refreshCart: fetchCartItems,
        addToCart,
        updateQuantity,
        removeItem,
        clearCart,
      }}
    >
      {children}
    </CartContext.Provider>
  );
}

export function useCart() {
  const ctx = useContext(CartContext);
  if (!ctx) throw new Error("useCart must be inside CartProvider");
  return ctx;
}
