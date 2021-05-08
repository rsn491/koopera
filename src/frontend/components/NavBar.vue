<template>
  <div id='nav' class='navbar'>
    <div v-if='!!userName'>
      <router-link
        class='btn float-left p-0 mr-2'
        to='/'>
        <div class="koopera-image"></div>
      </router-link>
      <router-link
        class='btn float-left p-0'
        to='/notebooks'>
        Notebooks
      </router-link>
    </div>
    <div v-if='!!userName'>
      <Loader :show='!userName' />
      <div class='user-avatar'
        v-bind:style="{ 'background-image': 'url(' + avatarUrl + ')' }">
      </div>
      <div class='user-logout-container'>
        <a class='material-icons btn navbar-btn'
          v-on:click='logout'>
          logout
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
  background-color: var(--dark);
  color: white;
  height: 48px;
  padding: 0 1rem;
  top: 0;
  width: 100%;
  z-index: 99;
}

.navbar >div {
  align-items: center;
  display: flex;
  height: 100%;
}

.navbar .btn:hover {
  opacity: 0.7;
}

.user-avatar {
  background-size: contain;
  background-repeat: no-repeat;
  background-position: center;
  border: 1px solid var(--dark);
  border-radius: 8px;
  height: 32px;
  width: 32px;
}

.navbar .btn  {
  color: white;
  font-weight: 500;
  padding-bottom: 0;
  padding-top: 0;
}

.navbar .koopera-image {
  height: 32px;
  width: 32px;
}

</style>
