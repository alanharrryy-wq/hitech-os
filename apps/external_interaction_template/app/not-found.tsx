import Link from "next/link";
import { Radar, SearchX } from "lucide-react";

import { Button } from "@components/ui/button";
import { StatusPanel } from "@components/ui/status-panel";

export default function NotFound() {
  return (
    <div className="grid min-h-[60vh] place-items-center px-4 py-10">
      <StatusPanel
        tone="warning"
        size="lg"
        icon={<SearchX className="h-6 w-6" />}
        eyebrow="Not found"
        title="This route is missing from the constellation"
        description="The page or record you asked for is not available, or the identifier no longer maps to an active resource."
        actions={
          <div className="flex flex-wrap gap-2">
            <Link href="/">
              <Button variant="primary">
                <Radar className="mr-1.5 h-4 w-4" />
                Return to launcher
              </Button>
            </Link>
            <Link href="/inbox">
              <Button variant="ghost">Open inbox</Button>
            </Link>
          </div>
        }
      />
    </div>
  );
}
