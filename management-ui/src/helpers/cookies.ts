export const getCookie = (name: string): string | undefined => {
  const cookies: Record<string, string> = {};
  document.cookie.split('; ').forEach(cookieWithValue => {
    const idx = cookieWithValue.indexOf('=');
    const cookieName = cookieWithValue.slice(0, idx);
    const value = cookieWithValue.slice(idx + 1);
    cookies[cookieName] = value;
  });
  return cookies[name];
};
