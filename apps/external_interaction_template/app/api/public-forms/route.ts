import { NextResponse } from "next/server";

import { listPublicFormRegistrations } from "@/lib/integrations/public-forms";

export async function GET() {
  return NextResponse.json({
    forms: listPublicFormRegistrations()
  });
}

