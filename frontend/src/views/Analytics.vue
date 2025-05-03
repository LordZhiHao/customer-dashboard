<!-- views/Analytics.vue -->
<template>
  <div class="analytics-page">
    <AnalyticsDashboard />
  </div>
</template>

<script>
import AnalyticsDashboard from "@/components/AnalyticsDashboard.vue";

export default {
  name: "AnalyticsView",
  components: {
    AnalyticsDashboard,
  },
};
</script>

<style scoped>
.analytics-page {
  margin-bottom: 30px;
}
</style>
