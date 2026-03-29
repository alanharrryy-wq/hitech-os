import { notFound } from "next/navigation";
import { StyleLabClient } from "./StyleLabClient";

export const dynamic = "force-dynamic";
export const revalidate = 0;

export default function StyleLabPage() {
  if (process.env.NODE_ENV === "production") {
    notFound();
  }

  return <StyleLabClient />;
}
