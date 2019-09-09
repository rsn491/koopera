<template>
  <div class='container box-container'>
    <div class='row'>
      <div class='col-3 file-explorer-container text-left'>
        <h3>Files</h3>
        <div class='file-list'>
          <Loader v-bind:show='files.length === 0' />
          <div v-for='file in files' v-bind:key='file.path'>
              <a v-bind:class="file.status === 'removed' ?
                'btn alert alert-danger p-0 mb-1' :
                'btn alert-success p-0 mb-1'"
                v-on:click='() => getFile(file.path, file.ref, file.sha)'>
                {{ file.path }}
              </a>
          </div>
        </div>
      </div>
      <div class='col-9 file-view-container' >
        <Loader v-bind:show="loadingFile" />
        <div :class="loadingFile && 'd-none'" v-html="fileDisplay"/>
        <div/>
      </div>
    </div>
  </div>
</template>

<script>

import getAPIUrl from '../shared/getAPIUrl';
import CredentialManager from '../shared/credentialManager';
import Loader from '../components/Loader.vue';
import CodeComment from '../components/codeComment';

export default {
  name: 'PullRequest',
  components: {
    Loader,
  },
  methods: {
    addComment(path, codeBlockId, comment) {
      fetch(
        getAPIUrl(`coderepositories/${this.$route.params.codeRepositoryId}/pullrequests/${this.$route.params.pullRequestNumber}/comment`),
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${this.userCredentials.apiAccessToken}`,
          },
          body: JSON.stringify({
            path,
            codeBlockId,
            comment,
          }),
        },
      ).then(() => {
        this.openedCodeComment.addComment(comment);
        // register code block comment
        this.fileComments[codeBlockId] = this.openedCodeComment;
        this.openedCodeComment = null;
        this.$forceUpdate();
      });
    },
    getFile(path, ref, sha) {
      this.loadingFile = true;

      fetch(getAPIUrl(`coderepositories/${this.$route.params.codeRepositoryId}/file?path=${path}&ref=${ref}&sha=${sha}`), {
        headers: {
          Authorization: `Bearer ${this.userCredentials.apiAccessToken}`,
        },
      }).then((response) => {
        response.json().then((json) => {
          this.fileDisplay = json.body;
          this.loadingFile = false;
          this.filePath = path;
          this.renderFileComments = true;
        });
      });
    },
    openComment(elementToAttach, codeBlockId) {
      // check if there is any comment currently opened
      if (this.openedCodeComment != null) {
        if (this.openedCodeComment.parentElement === elementToAttach) {
          // ignore
          return;
        }

        this.openedCodeComment.close();
      }

      // no comment is opened
      // check if there are already comments for this code block
      if (!this.fileComments[codeBlockId]) {
        // first comment for this code block
        this.openedCodeComment = CodeComment.createNew(elementToAttach, codeBlockId);
      } else {
        this.fileComments[codeBlockId].open();
        this.openedCodeComment = this.fileComments[codeBlockId];
      }

      this.$forceUpdate();
    },
    attachCodeCommentHandlers(matches) {
      const codeCommentsForCurrentFile = this.pullRequestComments[this.filePath];

      if (!this.renderFileComments) {
        return;
      }

      for (let i = 0; i < matches.length; i += 1) {
        const elementToAttach = matches[i];
        const codeBlockId = i;
        const codeBlockComments = codeCommentsForCurrentFile
          && codeCommentsForCurrentFile[codeBlockId];

        if (this.renderFileComments && !!codeBlockComments) {
          // has code block comment -> register and render!
          this.fileComments[codeBlockId] = CodeComment.createExisting(
            elementToAttach, codeBlockId, codeBlockComments,
          );
        }

        elementToAttach.onclick = () => this.openComment(elementToAttach, codeBlockId);
      }

      this.renderFileComments = false;
    },
  },
  data() {
    return {
      userCredentials: CredentialManager.load(),
      loadingFile: false,
      renderFileComments: false,
      files: [],
      filePath: '',
      fileDisplay: '',
      openedCodeComment: null,
      commentToClose: null,
      pullRequestComments: {},
      fileComments: {},
    };
  },
  updated() {
    if (this.loadingFile) {
      return;
    }

    const saveCodeCommentButtons = document.getElementsByClassName('save-code-comment-btn');

    if (saveCodeCommentButtons.length > 0) {
      saveCodeCommentButtons[0].onclick = () => {
        const comment = document.getElementsByClassName('code-comment-text')[0].value;
        this.addComment(this.filePath, this.openedCodeComment.codeBlockId, comment);
      };
    }

    this.attachCodeCommentHandlers(document.getElementsByClassName('inner_cell'));
  },
  created() {
    if (!this.userCredentials.isValid()) {
      this.$router.push({ name: 'login' });
    }

    fetch(getAPIUrl(`coderepositories/${this.$route.params.codeRepositoryId}/pullrequests/${this.$route.params.pullRequestNumber}`), {
      headers: {
        Authorization: `Bearer ${this.userCredentials.apiAccessToken}`,
      },
    }).then((response) => {
      if (response.status === 401 || response.status === 422) {
        this.$router.push({ name: 'login' });
      }

      response.json().then((json) => {
        this.files = json.files;

        this.pullRequestComments = {};
        json.issueComments.forEach((issueComment) => {
          const { filePath } = issueComment;
          const { codeBlockId } = issueComment;

          if ((filePath in this.pullRequestComments) === false) {
            this.pullRequestComments[filePath] = {};
          }

          if ((codeBlockId in this.pullRequestComments[filePath]) === false) {
            this.pullRequestComments[filePath][codeBlockId] = [];
          }

          this.pullRequestComments[filePath][codeBlockId].push({
            author: issueComment.author,
            comment: issueComment.body,
            updatedAt: issueComment.updatedAt,
          });
        });
      });
    });
  },
};


</script>

<style>

.inner_cell {
  cursor: pointer;
}

.file-explorer-container {
  border-right: 1px solid var(--lighter);
}

.file-view-container {
  cursor: default;
  overflow: auto;
  padding: 16px 32px;
}

.file-list {
  overflow: auto;
}

.code-comment-container {
  background-color: #f8f9fa;
  border: 1px solid var(--dark);
  border-radius: 2px;
  padding: 8px;
  margin-bottom: 16px;
}

.code-comment-text {
  width: 100%;
  resize: none;
  overflow-y: auto;
  padding: 4px;
}

.code-block-single-comment {
  background-color: white;
  border: 1px solid var(--dark);
  border-radius: 2px;
  overflow-wrap: break-word;
}

.code-comment-header {
  background-color: var(--normal);
  color: white;
  font-weight: bold;
  padding: 4px 8px;
}

.code-comment--closed {
  cursor: pointer;
  opacity: 0.7;
}

.code-comment--closed:hover {
  border: 2px solid var(--darker);
  opacity: 0.95;
}

.code-comment-done-text {
  padding: 1px 8px;
}

</style>
