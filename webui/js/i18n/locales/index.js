import en from "./en.js";
import ko from "./ko.js";

export const DEFAULT_LOCALE = "en";

// Add WebUI languages by creating a locale module next to this file and
// registering it here. English stays in the HTML as the fallback text.
export const LOCALES = Object.freeze({
  en,
  ko,
});
