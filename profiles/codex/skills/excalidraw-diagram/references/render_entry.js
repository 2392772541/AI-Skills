import { exportToSvg } from "@excalidraw/excalidraw";

window.renderDiagram = async function (jsonData) {
  try {
    const data = typeof jsonData === "string" ? JSON.parse(jsonData) : jsonData;
    const appState = data.appState || {};
    appState.viewBackgroundColor = appState.viewBackgroundColor || "#ffffff";
    appState.exportWithDarkMode = false;

    const svg = await exportToSvg({
      elements: data.elements || [],
      appState: { ...appState, exportBackground: true },
      files: data.files || {},
    });

    const root = document.getElementById("root");
    root.innerHTML = "";
    root.appendChild(svg);
    window.__renderComplete = true;
    window.__renderError = null;
    return {
      success: true,
      width: svg.getAttribute("width"),
      height: svg.getAttribute("height"),
    };
  } catch (error) {
    window.__renderComplete = true;
    window.__renderError = error.message;
    return { success: false, error: error.message };
  }
};

window.__moduleReady = true;
