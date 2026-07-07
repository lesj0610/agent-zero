import { createStore } from "/js/AlpineStore.js";
import { store as fileBrowserStore } from "/components/modals/file-browser/file-browser-store.js";
import { translateStaticText } from "/js/i18n/index.js";

const fetchApi = globalThis.fetchApi;

function tr(value) {
  return translateStaticText(value);
}

function matchesSearchQuery(query, values) {
  const normalized = String(query || "").trim().toLowerCase();
  if (!normalized) return true;
  return values.some((value) => String(value ?? "").toLowerCase().includes(normalized));
}

const model = {
  loading: false,
  error: "",
  skills: [],
  projects: [],
  projectName: "",
  skillSearch: "",

  async init() {
    this.resetState();
    await this.loadProjects();
    await this.loadSkills();
  },

  resetState() {
    this.loading = false;
    this.error = "";
    this.skills = [];
    this.projects = [];
    this.projectName = "";
    this.skillSearch = "";
  },

  onClose() {
    this.resetState();
  },

  async loadProjects() {
    try {
      const response = await fetchApi("/projects", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: "list_options" }),
      });
      const data = await response.json().catch(() => ({}));
      this.projects = data.ok ? (data.data || []) : [];
    } catch (e) {
      console.error("Failed to load projects:", e);
      this.projects = [];
    }
  },

  async loadSkills() {
    try {
      this.loading = true;
      this.error = "";
      const response = await fetchApi("/skills", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          action: "list",
          project_name: this.projectName || null,
        }),
      });
      const result = await response.json().catch(() => ({}));
      if (!result.ok) {
        this.error = result.error || tr("Failed to load skills");
        this.skills = [];
        return;
      }
      this.skills = Array.isArray(result.data) ? result.data : [];
    } catch (e) {
      this.error = e?.message || tr("Failed to load skills");
      this.skills = [];
    } finally {
      this.loading = false;
    }
  },

  get filteredSkills() {
    return this.skills.filter((skill) => matchesSearchQuery(this.skillSearch, [
      skill.name,
      skill.description,
      skill.path,
      skill.scope,
      skill.project_name,
    ]));
  },

  get skillSearchActive() {
    return !!String(this.skillSearch || "").trim();
  },

  clearSkillSearch() {
    this.skillSearch = "";
  },

  displaySkillName(skill) {
    return skill?.name || tr("(unnamed skill)");
  },

  displaySkillDescription(skill) {
    return skill?.description || tr("No description provided.");
  },

  async deleteSkill(skill) {
    if (!skill) return;
    try {
      const response = await fetchApi("/skills", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          action: "delete",
          skill_path: skill.path,
        }),
      });
      const result = await response.json().catch(() => ({}));
      if (!result.ok) {
        throw new Error(result.error || tr("Delete failed"));
      }
      if (window.toastFrontendSuccess) {
        window.toastFrontendSuccess(tr("Skill deleted"), tr("Skills"));
      }
      await this.loadSkills();
    } catch (e) {
      const msg = e?.message || tr("Delete failed");
      if (window.toastFrontendError) {
        window.toastFrontendError(msg, tr("Skills"));
      }
    }
  },

  async openSkill(skill) {
    await fileBrowserStore.open(skill.path);
  },
};

const store = createStore("skillsListStore", model);
export { store };
