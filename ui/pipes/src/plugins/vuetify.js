/**
 * plugins/vuetify.js
 *
 * Framework documentation: https://vuetifyjs.com`
 */

// Styles
import "@mdi/font/css/materialdesignicons.css";
import "vuetify/styles";

// Composables
import { createVuetify } from "vuetify";

// https://vuetifyjs.com/en/introduction/why-vuetify/#feature-guides

const nebulaTheme = {
  dark: true,
  colors: {
    background: "#0f172a",
    primary: "#3462e3",
    surface: "#1e293b",
    info: "#64748b",
    accent: "#0ea5e9",
    success: "#14b8a6",
    "surface-light": "#2e3d59",
    "surface-bright": "#87a7ff",
    "surface-variant": "#334155",
    "on-surface-variant": "#FFFFFF",
    "primary-darken-1": "#1c2d60",
    secondary: "#0284c7",
    "secondary-darken-1": "#0369a1",
    error: "#ef4444",
    warning: "#f97316",
  },
  variables: {
    "border-color": "#ffffff",
    "border-opacity": 0.2,
    "high-emphasis-opacity": 0.87,
    "medium-emphasis-opacity": 0.6,
    "disabled-opacity": 0.38,
    "idle-opacity": 0.1,
    "hover-opacity": 0.08,
    "focus-opacity": 0.12,
    "selected-opacity": 0.12,
    "activated-opacity": 0.12,
    "pressed-opacity": 0.16,
    "dragged-opacity": 0.08,
    "theme-kbd": "#1e40af",
    "theme-on-kbd": "#dbeafe",
    "theme-code": "#0f172a",
    "theme-on-code": "#93c5fd",
  },
};

export default createVuetify({
  theme: {
    defaultTheme: "nebulaTheme",
    themes: {
      nebulaTheme
    }
  },
});
