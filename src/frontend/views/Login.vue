<template>
  <div class='container box-container'>
    <div class='row m-2 source-control-provider'>
      <div class='col-8 offset-2 github-image'/>
    </div>

    <div class='row m-2'>
      <input type='password'
        class='col-8 offset-2 access-token-input'
        placeholder='Your personal access token'
        v-model='personalAccessToken' />
      <button class='col-8 offset-2 mt-1 login-btn'
        v-on:click='() => login()'>
        Login
      </button>
    </div>
  </div>
</template>

<script>

import getAPIUrl from '../shared/getAPIUrl';
import CredentialManager from '../shared/credentialManager';

export default {
  name: 'Login',
  data() {
    return {
      personalAccessToken: '',
    };
  },
  methods: {
    login() {
      fetch(getAPIUrl('login'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          personalAccessToken: this.personalAccessToken,
        }),
      }).then((response) => {
        if (response.status !== 200) {
          alert('Invalid credentials!');
          return;
        }

        response.json().then(json => this.saveAccessToken(json.accessToken));
      });
    },
    saveAccessToken(accessToken) {
      CredentialManager.store(this.personalAccessToken, accessToken);
      window.location.href = '/';
    },
  },
};

</script>

<style>

.access-token-input {
  border: 1px solid var(--dark);
  font-size: medium;
  border-radius: 4px;
  text-align: center;
}

.login-btn {
  font-size: medium;
  border-radius: 4px;
  border: 1px solid var(--dark);
}

.source-control-provider .github-image {
  height: 120px;
}

</style>
