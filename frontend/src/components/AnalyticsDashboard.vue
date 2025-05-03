<!-- AnalyticsDashboard.vue -->
<template>
  <div class="analytics-dashboard">
    <h2>Analytics Dashboard</h2>

    <div class="date-filter">
      <label for="period">Time Period:</label>
      <select
        id="period"
        v-model="period"
        @change="fetchData"
        class="form-control">
        <option value="7">Last 7 Days</option>
        <option value="30">Last 30 Days</option>
        <option value="90">Last 3 Months</option>
        <option value="180">Last 6 Months</option>
        <option value="365">Last Year</option>
      </select>
    </div>

    <div class="loading" v-if="loading">Loading analytics data...</div>

    <div v-else class="dashboard-content">
      <div class="stats-cards">
        <div class="stat-card">
          <h3>Total Members</h3>
          <div class="stat-value">{{ stats.totalMembers }}</div>
        </div>
        <div class="stat-card">
          <h3>New Members</h3>
          <div class="stat-value">{{ stats.newMembers }}</div>
          <div class="stat-period">In selected period</div>
        </div>
        <div class="stat-card">
          <h3>Total Visits</h3>
          <div class="stat-value">{{ stats.totalVisits }}</div>
          <div class="stat-period">In selected period</div>
        </div>
        <div class="stat-card">
          <h3>Return Rate</h3>
          <div class="stat-value">{{ stats.returnRate }}%</div>
          <div class="stat-period">Returning visits / total visits</div>
        </div>
      </div>

      <div class="charts-grid">
        <div class="chart-container">
          <h3>Member Growth</h3>
          <canvas ref="memberGrowthChart"></canvas>
        </div>

        <div class="chart-container">
          <h3>Visits by Type</h3>
          <canvas ref="visitTypeChart"></canvas>
        </div>

        <div class="chart-container">
          <h3>Referral Sources</h3>
          <canvas ref="referralSourceChart"></canvas>
        </div>

        <div class="chart-container">
          <h3>Visits by Day</h3>
          <canvas ref="visitsTimeChart"></canvas>
        </div>
      </div>

      <div class="data-export">
        <button @click="exportData" class="btn btn-secondary">
          Export Full Data
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import Chart from "chart.js/auto";

export default {
  name: "AnalyticsDashboard",
  data() {
    return {
      period: "30", // Default to last 30 days
      loading: true,
      stats: {
        totalMembers: 0,
        newMembers: 0,
        totalVisits: 0,
        returnRate: 0,
      },
      chartData: {
        memberGrowth: [],
        visitTypes: [],
        referralSources: [],
        visitsTime: [],
      },
      charts: {
        memberGrowth: null,
        visitType: null,
        referralSource: null,
        visitsTime: null,
      },
    };
  },
  mounted() {
    this.fetchData();
  },
  methods: {
    async fetchData() {
      this.loading = true;

      try {
        // Fetch statistics
        const statsResponse = await fetch(
          `/api/analytics/stats?period=${this.period}`
        );
        const statsData = await statsResponse.json();
        this.stats = statsData;

        // Fetch chart data
        const chartsResponse = await fetch(
          `/api/analytics/charts?period=${this.period}`
        );
        const chartsData = await chartsResponse.json();
        this.chartData = chartsData;

        // Render charts
        this.$nextTick(() => {
          this.renderCharts();
        });
      } catch (error) {
        console.error("Error fetching analytics data:", error);
      } finally {
        this.loading = false;
      }
    },
    renderCharts() {
      // Destroy previous charts if they exist
      if (this.charts.memberGrowth) this.charts.memberGrowth.destroy();
      if (this.charts.visitType) this.charts.visitType.destroy();
      if (this.charts.referralSource) this.charts.referralSource.destroy();
      if (this.charts.visitsTime) this.charts.visitsTime.destroy();

      // Member Growth Line Chart
      this.charts.memberGrowth = new Chart(this.$refs.memberGrowthChart, {
        type: "line",
        data: {
          labels: this.chartData.memberGrowth.map((d) => d.date),
          datasets: [
            {
              label: "New Members",
              data: this.chartData.memberGrowth.map((d) => d.count),
              borderColor: "#4CAF50",
              backgroundColor: "rgba(76, 175, 80, 0.1)",
              tension: 0.4,
              fill: true,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
        },
      });

      // Visit Types Pie Chart
      this.charts.visitType = new Chart(this.$refs.visitTypeChart, {
        type: "pie",
        data: {
          labels: ["New Customers", "Returning Customers"],
          datasets: [
            {
              data: [
                this.chartData.visitTypes.new || 0,
                this.chartData.visitTypes.returning || 0,
              ],
              backgroundColor: ["#FF9800", "#2196F3"],
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
        },
      });

      // Referral Sources Bar Chart
      this.charts.referralSource = new Chart(this.$refs.referralSourceChart, {
        type: "bar",
        data: {
          labels: Object.keys(this.chartData.referralSources),
          datasets: [
            {
              label: "New Customer Sources",
              data: Object.values(this.chartData.referralSources),
              backgroundColor: "#9C27B0",
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: true,
              ticks: {
                precision: 0,
              },
            },
          },
        },
      });

      // Visits by Day Line Chart
      this.charts.visitsTime = new Chart(this.$refs.visitsTimeChart, {
        type: "line",
        data: {
          labels: this.chartData.visitsTime.map((d) => d.date),
          datasets: [
            {
              label: "Daily Visits",
              data: this.chartData.visitsTime.map((d) => d.count),
              borderColor: "#03A9F4",
              backgroundColor: "rgba(3, 169, 244, 0.1)",
              tension: 0.4,
              fill: true,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
        },
      });
    },
    exportData() {
      // Redirect to data export endpoint
      window.open(`/api/export?period=${this.period}`, "_blank");
    },
  },
};
</script>

<style scoped>
.analytics-dashboard {
  padding: 20px;
  background-color: #fff;
  border: 1px solid #ddd;
  border-radius: 5px;
}

.date-filter {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.date-filter label {
  margin-right: 10px;
  font-weight: bold;
}

.date-filter .form-control {
  width: 200px;
}

.loading {
  text-align: center;
  padding: 40px;
  color: #666;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 30px;
}

.stat-card {
  background-color: #f9f9f9;
  border-radius: 5px;
  padding: 15px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.stat-card h3 {
  margin: 0 0 10px 0;
  font-size: 16px;
  color: #666;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #4caf50;
}

.stat-period {
  font-size: 12px;
  color: #999;
  margin-top: 5px;
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(45%, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.chart-container {
  background-color: #fff;
  border: 1px solid #eee;
  border-radius: 5px;
  padding: 15px;
  height: 300px;
}

.chart-container h3 {
  margin-top: 0;
  margin-bottom: 15px;
  font-size: 16px;
  color: #333;
}

.data-export {
  text-align: right;
  margin-top: 20px;
}

.btn-secondary {
  background-color: #607d8b;
  color: white;
  padding: 8px 15px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-secondary:hover {
  background-color: #546e7a;
}

canvas {
  width: 100% !important;
  height: 230px !important;
}
</style>
