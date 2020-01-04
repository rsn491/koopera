<template>
  <div id='nav' class='navbar'>
    <div v-if='!!userName' class='col-8'>
      <router-link
        class='btn float-left p-0 mr-2'
        to='/'>
        Home
      </router-link>
      <router-link
        class='btn float-left p-0'
        to='/notebooks'>
        Notebooks
      </router-link>
    </div>
    <div v-if='!!userName' class='col-4 user-info-container'>
      <Loader :show='!userName' />
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
      if (response.status === 401) {
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
  display: flex;
  justify-content: flex-end;
}

.user-avatar {
  background-size: contain;
  background-repeat: no-repeat;
  background-position: center;
  border: 1px solid var(--dark);
  border-radius: 8px;
  display: inline-flex;
  height: 32px;
  margin: -4px;
  width: 32px;
}

.user-logout-container {
  display: inline-flex;
}

.navbar .btn  {
  padding-top: 0;
  color: white;
}

</style>
