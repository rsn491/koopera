<template>
  <div class="box-container">
    <Loader v-bind:show='!loaded' />
    <div class="list-row"
      v-for="pullRequest in pullRequests"
      v-bind:key="pullRequest.id">
      <div class="d-flex flex-grow-1">
        <div class='author-avatar row-image'
        :style="`background-image: url(${pullRequest.userAvatarUrl})`"/>
        <h5>{{ pullRequest.title }}</h5>
      </div>
      <div>
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
  </div>
</template>

<script>

import getAPIUrl from '../shared/getAPIUrl';
import CredentialManager from '../shared/credentialManager';
import Loader from '../components/Loader.vue';
import store from '../store';

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
        store.setCodeRepo(this.$route.params.codeRepositoryId, json.codeRepoName);
        this.pullRequests = json.pullRequests;
        this.loaded = true;
      });
    });
  },
};

</script>

<style>

.list-row .author-avatar {
  background-size: contain;
  background-position-x: center;
  background-repeat: no-repeat;
  border-radius: 2px;
}

</style>
