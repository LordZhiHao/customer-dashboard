// main.js
import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import Chart from "chart.js/auto";

Vue.config.productionTip = false;

// Global chart configuration
Chart.defaults.font.family =
  "'Segoe UI', 'Helvetica Neue', 'Helvetica', 'Arial', sans-serif";
Chart.defaults.color = "#666";
Chart.defaults.responsive = true;

new Vue({
  router,
  render: (h) => h(App),
}).$mount("#app");
