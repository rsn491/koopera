<template>
  <div class='box-container'>
    <div :class="loadingPr ? 'd-none' : 'pr-header'">
      <div class="pr-header__info">
        <h1 class='pr-title'>
          {{ title }}
        </h1>
        <div>
          <div class='author-avatar' :style="`background-image: url(${authorAvatarUrl})`"/>
          <div :class="state === 'Open' ?
            'pr-status pr-status--open' :
            'pr-status'">
            <span class='dot'/>
            {{ state }}
          </div>
        </div>
      </div>
      <div class="pr-header__actions">
        <div class="pr-header__links">
          <div :class="showDescription ?
            'pr-header__links__link pr-header__links__link--active' :
            'pr-header__links__link'"
            v-on:click="() => this.showDescription = true">
            <span class="material-icons" >subject</span>
            Description
          </div>
          <div :class="showDescription ?
            'pr-header__links__link' :
            'pr-header__links__link pr-header__links__link--active'"
            v-on:click="() => this.showDescription = false">
            <span class="material-icons">code</span>
            Files ({{ files.length }})
          </div>
        </div>
        <div class='pr-header__btns'>
          <div :class="showMergeStrategies ?
            'pr-header__btns__btn pr-header__btns__btn--active' :
            'pr-header__btns__btn'"
            v-on:click="() => showMergeStrategies = !showMergeStrategies">
            <span class="material-icons" >done</span>
            Merge
          </div>
          <div class='pr-merge-strategies' v-if=showMergeStrategies>
            <div class='pr-merge-strategies__strategy'
              v-on:click="() => merge('merge')">
              Merge
            </div>
            <div class='pr-merge-strategies__strategy'
              v-on:click="() => merge('squash')">
              Squash
            </div>
            <div class='pr-merge-strategies__strategy'
              v-on:click="() => merge('rebase')">
              Rebase
            </div>
          </div>
        </div>
      </div>
    </div>
    <Loader v-bind:show="loadingPr" />
    <div :class="loadingPr ? 'd-none' : 'row'">
      <div class='col-12' v-if="showDescription" v-html="body"/>
      <div class='col-3 file-explorer-container text-left' v-if="!showDescription">
        <div class='file-list'>
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
      <div class='col-9 file-view-container' v-if="!showDescription">
        <Loader v-bind:show="loadingFile" />
        <div :class="loadingFile ? 'd-none' : isIpynbFile && 'koopera-nb'" v-html="fileDisplay"/>
      </div>
    </div>
  </div>
</template>

<script>

import getAPIUrl from '../shared/getAPIUrl';
import CredentialManager from '../shared/credentialManager';
import Loader from '../components/Loader.vue';
import CodeComment from '../components/codeComment';
import store from '../store';

export default {
  name: 'PullRequest',
  components: {
    Loader,
  },
  data() {
    return {
      userCredentials: CredentialManager.load(),
      loadingFile: false,
      loadingPr: true,
      renderFileComments: false,
      showMergeStrategies: false,
      showDescription: true,
      files: [],
      filePath: '',
      fileDisplay: '',
      pullRequestComments: {},
      fileComments: {},
      title: null,
      state: null,
      authorAvatarUrl: null,
      body: null,
      isIpynbFile: null,
      penedCodeComment: null,
    };
  },
  methods: {
    merge(mergeStrategy) {
      fetch(
        getAPIUrl(`coderepositories/${this.$route.params.codeRepositoryId}/pullrequests/${this.$route.params.pullRequestNumber}/merge`),
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${this.userCredentials.apiAccessToken}`,
          },
          body: JSON.stringify({
            mergeStrategy
          }),
        },
      ).then((response) => {
        this.showMergeStrategies = false;
        this.state = 'Closed';

        if (response.status !== 200) {
          response.json().then((json) => {
            alert(json.message);
          });
        }
      });
    },
    addComment(codeComment, newComment, inReplyToCommentId) {
      const { codeBlockId } = codeComment;

      fetch(
        getAPIUrl(`coderepositories/${this.$route.params.codeRepositoryId}/pullrequests/${this.$route.params.pullRequestNumber}/comment`),
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${this.userCredentials.apiAccessToken}`,
          },
          body: JSON.stringify({
            path: codeComment.path,
            comment: newComment,
            codeBlockId,
            inReplyToCommentId
          }),
        },
      ).then((response) => {
        response.json().then((json) => {
          this.openedCodeComment.addComment(json.id, newComment);
          // register code block comment
          this.fileComments[codeBlockId] = this.openedCodeComment;
          this.openedCodeComment = null;
          this.$forceUpdate();
        });
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
          this.fileComments = {};
          this.isIpynbFile = this.filePath.endsWith('.ipynb');
        });
      });
    },
    openComment(elementToAttach, codeBlockId) {
      // check if there is any comment currently opened
      if (this.openedCodeComment != null) {
        if (this.openedCodeComment.codeBlockId === codeBlockId) {
          // ignore
          return;
        }

        this.openedCodeComment.close();
      }

      // no comment is opened
      // check if there are already comments for this code block
      if (!this.fileComments[codeBlockId]) {
        // first comment for this code block
        this.openedCodeComment = CodeComment.createNew(
          this.createContainerElement(elementToAttach, codeBlockId),
          this.filePath,
          codeBlockId,
          this.addComment
        );
      } else {
        this.fileComments[codeBlockId].open();
        this.openedCodeComment = this.fileComments[codeBlockId];
      }

      this.$forceUpdate();
    },
    createContainerElement(elementToAttach, codeBlockId) {
      const containerElement = document.createElement('div');
      containerElement.setAttribute('class', 'd-flex');

      if (!this.isIpynbFile) {
        const linenoElements = document.getElementsByClassName('lineno');

        if (codeBlockId + 1 >= linenoElements.length) {
          // comment in last line
          elementToAttach.parentElement.appendChild(containerElement);
        } else {
          const targetElement = linenoElements[codeBlockId + 1];
          targetElement.parentElement.insertBefore(containerElement, targetElement);
        }
      } else {
        elementToAttach.appendChild(containerElement);
      }

      return containerElement;
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
          const containerElement = this.createContainerElement(elementToAttach, codeBlockId);
          this.fileComments[codeBlockId] = CodeComment.createExisting(
            containerElement, this.filePath, codeBlockId, this.addComment, codeBlockComments,
          );

          if (!this.isIpynbFile) {
            containerElement.onclick = () => this.openComment(elementToAttach, codeBlockId);
          }
        }

        elementToAttach.onclick = () => this.openComment(elementToAttach, codeBlockId);
      }

      this.renderFileComments = false;
    },
  },
  updated() {
    if (this.loadingFile) {
      return;
    }

    if (this.isIpynbFile) {
      this.attachCodeCommentHandlers(document.getElementsByClassName('inner_cell'));
    } else {
      this.attachCodeCommentHandlers(document.getElementsByClassName('lineno'));
    }
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
        this.loadingPr = false;
        store.setCodeRepo(this.$route.params.codeRepositoryId, json.codeRepoName);
        this.authorAvatarUrl = json.userAvatarUrl;
        this.body = json.body;
        this.state = json.state;
        this.files = json.files;
        this.title = json.title;

        this.pullRequestComments = {};
        json.comments.forEach((comment) => {
          const { filePath, codeBlockId } = comment;

          if ((filePath in this.pullRequestComments) === false) {
            this.pullRequestComments[filePath] = {};
          }

          if ((codeBlockId in this.pullRequestComments[filePath]) === false) {
            this.pullRequestComments[filePath][codeBlockId] = [];
          }

          this.pullRequestComments[filePath][codeBlockId].push({
            id: comment.id,
            author: comment.author,
            comment: comment.body,
            updatedAt: comment.updatedAt,
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

.file-view-container .lineno:hover {
  opacity: 0.6;
  background-color: var(--darker);
}

.file-view-container span.lineno {
  background-color: var(--dark);
  cursor: pointer;
  color: var(--lighter);
  margin-right: 8px;
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
  display: table;
  padding: 8px;
  margin-bottom: 8px;
  margin-top: 8px;
}

.code-comment-text {
  display: table;
  margin-top: 4px;
  overflow-y: auto;
  padding: 4px;
  resize: none;
  width: 100%;
}

.code-block-single-comment {
  background-color: white;
  border: 1px solid var(--dark);
  border-radius: 2px;
  display: table;
  margin-bottom: 8px;
  overflow-wrap: break-word;
  width: 100%;
}

.code-comment-header {
  background-color: var(--normal);
  color: white;
  display: flex;
  font-weight: bold;
  justify-content: space-between;
  padding: 4px 8px;
}

.code-comment--closed {
  cursor: pointer;
  opacity: 0.75;
}

.code-comment--closed:hover {
  border: 2px solid var(--darker);
  opacity: 0.95;
}

.code-comment-done-text {
  padding: 1px 8px;
}

.pr-header {
  margin-bottom: 24px;
}

.pr-header__info {
  margin-bottom: 18px;
  padding: 0 4px;
}

.pr-header__actions {
  display: flex;
  font-weight: bold;
  border-bottom: 1px solid var(--lighter);
}

.pr-header__links {
  display: flex;
  flex-grow: 1;
}

.pr-header__links__link {
  align-items: center;
  color: var(--light);
  cursor: pointer;
  display: flex;
  margin-right: 8px;
  padding: 4px 2px;
}

.pr-header__links__link--active {
  border-bottom: 2px solid var(--dark);
  color: var(--dark);
  padding-bottom: 2px;
}

.pr-header__btns {
  display: flex;
  position: relative;
}

.pr-header__btns__btn {
  align-items: center;
  background-color: var(--lighter);
  border: 1px solid var(--light);
  border-radius: 4px;
  color: var(--dark);
  cursor: pointer;
  display: flex;
  padding: 4px 2px;
}

.pr-header__btns__btn--active {
  color: var(--light);
}

.pr-header__btns__btn .material-icons {
  color:  var(--success);
}

.pr-header__actions .material-icons {
  margin-right: 2px;
}

.pr-header .pr-title {
  color: var(--darker);
  font-size: 24px;
  margin-bottom: 14px;
}

.pr-header .author-avatar {
  background-size: contain;
  background-position-x: center;
  height: 60px;
  width: 60px;
  background-repeat: no-repeat;
  border-radius: 4px;
}

.pr-merge-strategies {
  background-color: var(--lighter);
  border: 1px solid var(--light);
  border-radius: 4px;
  height: 88px;
  overflow: hidden;
  position: absolute;
  text-align: center;
  top: 35px;
  width: 80px;
  z-index: 1;
}

.pr-merge-strategies__strategy {
  color: var(--dark);
  cursor: pointer;
  border-bottom: 1px solid var(--light);
  padding: 2px 4px;
}

.pr-merge-strategies__strategy:hover {
  color: var(--darker);
}

.pr-status {
  align-items: center;
  color: var(--light);
  display: flex;
  font-size: 14px;
  margin-top: 8px;
}

.pr-status--open {
  color: var(--success);
}

.pr-status .dot {
  background-color: var(--light);
  border-radius: 7px;
  float: left;
  height: 14px;
  margin-right: 2px;
  width: 14px;
}

.pr-status--open .dot {
  background-color: var(--success);
}

</style>
