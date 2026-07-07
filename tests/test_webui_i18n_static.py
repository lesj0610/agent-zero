from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _read(relative_path: str) -> str:
    return (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")


def test_webui_i18n_runtime_is_loaded_and_applies_component_translations() -> None:
    index_js = _read("webui/index.js")
    components_js = _read("webui/js/components.js")
    extensions_js = _read("webui/js/extensions.js")
    modals_js = _read("webui/js/modals.js")
    i18n_js = _read("webui/js/i18n/index.js")
    locale_index_js = _read("webui/js/i18n/locales/index.js")
    ko_js = _read("webui/js/i18n/locales/ko.js")

    assert 'import { initI18n, t } from "/js/i18n/index.js";' in index_js
    assert "initI18n();" in index_js
    assert 'import { scheduleTranslations } from "/js/i18n/index.js";' in components_js
    assert "scheduleTranslations(targetElement);" in components_js
    assert 'import { scheduleTranslations } from "./i18n/index.js";' in extensions_js
    assert "function renderHtmlExtension(targetElement, html)" in extensions_js
    assert "scheduleTranslations(targetElement);" in extensions_js
    assert 'from "./locales/index.js";' in i18n_js
    assert 'replaceAll("_", "-")' in i18n_js
    assert "export function setLocalePreference" in i18n_js
    assert 'globalThis.Alpine.store("i18n"' in i18n_js
    assert "function getReactiveLocale()" in i18n_js
    assert "export function scheduleTranslations" in i18n_js
    assert "function registerAlpineTranslationHook()" in i18n_js
    assert "globalThis.Alpine.interceptInit" in i18n_js
    assert "function queueDynamicTranslations(root)" in i18n_js
    assert "const pendingTranslationRoots = new Set();" in i18n_js
    assert "globalThis.Alpine.nextTick(reapply)" in i18n_js
    assert 'document.addEventListener("alpine:initialized", reapply' in i18n_js
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
    assert "function isInsideSettings(targetElement)" in components_js
    assert "function getTranslationRootForAddedNode(node)" not in components_js
    assert "scheduleTranslations(translationRoot);" not in components_js
    assert "isSettingsComponent(componentUrl) || isInsideSettings(targetElement)" in components_js
    assert 'targetElement.setAttribute("data-i18n-scope", "settings")' in components_js
    assert 'targetElement.closest?.(".settings-modal, .settings-pane, #settings-sections")' in extensions_js
    assert 'import { translateStaticText } from "/js/i18n/index.js";' in modals_js
    assert "if (!modal.title.textContent.trim())" in modals_js
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
    assert "scheduleSettingsTranslations()" in store
    assert "scheduleTranslations(root);" in store
    assert "window.requestAnimationFrame(retry)" not in store
    assert "window.setTimeout(retry, 50)" not in store
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
        "discovery": _read("plugins/_discovery/extensions/webui/welcome-actions-end/discovery-cards.html"),
        "chat_input": _read("webui/components/chat/input/chat-bar-input.html"),
        "sidebar": _read("webui/components/sidebar/top-section/header-icons.html"),
        "preferences": _read("webui/components/sidebar/bottom/preferences/preferences-panel.html"),
    }

    assert 'data-i18n-title="app.scroll.top"' in surfaces["index"]
    assert 'data-i18n-placeholder="settings.search"' in surfaces["settings"]
    assert 'data-i18n="welcome.title">Hello! I\'m Agent Zero' in surfaces["welcome"]
    assert 'data-i18n="welcome.connectChannels">Connect Channels' in surfaces["discovery"]
    assert 'data-i18n-aria-label="chat.moreActions"' in surfaces["chat_input"]
    assert 'data-i18n="sidebar.navigation">Navigation' in surfaces["sidebar"]
    assert 'data-i18n="preferences.title">Preferences' in surfaces["preferences"]


def test_settings_dynamic_surfaces_use_i18n_helpers() -> None:
    tunnel_store = _read("webui/components/settings/tunnel/tunnel-store.js")
    mcp_store = _read("webui/components/settings/mcp/client/mcp-servers-store.js")
    skills_scan_store = _read("webui/components/settings/skills/skills-scan-store.js")
    plugins_store = _read("webui/components/settings/plugins/plugins-subsection-store.js")
    kokoro_store = _read("plugins/_kokoro_tts/webui/kokoro-tts-store.js")
    kokoro_panel = _read("plugins/_kokoro_tts/webui/main.html")
    whisper_store = _read("plugins/_whisper_stt/webui/whisper-stt-store.js")
    whisper_panel = _read("plugins/_whisper_stt/webui/main.html")
    model_config_store = _read("plugins/_model_config/webui/model-config-store.js")
    model_config = _read("plugins/_model_config/webui/config.html")
    model_field = _read("plugins/_model_config/webui/model-field.html")
    model_presets = _read("plugins/_model_config/webui/main.html")
    model_api_keys = _read("plugins/_model_config/webui/api-keys.html")
    model_summary = _read("plugins/_model_config/webui/models-summary.html")
    model_switcher = _read("plugins/_model_config/extensions/webui/chat-input-progress-start/model-switcher.html")
    switcher_store = _read("plugins/_model_config/webui/switcher-mixin.js")
    plugin_settings = _read("webui/components/plugins/plugin-settings.html")
    plugin_settings_store = _read("webui/components/plugins/plugin-settings-store.js")
    plugin_configs = _read("webui/components/plugins/plugin-configs.html")
    plugin_toggles = _read("webui/components/plugins/toggle/plugin-toggles.html")
    agent_settings = _read("webui/components/settings/agent/agent-settings.html")
    agent_config = _read("webui/components/settings/agent/agent.html")
    agent_workdir = _read("webui/components/settings/agent/workdir.html")
    agent_voice = _read("webui/components/settings/agent/voice.html")
    email_store = _read("plugins/_email_integration/webui/email-config-store.js")
    email_config = _read("plugins/_email_integration/webui/config.html")
    welcome_store = _read("webui/components/welcome/welcome-store.js")
    discovery_store = _read("plugins/_discovery/webui/discovery-store.js")
    ko_js = _read("webui/js/i18n/locales/ko.js")

    assert 'this.localizeText("Remote Control")' in tunnel_store
    assert 'tr("Failed to create scan chat")' in mcp_store
    assert 'tr("Failed to create scan chat")' in skills_scan_store
    assert "displayPluginName(plugin)" in plugins_store
    assert "displayPluginDescription(plugin)" in plugins_store
    assert 'return tr(plugin?.display_name || plugin?.name || "(unnamed plugin)")' in plugins_store
    assert 'return tr(plugin?.description || "No description provided.")' in plugins_store
    assert 'import { translateStaticText } from "/js/i18n/index.js";' in kokoro_store
    assert 'return translateStaticText("Idle");' in kokoro_store
    assert "get enabledText()" in kokoro_store
    assert 'translateStaticText(this.enabled ? "Yes" : "No")' in kokoro_store
    assert 'x-text="$store.kokoroTts.enabledText"' in kokoro_panel
    assert 'import { translateStaticText } from "/js/i18n/index.js";' in whisper_store
    assert 'translateStaticText(MicStatusLabels[status] || "Microphone")' in whisper_store
    assert 'translateStaticText("System default")' in whisper_store
    assert '"Send immediately" : "Draft in composer"' in whisper_store
    assert "get enabledText()" in whisper_store
    assert 'translateStaticText(this.enabled ? "Yes" : "No")' in whisper_store
    assert 'x-text="$store.whisperStt.enabledText"' in whisper_panel
    assert 'import { translateStaticText } from "/js/i18n/index.js";' in model_config_store
    assert "uiLocale: \"\"" in model_config_store
    assert "getModelSections()" in model_config_store
    assert "presetDisplayName(preset)" in model_config_store
    assert "defaultPresetName(index)" in model_config_store
    assert "title: translateStaticText('Main')" in model_config_store
    assert 'import { translateStaticText } from "/js/i18n/index.js";' in switcher_store
    assert 'return preset?.name || tr("Unnamed")' in switcher_store
    assert 'if (!o) return tr("Default LLM")' in switcher_store
    assert '|| tr("Custom")' in switcher_store
    assert 'x-effect="context.settingsComponentHtml; $nextTick(() => globalThis.A0_I18N?.scheduleTranslations?.($el))"' in plugin_settings
    assert 'data-i18n="Settings scope"' in plugin_settings
    assert 'data-i18n="All profiles"' in plugin_settings
    assert 'data-i18n-title="Show existing configurations"' in plugin_settings
    assert 'import { translateStaticText } from "/js/i18n/index.js";' in plugin_settings_store
    assert "scopeDescription()" in plugin_settings_store
    assert 'tr("This plugin supports settings per project or agent profile.")' in plugin_settings_store
    assert "localizeText(value = \"\")" in plugin_settings_store
    assert 'data-i18n-scope="settings"' in plugin_configs
    assert 'data-i18n="Loading configurations..."' in plugin_configs
    assert 'data-i18n="No configurations found."' in plugin_configs
    assert 'data-i18n-scope="settings"' in plugin_toggles
    assert 'data-i18n="No activation rules found. This plugin is currently using its default ON state."' in plugin_toggles
    assert 'data-i18n-scope="settings"' in model_config
    assert "$store.modelConfig.getModelSections()" in model_config
    assert 'data-i18n-scope="settings"' in model_field
    assert 'data-i18n="Supports Vision"' in model_field
    assert 'data-i18n="Provider"' in model_field
    assert 'data-i18n="Context window size"' in model_field
    assert 'data-i18n-scope="settings"' in model_presets
    assert "$store.modelConfig.presetDisplayName(preset)" in model_presets
    assert "$store.modelConfig.defaultPresetName(idx + 1)" in model_presets
    assert "$store.modelConfig.defaultPresetName(presets.length + 1)" in model_presets
    assert 'data-i18n-scope="settings"' in model_api_keys
    assert 'data-i18n-scope="settings"' in model_summary
    assert 'data-i18n-scope="settings"' in model_switcher
    assert 'data-i18n-scope="settings"' in agent_settings
    assert 'data-i18n="Agent Config"' in agent_settings
    assert 'data-i18n-scope="settings"' in agent_config
    assert 'data-i18n="Default agent profile"' in agent_config
    assert 'data-i18n-scope="settings"' in agent_workdir
    assert 'data-i18n="Workdir path"' in agent_workdir
    assert 'data-i18n-scope="settings"' in agent_voice
    assert 'data-i18n-scope="settings"' in email_config
    assert 'data-i18n-placeholder="email.placeholder.routing"' in email_config
    assert 'data-i18n-placeholder="email.placeholder.reply"' in email_config
    assert "localizeText(value = \"\")" in email_store
    assert "label: tr(provider.label)" in email_store
    assert "hint: tr(provider.hint)" in email_store
    assert 'return tr("Use a Google App Password. A regular Gmail password usually will not work here.")' in email_store
    assert 'return tr(result.message || (result.ok ? "Done." : "Something went wrong."))' in email_store
    assert 'pieces.push(`${tr("Project")}: ${handler.project}`)' in email_store
    assert 'import { getCurrentLocale, t, translateStaticText } from "/js/i18n/index.js";' in welcome_store
    assert "localizeSystemResourceHtml(html)" in welcome_store
    assert "localizeBanner(banner)" in welcome_store
    assert "localizeBannerHtml(html)" in welcome_store
    assert ".map((banner) => this.localizeBanner(banner))" in welcome_store
    assert 'import { getCurrentLocale, t, translateStaticText } from "/js/i18n/index.js";' in discovery_store
    assert "featureCardTitle(card)" in discovery_store
    assert '"LiteLLM Global Settings": "LiteLLM 전역 설정"' in ko_js
    assert '"This browser\'s Agent Zero WebUI language.": "이 브라우저에서 사용할 Agent Zero WebUI 언어입니다."' in ko_js
    assert '"Conflict policy:": "충돌 정책:"' in ko_js
    assert '"Tools exposed by this MCP server.": "이 MCP 서버가 노출하는 도구입니다."' in ko_js
    assert '"Draft in composer": "작성창에 초안으로 넣기"' in ko_js
    assert '"Main": "메인"' in ko_js
    assert '"Memory": "메모리"' in ko_js
    assert '"Manages LLM model selection and configuration for chat, utility, and embedding models. Supports per-project and per-agent overrides with optional per-chat model switching.":' in ko_js
    assert '"System default": "시스템 기본값"' in ko_js
    assert '"Whisper STT disabled": "Whisper STT 비활성화됨"' in ko_js
    assert '"Provider State": "제공자 상태"' in ko_js
    assert '"Settings scope": "설정 범위"' in ko_js
    assert '"This plugin supports settings per project or agent profile.":' in ko_js
    assert '"All profiles": "모든 프로필"' in ko_js
    assert '"Show existing configurations": "기존 구성 보기"' in ko_js
    assert '"Loading configurations...": "구성 목록 불러오는 중..."' in ko_js
    assert '"No configurations found.": "구성이 없습니다."' in ko_js
    assert '"No activation rules found. This plugin is currently using its default ON state.":' in ko_js
    assert '"Project:": "프로젝트:"' in ko_js
    assert '"Agent profile:": "Agent 프로필:"' in ko_js
    assert '"Show": "보기"' in ko_js
    assert '"Main Model": "메인 모델"' in ko_js
    assert '"Utility Model": "유틸리티 모델"' in ko_js
    assert '"Embedding Model": "임베딩 모델"' in ko_js
    assert '"Model name": "모델 이름"' in ko_js
    assert '"Supports Vision": "Vision 지원"' in ko_js
    assert '"Per-Chat Override": "채팅별 재정의"' in ko_js
    assert '"Default LLM": "기본 LLM"' in ko_js
    assert '"Use Default": "기본값 사용"' in ko_js
    assert '"Active agent profile": "활성 Agent 프로필"' in ko_js
    assert '"Create new Agent Profile": "새 Agent 프로필 만들기"' in ko_js
    assert '"e.g. GPT-4o, Claude Sonnet": "예: GPT-4o, Claude Sonnet"' in ko_js
    assert '"For more information about Agent Zero Venice provider, see":' in ko_js
    assert '"Voice capabilities are provided by built-in plugins. Browser-native speech remains available as the fallback output path when no TTS plugin is active. Enable or disable providers from the Agent Plugins section below.":' in ko_js
    assert '"Email Integration": "Email 통합"' in ko_js
    assert '"Connect Agent Zero and your email account": "Agent Zero와 이메일 계정을 연결하세요"' in ko_js
    assert '"Use a Google App Password. A regular Gmail password usually will not work here.":' in ko_js
    assert '"Incoming mail server": "수신 메일 서버"' in ko_js
    assert '"Check setup": "설정 확인"' in ko_js
    assert '"email.placeholder.routing": "송장이나 청구 관련 질문은 항상 새 채팅을 시작하세요."' in ko_js
    assert '"Enabled": "활성화"' in ko_js
    assert '"Yes": "예"' in ko_js
    assert '"No": "아니요"' in ko_js
    assert '"Request Mic Permission": "마이크 권한 요청"' in ko_js
    assert '"Your AI accounts": "AI 계정"' in ko_js
    assert '"System Resources": "시스템 리소스"' in ko_js
    assert '"Unsecured Connection": "보호되지 않은 연결"' in ko_js
    assert '"Configure credentials": "자격 증명 구성"' in ko_js
    assert '"Use your subscription-backed logins for model access.": "구독 기반 로그인으로 모델에 접근합니다."' in ko_js
    assert '"welcome.connectChannels": "채널 연결"' in ko_js


def test_model_config_summary_routes_keep_their_modal_contracts() -> None:
    model_config_store = _read("plugins/_model_config/webui/model-config-store.js")
    model_config_html = _read("plugins/_model_config/webui/config.html")
    plugin_settings_html = _read("webui/components/plugins/plugin-settings.html")
    i18n_js = _read("webui/js/i18n/index.js")
    modals_js = _read("webui/js/modals.js")

    assert "pluginSettingsStore.openConfig('_model_config', '', '', {" in model_config_store
    assert "title: translateStaticText('Model Configuration')" in model_config_store
    assert "pluginSettingsStore.openConfig('_model_config');" not in model_config_store
    assert "installSettingsHooks(context)" in model_config_html
    assert "context.modalTitle || fallbackTitle" in plugin_settings_html
    assert "globalThis.A0_I18N?.translateStaticText?.('Plugin Settings')" in plugin_settings_html
    assert "Some modal components set a more specific title while mounting." in modals_js
    assert "if (!modal.title.textContent.trim())" in modals_js
    assert "await window.openModal?.('/plugins/_model_config/webui/main.html')" in model_config_store
    assert "await window.openModal?.('/plugins/_model_config/webui/api-keys.html')" in model_config_store
    assert 'const STATIC_ATTRIBUTE_NAMES = ["title", "aria-label", "placeholder", "data-placeholder"];' in i18n_js
    assert "data-banner-action" not in i18n_js
    assert "href" not in i18n_js


def test_oauth_settings_dynamic_surfaces_are_localized() -> None:
    config_html = _read("plugins/_oauth/webui/config.html")
    oauth_store = _read("plugins/_oauth/webui/oauth-config-store.js")
    ko_js = _read("webui/js/i18n/locales/ko.js")

    assert 'import { getCurrentLocale, t, translateStaticText } from "/js/i18n/index.js";' in oauth_store
    assert "bindUiLocaleRuntime()" in oauth_store
    assert "localizeText(value = \"\")" in oauth_store
    assert "get modelSlots()" in oauth_store
    assert "providerConnectionStateLabel(connected)" in oauth_store
    assert "providerDisconnectLabel(providerId)" in oauth_store
    assert "modelInputPlaceholder(key)" in oauth_store
    assert 't("oauth.percentLeft"' in oauth_store
    assert 't("oauth.resetsIn"' in oauth_store
    assert 't("oauth.availableModelsFrom"' in oauth_store
    assert 't("oauth.currentlyProvider"' in oauth_store
    assert 'data-i18n-scope="settings"' in config_html
    assert "$store.oauthConfig.providerConnectionStateLabel(card.connected)" in config_html
    assert "$store.oauthConfig.providerDisconnectLabel(card.provider_id)" in config_html
    assert "$store.oauthConfig.modelInputPlaceholder(slot.key)" in config_html
    assert "$store.oauthConfig.formatResetLabel(window)" in config_html
    assert "$store.oauthConfig.localizeText('No models found. You can still type the model name manually.')" in config_html
    assert '"oauth.percentLeft": "{percent}% 남음"' in ko_js
    assert '"Ready to connect": "연결 준비됨"' in ko_js
    assert '"Check models": "모델 확인"' in ko_js
