from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _read(relative_path: str) -> str:
    return (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")


def test_webui_i18n_runtime_is_loaded_and_applies_component_translations() -> None:
    index_js = _read("webui/index.js")
    components_js = _read("webui/js/components.js")
    modals_js = _read("webui/js/modals.js")
    i18n_js = _read("webui/js/i18n/index.js")
    locale_index_js = _read("webui/js/i18n/locales/index.js")
    ko_js = _read("webui/js/i18n/locales/ko.js")

    assert 'import { initI18n, t } from "/js/i18n/index.js";' in index_js
    assert "initI18n();" in index_js
    assert 'import { applyTranslations } from "/js/i18n/index.js";' in components_js
    assert "applyTranslations(targetElement);" in components_js
    assert 'from "./locales/index.js";' in i18n_js
    assert 'replaceAll("_", "-")' in i18n_js
    assert "export function setLocalePreference" in i18n_js
    assert 'globalThis.Alpine.store("i18n"' in i18n_js
    assert "function getReactiveLocale()" in i18n_js
    assert "window.addEventListener(\"load\", reapplyInitialLocale" in i18n_js
    assert "document.dispatchEvent(" in i18n_js
    assert '"a0:locale-changed"' in i18n_js
    assert "globalThis.A0_I18N" in i18n_js
    assert "staticText" in i18n_js
    assert "staticAttributes" in i18n_js
    assert "data-i18n-scope" in i18n_js
    assert "document.createTreeWalker" in i18n_js
    assert ".material-symbols-outlined" in i18n_js
    assert "AUTO_LOCALE" not in i18n_js
    assert "getBrowserLocale" not in i18n_js
    assert 'if (!el.hasAttribute("data-i18n-fallback"))' in i18n_js
    assert "const fallbackAttr = `data-i18n-${targetAttr}-fallback`;" in i18n_js
    assert "if (!el.hasAttribute(fallbackAttr))" in i18n_js
    assert "function isSettingsComponent(componentUrl)" in components_js
    assert 'targetElement.setAttribute("data-i18n-scope", "settings")' in components_js
    assert 'import { translateStaticText } from "/js/i18n/index.js";' in modals_js
    assert "modal.title.textContent = translateStaticText(doc.title || modalPath);" in modals_js
    assert 'import ko from "./ko.js";' in locale_index_js
    assert "ko," in locale_index_js
    assert '"settings.locale.uiLanguage"' in ko_js
    assert "staticText:" in ko_js
    assert "staticAttributes:" in ko_js
    assert '"Agent Config": "Agent 구성"' in ko_js
    assert '"Remote Control": "원격 제어"' in ko_js
    assert '"MCP Servers": "MCP 서버"' in ko_js
    assert '"chat.placeholder.start": "아무거나 물어보면 새 채팅이 시작됩니다"' in ko_js


def test_settings_locale_section_exposes_ui_language_choice() -> None:
    store = _read("webui/components/settings/settings-store.js")
    locale = _read("webui/components/settings/agent/locale.html")
    ko_js = _read("webui/js/i18n/locales/ko.js")
    locale_index_js = _read("webui/js/i18n/locales/index.js")

    assert "labelKey" in store
    assert "localizeNavItem(item)" in store
    assert "get uiLanguageOptions()" in store
    assert "setUiLanguagePreference(value)" in store
    assert "bindUiLocaleRuntime()" in store
    assert "getLocalePreference()" in store
    assert "getLocaleOptions()" in store
    assert 'data-i18n="settings.locale.uiLanguage"' in locale
    assert "uiLocalePreference || 'en'" in locale
    assert "uiLocalePreference || 'auto'" not in locale
    assert "$store.settings.setUiLanguagePreference($event.target.value)" in locale
    assert "option in $store.settings.uiLanguageOptions" in locale
    assert "settings.locale.uiLanguage.auto" not in ko_js
    assert "AUTO_LOCALE" not in locale_index_js


def test_common_webui_surfaces_have_i18n_keys_with_english_fallbacks() -> None:
    surfaces = {
        "index": _read("webui/index.html"),
        "settings": _read("webui/components/settings/settings.html"),
        "welcome": _read("webui/components/welcome/welcome-screen.html"),
        "chat_input": _read("webui/components/chat/input/chat-bar-input.html"),
        "sidebar": _read("webui/components/sidebar/top-section/header-icons.html"),
        "preferences": _read("webui/components/sidebar/bottom/preferences/preferences-panel.html"),
    }

    assert 'data-i18n-title="app.scroll.top"' in surfaces["index"]
    assert 'data-i18n-placeholder="settings.search"' in surfaces["settings"]
    assert 'data-i18n="welcome.title">Hello! I\'m Agent Zero' in surfaces["welcome"]
    assert 'data-i18n-aria-label="chat.moreActions"' in surfaces["chat_input"]
    assert 'data-i18n="sidebar.navigation">Navigation' in surfaces["sidebar"]
    assert 'data-i18n="preferences.title">Preferences' in surfaces["preferences"]


def test_settings_dynamic_surfaces_use_i18n_helpers() -> None:
    tunnel_store = _read("webui/components/settings/tunnel/tunnel-store.js")
    mcp_store = _read("webui/components/settings/mcp/client/mcp-servers-store.js")
    skills_scan_store = _read("webui/components/settings/skills/skills-scan-store.js")
    plugins_store = _read("webui/components/settings/plugins/plugins-subsection-store.js")
    ko_js = _read("webui/js/i18n/locales/ko.js")

    assert 'this.localizeText("Remote Control")' in tunnel_store
    assert 'tr("Failed to create scan chat")' in mcp_store
    assert 'tr("Failed to create scan chat")' in skills_scan_store
    assert "displayPluginName(plugin)" in plugins_store
    assert "displayPluginDescription(plugin)" in plugins_store
    assert '"LiteLLM Global Settings": "LiteLLM 전역 설정"' in ko_js
    assert '"This browser\'s Agent Zero WebUI language.": "이 브라우저에서 사용할 Agent Zero WebUI 언어입니다."' in ko_js
    assert '"Conflict policy:": "충돌 정책:"' in ko_js
    assert '"Tools exposed by this MCP server.": "이 MCP 서버가 노출하는 도구입니다."' in ko_js
