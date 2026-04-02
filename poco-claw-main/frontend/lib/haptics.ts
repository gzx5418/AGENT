/**
 * Haptic feedback utilities for mobile and supported browsers
 */

/**
 * Trigger a success haptic feedback
 * A short, strong vibration to confirm successful completion
 */
export function triggerSuccessHaptic() {
  if (typeof window !== "undefined" && "vibrate" in navigator) {
    // Short, strong vibration pattern for success
    navigator.vibrate(50);
  }
}

/**
 * Trigger a light haptic feedback
 * A very short, gentle vibration for UI interactions
 */
export function triggerLightHaptic() {
  if (typeof window !== "undefined" && "vibrate" in navigator) {
    navigator.vibrate(10);
  }
}

/**
 * Trigger an error haptic feedback
 * A pattern of vibrations to indicate an error
 */
export function triggerErrorHaptic() {
  if (typeof window !== "undefined" && "vibrate" in navigator) {
    navigator.vibrate([50, 50, 50]);
  }
}
