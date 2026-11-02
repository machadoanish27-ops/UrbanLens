/**
 * Reusable utility for safe external URL handling and sanitization.
 */

const SAFE_PROTOCOLS = new Set(['http:', 'https:']);

/**
 * Sanitize an external URL. Returns null if invalid or unsafe.
 */
export function sanitizeExternalUrl(url?: string | null): string | null {
  if (!url || typeof url !== 'string') return null;

  const trimmed = url.trim();
  if (!trimmed || trimmed.toLowerCase() === 'nan' || trimmed.toLowerCase() === 'null' || trimmed === '#') {
    return null;
  }

  // Strictly block unsafe schemes
  const lower = trimmed.toLowerCase();
  if (
    lower.startsWith('javascript:') ||
    lower.startsWith('data:') ||
    lower.startsWith('vbscript:') ||
    lower.startsWith('file:')
  ) {
    return null;
  }

  const withProto = lower.startsWith('http://') || lower.startsWith('https://')
    ? trimmed
    : `https://${trimmed}`;

  try {
    const parsed = new URL(withProto);
    if (!SAFE_PROTOCOLS.has(parsed.protocol)) {
      return null;
    }
    // Must contain valid hostname with dot or localhost
    if (!parsed.hostname || (!parsed.hostname.includes('.') && parsed.hostname !== 'localhost')) {
      return null;
    }
    return parsed.toString();
  } catch {
    return null;
  }
}

/**
 * Extract human-readable domain name for external links.
 */
export function getDisplayDomain(url?: string | null, fallback = 'Official Portal'): string {
  const sanitized = sanitizeExternalUrl(url);
  if (!sanitized) return fallback;
  try {
    const parsed = new URL(sanitized);
    return parsed.hostname.replace(/^www\./, '');
  } catch {
    return fallback;
  }
}

/**
 * Check if URL is valid and safe to navigate.
 */
export function isValidExternalUrl(url?: string | null): boolean {
  return sanitizeExternalUrl(url) !== null;
}
