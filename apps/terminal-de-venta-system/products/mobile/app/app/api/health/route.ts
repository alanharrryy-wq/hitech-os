export const dynamic = "force-dynamic";
export const revalidate = 0;

export async function GET() {
  return Response.json({
    system: "PRISMA",
    app: "mobile-adder",
    status: "ok"
  });
}
