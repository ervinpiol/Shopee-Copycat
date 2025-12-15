import { Header } from "@/components/header";
import { ProductDetail } from "@/components/product-detail";

export default async function ProductPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;

  return (
    <div>
      <Header />
      <ProductDetail productId={id} />
    </div>
  );
}
