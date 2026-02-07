import { cn } from "@/lib/utils";

interface LogoProps {
  className?: string;
}

export function Logo({ className }: LogoProps) {
  return (
    <svg
      viewBox="0 0 48 48"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={cn("text-orange-500", className)}
      style={{ imageRendering: "pixelated" }}
    >
      {/* Pixel key shape */}
      <rect x="18" y="4" width="12" height="4" fill="currentColor" />
      <rect x="14" y="8" width="4" height="4" fill="currentColor" />
      <rect x="30" y="8" width="4" height="4" fill="currentColor" />
      <rect x="14" y="12" width="4" height="4" fill="currentColor" />
      <rect x="30" y="12" width="4" height="4" fill="currentColor" />
      <rect x="18" y="16" width="12" height="4" fill="currentColor" />
      {/* Key stem */}
      <rect x="22" y="20" width="4" height="16" fill="currentColor" />
      {/* Key teeth */}
      <rect x="26" y="28" width="6" height="4" fill="currentColor" />
      <rect x="26" y="34" width="4" height="4" fill="currentColor" />
      {/* Key bottom */}
      <rect x="20" y="36" width="8" height="4" fill="currentColor" />
      {/* Inner hole */}
      <rect x="20" y="10" width="8" height="4" fill="currentColor" opacity="0.2" />
      {/* Sparkle pixels */}
      <rect x="36" y="6" width="2" height="2" fill="currentColor" opacity="0.5" />
      <rect x="10" y="18" width="2" height="2" fill="currentColor" opacity="0.3" />
    </svg>
  );
}

export function LogoLarge({ className }: LogoProps) {
  return (
    <div className={cn("flex items-center gap-3", className)}>
      <Logo className="h-10 w-10" />
      <div className="flex flex-col">
        <span className="font-pixel text-lg text-orange-500 leading-tight">
          Le Sésame
        </span>
        <span className="text-xs text-muted-foreground tracking-widest uppercase font-mono">
          Secret Keeper
        </span>
      </div>
    </div>
  );
}
