import Link from "next/link";
import { sheetsOf } from "@/lib/sheets";
import "@/app/striver.css";

/** "A2Z" / "SDE" / "M50" pills for the sheets a problem is on; renders nothing for any other problem. */
export default function SheetPills({ tags }: { tags: readonly string[] }) {
  return (
    <>
      {sheetsOf(tags).map((s) => (
        <Link key={s.tag} href={`/striver?sheet=${s.short.toLowerCase()}`} className={`sheetpill ${s.short}`} title={`${s.full}: open the sheet`}>
          {s.short}
        </Link>
      ))}
    </>
  );
}
