<template>
  <div class='container box-container'>
    <div class='row m-2'>
      <div class='col-8 offset-2 source-control-provider-image'/>
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

.source-control-provider-image {
  height: 120px;
  background-size: contain;
  background-position-x: center;
  background-repeat: no-repeat;
  background-image: url(https://slack-files2.s3-us-west-2.amazonaws.com/avatars/2017-12-19/288981919427_f45f04edd92902a96859_512.png);
}

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

</style>
