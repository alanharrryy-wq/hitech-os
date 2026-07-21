-- PRISMA_PRICING_OWNER_V1
ALTER TABLE "PriceList" ADD COLUMN "idempotencyKey" TEXT;
ALTER TABLE "PriceList" ADD COLUMN "version" INTEGER NOT NULL DEFAULT 1;
ALTER TABLE "PriceListItem" ADD COLUMN "idempotencyKey" TEXT;
ALTER TABLE "PriceListItem" ADD COLUMN "version" INTEGER NOT NULL DEFAULT 1;
ALTER TABLE "TaxRate" ADD COLUMN "idempotencyKey" TEXT;
ALTER TABLE "TaxRate" ADD COLUMN "version" INTEGER NOT NULL DEFAULT 1;

CREATE UNIQUE INDEX "PriceList_businessId_idempotencyKey_key" ON "PriceList"("businessId", "idempotencyKey");
CREATE UNIQUE INDEX "PriceListItem_businessId_idempotencyKey_key" ON "PriceListItem"("businessId", "idempotencyKey");
CREATE UNIQUE INDEX "TaxRate_businessId_idempotencyKey_key" ON "TaxRate"("businessId", "idempotencyKey");

CREATE TABLE "PromotionRule" (
  "id" TEXT NOT NULL PRIMARY KEY,
  "businessId" TEXT NOT NULL,
  "name" TEXT NOT NULL,
  "description" TEXT,
  "ruleType" TEXT NOT NULL,
  "priority" INTEGER NOT NULL DEFAULT 100,
  "stackingPolicy" TEXT NOT NULL DEFAULT 'EXCLUSIVE',
  "eligibilityJson" TEXT NOT NULL,
  "benefitJson" TEXT NOT NULL,
  "startsAt" DATETIME NOT NULL,
  "endsAt" DATETIME,
  "status" TEXT NOT NULL DEFAULT 'ACTIVE',
  "idempotencyKey" TEXT,
  "version" INTEGER NOT NULL DEFAULT 1,
  "createdById" TEXT,
  "updatedById" TEXT,
  "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updatedAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "PromotionRule_businessId_fkey" FOREIGN KEY ("businessId") REFERENCES "Business" ("id") ON DELETE CASCADE ON UPDATE CASCADE
);
CREATE UNIQUE INDEX "PromotionRule_businessId_name_key" ON "PromotionRule"("businessId", "name");
CREATE UNIQUE INDEX "PromotionRule_businessId_idempotencyKey_key" ON "PromotionRule"("businessId", "idempotencyKey");
CREATE INDEX "PromotionRule_businessId_status_priority_idx" ON "PromotionRule"("businessId", "status", "priority");
CREATE INDEX "PromotionRule_businessId_startsAt_endsAt_idx" ON "PromotionRule"("businessId", "startsAt", "endsAt");

CREATE TABLE "PricingAuthorizationRule" (
  "id" TEXT NOT NULL PRIMARY KEY,
  "businessId" TEXT NOT NULL,
  "name" TEXT NOT NULL,
  "actionType" TEXT NOT NULL,
  "thresholdType" TEXT NOT NULL,
  "thresholdValue" INTEGER NOT NULL,
  "requiredPermission" TEXT NOT NULL,
  "status" TEXT NOT NULL DEFAULT 'ACTIVE',
  "idempotencyKey" TEXT,
  "version" INTEGER NOT NULL DEFAULT 1,
  "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updatedAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "PricingAuthorizationRule_businessId_fkey" FOREIGN KEY ("businessId") REFERENCES "Business" ("id") ON DELETE CASCADE ON UPDATE CASCADE
);
CREATE UNIQUE INDEX "PricingAuthorizationRule_businessId_name_key" ON "PricingAuthorizationRule"("businessId", "name");
CREATE UNIQUE INDEX "PricingAuthorizationRule_businessId_idempotencyKey_key" ON "PricingAuthorizationRule"("businessId", "idempotencyKey");
CREATE UNIQUE INDEX "PricingAuthorizationRule_id_businessId_key" ON "PricingAuthorizationRule"("id", "businessId");
CREATE INDEX "PricingAuthorizationRule_businessId_status_actionType_idx" ON "PricingAuthorizationRule"("businessId", "status", "actionType");

CREATE TABLE "DiscountPolicy" (
  "id" TEXT NOT NULL PRIMARY KEY,
  "businessId" TEXT NOT NULL,
  "name" TEXT NOT NULL,
  "discountType" TEXT NOT NULL,
  "valueBps" INTEGER,
  "valueCents" INTEGER,
  "minimumSubtotalCents" INTEGER NOT NULL DEFAULT 0,
  "maximumDiscountCents" INTEGER,
  "scopeJson" TEXT NOT NULL,
  "authorizationRuleId" TEXT,
  "startsAt" DATETIME NOT NULL,
  "endsAt" DATETIME,
  "status" TEXT NOT NULL DEFAULT 'ACTIVE',
  "idempotencyKey" TEXT,
  "version" INTEGER NOT NULL DEFAULT 1,
  "createdById" TEXT,
  "updatedById" TEXT,
  "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updatedAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "DiscountPolicy_businessId_fkey" FOREIGN KEY ("businessId") REFERENCES "Business" ("id") ON DELETE CASCADE ON UPDATE CASCADE
);
CREATE UNIQUE INDEX "DiscountPolicy_businessId_name_key" ON "DiscountPolicy"("businessId", "name");
CREATE UNIQUE INDEX "DiscountPolicy_businessId_idempotencyKey_key" ON "DiscountPolicy"("businessId", "idempotencyKey");
CREATE INDEX "DiscountPolicy_businessId_status_startsAt_idx" ON "DiscountPolicy"("businessId", "status", "startsAt");
CREATE INDEX "DiscountPolicy_businessId_authorizationRuleId_idx" ON "DiscountPolicy"("businessId", "authorizationRuleId");

CREATE TABLE "PricingAuthorizationRequest" (
  "id" TEXT NOT NULL PRIMARY KEY,
  "businessId" TEXT NOT NULL,
  "ruleId" TEXT NOT NULL,
  "requestedById" TEXT,
  "requestedActionJson" TEXT NOT NULL,
  "reason" TEXT NOT NULL,
  "status" TEXT NOT NULL DEFAULT 'PENDING',
  "decidedById" TEXT,
  "decisionReason" TEXT,
  "decidedAt" DATETIME,
  "idempotencyKey" TEXT,
  "version" INTEGER NOT NULL DEFAULT 1,
  "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updatedAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "PricingAuthorizationRequest_businessId_fkey" FOREIGN KEY ("businessId") REFERENCES "Business" ("id") ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT "PricingAuthorizationRequest_ruleId_businessId_fkey" FOREIGN KEY ("ruleId", "businessId") REFERENCES "PricingAuthorizationRule" ("id", "businessId") ON DELETE RESTRICT ON UPDATE CASCADE
);
CREATE UNIQUE INDEX "PricingAuthorizationRequest_businessId_idempotencyKey_key" ON "PricingAuthorizationRequest"("businessId", "idempotencyKey");
CREATE INDEX "PricingAuthorizationRequest_businessId_status_createdAt_idx" ON "PricingAuthorizationRequest"("businessId", "status", "createdAt");
CREATE INDEX "PricingAuthorizationRequest_businessId_ruleId_idx" ON "PricingAuthorizationRequest"("businessId", "ruleId");
