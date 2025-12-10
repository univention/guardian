import {test, expect} from '@playwright/test';

test('visiting root redirects to /roles', async ({page}) => {
  await page.goto('/');
  await expect(page).toHaveURL(/\/guardian\/management-ui\/roles/);
});

test('navigation', async ({page}) => {
  await page.goto('/univention/guardian/management-ui/roles');

  await page.getByRole('link', {name: 'Namespaces', exact: true}).click();
  await expect(page).toHaveURL(/\/univention\/guardian\/management-ui\/namespaces/);
  await page.getByRole('link', {name: 'Contexts', exact: true}).click();
  await expect(page).toHaveURL(/\/univention\/guardian\/management-ui\/contexts/);
  await page.getByRole('link', {name: 'Rollen', exact: true}).click();
  await expect(page).toHaveURL(/\/univention\/guardian\/management-ui\/roles/);

  await page.goto('/univention/guardian/management-ui/roles/edit/app-1:namespace-1:role-1');
  await page.getByRole('link', {name: 'Capabilities', exact: true}).click();
  await expect(page).toHaveURL(
    /\/univention\/guardian\/management-ui\/roles\/edit\/app-1:namespace-1:role-1\/capabilties/
  );
  await page.getByRole('link', {name: 'Rolle', exact: true}).click();
  await expect(page).toHaveURL(/\/univention\/guardian\/management-ui\/roles\/edit\/app-1:namespace-1:role-1/);
});
