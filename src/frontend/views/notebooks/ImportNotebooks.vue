<template>
  <div class='box-container'>
    <div class="code-repos-container">
      <div class="d-flex mb-1">
        <input class="mr-2" type="checkbox"
          :checked="allSelected()"
          :disabled="importedNotebooks || importingNotebooks"
          @change='() => selectAllCodeRepo()'/>
        <label class="font-weight-bold">Select All</label>
      </div>
      <Loader v-bind:show="codeRepositories.length === 0" />
      <div id='codeRepos'
        class="d-flex"
        v-for="codeRepository in codeRepositories" v-bind:key="codeRepository.id">
        <input :id="codeRepository.id"
          class="mr-2"
          :value="codeRepository.id"
          :disabled="importedNotebooks || importingNotebooks"
          v-model="selectedCodeRepos"
          type="checkbox" />
        <span class="github-image" />
        <label>{{ codeRepository.owner }}/{{ codeRepository.name }}</label>
      </div>
    </div>
    <div class="mt-2">
      <button
        v-bind:class="importedNotebooks || importingNotebooks ? 'd-none': 'btn btn-light'"
        v-bind:disabled="selectedCodeRepos.length == 0"
        v-on:click="() => importNotebooks()">
        Import Notebooks
      </button>
      <Loader v-bind:show="importingNotebooks"/>
      <div v-bind:class="importedNotebooks && notebooksImported > 0 ? 'text-center' : 'd-none'">
        <i class="material-icons text-success">check_circle</i>
        <p>
          Successfully imported {{ notebooksImported }} notebooks...
        </p>
        <router-link
          class="btn btn-light"
          v-bind:to="'/notebooks'">
          Back
        </router-link>
      </div>
      <div v-bind:class="importedNotebooks && notebooksImported == 0 ? 'text-center' : 'd-none'">
        <i class="material-icons text-warning">error_outline</i>
        <p>
          Unfortunately, we could not found any jupyter notebook
          in the selected repositories...
        </p>
        <router-link
          class="btn btn-light"
          v-bind:to="'/notebooks'">
          Back
        </router-link>
      </div>
    </div>
  </div>
</template>

<script>
import CredentialManager from '../../shared/credentialManager';
import getAPIUrl from '../../shared/getAPIUrl';
import Loader from '../../components/Loader.vue';

export default {
  name: 'Notebooks',
  components: {
    Loader
  },
  data() {
    return {
      userCredentials: CredentialManager.load(),
      codeRepositories: [],
      selectedCodeRepos: [],
      importingNotebooks: false,
      importedNotebooks: false,
      notebooksImported: null,
    };
  },
  methods: {
    allSelected() {
      return this.selectedCodeRepos.length > 0
        && this.selectedCodeRepos.length === this.codeRepositories.length;
    },
    importNotebooks() {
      this.importingNotebooks = true;

      fetch(
        getAPIUrl('notebooks'),
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${this.userCredentials.apiAccessToken}`,
          },
          body: JSON.stringify({
            codeRepositories: this.codeRepositories
              .filter(codeRepo => this.selectedCodeRepos.includes(codeRepo.id))
              .map(codeRepo => ({
                id: codeRepo.id,
                owner: codeRepo.owner
              }))
          }),
        },
      ).then((response) => {
        response.json().then((json) => {
          this.importingNotebooks = false;
          this.importedNotebooks = true;
          this.notebooksImported = json.notebooksAdded + json.notebooksUpdated;
        });
      });
    },
    selectAllCodeRepo() {
      if (this.allSelected()) {
        // unselected all
        this.selectedCodeRepos = [];
      } else {
        this.selectedCodeRepos = this.codeRepositories.map(codeRepo => codeRepo.id);
      }
    },
  },
  created() {
    if (!this.userCredentials.isValid()) {
      this.$router.push({ name: 'login' });
    }

    fetch(getAPIUrl('coderepositories'), {
      headers: {
        Authorization: `Bearer ${this.userCredentials.apiAccessToken}`,
      },
    }).then((response) => {
      if (response.status === 401 || response.status === 422) {
        this.$router.push({ name: 'login' });
      }

      response.json().then((json) => {
        this.codeRepositories = json.codeRepositories.sort(repo => repo.owner);
      });
    });
  }
};
</script>

<style>

.code-repos-container {
  border: 1px solid var(--light);
  contain: content;
  height: 400px;
  overflow-y: auto;
  padding: 12px;
}

.code-repos-container .github-image {
  float: left;
  height: 20px;
  margin-right: 4px;
  width: 20px;
}

.code-repos-container input {
  margin-top: 2px;
}

</style>
