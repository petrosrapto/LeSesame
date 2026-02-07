export interface UserProfile {
  displayName: string;
  accent: string;
}

const PROFILE_STORAGE_KEY = "le-sesame-profile";

export function getInitials(name: string): string {
  if (!name) return "??";
  const parts = name.trim().split(/\s+/);
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return `${parts[0][0]}${parts[1][0]}`.toUpperCase();
}

export function getStoredProfile(): UserProfile | null {
  try {
    if (typeof window === "undefined") return null;
    const raw = localStorage.getItem(PROFILE_STORAGE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as UserProfile;
    if (!parsed?.displayName || !parsed?.accent) return null;
    return parsed;
  } catch {
    return null;
  }
}

export function storeProfile(profile: UserProfile): void {
  try {
    if (typeof window === "undefined") return;
    localStorage.setItem(PROFILE_STORAGE_KEY, JSON.stringify(profile));
    window.dispatchEvent(new CustomEvent("profile-updated"));
  } catch {
    // Ignore storage errors.
  }
}
