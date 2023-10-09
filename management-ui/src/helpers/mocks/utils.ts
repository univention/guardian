export const fetchMockData = <T>(mockData: T, name: string): Promise<T> => {
  console.debug(`${name}. VITE_USE_REAL_BACKEND===false in DEV mode. Returning mock data:`, mockData);
  return new Promise(resolve => {
    setTimeout(() => {
      resolve(mockData);
    }, 1000);
  });
};

