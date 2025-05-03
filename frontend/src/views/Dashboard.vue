<!-- views/Dashboard.vue -->
<template>
    <div class="dashboard">
      <div class="form-switcher">
        <div class="tabs">
          <button
            @click="activeForm = 'membership'"
            :class="{ active: activeForm === 'membership' }"
            class="tab-button"
          >
            New Member
          </button>
          <button
            @click="activeForm = 'visit'"
            :class="{ active: activeForm === 'visit' }"
            class="tab-button"
          >
            Log Visit
          </button>
        </div>
  
        <div class="form-container">
          <div v-if="activeForm === 'membership'" class="form-wrapper">
            <MembershipForm @member-added="onMemberAdded" />
          </div>
  
          <div v-if="activeForm === 'visit'" class="form-wrapper">
            <VisitForm @visit-added="onVisitAdded" />
          </div>
        </div>
      </div>
  
      <RecentEntries :newMember="newMember" :newVisit="newVisit" />
    </div>
  </template>
  
  <script>
  import MembershipForm from "@/components/MembershipForm.vue";
  import VisitForm from "@/components/VisitForm.vue";
  import RecentEntries from "@/components/RecentEntries.vue";
  
  export default {
    name: "DashboardView",
    components: {
      MembershipForm,
      VisitForm,
      RecentEntries,
    },
    data() {
      return {
        activeForm: "membership", // Default to membership form
        newMember: null,
        newVisit: null,
      };
    },
    methods: {
      onMemberAdded(member) {
        this.newMember = member;
        this.$emit("member-added", member);
      },
      onVisitAdded(visit) {
        this.newVisit = visit;
        this.$emit("visit-added", visit);
      },
    },
  };
  </script>
  
  <style scoped>
  .dashboard {
    margin-bottom: 30px;
  }
  
  .form-switcher {
    max-width: 600px;
    margin: 0 auto 30px;
  }
  
  .tabs {
    display: flex;
    justify-content: center;
    margin-bottom: 20px;
    gap: 15px;
  }
  
  .tab-button {
    padding: 10px 25px;
    border: 1px solid #ddd;
    border-radius: 20px;
    background: #f8f8f8;
    cursor: pointer;
    font-size: 16px;
    transition: all 0.3s ease;
  }
  
  .tab-button.active {
    background: linear-gradient(135deg, #4caf50, #45a049);
    color: white;
    font-weight: bold;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  }
  
  .form-container {
    background-color: #fff;
    border: 1px solid #ddd;
    border-radius: 5px;
  }
  
  .form-wrapper {
    min-width: 0;
  }
  
  @media (max-width: 768px) {
    .tabs {
      flex-direction: row;
    }
    
    .tab-button {
      flex: 1;
      text-align: center;
    }
  }
  </style>