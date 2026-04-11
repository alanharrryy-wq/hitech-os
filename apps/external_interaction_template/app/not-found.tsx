"use client";

import Link from "next/link";
import { Radar, SearchX } from "lucide-react";

import { Button } from "@components/ui/button";
import { StatusPanel } from "@components/ui/status-panel";

import { useT } from "@/lib/i18n/use-t";

export default function NotFound() {
  const t = useT();

  return (
    <div className="grid min-h-[60vh] place-items-center px-4 py-10">
      <StatusPanel
        tone="warning"
        size="lg"
        icon={<SearchX className="h-6 w-6" />}
        eyebrow={t("status.notFound.eyebrow")}
        title={t("status.notFound.title")}
        description={t("status.notFound.description")}
        actions={
          <div className="flex flex-wrap gap-2">
            <Link href="/">
              <Button variant="primary">
                <Radar className="mr-1.5 h-4 w-4" />
                {t("status.notFound.goHome")}
              </Button>
            </Link>
            <Link href="/inbox">
              <Button variant="ghost">{t("status.notFound.openInbox")}</Button>
            </Link>
          </div>
        }
      />
    </div>
  );
}
