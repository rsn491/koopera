<template>
  <div class='box-container'>
    <Loader v-bind:show='!loaded' />
    <div class='list-row'
      v-for='codeRepository in codeRepositories'
      v-bind:key='codeRepository.id'>
        <div class='d-flex flex-grow-1'>
          <div class='github-image row-image'/>
          <h5>{{ codeRepository.name }}</h5>
        </div>
        <div>
          <router-link
            v-bind:class='codeRepository.openPullRequestCount > 0 ?
              "btn btn-link p-0" :
              "btn btn-link p-0 disabled"'
            v-bind:to='`/coderepositories/${codeRepository.id}/pullrequests`' >
            Pull Requests ({{ codeRepository.openPullRequestCount }} open)
          </router-link>
        </div>
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

<style>

.list-row {
  align-items: center;
  border: 1px solid var(--lighter);
  border-radius: 2px;
  display: flex;
  margin-bottom: 8px;
  padding: 12px 24px;
}

.list-row >div {
  align-items: center;
  display: flex;
}

.list-row .row-image {
  height: 36px;
  margin-right: 12px;
  width: 36px;
}

.list-row h5 {
  margin-bottom: 0;
}

</style>
