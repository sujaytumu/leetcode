import { useId } from "react";

/** The app's own mark: an amber rounded tile with code brackets and a slash. */
export default function Logo({ size = 28 }: { size?: number }) {
  const gid = `lm-${useId().replace(/:/g, "")}`;
  return (
    <svg width={size} height={size} viewBox="0 0 32 32" role="img" aria-label="LeetCode Practice" className="logomark">
      <defs>
        <linearGradient id={gid} x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#ffc01e" />
          <stop offset="1" stopColor="#ff7a18" />
        </linearGradient>
      </defs>
      <rect width="32" height="32" rx="8" fill={`url(#${gid})`} />
      <path d="M12.5 10.5 7 16l5.5 5.5M19.5 10.5 25 16l-5.5 5.5" fill="none" stroke="#1a1206" strokeWidth="2.6" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M17.6 9.5 14.4 22.5" stroke="#1a1206" strokeWidth="2.6" strokeLinecap="round" />
    </svg>
  );
}
