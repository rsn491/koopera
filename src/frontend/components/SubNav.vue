<template>
  <div v-if='shouldRender()' class='subnav'>
    <router-link class='subnav--baselink' v-bind:to='getBaseLinkRef()'>
      {{ getBaseLinkTitle() }}
    </router-link>
    /
    <router-link class='subnav--secondlink'
      v-if='getSecondLinkTitle()' v-bind:to='getSecondLinkRef()'>
      {{ getSecondLinkTitle() }}
    </router-link>
  </div>
</template>

<script>

import store from '../store';

export default {
  name: 'SubNav',
  methods: {
    shouldRender() {
      return window.location.pathname !== '/login';
    },
    isPullRequestView() {
      return window.location.pathname === '/'
        || window.location.pathname.startsWith('/coderepositories');
    },
    getBaseLinkTitle() {
      return this.isPullRequestView() ? 'Pull Requests' : 'Notebooks';
    },
    getBaseLinkRef() {
      return this.isPullRequestView() ? '/' : '/notebooks/';
    },
    getSecondLinkTitle() {
      return store.getCodeRepoName(this.$route.params.codeRepositoryId);
    },
    getSecondLinkRef() {
      return this.$route.params.codeRepositoryId && `/coderepositories/${this.$route.params.codeRepositoryId}/pullrequests/`;
    },
  },
  data() {
    return {
      state: store.state,
    };
  },
};

</script>

<style>

.subnav {
  color: var(--light);
  font-weight: 500;
  margin-bottom: 8px;
  margin-top: 16px;
}

.subnav--baselink {
 color: var(--darker);
}

.subnav--secondlink {
 color: var(--dark);
}

</style>
