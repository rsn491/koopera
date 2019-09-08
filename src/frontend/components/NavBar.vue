<template>
  <div id='nav' class='navbar'>
    <div v-if='!!userName' class='col-6'>
      <router-link
        class='btn float-left'
        to='/'>
      Home
      </router-link>
    </div>
    <div v-if='!!userName' class='row col-6 user-info-container'>
      <Loader :show='!userName' />
      <div class='user-name'>
      {{ userName }}
      </div>
      <div class='user-avatar'
        v-bind:style="{ 'background-image': 'url(' + avatarUrl + ')' }">
      </div>
      <div class='user-logout-container'>
        <a class='btn navbar-btn'
          v-on:click='logout'>
          Logout
        </a>
      </div>
    </div>
  </div>
</template>

<script>

import CredentialManager from '../shared/credentialManager';
import getAPIUrl from '../shared/getAPIUrl';
import Loader from './Loader.vue';

export default {
  name: 'NavBar',
  components: {
    Loader,
  },
  methods: {
    logout() {
      CredentialManager.erase();
      window.location.href = '/login';
    },
  },
  data() {
    return {
      userName: null,
      avatarUrl: '',
    };
  },
  created() {
    const userCredentials = CredentialManager.load();

    fetch(getAPIUrl('me'), {
      headers: {
        Authorization: `Bearer ${userCredentials.apiAccessToken}`,
      },
    }).then((response) => {
        if(response.status === 401) {
          alert('please enable "user" scope for your personal access token!');
          this.logout();
        }

        response.json().then((json) => {
          this.userName = json.name;
          this.avatarUrl = json.avatarUrl;
      });
    });
  },
};

</script>

<style>

#nav {
  display: -webkit-box;
  background-color: var(--dark);
  color: white;
  padding: 8px;
  width: 100%;
  z-index: 99;
  height: 40px;
  margin-bottom: 32px;
}

.user-info-container {
  justify-content: flex-end;
}

.user-name {
}

.user-avatar {
  margin-left: 8px;
  background-size: contain;
  background-repeat: no-repeat;
  background-position: center;
  height: 26px;
  width: 26px;
}

.user-logout-container {
  margin-left: 8px;
}

.navbar .btn  {
  padding-top: 0;
  color: white;
}

</style>
