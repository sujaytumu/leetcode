import type { ReactNode } from "react";

const S = { width: 24, height: 24, viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", strokeWidth: 1.8, strokeLinecap: "round" as const, strokeLinejoin: "round" as const, "aria-hidden": true };
const I = (children: ReactNode) => <svg {...S}>{children}</svg>;

export const ICONS: Record<string, ReactNode> = {
  displayName: I(<><circle cx="12" cy="8" r="4" fill="currentColor" stroke="none" /><path d="M4 21c0-4.4 3.6-7 8-7s8 2.6 8 7" fill="currentColor" stroke="none" /></>),
  gender: I(<><circle cx="10" cy="14" r="5" /><path d="M14 10l6-6M15 4h5v5M10 19v3M8 21h4" /></>),
  location: I(<><path d="M12 22s7-6.3 7-12a7 7 0 10-14 0c0 5.7 7 12 7 12z" fill="currentColor" stroke="none" /><circle cx="12" cy="10" r="2.5" fill="var(--panel)" stroke="none" /></>),
  birthday: I(<><path d="M4 21h16v-8H4zM4 17c2 0 2 1.5 4 1.5S10 17 12 17s2 1.5 4 1.5S18 17 20 17" /><path d="M8 13V9M12 13V9M16 13V9M8 6.5v.01M12 6.5v.01M16 6.5v.01" /></>),
  website: I(<><path d="M10 14a4 4 0 005.7 0l3-3a4 4 0 00-5.7-5.7l-1 1M14 10a4 4 0 00-5.7 0l-3 3a4 4 0 005.7 5.7l1-1" /></>),
  github: I(<path d="M12 2a10 10 0 00-3.2 19.5c.5.1.7-.2.7-.5v-1.8c-2.8.6-3.4-1.2-3.4-1.2-.5-1.2-1.1-1.5-1.1-1.5-.9-.6.1-.6.1-.6 1 .1 1.5 1 1.5 1 .9 1.5 2.4 1.1 3 .8.1-.7.4-1.1.6-1.4-2.2-.3-4.6-1.1-4.6-5 0-1.1.4-2 1-2.7-.1-.3-.5-1.300.1-2.700 0 0 .8-.3 2.800 1a9.600 9.600 0 015 0c2-1.300 2.800-1 2.800-1 .6 1.400.2 2.400.1 2.700.7.700 1 1.600 1 2.700 0 3.900-2.400 4.700-4.600 5 .4.300.7.900.7 1.800v2.700c0 .3.200.6.700.5A10 10 0 0012 2z" fill="currentColor" stroke="none" />),
  linkedin: I(<><rect x="3" y="3" width="18" height="18" rx="3" /><path d="M8 10v7M8 7v.01M12 17v-4a2 2 0 014 0v4M12 10v7" /></>),
  company: I(<><path d="M4 21V4h10v17M14 9h6v12M8 8h2M8 12h2M8 16h2" /></>),
  school: I(<><path d="M2 9l10-5 10 5-10 5zM6 11.500V16c0 1.500 3 3 6 3s6-1.500 6-3v-4.500" /></>),
  headline: I(<><path d="M4 6h16M4 12h16M4 18h10" /></>),
  username: I(<><circle cx="12" cy="12" r="4" /><path d="M16 12v1.500a2.500 2.500 0 005 0V12a9 9 0 10-3.500 7.100" /></>),
};

export const SIDEBAR_ICONS: Record<string, ReactNode> = {
  library: I(<><path d="M4 4v16M9 4v16M14 6l4 14M4 4h5" /></>),
  project: I(<><path d="M12 3l8 4.500v9L12 21l-8-4.500v-9zM12 12l8-4.500M12 12v9M12 12L4 7.500" /></>),
  quest: I(<><path d="M5 19L19 5M14 5h5v5M5 5l14 14" /></>),
  explore: I(<><path d="M3 5c3-1.500 6-1.500 9 1 3-2.500 6-2.500 9-1v14c-3-1.500-6-1.500-9 1-3-2.500-6-2.500-9-1z M12 6v14" /></>),
  plan: I(<><path d="M2 10l10-5 10 5-10 5zM6 12v5c0 1 3 3 6 3s6-2 6-3v-5" /></>),
  lock: <svg {...S} width={18} height={18}><rect x="5" y="11" width="14" height="10" rx="2" /><path d="M8 11V8a4 4 0 118 0v3" /></svg>,
  star: <svg {...S} width={18} height={18}><path d="M12 3l2.800 5.800 6.200.9-4.500 4.400 1.100 6.200L12 17.400 6.400 20.300l1.100-6.200L3 9.700l6.200-.9z" fill="#ffa116" stroke="none" /></svg>,
  list: <svg {...S} width={18} height={18}><rect x="5" y="3" width="14" height="18" rx="2" fill="currentColor" stroke="none" opacity=".85" /></svg>,
};
