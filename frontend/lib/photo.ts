import { API, clientId, ProfileInfo } from "@/lib/api";

/** URL of an uploaded profile photo, or null when the person has none. Works for your own card and for public profiles. */
export function uploadedPhoto(info: Pick<ProfileInfo, "photo" | "username"> | null | undefined, selfFallback = true): string | null {
  if (!info?.photo) return null;
  const key = info.username || (selfFallback ? clientId() : "");
  return key ? `${API}/api/profile/info/avatar/${encodeURIComponent(key)}?v=${info.photo}` : null;
}

/** Reads an image file, centre-crops it to a square and shrinks it to a small JPEG data URL (a few tens of KB). */
export function resizeToDataUrl(file: File, size = 256): Promise<string> {
  return new Promise((resolve, reject) => {
    if (!file.type.startsWith("image/")) { reject(new Error("Please choose an image file.")); return; }
    const url = URL.createObjectURL(file);
    const img = new Image();
    img.onload = () => {
      try {
        const side = Math.min(img.width, img.height);
        const canvas = document.createElement("canvas");
        canvas.width = canvas.height = size;
        const ctx = canvas.getContext("2d");
        if (!ctx) throw new Error("Your browser could not process the image.");
        ctx.drawImage(img, (img.width - side) / 2, (img.height - side) / 2, side, side, 0, 0, size, size);
        resolve(canvas.toDataURL("image/jpeg", 0.85));
      } catch (e) { reject(e as Error); } finally { URL.revokeObjectURL(url); }
    };
    img.onerror = () => { URL.revokeObjectURL(url); reject(new Error("That image could not be read.")); };
    img.src = url;
  });
}
