import { redirect } from "next/navigation";

export default async function Page({
  params,
}: {
  params: Promise<{ lng: string }>;
}) {
  const { lng } = await params;
  redirect(`/${lng}/home`);
}
