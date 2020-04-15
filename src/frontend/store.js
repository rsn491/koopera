const store = {
  state: {
    codeRepoId: null,
    codeRepoName: ''
  },
  setCodeRepo(id, name) {
    this.state.codeRepoId = id;
    this.state.codeRepoName = name;
  },
  getCodeRepoName(id) {
    if (this.state.codeRepoId !== id) {
      return null;
    }
    return this.state.codeRepoName;
  }
};

export default store;
