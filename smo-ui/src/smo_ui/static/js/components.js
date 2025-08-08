/**
 * SmoSidebar is a custom HTML element that renders the sidebar navigation
 * for the SMO dashboard. It highlights the active page based on the
 * "active-page" attribute.
 */
class SmoSidebar extends HTMLElement {
  connectedCallback() {
    // Get the active page from the element's attribute, default to "dashboard"
    const activePage = this.getAttribute("active-page") || "dashboard";

    // Set the inner HTML of the sidebar with all navigation links (in English)
    this.innerHTML = `
      <div class="sidebar">
        <div class="logo">SMO</div>
        <nav class="sidebar-menu">
          <a href="/" data-page="dashboard">Dashboard</a>
          <a href="/graphs" data-page="graphs">Graphs</a>
          <a href="/projects" data-page="projects">Projects</a>
          <a href="/clusters" data-page="clusters">Clusters</a>
          <a href="/marketplace" data-page="marketplace">Marketplace</a>
          <a href="/events" data-page="events">Events</a>
          <hr class="separator">
          <a href="/docs" data-page="docs">API Documentation</a>
          <a href="/settings" data-page="settings">Settings</a>
        </nav>
      </div>
    `;

    // Highlight the link corresponding to the active page
    const activeLink = this.querySelector(`[data-page="${activePage}"]`);
    if (activeLink) {
      activeLink.classList.add("active");
    }
  }
}

// Register the custom element so it can be used as <smo-sidebar>
customElements.define("smo-sidebar", SmoSidebar);
