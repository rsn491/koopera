<template>
  <div class='container box-container'>
    <div :class="loadingPr ? 'd-none' : 'pr-header'">
      <div class="pr-header__info">
        <div class='pr-title'>
          {{ title }}
        </div>
        <div class='author-avatar' :style="`background-image: url(${authorAvatarUrl})`"/>
      </div>
      <div class="pr-header__actions">
        <div :class="showDescription ?
          'pr-header__actions__action pr-header__actions__action--active' :
          'pr-header__actions__action'"
          v-on:click="() => this.showDescription = true">
          <span class="material-icons" >subject</span>
          Description
        </div>
        <div :class="showDescription ?
          'pr-header__actions__action' :
          'pr-header__actions__action pr-header__actions__action--active'"
          v-on:click="() => this.showDescription = false">
          <span class="material-icons">code</span>
          Files ({{ files.length }})
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
      title: null,
      authorAvatarUrl: null,
      body: null,
      showDescription: true,
      files: [],
      filePath: '',
      fileDisplay: '',
      openedCodeComment: null,
      pullRequestComments: {},
      fileComments: {},
      isIpynbFile: null,
    };
  },
  methods: {
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
        this.files = json.files;
        this.title = json.title;
        this.authorAvatarUrl = json.userAvatarUrl;
        this.body = json.body;

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
  border-bottom: 1px solid var(--lighter);
  margin-bottom: 24px;
}

.pr-header__info {
  align-items: center;
  display: flex;
  margin-bottom: 18px;
  padding: 0 4px;
}

.pr-header__actions {
  display: flex;
  font-weight: bold;
  color: var(--dark);
}

.pr-header__actions__action {
  align-items: center;
  cursor: pointer;
  display: flex;
  margin-right: 8px;
  padding: 4px 2px;
}

.pr-header__actions__action--active {
  border-bottom: 2px solid var(--darker);
  color: var(--darker);
  padding-bottom: 2px;
}

.pr-header__actions .material-icons {
  margin-right: 2px;
}

.pr-header .pr-title {
  color: var(--darker);
  font-size: 24px;
  flex-grow: 1;
}

.pr-header .author-avatar {
  background-size: contain;
  background-position-x: center;
  height: 60px;
  width: 60px;
  background-repeat: no-repeat;
  border-radius: 4px;
}

</style>
