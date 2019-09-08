import UserCredentials from './userCredentials';

export default class CredentialManager {
  static store(sourceControlAccessToken, apiAccessToken) {
    localStorage.setItem('sourceControlAccessToken', sourceControlAccessToken);
    localStorage.setItem('apiAccessToken', apiAccessToken);
  }

  static load() {
    return new UserCredentials(
      localStorage.getItem('sourceControlAccessToken'),
      localStorage.getItem('apiAccessToken'),
    );
  }

  static erase() {
    localStorage.removeItem('sourceControlAccessToken');
    localStorage.removeItem('apiAccessToken');
  }
}
