"use client";

import { GoogleOAuthProvider } from "@react-oauth/google";
import { GoogleReCaptchaProvider } from "react-google-recaptcha-v3";

const GOOGLE_CLIENT_ID = process.env.NEXT_PUBLIC_GOOGLE_OAUTH_CLIENT_ID ?? "";
const RECAPTCHA_SITE_KEY = process.env.NEXT_PUBLIC_RECAPTCHA_SITE_KEY ?? "";

/**
 * Wraps children with Google OAuth + reCAPTCHA v3 providers.
 * Both providers are always mounted so hooks can be called unconditionally.
 * When keys are empty the providers are essentially no-ops (the backend
 * gracefully skips verification when its own keys are not configured).
 */
export function AuthProviders({ children }: { children: React.ReactNode }) {
  return (
    <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID || "not-configured"}>
      <GoogleReCaptchaProvider reCaptchaKey={RECAPTCHA_SITE_KEY || "not-configured"}>
        {children}
      </GoogleReCaptchaProvider>
    </GoogleOAuthProvider>
  );
}
