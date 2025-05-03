<!-- MembershipForm.vue -->
<template>
    <div class="membership-form">
      <h2>New Member Registration</h2>
      <form @submit.prevent="submitForm">
        <div class="form-group">
          <label for="name">Full Name*</label>
          <input
            type="text"
            id="name"
            v-model="member.name"
            required
            class="form-control"
          />
        </div>
  
        <div class="form-group">
          <label for="email">Email Address*</label>
          <input
            type="email"
            id="email"
            v-model="member.email"
            required
            class="form-control"
          />
        </div>
  
        <div class="form-group">
          <label for="phone">Phone Number</label>
          <input
            type="tel"
            id="phone"
            v-model="member.phone"
            class="form-control"
          />
        </div>
  
        <div class="form-group">
          <label for="joinDate">Join Date</label>
          <input
            type="date"
            id="joinDate"
            v-model="member.joinDate"
            class="form-control"
          />
        </div>
  
        <div class="form-group">
          <label for="referredBy">Referred By</label>
          <select id="referredBy" v-model="member.referredBy" class="form-control">
            <option value="">-- Not Referred --</option>
            <option v-for="existingMember in existingMembers" :key="existingMember.id" :value="existingMember.id">
              {{ existingMember.name }}
            </option>
          </select>
        </div>
  
        <button type="submit" class="btn btn-primary">Register Member</button>
      </form>
    </div>
  </template>
  
  <script>
  export default {
    name: 'MembershipForm',
    data() {
      return {
        member: {
          name: '',
          email: '',
          phone: '',
          joinDate: new Date().toISOString().substr(0, 10),
          referredBy: '',
        },
        existingMembers: []
      }
    },
    mounted() {
      // Fetch existing members for the referral dropdown
      this.fetchExistingMembers();
    },
    methods: {
      fetchExistingMembers() {
        // API call to fetch existing members
        fetch('/api/members')
          .then(response => response.json())
          .then(data => {
            this.existingMembers = data;
          })
          .catch(error => {
            console.error('Error fetching members:', error);
          });
      },
      submitForm() {
        // API call to save the new member
        fetch('/api/members', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(this.member),
        })
          .then(response => response.json())
          .then(data => {
            alert('Member registered successfully!');
            // Reset form
            this.member = {
              name: '',
              email: '',
              phone: '',
              joinDate: new Date().toISOString().substr(0, 10),
              referredBy: '',
            };
            // Emit event to update recent entries table
            this.$emit('member-added', data);
          })
          .catch(error => {
            console.error('Error registering member:', error);
          });
      }
    }
  }
  </script>
  
  <style scoped>
  .membership-form {
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
  
  .form-control {
    width: 100%;
    padding: 8px;
    border: 1px solid #ddd;
    border-radius: 4px;
  }
  
  .btn-primary {
    background-color: #4CAF50;
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