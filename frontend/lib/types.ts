export interface Product {
  id: string;
  name: string;
  description: string;
  price: number;
  image: string;
  rating: number;
  reviews: number;
  stock: number;
  category: "Electronics" | "Accessories" | "Storage";
}

export interface OrderItems {
  id: number;
  product_id: number;
  quantity: number;
  total_price: number;
  product_name: string;
}

export interface Order {
  id: number;
  owner_id: number;
  owner_name: string;
  status: "pendng" | "null" | "string";
  total_price: number;
  items: OrderItems[];
  order_date: string;
}
