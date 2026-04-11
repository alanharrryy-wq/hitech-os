import { promises as fs } from "fs";
import path from "path";

import { NextResponse } from "next/server";

import { getActorFromHeaders } from "@/lib/request-context";
import { addAttachmentMetadata } from "@/lib/services/records";

interface RouteContext {
  params: Promise<{ recordId: string }>;
}

const ATTACHMENT_DIR = path.resolve(process.cwd(), "storage", "attachments");

export async function POST(request: Request, context: RouteContext) {
  const { recordId } = await context.params;
  const actor = await getActorFromHeaders();

  try {
    const formData = await request.formData();
    const file = formData.get("file");
    if (!(file instanceof File)) {
      return NextResponse.json({ error: "Missing file" }, { status: 400 });
    }

    const extension = file.name.includes(".") ? file.name.slice(file.name.lastIndexOf(".")) : "";
    const storageKey = `${recordId}_${Date.now()}${extension}`;

    await fs.mkdir(ATTACHMENT_DIR, { recursive: true });
    const bytes = Buffer.from(await file.arrayBuffer());
    const outputPath = path.join(ATTACHMENT_DIR, storageKey);
    await fs.writeFile(outputPath, bytes);

    const attachment = await addAttachmentMetadata(recordId, actor, {
      name: file.name,
      mimeType: file.type,
      size: file.size,
      storageKey
    });

    return NextResponse.json({ attachment }, { status: 201 });
  } catch (error) {
    return NextResponse.json(
      {
        error: error instanceof Error ? error.message : "Attachment upload failed"
      },
      { status: 400 }
    );
  }
}
