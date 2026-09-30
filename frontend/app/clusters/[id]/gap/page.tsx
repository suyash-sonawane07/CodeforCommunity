import { redirect } from "next/navigation";

interface Props {
  params: { id: string };
}

export default function GapViewPage({ params }: Props) {
  redirect(`/clusters/${params.id}`);
}
