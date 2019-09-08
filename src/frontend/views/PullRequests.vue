<template>
  <div class="container box-container">
    <Loader v-bind:show='!loaded' />
    <div class="col-12"
      v-for="pullRequest in pullRequests"
      v-bind:key="pullRequest.id">
      <div class="row text-left">
        <div class="col-2">
        {{ pullRequest.id }}
        </div>
        <div class="col-2">
        {{ pullRequest.userName }}
        </div>
        <div class="col-6">
        {{ pullRequest.title }}
        </div>
        <div class="col-2">
        <router-link
          class="btn btn-link p-0"
          v-bind:to="'/coderepositories/' +
            $route.params.codeRepositoryId +
            '/pullrequests/' +
            pullRequest.number">
          Review
        </router-link>
        </div>
      </div>
      <div class="row border-lighter"/>
      <br/>
    </div>
  </div>
</template>

<script>

import getAPIUrl from '../shared/getAPIUrl';
import CredentialManager from '../shared/credentialManager';
import Loader from '../components/Loader.vue';

export default {
  name: 'PullRequests',
  components: {
    Loader,
  },
  data() {
    return {
      loaded: false,
      pullRequests: [],
    };
  },
  created() {
    const userCredentials = CredentialManager.load();

    if (!userCredentials.isValid()) {
      this.$router.push({ name: 'login' });
    }

    fetch(getAPIUrl(`coderepositories/${this.$route.params.codeRepositoryId}/pullrequests`), {
      headers: {
        Authorization: `Bearer ${userCredentials.apiAccessToken}`,
      },
    }).then((response) => {
      if (response.status === 401 || response.status === 422) {
        this.$router.push({ name: 'login' });
      }

      response.json().then((json) => {
        this.pullRequests = json.pullRequests;
        this.loaded = true;
      });
    });
  },
};

</script>
