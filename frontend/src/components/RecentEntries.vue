<!-- RecentEntries.vue -->
<template>
  <div class="recent-entries">
    <h2>Recent Activity (Last 24 Hours)</h2>

    <div class="entries-tabs">
      <button
        :class="['tab-button', activeTab === 'all' ? 'active' : '']"
        @click="activeTab = 'all'">
        All Entries
      </button>
      <button
        :class="['tab-button', activeTab === 'members' ? 'active' : '']"
        @click="activeTab = 'members'">
        New Members
      </button>
      <button
        :class="['tab-button', activeTab === 'visits' ? 'active' : '']"
        @click="activeTab = 'visits'">
        Visits
      </button>
    </div>

    <div v-if="loading" class="loading">Loading recent entries...</div>

    <div
      v-else-if="activeTab === 'all' || activeTab === 'members'"
      class="entries-table">
      <h3 v-if="activeTab === 'members'">New Members</h3>
      <table v-if="recentMembers.length > 0">
        <thead>
          <tr>
            <th>Name</th>
            <th>Email</th>
            <th>Join Date</th>
            <th>Referred By</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="member in recentMembers" :key="'member-' + member.id">
            <td>{{ member.name }}</td>
            <td>{{ member.email }}</td>
            <td>{{ formatDate(member.joinDate) }}</td>
            <td>{{ member.referredByName || "N/A" }}</td>
          </tr>
        </tbody>
      </table>
      <p v-else>No new members in the last 24 hours.</p>
    </div>

    <div
      v-if="activeTab === 'all' || activeTab === 'visits'"
      class="entries-table">
      <h3 v-if="activeTab === 'visits'">Recent Visits</h3>
      <table v-if="recentVisits.length > 0">
        <thead>
          <tr>
            <th>Type</th>
            <th>Customer</th>
            <th>Date</th>
            <th>Channel</th>
            <th>Notes</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="visit in recentVisits" :key="'visit-' + visit.id">
            <td>{{ visit.type === "returning" ? "Returning" : "New" }}</td>
            <td>
              {{
                visit.type === "returning"
                  ? visit.memberName
                  : visit.visitorName
              }}
            </td>
            <td>{{ formatDate(visit.date) }}</td>
            <td>{{ getChannelDisplay(visit) }}</td>
            <td>{{ visit.notes || "-" }}</td>
          </tr>
        </tbody>
      </table>
      <p v-else>No visits logged in the last 24 hours.</p>
    </div>
  </div>
</template>

<script>
export default {
  name: "RecentEntries",
  props: {
    newMember: Object,
    newVisit: Object,
  },
  data() {
    return {
      recentMembers: [],
      recentVisits: [],
      loading: true,
      activeTab: "all",
    };
  },
  watch: {
    newMember(newVal) {
      if (newVal) {
        this.fetchRecentEntries();
      }
    },
    newVisit(newVal) {
      if (newVal) {
        this.fetchRecentEntries();
      }
    },
  },
  mounted() {
    this.fetchRecentEntries();
  },
  methods: {
    fetchRecentEntries() {
      this.loading = true;

      // Fetch recent members (last 24 hours)
      fetch("/api/members/recent")
        .then((response) => response.json())
        .then((data) => {
          this.recentMembers = data;
        })
        .catch((error) => {
          console.error("Error fetching recent members:", error);
        });

      // Fetch recent visits (last 24 hours)
      fetch("/api/visits/recent")
        .then((response) => response.json())
        .then((data) => {
          this.recentVisits = data;
          this.loading = false;
        })
        .catch((error) => {
          console.error("Error fetching recent visits:", error);
          this.loading = false;
        });
    },
    formatDate(dateString) {
      const date = new Date(dateString);
      return new Intl.DateTimeFormat("en-US", {
        year: "numeric",
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      }).format(date);
    },
    getChannelDisplay(visit) {
      if (visit.type === "returning") {
        return "-";
      }

      const channelMap = {
        social: "Social Media",
        search: "Search Engine",
        referral: "Personal Referral",
        advertisement: "Advertisement",
        other: visit.otherChannel || "Other",
      };

      return channelMap[visit.channel] || visit.channel;
    },
  },
};
</script>

<style scoped>
.recent-entries {
  margin-top: 30px;
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 5px;
  background-color: #fff;
}

.entries-tabs {
  display: flex;
  margin-bottom: 15px;
}

.tab-button {
  padding: 8px 16px;
  background-color: #f0f0f0;
  border: 1px solid #ddd;
  border-radius: 4px;
  margin-right: 10px;
  cursor: pointer;
}

.tab-button.active {
  background-color: #4caf50;
  color: white;
  border-color: #4caf50;
}

.entries-table {
  margin-bottom: 20px;
}

h3 {
  margin-bottom: 10px;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th,
td {
  padding: 10px;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

th {
  background-color: #f5f5f5;
}

.loading {
  text-align: center;
  padding: 20px;
  color: #666;
}
</style>
