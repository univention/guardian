import {defineStore} from 'pinia';
import {ref} from 'vue';

export interface ApplicationError {
  message: string;
  title?: string;
  unRecoverable?: boolean;
}

const errorsEqual = (a: ApplicationError, b: ApplicationError): boolean =>
  a.message === b.message && a.title === b.title && a.unRecoverable === b.unRecoverable;

export const useErrorStore = defineStore('error', () => {
  const activeError = ref<ApplicationError | null>(null);

  const errorQueue: ApplicationError[] = [];

  const _updateActiveError = (): void => {
    if (errorQueue.length > 0) {
      // TODO typing
      // @ts-ignore
      activeError.value = errorQueue[0];
    } else {
      activeError.value = null;
    }
  };

  const push = (error: ApplicationError): void => {
    if (errorQueue.find(existingError => errorsEqual(existingError, error))) {
      // This exact error is already in queue -> skip
      return;
    }
    errorQueue.push(error);
    _updateActiveError();
  };

  const advance = (): void => {
    errorQueue.shift();
    _updateActiveError();
  };

  return {
    activeError,
    push,
    advance,
  };
});
