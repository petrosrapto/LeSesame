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
      className={cn("text-gold-500", className)}
    >
      {/* Key shape */}
      <circle
        cx="24"
        cy="16"
        r="10"
        stroke="currentColor"
        strokeWidth="2.5"
        fill="none"
      />
      <circle cx="24" cy="16" r="4" fill="currentColor" opacity="0.3" />
      
      {/* Key stem */}
      <rect
        x="22"
        y="26"
        width="4"
        height="18"
        rx="2"
        fill="currentColor"
      />
      
      {/* Key teeth */}
      <rect x="26" y="36" width="6" height="3" rx="1" fill="currentColor" />
      <rect x="26" y="42" width="4" height="3" rx="1" fill="currentColor" />
      
      {/* Decorative elements */}
      <circle cx="24" cy="16" r="13" stroke="currentColor" strokeWidth="1" opacity="0.2" />
      
      {/* Sparkle effects */}
      <circle cx="34" cy="10" r="1.5" fill="currentColor" opacity="0.6" />
      <circle cx="14" cy="22" r="1" fill="currentColor" opacity="0.4" />
    </svg>
  );
}

export function LogoLarge({ className }: LogoProps) {
  return (
    <div className={cn("flex items-center gap-3", className)}>
      <Logo className="h-10 w-10" />
      <div className="flex flex-col">
        <span className="font-display text-2xl font-bold gradient-text leading-tight">
          Le Sésame
        </span>
        <span className="text-xs text-muted-foreground tracking-wider uppercase">
          The Secret Keeper
        </span>
      </div>
    </div>
  );
}
