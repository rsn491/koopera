<template>
  <div class='container box-container'>
    <Loader v-bind:show='fetchingNotebooks && !has_notebooks()' />
    <div :class="has_notebooks() ? 'mb-3 d-flex justify-content-end' : 'd-none'">
      <div class='refresh-notebooks-container'>
        <Loader v-bind:show='is_refreshing()' />
        <button
          :class="is_refreshing() ?
            'd-none' :
            'btn material-icons refresh-notebooks-btn'"
          v-on:click="() => refresh_notebooks()">
          refresh
        </button>
      </div>
      <router-link
        class="btn btn-light"
        v-bind:to="'notebooks/import'">
        Import
      </router-link>
    </div>
    <div class='container'>
      <div
        class='code-repo-notebooks'
        v-bind:key='codeRepoName'
        v-for='codeRepoName in Object.keys(notebooksPerCodeRepo)'>
        <div class='code-repo-name'>
          <h5>{{ codeRepoName }}</h5>
        </div>
        <div
          class='notebook-container'
          v-bind:key='notebook.id'
          v-for='notebook in notebooksPerCodeRepo[codeRepoName]'>
            <div class="d-flex mb-3">
              <div class="col-8">
                <div class="github-image"/>
              </div>
              <div class="col-4 d-flex justify-content-end">
                <!-- <i class="material-icons"
                  v-on:click='() => deleteNotebook(codeRepoName, notebook.id)'>
                  delete
                </i> -->
              </div>
            </div>
            <div class="d-flex">
              <div class="col-12">
                <b v-on:click='() => goToNotebook(notebook.id)'>
                {{ notebook.title }}
                </b>
              </div>
            </div>
        </div>
      </div>
    </div>
    <div
      :class="!fetchingNotebooks && !has_notebooks() ? 'no-notebooks-found': 'd-none'">
      <h3>No notebooks found...</h3>
      <div class="m-4">
        <div class="koopera-image"></div>
      </div>
      <div>Want to import your jupyter notebooks directly from your <b>GitHub</b>?</div>
      <div class="mt-4 mb-2">
        <router-link
          class="btn btn-light"
          v-bind:to="'notebooks/import'">
          Import
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
    Loader,
  },
  data() {
    return {
      initial_fetch_triggered: false,
      fetchingNotebooks: true,
      userCredentials: CredentialManager.load(),
      notebooksPerCodeRepo: {},
    };
  },
  methods: {
    has_notebooks() {
      return Object.keys(this.notebooksPerCodeRepo).length > 0;
    },
    is_refreshing() {
      return this.fetchingNotebooks && this.has_notebooks();
    },
    refresh_notebooks() {
      this.fetchingNotebooks = true;

      fetch(
        getAPIUrl('notebooks'),
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${this.userCredentials.apiAccessToken}`,
          },
        },
      ).then((response) => {
        response.json().then((json) => {
          if (json.notebooksAdded > 0 || !this.initial_fetch_triggered) {
            // new notebooks found!
            // or just first fetch
            this.getAllNotebooks();
          } else {
            this.fetchingNotebooks = false;
          }
        });
      });
    },
    deleteNotebook(codeRepoName, notebookId) {
      this.notebooksPerCodeRepo[codeRepoName] = this.notebooksPerCodeRepo[codeRepoName].filter(
        notebook => notebook.id !== notebookId
      );

      if (this.notebooksPerCodeRepo[codeRepoName].length === 0) {
        delete this.notebooksPerCodeRepo[codeRepoName];
      }

      fetch(getAPIUrl(`notebooks/${notebookId}`), {
        method: 'DELETE',
        headers: {
          Authorization: `Bearer ${this.userCredentials.apiAccessToken}`,
        },
      });

      this.$forceUpdate();
    },
    goToNotebook(notebookId) {
      this.$router.push({ name: 'notebook', params: { notebookId } });
    },
    getAllNotebooks() {
      this.fetchingNotebooks = true;
      this.initial_fetch_triggered = true;

      fetch(getAPIUrl('notebooks'), {
        headers: {
          Authorization: `Bearer ${this.userCredentials.apiAccessToken}`,
        },
      }).then((response) => {
        if (response.status === 401 || response.status === 422) {
          this.$router.push({ name: 'login' });
        }

        response.json().then((json) => {
          this.notebooksPerCodeRepo = {};

          json.notebooks.forEach((notebook) => {
            if (!this.notebooksPerCodeRepo[notebook.repoName]) {
              this.notebooksPerCodeRepo[notebook.repoName] = [];
            }

            this.notebooksPerCodeRepo[notebook.repoName].push(notebook);
          });

          this.fetchingNotebooks = false;
        });
      });
    },
  },
  created() {
    if (!this.userCredentials.isValid()) {
      this.$router.push({ name: 'login' });
    }

    this.refresh_notebooks();
  }
};
</script>

<style>

.code-repo-notebooks {
  margin-bottom: 28px;
}

.code-repo-name {
  color: var(--darker);
}

.refresh-notebooks-btn {
  color: var(--darker);
}

.refresh-notebooks-btn:hover {
  color: var(--dark);
}

.refresh-notebooks-container {
  justify-content: center;
}

.refresh-notebooks-container .spinner-border {
  height: 20px;
  margin: 8px;
  margin-right: 16px;
  width: 20px;
}

.notebook-container {
  border: 1px solid var(--light);
  border-radius: 4px;
  margin: 10px 0;
  padding: 12px 0;
}

.notebook-container b {
  cursor: pointer;
}

.notebook-container .github-image {
  width: 24px;
  height: 24px;
}

.notebook-container .material-icons {
  color: var(--light);
  cursor: pointer;
}

.no-notebooks-found {
  text-align: center
}

.no-notebooks-found .koopera-image {
  height: 200px;
}

</style>
