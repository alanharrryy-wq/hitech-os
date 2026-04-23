import Link from "next/link";

import { Button } from "@components/ui/button";
import { Input } from "@components/ui/input";
import { Surface } from "@components/ui/surface";

export function ResumeSessionCard({
  schemaId,
  queryToken,
  t
}: {
  schemaId: string;
  queryToken: string;
  t: (key: string, values?: Record<string, string | number>) => string;
}) {
  return (
    <Surface title={t("flow.page.resume.title")} subtitle={t("flow.page.resume.subtitle")} padding="sm">
      <form action={`/flow/${schemaId}`} method="get" className="grid gap-3">
        <label className="grid gap-1.5 text-sm text-muted">
          <span className="eyebrow">{t("flow.page.resume.label")}</span>
          <Input name="token" placeholder={t("flow.page.resume.placeholder")} defaultValue={queryToken} />
        </label>

        <div className="flex flex-wrap gap-2">
          <Button variant="secondary" type="submit">
            {t("flow.page.resume.submit")}
          </Button>
          <Link href={`/flow/${schemaId}`}>
            <Button variant="ghost">{t("flow.page.resume.clear")}</Button>
          </Link>
        </div>

        <p className="text-xs leading-4.5 text-muted">{t("flow.route.resume.hint")}</p>
      </form>
    </Surface>
  );
}
