import { redirect } from "next/navigation";

interface Props {
  params: { id: string };
}

export default function ReviewDetailPage({ params }: Props) {
  redirect(`/clusters/${params.id}`);
}
