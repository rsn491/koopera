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
            Overview
          </div>
          <div :class="showDescription ?
            'pr-header__links__link' :
            'pr-header__links__link pr-header__links__link--active'"
            v-on:click="() => this.showDescription = false">
            <span class="material-icons">code</span>
            Files ({{ files.length }})
          </div>
        </div>
      </div>
    </div>
    <Loader v-bind:show="loadingPr" />
    <div :class="loadingPr ? 'd-none' : 'row'">
      <div class='col-12' v-if="showDescription">
        <div class='description-container'>
          <h6>
            Description
          </h6>
          <div v-html="body"/>
        </div>

        <div class='merge-container'>
          <div class='merge-btn btn btn-success'>
            <button class='btn btn-success' v-on:click='merge'>
              {{ this.mergeStrategy }}
            </button>
            <button class="btn btn-success material-icons"
              v-on:click="() => showMergeStrategies = !showMergeStrategies">
              merge_type
            </button>
          </div>
          <div class='pr-merge-strategies' v-if=showMergeStrategies>
            <div class='pr-merge-strategies__strategy'
              v-on:click="() => selectMergeStrategy('merge')">
              Merge
            </div>
            <div class='pr-merge-strategies__strategy'
              v-on:click="() => selectMergeStrategy('squash')">
              Squash
            </div>
            <div class='pr-merge-strategies__strategy'
              v-on:click="() => selectMergeStrategy('rebase')">
              Rebase
            </div>
          </div>
        </div>
      </div>
      <div class='col-3 file-explorer-container text-left' v-if="!showDescription">
        <div class='file-list'>
          <div class='file-change' v-for='file in files' v-bind:key='file.path'>
            <span v-if="file.status === 'removed'" class="material-icons removed-file">remove</span>
            <span v-else-if="file.status === 'added'" class="material-icons added-file">add</span>
            <span v-else class="material-icons modified-file">emergency</span>
              <a v-bind:class="filePath === file.path ?
                'btn alert p-0 mb-1 file-selected' :
                'btn alert p-0 mb-1'"
                v-on:click='() =>
                loadFile(file.path, file.ref, file.prevRef, file.status, file.patch)'>
                {{ file.path }}
              </a>
          </div>
        </div>
      </div>
      <div class='col-9 file-view-container' v-if="!showDescription">
        <Loader v-bind:show="loadingFile" />
        <div id="code-change-wrapper"
          :class="loadingFile ? 'd-none' : isIpynbFile && 'koopera-nb'"
          v-html="fileDisplay"/>
      </div>
    </div>
  </div>
</template>

<script>

import HtmlDiff from 'htmldiff-js';
import { Diff2HtmlUI } from 'diff2html/lib/ui/js/diff2html-ui-slim';

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
      mergeStrategy: 'merge',
      files: [],
      filePath: '',
      fileDisplay: '',
      fileComments: [],
      fileCommentElements: {},
      title: null,
      state: null,
      authorAvatarUrl: null,
      body: null,
      isIpynbFile: null,
      penedCodeComment: null,
    };
  },
  methods: {
    selectMergeStrategy(mergeStrategy) {
      this.mergeStrategy = mergeStrategy;
      this.showMergeStrategies = false;
    },
    merge() {
      fetch(
        getAPIUrl(`coderepositories/${this.$route.params.codeRepositoryId}/pullrequests/${this.$route.params.pullRequestNumber}/merge`),
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${this.userCredentials.apiAccessToken}`,
          },
          body: JSON.stringify({
            mergeStrategy: this.mergeStrategy
          }),
        },
      ).then((response) => {
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
          this.fileCommentElements[codeBlockId] = this.openedCodeComment;
          this.openedCodeComment = null;
          this.$forceUpdate();
        });
      });
    },
    async getFileContent(path, ref) {
      return new Promise(resolve => fetch(getAPIUrl(`coderepositories/${this.$route.params.codeRepositoryId}/file?path=${path}&ref=${ref}`), {
        headers: {
          Authorization: `Bearer ${this.userCredentials.apiAccessToken}`,
        },
      }).then(response => response.json().then(json => resolve(json.body))));
    },
    async getPullRequestData() {
      return new Promise(resolve => fetch(getAPIUrl(`coderepositories/${this.$route.params.codeRepositoryId}/pullrequests/${this.$route.params.pullRequestNumber}`), {
        headers: {
          Authorization: `Bearer ${this.userCredentials.apiAccessToken}`,
        },
      }).then((response) => {
        if (response.status === 401 || response.status === 422) {
          this.$router.push({ name: 'login' });
          return;
        }
        response.json().then(json => resolve(json));
      }));
    },
    async loadPullRequestData() {
      const pullRequestInfo = await this.getPullRequestData();

      store.setCodeRepo(this.$route.params.codeRepositoryId, pullRequestInfo.codeRepoName);
      this.authorAvatarUrl = pullRequestInfo.userAvatarUrl;
      this.body = pullRequestInfo.body;
      this.state = pullRequestInfo.state;
      this.files = pullRequestInfo.files;
      this.title = pullRequestInfo.title;
      this.fileComments = {};

      if (this.filePath) {
        pullRequestInfo.comments
          .filter(comment => comment.filePath === this.filePath)
          .forEach((comment) => {
            const { codeBlockId } = comment;

            if (!(codeBlockId in this.fileComments)) {
              this.fileComments[codeBlockId] = [];
            }

            this.fileComments[codeBlockId].push({
              id: comment.id,
              author: comment.author,
              comment: comment.body,
              updatedAt: comment.updatedAt,
            });
          });
      }
    },
    async loadFile(path, ref, prevRef, status, patch) {
      this.filePath = path;
      this.loadingFile = true;

      this.isIpynbFile = this.filePath.endsWith('.ipynb');
      if (this.isIpynbFile) {
        const fileContent = status === 'removed'
          ? ''
          : await this.getFileContent(path, ref);
        const prevFileContent = status === 'added'
          ? ''
          : await this.getFileContent(path, prevRef);
        this.fileDisplay = HtmlDiff.execute(prevFileContent, fileContent);
      } else {
        const diff = `--- ${path}\n+++ ${path}\n${patch}`;
        // eslint-disable-next-line no-undef
        const diff2htmlUi = new Diff2HtmlUI(document.getElementById('code-change-wrapper'), diff, {
          drawFileList: false,
          matching: 'lines',
          rawTemplates: {
            'line-by-line-file-diff': `
            <div id="{{fileHtmlId}}" class="d2h-file-wrapper" data-lang="{{file.language}}">
                <div class="d2h-file-diff">
                    <div class="d2h-code-wrapper">
                        <table class="d2h-diff-table">
                            <tbody class="d2h-diff-tbody">
                            {{{diffs}}}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>`
          }
        });
        diff2htmlUi.draw();
        diff2htmlUi.highlightCode();
      }

      // refresh pull request data
      await this.loadPullRequestData();
      this.loadingFile = false;
      this.renderFileComments = true;
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
      if (!this.fileCommentElements[codeBlockId]) {
        // first comment for this code block
        this.openedCodeComment = CodeComment.createNew(
          this.createContainerElement(elementToAttach, codeBlockId),
          this.filePath,
          codeBlockId,
          this.addComment
        );
      } else {
        this.fileCommentElements[codeBlockId].open();
        this.openedCodeComment = this.fileCommentElements[codeBlockId];
      }

      this.$forceUpdate();
    },
    createContainerElement(elementToAttach, codeBlockId) {
      if (this.isIpynbFile) {
        const containerElement = document.createElement('div');
        containerElement.setAttribute('class', 'd-flex');
        elementToAttach.appendChild(containerElement);
        return containerElement;
      }

      const containerElement = document.createElement('tr');
      const linenoElements = Array.from(document.getElementsByClassName('d2h-code-linenumber')).map(element => element.parentElement);

      if (codeBlockId + 1 >= linenoElements.length) {
        // comment in last line
        elementToAttach.parentElement.appendChild(containerElement);
      } else {
        const targetElement = linenoElements[codeBlockId + 1];
        targetElement.parentElement.insertBefore(containerElement, targetElement);
      }

      containerElement.appendChild(document.createElement('td'));
      containerElement.appendChild(document.createElement('td'));

      return containerElement.lastChild;
    },
    attachCodeCommentHandlers(matches) {
      if (!this.renderFileComments) {
        return;
      }

      for (let i = 0; i < matches.length; i += 1) {
        const elementToAttach = matches[i];
        const codeBlockId = i;
        const codeBlockComments = this.fileComments
          && this.fileComments[codeBlockId];

        if (this.renderFileComments && !!codeBlockComments) {
          // has code block comment -> register and render!
          const containerElement = this.createContainerElement(elementToAttach, codeBlockId);
          this.fileCommentElements[codeBlockId] = CodeComment.createExisting(
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
    if (this.loadingFile || !this.filePath) {
      return;
    }

    if (this.isIpynbFile) {
      this.attachCodeCommentHandlers(document.getElementsByClassName('inner_cell'));
    } else {
      this.attachCodeCommentHandlers(Array.from(document.getElementsByClassName('d2h-code-linenumber')).map(element => element.parentElement));
    }
  },
  async created() {
    if (!this.userCredentials.isValid()) {
      this.$router.push({ name: 'login' });
    }

    await this.loadPullRequestData();
    this.loadingPr = false;
  },
};


</script>

<style>

.inner_cell {
  cursor: pointer;
}

.file-view-container ins {
    text-decoration: none;
    background-color: #d4fcbc;
}

.file-view-container ins img {
    border: 2px solid var(--success);
    padding: 4px;
}

.file-view-container .output_png ins {
    background-color: unset;
}

.file-view-container del {
    text-decoration: none;
    background-color: #fbb6c2;
    color: #555;
}

.file-view-container del img {
    border: 2px solid #fbb6c2;
    padding: 8px;
    margin-right: 8px;
}

.file-view-container .output_png del {
    background-color: unset;
}

.file-view-container .linenos:hover {
  opacity: 0.6;
  background-color: var(--darker);
}

.file-view-container span.linenos {
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

.file-list .file-change {
  align-items: center;
  color: var(--dark);
  display: flex;
}

.file-list .file-change a:hover {
  color: var(--darker);
  font-weight: bold;
}

.file-list .file-change .file-selected {
  color: var(--darker);
  font-weight: bold;
}

.file-list .file-change a {
  margin-bottom: 0!important;
}

.file-list .file-change .material-icons {
  font-size: 20px;
  margin-right: 4px;
}

.file-list .file-change span {
  margin: 4px 0;
}

.file-list .file-change .removed-file {
  color: red
}

.file-list .file-change .added-file {
  color: var(--success);
}

.file-list .file-change .modified-file {
  color: var(--dark);
}

.code-comment-container {
  background-color: #f8f9fa;
  border: 1px solid var(--dark);
  border-radius: 2px;
  font-size: 1rem;
  font-weight: 400;
  margin-bottom: 8px;
  margin-left: 0;
  margin-top: 8px;
  padding: 8px;
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
  top: 60px;
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
  font-weight: bold;
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

.description-container h6 {
  border-bottom: 1px solid var(--lighter);
  color: var(--darker);
  font-weight: bold;
}

.description-container div {
  padding: 24px;
}

.merge-container {
  border-top: 1px solid var(--lighter);
  margin-top: 24px;
  padding-top: 16px;
  position: relative;
}

.merge-btn {
  padding: 0;
}

.merge-btn button:first-of-type {
  text-transform: capitalize;
}

.merge-btn .material-icons {
  border-left: 1px solid var(--light);
  border-radius: 0;
}

</style>
