// main.js
import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import Chart from "chart.js/auto";

// Global chart configuration
Chart.defaults.font.family =
  "'Segoe UI', 'Helvetica Neue', 'Helvetica', 'Arial', sans-serif";
Chart.defaults.color = "#666";
Chart.defaults.responsive = true;

// Create Vue 3 app
const app = createApp(App);
app.use(router);
app.mount("#app");
