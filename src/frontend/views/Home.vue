<template>
  <div class='box-container'>
    <Loader v-bind:show='!loaded' />
    <div class='col-12'
      v-for='codeRepository in codeRepositories'
      v-bind:key='codeRepository.id'>
      <div class='row text-left'>
        <div class='col-2'>
        {{ codeRepository.id }}
        </div>
        <div class='col-7'>
        {{ codeRepository.name }}
        </div>
        <div class='col-3'>
        <router-link
          v-bind:class='codeRepository.openPullRequestCount > 0 ?
            "btn btn-link p-0" :
            "btn btn-link p-0 disabled"'
          v-bind:to='`/coderepositories/${codeRepository.id}/pullrequests`' >
          Pull Requests ({{ codeRepository.openPullRequestCount }} open)
        </router-link>
        </div>
      </div>
      <div class='row border-lighter'/>
      <br/>
    </div>
  </div>
</template>

<script>

import getAPIUrl from '../shared/getAPIUrl';
import CredentialManager from '../shared/credentialManager';
import Loader from '../components/Loader.vue';

export default {
  name: 'home',
  components: {
    Loader,
  },
  data() {
    return {
      loaded: false,
      codeRepositories: [],
    };
  },
  created() {
    const userCredentials = CredentialManager.load();

    if (!userCredentials.isValid()) {
      this.$router.push({ name: 'login' });
    }

    fetch(getAPIUrl('coderepositories'), {
      headers: {
        Authorization: `Bearer ${userCredentials.apiAccessToken}`,
      },
    }).then((response) => {
      if (response.status === 401 || response.status === 422) {
        this.$router.push({ name: 'login' });
      }

      response.json().then((json) => {
        this.codeRepositories = json.codeRepositories.sort(
          (a, b) => b.openPullRequestCount - a.openPullRequestCount,
        );
        this.loaded = true;
      });
    });
  },
};
</script>
