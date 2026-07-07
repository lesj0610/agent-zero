import { DEFAULT_LOCALE, LOCALES } from "./locales/index.js";

const LOCALE_STORAGE_KEY = "a0:webui-locale";
const STATIC_ATTRIBUTE_NAMES = ["title", "aria-label", "placeholder", "data-placeholder"];
const TRANSLATABLE_SELECTOR = [
  "[data-i18n-scope]",
  "[data-i18n]",
  "[data-i18n-title]",
  "[data-i18n-aria-label]",
  "[data-i18n-placeholder]",
  "[data-i18n-alt]",
  "[data-i18n-data-placeholder]",
].join(",");
const STATIC_SKIP_SELECTOR = [
  "script",
  "style",
  "code",
  "pre",
  "textarea",
  "[x-text]",
  "[x-html]",
  ".material-symbols-outlined",
].join(",");
const staticTextFallbacks = new WeakMap();
const staticAttributeFallbacks = new WeakMap();
const reactiveLocaleState = {
  locale: DEFAULT_LOCALE,
  preference: DEFAULT_LOCALE,
};
const pendingTranslationRoots = new Set();
let dynamicTranslationFlushQueued = false;
let alpineTranslationHookRegistered = false;

function normalizeLocale(locale) {
  const code = String(locale || "").toLowerCase().replaceAll("_", "-");
  if (LOCALES[code]) return code;
  const language = code.split("-")[0];
  return LOCALES[language] ? language : DEFAULT_LOCALE;
}

export function getLocalePreference() {
  try {
    return normalizeLocale(localStorage.getItem(LOCALE_STORAGE_KEY) || DEFAULT_LOCALE);
  } catch {
    return DEFAULT_LOCALE;
  }
}

export function getCurrentLocale() {
  return getLocalePreference();
}

function getI18nStore() {
  try {
    return globalThis.Alpine?.store?.("i18n");
  } catch {
    return null;
  }
}

function setReactiveLocale(locale, preference = locale) {
  reactiveLocaleState.locale = locale;
  reactiveLocaleState.preference = preference;
  const store = getI18nStore();
  if (store) {
    store.locale = locale;
    store.preference = preference;
  }
}

function getReactiveLocale() {
  return normalizeLocale(getI18nStore()?.locale || reactiveLocaleState.locale || getCurrentLocale());
}

function registerI18nStore() {
  const register = () => {
    const existing = getI18nStore();
    if (existing) {
      existing.locale = reactiveLocaleState.locale;
      existing.preference = reactiveLocaleState.preference;
      return;
    }
    globalThis.Alpine.store("i18n", { ...reactiveLocaleState });
  };

  if (globalThis.Alpine) {
    register();
  } else {
    document.addEventListener("alpine:init", register, { once: true });
  }
}

function getElementNodeType() {
  return globalThis.Node?.ELEMENT_NODE ?? 1;
}

function getDynamicTranslationRoot(node) {
  if (!node || node.nodeType !== getElementNodeType()) return null;
  const hasTranslationTarget =
    node.matches?.(TRANSLATABLE_SELECTOR) || node.querySelector?.(TRANSLATABLE_SELECTOR);
  if (!hasTranslationTarget) return null;
  return node.closest?.("[data-i18n-scope]") || node;
}

function flushDynamicTranslations() {
  const roots = Array.from(pendingTranslationRoots);
  pendingTranslationRoots.clear();
  dynamicTranslationFlushQueued = false;

  for (const root of roots) {
    if (root === document || root.isConnected) {
      scheduleTranslations(root);
    }
  }
}

function queueDynamicTranslations(root) {
  if (!root) return;
  pendingTranslationRoots.add(root);
  if (dynamicTranslationFlushQueued) return;
  dynamicTranslationFlushQueued = true;

  if (typeof queueMicrotask === "function") {
    queueMicrotask(flushDynamicTranslations);
  } else {
    Promise.resolve().then(flushDynamicTranslations);
  }
}

function registerAlpineTranslationHook() {
  const register = () => {
    if (alpineTranslationHookRegistered || !globalThis.Alpine?.interceptInit) return;
    alpineTranslationHookRegistered = true;
    globalThis.Alpine.interceptInit((el) => {
      queueDynamicTranslations(getDynamicTranslationRoot(el));
    });
  };

  if (globalThis.Alpine?.interceptInit) {
    register();
  } else {
    document.addEventListener("alpine:init", register, { once: true });
  }
}

function setDocumentLocale(locale) {
  document.documentElement.lang = LOCALES[locale]?.htmlLang || locale;
}

function dispatchLocaleChanged(locale, preference = locale) {
  document.dispatchEvent(
    new CustomEvent("a0:locale-changed", {
      detail: { locale, preference },
    })
  );
}

export function isSupportedLocalePreference(preference) {
  const code = String(preference || "").toLowerCase().replaceAll("_", "-");
  const language = code.split("-")[0];
  return Boolean(LOCALES[code] || LOCALES[language]);
}

function translate(locale, key, fallback = "", params = {}) {
  let value = LOCALES[locale]?.messages?.[key] ?? fallback ?? key;
  for (const [name, replacement] of Object.entries(params || {})) {
    value = String(value).replaceAll(`{${name}}`, String(replacement));
  }
  return value;
}

export function t(key, fallback = "", params = {}) {
  return translate(getCurrentLocale(), key, fallback, params);
}

function normalizeStaticText(value = "") {
  return String(value).replace(/\s+/g, " ").trim();
}

function preserveOuterWhitespace(original, translated) {
  const leading = String(original).match(/^\s*/)?.[0] || "";
  const trailing = String(original).match(/\s*$/)?.[0] || "";
  return `${leading}${translated}${trailing}`;
}

export function translateStaticText(value = "") {
  const original = String(value ?? "");
  const key = normalizeStaticText(original);
  if (!key) return original;
  const locale = getReactiveLocale();
  const translated = LOCALES[locale]?.staticText?.[key];
  return translated ? preserveOuterWhitespace(original, translated) : original;
}

export function getLocaleOptions() {
  return Object.entries(LOCALES).map(([value, config]) => ({ value, label: config.label }));
}

export function setLocalePreference(preference) {
  const nextPreference = isSupportedLocalePreference(preference) ? normalizeLocale(preference) : DEFAULT_LOCALE;
  try {
    localStorage.setItem(LOCALE_STORAGE_KEY, nextPreference);
  } catch {}

  const locale = nextPreference;
  setReactiveLocale(locale, nextPreference);
  setDocumentLocale(locale);
  applyTranslations(document);
  dispatchLocaleChanged(locale, nextPreference);
}

function applyText(el) {
  const key = el.getAttribute("data-i18n");
  if (!key) return;
  if (!el.hasAttribute("data-i18n-fallback")) {
    el.setAttribute("data-i18n-fallback", el.textContent ?? "");
  }
  const fallback = el.getAttribute("data-i18n-fallback");
  el.textContent = t(key, fallback);
}

function applyAttribute(el, dataAttr, targetAttr) {
  const key = el.getAttribute(dataAttr);
  if (!key) return;
  const fallbackAttr = `data-i18n-${targetAttr}-fallback`;
  if (!el.hasAttribute(fallbackAttr)) {
    el.setAttribute(fallbackAttr, el.getAttribute(targetAttr) ?? "");
  }
  const fallback = el.getAttribute(fallbackAttr);
  el.setAttribute(targetAttr, t(key, fallback));
}

function shouldSkipStaticTextNode(node) {
  const parent = node.parentElement;
  if (!parent) return true;
  if (!normalizeStaticText(node.nodeValue)) return true;
  if (parent.closest(STATIC_SKIP_SELECTOR)) return true;
  return Boolean(parent.closest("[data-i18n]"));
}

function getScopedStaticRoots(root) {
  const roots = [];
  if (root.nodeType === Node.ELEMENT_NODE && root.matches?.("[data-i18n-scope]")) {
    roots.push(root);
  }
  roots.push(...(root.querySelectorAll?.("[data-i18n-scope]") || []));
  return roots;
}

function applyScopedStaticText(scopeRoot) {
  const walker = document.createTreeWalker(scopeRoot, NodeFilter.SHOW_TEXT, {
    acceptNode(node) {
      return shouldSkipStaticTextNode(node) ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT;
    },
  });

  let node = walker.nextNode();
  while (node) {
    if (!staticTextFallbacks.has(node)) {
      staticTextFallbacks.set(node, node.nodeValue ?? "");
    }
    node.nodeValue = translateStaticText(staticTextFallbacks.get(node));
    node = walker.nextNode();
  }
}

function getStaticAttributeFallbacks(el) {
  let fallbacks = staticAttributeFallbacks.get(el);
  if (!fallbacks) {
    fallbacks = {};
    staticAttributeFallbacks.set(el, fallbacks);
  }
  return fallbacks;
}

function applyScopedStaticAttributes(scopeRoot) {
  const elements = [scopeRoot, ...(scopeRoot.querySelectorAll?.("*") || [])];
  const locale = getCurrentLocale();
  for (const el of elements) {
    if (el.closest?.(STATIC_SKIP_SELECTOR)) continue;
    const fallbacks = getStaticAttributeFallbacks(el);
    for (const attr of STATIC_ATTRIBUTE_NAMES) {
      if (!el.hasAttribute?.(attr)) continue;
      if (el.hasAttribute(`data-i18n-${attr}`)) continue;
      if (fallbacks[attr] === undefined) {
        fallbacks[attr] = el.getAttribute(attr) ?? "";
      }
      const fallback = fallbacks[attr];
      const key = normalizeStaticText(fallback);
      const translated = LOCALES[locale]?.staticAttributes?.[attr]?.[key]
        ?? LOCALES[locale]?.staticText?.[key]
        ?? fallback;
      el.setAttribute(attr, translated);
    }
  }
}

function applyScopedStaticTranslations(root) {
  for (const scopeRoot of getScopedStaticRoots(root)) {
    applyScopedStaticText(scopeRoot);
    applyScopedStaticAttributes(scopeRoot);
  }
}

export function applyTranslations(root = document) {
  if (!root) return;
  const elements = [];
  if (root.nodeType === Node.ELEMENT_NODE) {
    elements.push(root);
  }
  const translatable = root.querySelectorAll?.(
    [
      "[data-i18n]",
      "[data-i18n-title]",
      "[data-i18n-aria-label]",
      "[data-i18n-placeholder]",
      "[data-i18n-alt]",
      "[data-i18n-data-placeholder]",
    ].join(",")
  ) || [];
  elements.push(...translatable);

  for (const el of elements) {
    applyText(el);
    applyAttribute(el, "data-i18n-title", "title");
    applyAttribute(el, "data-i18n-aria-label", "aria-label");
    applyAttribute(el, "data-i18n-placeholder", "placeholder");
    applyAttribute(el, "data-i18n-alt", "alt");
    applyAttribute(el, "data-i18n-data-placeholder", "data-placeholder");
  }
  applyScopedStaticTranslations(root);
}

export function scheduleTranslations(root = document) {
  if (!root) return;
  applyTranslations(root);

  const reapply = () => applyTranslations(root);
  if (typeof queueMicrotask === "function") {
    queueMicrotask(reapply);
  } else {
    Promise.resolve().then(reapply);
  }

  if (globalThis.Alpine?.nextTick) {
    globalThis.Alpine.nextTick(reapply);
  } else {
    document.addEventListener("alpine:init", () => {
      if (globalThis.Alpine?.nextTick) {
        globalThis.Alpine.nextTick(reapply);
      } else {
        reapply();
      }
    }, { once: true });
    document.addEventListener("alpine:initialized", reapply, { once: true });
  }

  if (typeof requestAnimationFrame === "function") {
    requestAnimationFrame(reapply);
  } else {
    setTimeout(reapply, 0);
  }
}

export function initI18n() {
  const locale = getCurrentLocale();
  const preference = getLocalePreference();
  setReactiveLocale(locale, preference);
  registerI18nStore();
  registerAlpineTranslationHook();
  setDocumentLocale(locale);
  scheduleTranslations(document);

  const reapplyInitialLocale = () => {
    const currentLocale = getCurrentLocale();
    const currentPreference = getLocalePreference();
    setReactiveLocale(currentLocale, currentPreference);
    setDocumentLocale(currentLocale);
    scheduleTranslations(document);
    dispatchLocaleChanged(currentLocale, currentPreference);
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", reapplyInitialLocale, { once: true });
  } else {
    queueMicrotask(reapplyInitialLocale);
  }
  window.addEventListener("load", reapplyInitialLocale, { once: true });
}

globalThis.A0_I18N = {
  getLocalePreference,
  getCurrentLocale,
  setLocalePreference,
  scheduleTranslations,
  translateStaticText,
  t,
};
