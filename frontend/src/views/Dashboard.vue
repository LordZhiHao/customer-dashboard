<!-- views/Dashboard.vue -->
<template>
  <div class="dashboard">
    <div class="forms-container">
      <div class="form-wrapper">
        <MembershipForm @member-added="onMemberAdded" />
      </div>

      <div class="form-wrapper">
        <VisitForm @visit-added="onVisitAdded" />
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

.forms-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.form-wrapper {
  min-width: 0;
}

@media (max-width: 768px) {
  .forms-container {
    grid-template-columns: 1fr;
  }
}
</style>
