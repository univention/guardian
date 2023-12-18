export const authenticationPortSetting = 'managementUi.adapter.authenticationPort';

export interface AuthenticationSuccess {
  Authorization: string;
}

export interface AuthenticationPort {
  authenticated: boolean;
  username: string;

  // Authenticate the user
  authenticate(): Promise<boolean>;
  // Return an authorization header for use with the backend API
  getValidAuthorizationHeader(minTokenValidity?: number): Promise<AuthenticationSuccess>;
  // Log the user out of an existing session; returns true if successfully logged out
  logout(): Promise<boolean>;
}
