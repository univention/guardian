import i18next from 'i18next';

export function validateName(value: string): string {
  const regEx = /^[a-z][a-z0-9\-_]*$/;
  if (value && !regEx.test(value)) {
    return i18next.t('validators.validateName');
  }
  return '';
}
