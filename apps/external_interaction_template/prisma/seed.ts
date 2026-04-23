import { PrismaClient } from "@prisma/client";

import { listSchemas } from "../src/lib/core/schema-registry";
import { randomToken } from "../src/lib/utils";

const prisma = new PrismaClient();

async function main() {
  const schemas = listSchemas();

  for (const schema of schemas) {
    await prisma.recordType.upsert({
      where: { schemaId: schema.id },
      create: {
        schemaId: schema.id,
        title: schema.title,
        summary: schema.summary,
        category: schema.category,
        config: JSON.stringify(schema)
      },
      update: {
        title: schema.title,
        summary: schema.summary,
        category: schema.category,
        config: JSON.stringify(schema)
      }
    });
  }

  const operator = await prisma.actor.upsert({
    where: { token: "seed_operator" },
    create: {
      label: "Seed Operator",
      role: "operator",
      token: "seed_operator"
    },
    update: {
      label: "Seed Operator",
      role: "operator"
    }
  });

  const requestType = await prisma.recordType.findUnique({ where: { schemaId: "service_request" } });
  if (!requestType) {
    throw new Error("service_request schema not found");
  }

  const approvalType = await prisma.recordType.findUnique({ where: { schemaId: "approval_packet" } });
  if (!approvalType) {
    throw new Error("approval_packet schema not found");
  }

  const inspectionType = await prisma.recordType.findUnique({ where: { schemaId: "inspection_checklist" } });
  if (!inspectionType) {
    throw new Error("inspection_checklist schema not found");
  }

  const seedRecords = [
    {
      typeId: requestType.id,
      title: "Cooling unit request",
      state: "submitted" as const,
      fields: {
        request_title: "Cooling unit request",
        request_description: "Need replacement on line 4 unit",
        request_priority: "high",
        requester_name: "Kai R.",
        requester_email: "kai@example.net",
        region: "north"
      }
    },
    {
      typeId: approvalType.id,
      title: "Vendor package approval",
      state: "in_review" as const,
      fields: {
        packet_title: "Vendor package approval",
        packet_owner: "Nia",
        packet_scope: "Approve rollout package for Q3",
        risk_level: "moderate",
        compliance_reviewed: true
      }
    },
    {
      typeId: inspectionType.id,
      title: "Facility inspection north-22",
      state: "awaiting_update" as const,
      fields: {
        site_name: "north-22",
        inspector: "Liam",
        inspection_date: new Date().toISOString().slice(0, 10),
        inspection_type: "routine",
        condition_score: 72,
        requires_follow_up: true,
        findings: "Corrosion near valve lane B"
      }
    }
  ];

  for (const seed of seedRecords) {
    const existing = await prisma.externalRecord.findFirst({
      where: {
        title: seed.title
      }
    });

    if (existing) continue;

    const record = await prisma.externalRecord.create({
      data: {
        recordTypeId: seed.typeId,
        actorId: operator.id,
        title: seed.title,
        state: seed.state,
        fields: JSON.stringify(seed.fields),
        secureToken: randomToken("seed")
      }
    });

    await prisma.submission.create({
      data: {
        recordId: record.id,
        actorId: operator.id,
        stepId: "seed",
        payload: JSON.stringify({
          seeded: true
        })
      }
    });

    await prisma.syncEvent.create({
      data: {
        recordId: record.id,
        direction: "inbound",
        adapterId: "local",
        status: "pending",
        summary: "Seeded record",
        payload: JSON.stringify({
          source: "seed"
        })
      }
    });
  }
}

main()
  .then(async () => {
    await prisma.$disconnect();
  })
  .catch(async (error) => {
    console.error(error);
    await prisma.$disconnect();
    process.exit(1);
  });
