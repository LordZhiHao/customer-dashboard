<!-- VisitForm.vue -->
<template>
  <div class="visit-form">
    <h2>Log Customer Visit</h2>
    <form @submit.prevent="submitForm">
      <div class="form-group">
        <label>Visit Type*</label>
        <div class="radio-group">
          <label>
            <input
              type="radio"
              v-model="visit.type"
              value="returning"
              name="visitType"
              checked />
            Returning Customer
          </label>
          <label>
            <input
              type="radio"
              v-model="visit.type"
              value="new"
              name="visitType" />
            New Customer
          </label>
        </div>
      </div>

      <!-- Fields for Returning Customer -->
      <div v-if="visit.type === 'returning'" class="form-group">
        <label for="existingMember">Select Member*</label>
        <select
          id="existingMember"
          v-model="visit.memberId"
          class="form-control"
          required>
          <option value="">-- Select Member --</option>
          <option
            v-for="member in existingMembers"
            :key="member.id"
            :value="member.id">
            {{ member.name }}
          </option>
        </select>
      </div>

      <!-- Fields for New Customer -->
      <div v-if="visit.type === 'new'">
        <div class="form-group">
          <label for="visitorName">Visitor Name*</label>
          <input
            type="text"
            id="visitorName"
            v-model="visit.visitorName"
            class="form-control"
            required />
        </div>

        <div class="form-group">
          <label for="channel">How did they find us?*</label>
          <select
            id="channel"
            v-model="visit.channel"
            class="form-control"
            required>
            <option value="">-- Select Channel --</option>
            <option value="social">Social Media</option>
            <option value="search">Search Engine</option>
            <option value="referral">Personal Referral</option>
            <option value="advertisement">Advertisement</option>
            <option value="other">Other</option>
          </select>
        </div>

        <div v-if="visit.channel === 'other'" class="form-group">
          <label for="otherChannel">Please specify:</label>
          <input
            type="text"
            id="otherChannel"
            v-model="visit.otherChannel"
            class="form-control" />
        </div>
      </div>

      <div class="form-group">
        <label for="visitDate">Visit Date*</label>
        <input
          type="date"
          id="visitDate"
          v-model="visit.date"
          class="form-control"
          required />
      </div>

      <div class="form-group">
        <label for="notes">Notes</label>
        <textarea
          id="notes"
          v-model="visit.notes"
          class="form-control"
          rows="3"></textarea>
      </div>

      <button type="submit" class="btn btn-primary">Log Visit</button>
    </form>
  </div>
</template>

<script>
export default {
  name: "VisitForm",
  data() {
    return {
      visit: {
        type: "returning",
        memberId: "",
        visitorName: "",
        channel: "",
        otherChannel: "",
        date: new Date().toISOString().substr(0, 10),
        notes: "",
      },
      existingMembers: [],
    };
  },
  mounted() {
    // Fetch existing members
    this.fetchExistingMembers();
  },
  methods: {
    fetchExistingMembers() {
      // API call to fetch existing members
      fetch("/api/members")
        .then((response) => response.json())
        .then((data) => {
          this.existingMembers = data;
        })
        .catch((error) => {
          console.error("Error fetching members:", error);
        });
    },
    submitForm() {
      const visitData = { ...this.visit };

      // Clean up data before submission
      if (visitData.type === "returning") {
        delete visitData.visitorName;
        delete visitData.channel;
        delete visitData.otherChannel;
      } else {
        delete visitData.memberId;
        if (visitData.channel !== "other") {
          delete visitData.otherChannel;
        }
      }

      // API call to save the visit
      fetch("/api/visits", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(visitData),
      })
        .then((response) => response.json())
        .then((data) => {
          alert("Visit logged successfully!");
          // Reset form
          this.visit = {
            type: "returning",
            memberId: "",
            visitorName: "",
            channel: "",
            otherChannel: "",
            date: new Date().toISOString().substr(0, 10),
            notes: "",
          };
          // Emit event to update recent entries table
          this.$emit("visit-added", data);
        })
        .catch((error) => {
          console.error("Error logging visit:", error);
        });
    },
  },
};
</script>

<style scoped>
.visit-form {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 5px;
  background-color: #fff;
}

.form-group {
  margin-bottom: 15px;
}

.radio-group {
  display: flex;
  gap: 20px;
  margin-bottom: 15px;
}

.form-control {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.btn-primary {
  background-color: #4caf50;
  color: white;
  padding: 10px 15px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-primary:hover {
  background-color: #45a049;
}
</style>
