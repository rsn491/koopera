<template>
  <div class='container box-container'>
    <Loader v-bind:show='loadingFile' />
    <div class='col-9 file-view-container' >
      <div :class="loadingFile ? 'd-none' : 'koopera-nb'" v-html="fileDisplay"/>
    </div>
  </div>
</template>

<script>

import CredentialManager from '../../shared/credentialManager';
import getAPIUrl from '../../shared/getAPIUrl';
import Loader from '../../components/Loader.vue';

export default {
  name: 'Notebook',
  components: {
    Loader,
  },
  data() {
    return {
      userCredentials: CredentialManager.load(),
      notebooks: [],
      loadingFile: true,
      fileDisplay: null
    };
  },
  created() {
    if (!this.userCredentials.isValid()) {
      this.$router.push({ name: 'login' });
    }

    fetch(getAPIUrl(`notebooks/${this.$route.params.notebookId}`), {
      headers: {
        Authorization: `Bearer ${this.userCredentials.apiAccessToken}`,
      },
    }).then((response) => {
      response.json().then((json) => {
        this.fileDisplay = json.body;
        this.loadingFile = false;
      });
    });
  }
};
</script>
