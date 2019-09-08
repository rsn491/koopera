export default class UserCredentials {

  constructor(sourceControlAccessToken, apiAccessToken) {
    this.sourceControlAccessToken = sourceControlAccessToken;
    this.apiAccessToken = apiAccessToken;
  }

  isValid() {
    return !!this.sourceControlAccessToken && !!this.apiAccessToken;
  }

};
