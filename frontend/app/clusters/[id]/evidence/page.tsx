import { redirect } from "next/navigation";

interface Props {
  params: { id: string };
}

export default function EvidencePanelPage({ params }: Props) {
  redirect(`/clusters/${params.id}`);
}
