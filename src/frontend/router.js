import Vue from 'vue';
import Router from 'vue-router';
import Home from './views/Home.vue';
import Login from './views/Login.vue';

Vue.use(Router);

export default new Router({
  mode: 'history',
  base: process.env.BASE_URL,
  routes: [
    {
      path: '/',
      name: 'home',
      component: Home,
    },
    {
      path: '/login',
      name: 'login',
      component: Login,
    },
    {
      path: '/coderepositories/:codeRepositoryId/pullrequests',
      name: 'pullRequests',
      component: () => import('./views/PullRequests.vue'),
    },
    {
      path: '/coderepositories/:codeRepositoryId/pullrequests/:pullRequestNumber',
      name: 'pullRequest',
      component: () => import('./views/PullRequest.vue'),
    },
  ],
});
