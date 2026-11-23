"use client";
import { useEffect } from "react";

export default function SettingsIndex() {
  useEffect(() => { window.location.replace("/settings/profile"); }, []);
  return null;
}
