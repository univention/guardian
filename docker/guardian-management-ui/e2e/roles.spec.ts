import {test, expect, Locator, Page} from '@playwright/test';

test('ListView - page tabs are correct', async ({page}) => {
  await page.goto('/guardian/management-ui/roles');
  const buttons = page.locator('.routeButtons');
  await expect(buttons.getByText('Rollen')).toHaveAttribute('aria-current', 'page');
  await expect(buttons.getByText('Namespaces')).not.toHaveAttribute('aria-current', 'page');
  await expect(buttons.getByText('Contexts')).not.toHaveAttribute('aria-current', 'page');
});

async function uComboBoxLocator(page: Page, label: string): Promise<{ standbyLoc: Locator; inputLoc: Locator; selectOption: (option: string) => Promise<void>; optionsLoc: Locator; buttonLoc: Locator; expectToHaveOptions: (expectedOptions: string[]) => Promise<void> }> {
  const inputLoc = page.getByLabel(label);
  const optionsLoc = inputLoc.locator('~ .uComboBox__popup');
  const standbyLoc = page.locator(`div.uStandby:has(+ input[id="${await inputLoc.getAttribute('id')}"])`);
  const buttonLoc = inputLoc.locator('+ button');

  async function expectToHaveOptions(expectedOptions: string[], withExactCount = true) {
    await inputLoc.click();
    if (withExactCount) {
      await expect(optionsLoc.getByRole('option')).toHaveCount(expectedOptions.length);
    }
    for (const o of expectedOptions) {
      await expect(optionsLoc.getByRole('option', {
        name: o,
        exact: true,
      })).toBeAttached();
    }
    await buttonLoc.click();
  }

  async function selectOption(option: string) {
    await inputLoc.click();
    await optionsLoc.getByRole('option', {
      name: option,
      exact: true,
    }).click();
  }

  return {
    inputLoc,
    optionsLoc,
    standbyLoc,
    buttonLoc,
    expectToHaveOptions,
    selectOption,
  };
}


test('ListView - search form has correct options', async ({page}) => {
  await page.goto('/guardian/management-ui/roles');

  const appComboBox = await uComboBoxLocator(page, 'App');
  const namespaceComboBox = await uComboBoxLocator(page, 'Namensraum');

  // assert initial state
  await expect(appComboBox.inputLoc).toHaveValue('Alle');
  await expect(namespaceComboBox.inputLoc).toHaveValue('Alle');

  await expect(appComboBox.inputLoc).toBeEditable();
  await expect(namespaceComboBox.inputLoc).not.toBeEditable();

  await appComboBox.expectToHaveOptions([
    'Alle',
    'App 1',
    'App 2'
  ]);

  // check namespaceComboBox.input options
  const expectedNamespaceOptions = {
    'App 1': [
      'Alle',
      'Namespace 1 for App 1',
      'Namespace 2 for App 1',
    ],
    'App 2': [
      'Alle',
      'Namespace 1 for App 2',
      'Namespace 2 for App 2',
    ],
  };
  for (const app in expectedNamespaceOptions) {
    await appComboBox.selectOption(app);

    await expect(namespaceComboBox.standbyLoc).toBeVisible();
    await expect(namespaceComboBox.inputLoc).toBeEditable();

    const expectedOptions = expectedNamespaceOptions[app];
    await namespaceComboBox.expectToHaveOptions(expectedOptions);
  }
});

test('ListView - behaviour of namespace selection in conjunction with app selection', async ({page}) => {
  await page.goto('/guardian/management-ui/roles');

  const appComboBox = await uComboBoxLocator(page, 'App');
  const namespaceComboBox = await uComboBoxLocator(page, 'Namensraum');

  // assert initial state
  await expect(appComboBox.inputLoc).toHaveValue('Alle');
  await expect(namespaceComboBox.inputLoc).toHaveValue('Alle');

  await expect(appComboBox.inputLoc).toBeEditable();
  await expect(namespaceComboBox.inputLoc).not.toBeEditable();

  // select non 'All' App option
  await appComboBox.selectOption('App 1');

  // Namespace field should load values and become editable
  await expect(namespaceComboBox.standbyLoc).toBeVisible();
  await expect(namespaceComboBox.inputLoc).toBeEditable();

  // Select non 'All' Namespace option
  await namespaceComboBox.selectOption('Namespace 1 for App 1');

  // Selecting 'All' App option should reset Namespace field
  await appComboBox.selectOption('Alle');

  await expect(namespaceComboBox.standbyLoc).not.toBeVisible();
  await expect(namespaceComboBox.inputLoc).toHaveValue('Alle');
  await expect(namespaceComboBox.inputLoc).not.toBeEditable();
});

test('ListView - search form reset button', async ({page}) => {
  await page.goto('/guardian/management-ui/roles');

  const appComboBox = await uComboBoxLocator(page, 'App');
  const namespaceComboBox = await uComboBoxLocator(page, 'Namensraum');

  await expect(appComboBox.inputLoc).toHaveValue('Alle');
  await expect(namespaceComboBox.inputLoc).toHaveValue('Alle');
  await appComboBox.selectOption('App 1');
  await namespaceComboBox.selectOption('Namespace 1 for App 1');
  await page.getByRole('button', {name: 'Zurücksetzen', exact: true}).click();
  await expect(appComboBox.inputLoc).toHaveValue('Alle');
  await expect(namespaceComboBox.inputLoc).toHaveValue('Alle');
});

test('ListView - grid layout', async ({page, browserName}) => {
  test.skip(browserName !== 'chromium', 'Only check screenshot on chromium for now');

  await page.goto('/guardian/management-ui/roles');
  await expect(page.locator('.uStandbyFullScreen').first()).toBeVisible();
  await expect(page.locator('.uStandbyFullScreen').first()).not.toBeAttached();
  await expect(page).toHaveScreenshot('ListView-layout.png');
});

test('ListView - search', async ({page}) => {
  await page.goto('/guardian/management-ui/roles');

  const tbody = page.locator('tbody').nth(0);
  const rows = tbody.getByRole('row');
  await expect(rows).toHaveCount(0);

  interface Expectation {
    role: string;
    app: string;
    namespace: string;
  }
  async function searchAndExpect(expectation: Expectation[], app?: string, namespace?: string, ) {
    const _app = app || 'Alle';
    const appComboBox = await uComboBoxLocator(page, 'App');
    const namespaceComboBox = await uComboBoxLocator(page, 'Namensraum');

    await appComboBox.selectOption(_app);

    if (_app !== 'Alle') {
      await expect(namespaceComboBox.standbyLoc).not.toBeAttached();

      const _namespace = namespace || 'Alle';
      await namespaceComboBox.selectOption(_namespace);
    }


    await page.getByRole('button', {name: 'Suchen', exact: true}).click();
    await expect(page.locator('.uStandbyFullScreen')).toBeVisible();
    await expect(rows).toHaveCount(expectation.length);

    for (const e of expectation) {
      const row = rows
        .filter({has: page.getByText(`role-${e.role}`, {exact: true})})
        .filter({has: page.getByText(`app-${e.app}`, {exact: true})})
        .filter({has: page.getByText(`namespace-${e.namespace}`, {exact: true})})
        .filter({has: page.getByText(`Role ${e.role} for App ${e.app}, Namespace ${e.namespace}`)});

      await expect(row).toBeAttached();
    }
  }

  await searchAndExpect([{
    role: '1',
    app: '1',
    namespace: '1',
  }, {
    role: '2',
    app: '1',
    namespace: '1',
  }, {
    role: '1',
    app: '1',
    namespace: '2',
  }, {
    role: '2',
    app: '1',
    namespace: '2',
  }, {
    role: '1',
    app: '2',
    namespace: '1',
  }, {
    role: '2',
    app: '2',
    namespace: '1',
  }, {
    role: '1',
    app: '2',
    namespace: '2',
  }, {
    role: '2',
    app: '2',
    namespace: '2',
  }]);

  await searchAndExpect([{
    role: '1',
    app: '1',
    namespace: '1',
  }, {
    role: '2',
    app: '1',
    namespace: '1',
  }, {
    role: '1',
    app: '1',
    namespace: '2',
  }, {
    role: '2',
    app: '1',
    namespace: '2',
  }], 'App 1');

  await searchAndExpect([{
    role: '1',
    app: '1',
    namespace: '1',
  }, {
    role: '2',
    app: '1',
    namespace: '1',
  }], 'App 1', 'Namespace 1 for App 1');

  await searchAndExpect([{
    role: '1',
    app: '1',
    namespace: '2',
  }, {
    role: '2',
    app: '1',
    namespace: '2',
  }], 'App 1', 'Namespace 2 for App 1');

  await searchAndExpect([{
    role: '1',
    app: '2',
    namespace: '1',
  }, {
    role: '2',
    app: '2',
    namespace: '1',
  }, {
    role: '1',
    app: '2',
    namespace: '2',
  }, {
    role: '2',
    app: '2',
    namespace: '2',
  }], 'App 2');

  await searchAndExpect([{
    role: '1',
    app: '2',
    namespace: '1',
  }, {
    role: '2',
    app: '2',
    namespace: '1',
  }], 'App 2', 'Namespace 1 for App 2');

  await searchAndExpect([{
    role: '1',
    app: '2',
    namespace: '2',
  }, {
    role: '2',
    app: '2',
    namespace: '2',
  }], 'App 2', 'Namespace 2 for App 2');
});

test('ListView - add button in grid redirects correctly', async ({page}) => {
  await page.goto('/guardian/management-ui/roles');
  await page.locator('.uGrid__header').getByRole('button', {name: 'Hinzufügen', exact: true}).click();
  await expect(page).toHaveURL(/\/guardian\/management-ui\/roles/);
});


test('EditView; create - layout', async ({page, browserName}) => {
  test.skip(browserName !== 'chromium', 'Only check screenshot on chromium for now');

  await page.goto('/guardian/management-ui/roles/add');
  await expect(page.locator('.uStandbyFullScreen').first()).toBeVisible();
  await expect(page.locator('.uStandbyFullScreen').first()).not.toBeAttached();
  await expect(page).toHaveScreenshot('EditView-create-layout.png');
});

test('EditView; create - form fields have correct values', async ({page}) => {
  await page.goto('/guardian/management-ui/roles/add');

  const appComboBox = await uComboBoxLocator(page, 'App');
  const namespaceComboBox = await uComboBoxLocator(page, 'Namensraum');

  await expect(appComboBox.inputLoc).toHaveValue('');
  await expect(namespaceComboBox.inputLoc).toHaveValue('');

  await appComboBox.expectToHaveOptions([
    'App 1',
    'App 2',
  ]);
  await namespaceComboBox.expectToHaveOptions([]);
  const expectedNamespaceOptions = {
    'App 1': [
      'Namespace 1 for App 1',
      'Namespace 2 for App 1',
    ],
    'App 2': [
      'Namespace 1 for App 2',
      'Namespace 2 for App 2',
    ],
  };
  for (const app in expectedNamespaceOptions) {
    await appComboBox.selectOption(app);

    await expect(namespaceComboBox.standbyLoc).toBeVisible();
    await expect(namespaceComboBox.inputLoc).toBeEditable();

    const expectedOptions = expectedNamespaceOptions[app];
    await namespaceComboBox.expectToHaveOptions(expectedOptions);
  }
});

test('EditView; create - back button', async ({page}) => {
  // if no inputs have been made the back button will just return to /roles
  await page.goto('/guardian/management-ui/roles/add');
  await page.getByRole('button', {name: 'Zurück', exact: true}).click();
  await expect(page).toHaveURL(/\/guardian\/management-ui\/roles/);

  // if inputs have been made a modal should appear
  const dialog = page.getByRole('dialog');

  await page.goto('/guardian/management-ui/roles/add');
  await page.getByLabel('Name', {exact: true}).fill('test');

  await page.getByRole('button', {name: 'Zurück', exact: true}).click();
  await expect(dialog).toContainText('Möchten Sie den Erstellungsdialog abbrechen?');
  await dialog.getByRole('button', {name: 'Erstellen fortführen', exact: true}).click();
  await expect(dialog).not.toBeAttached();
  await expect(page).toHaveURL(/\/guardian\/management-ui\/roles\/add/);

  await page.getByRole('button', {name: 'Zurück', exact: true}).click();
  await expect(dialog).toContainText('Möchten Sie den Erstellungsdialog abbrechen?');
  await dialog.getByRole('button', {name: 'Erstellen abbrechen', exact: true}).click();
  await expect(page).toHaveURL(/\/guardian\/management-ui\/roles/);
});

test('EditView; create - required fields are checked', async ({page}) => {
  await page.goto('/guardian/management-ui/roles/add');

  const labels = ['App', 'Namensraum', 'Name'];
  for (const label of labels) {
    await expect(page.getByLabel(label, {exact: true})).toHaveAttribute('aria-invalid', 'false');
  }

  await page.getByRole('button', {name: 'Rolle anlegen', exact: true}).click();

  for (const label of labels) {
    await expect(page.getByLabel(label, {exact: true})).toHaveAttribute('aria-invalid', 'true');
  }
});


const gridShouldReload = [true, false];
for (const doesGridReload of gridShouldReload) {
  test(`EditView; create - create object and grid reloads afterwards (${doesGridReload})`, async ({page}) => {
    await page.goto('/guardian/management-ui/roles');
    if (doesGridReload) {
      await page.getByRole('button', {name: 'Suchen', exact: true}).click();
      await expect(page.locator('.uStandbyFullScreen')).toBeVisible();
      await expect(page.locator('.uStandbyFullScreen')).not.toBeAttached();
    }
    await page.locator('.uGrid__header').getByRole('button', {name: 'Hinzufügen', exact: true}).click();

    await (await uComboBoxLocator(page,'App')).selectOption('App 1');
    await (await uComboBoxLocator(page,'Namensraum')).selectOption('Namespace 1 for App 1');
    const name = 'somename';
    await page.getByLabel('Name', {exact: true}).fill(name);

    await page.getByRole('button', {name: 'Rolle anlegen', exact: true}).click();

    const dialog = page.getByRole('dialog');
    await expect(dialog).toContainText(`Das Rollen-Objekt '${name}' wurde erfolgreich angelegt`);
    await dialog.getByRole('button', {name: 'OK', exact: true}).click();
    await expect(page).toHaveURL(/\/guardian\/management-ui\/roles/);

    const rows = page.locator('tbody').nth(0).getByRole('row');
    const row = rows
      .filter({has: page.getByText('somename', {exact: true})})
      .filter({has: page.getByText('app-1', {exact: true})})
      .filter({has: page.getByText('namespace-1', {exact: true})});
    if (doesGridReload) {
      await expect(page.locator('.uStandbyFullScreen').first()).toBeVisible();
      await expect(page.locator('.uStandbyFullScreen').first()).not.toBeAttached();

      await expect(rows).toHaveCount(9);
      await expect(row).toBeAttached();
    } else {
      await expect(rows).toHaveCount(0);
      await expect(row).not.toBeAttached();
    }
  });
}

test('ListView - grid edit button opens correct page', async ({page}) => {
  await page.goto('/guardian/management-ui/roles');
  await page.getByRole('button', {name: 'Suchen', exact: true}).click();

  const rows = page.locator('tbody').nth(0).getByRole('row');
  const row = rows
    .filter({has: page.getByText('role-1', {exact: true})})
    .filter({has: page.getByText('app-1', {exact: true})})
    .filter({has: page.getByText('namespace-1', {exact: true})});

  await row.getByRole('button', {name: 'role-1', exact: true}).click();

  await expect(page).toHaveURL(/\/guardian\/management-ui\/roles\/edit\/app-1:namespace-1:role-1/);
});

test('EditView; update - layout', async ({page, browserName}) => {
  test.skip(browserName !== 'chromium', 'Only check screenshot on chromium for now');

  await page.goto('/guardian/management-ui/roles/edit/app-1:namespace-1:role-1');
  await expect(page.locator('.uStandbyFullScreen').first()).toBeVisible();
  await expect(page.locator('.uStandbyFullScreen').first()).not.toBeAttached();
  await expect(page).toHaveScreenshot('EditView-update-layout.png');
});

test('EditView; update - back button', async ({page}) => {
  // if no inputs have been made the back button will just return to /roles
  await page.goto('/guardian/management-ui/roles/edit/app-1:namespace-1:role-1');
  await page.getByRole('button', {name: 'Zurück', exact: true}).click();
  await expect(page).toHaveURL(/\/guardian\/management-ui\/roles/);

  // if inputs have been made a modal should appear
  const dialog = page.getByRole('dialog');

  await page.goto('/guardian/management-ui/roles/edit/app-1:namespace-1:role-1');
  await page.getByLabel('Anzeigename', {exact: true}).fill('test');

  await page.getByRole('button', {name: 'Zurück', exact: true}).click();
  await expect(dialog).toContainText('Einige Änderungen sind noch nicht gespeichert. Möchten Sie abbrechen?');
  await dialog.getByRole('button', {name: 'Bearbeiten fortführen', exact: true}).click();
  await expect(dialog).not.toBeAttached();
  await expect(page).toHaveURL(/\/guardian\/management-ui\/roles/);

  await page.getByRole('button', {name: 'Zurück', exact: true}).click();
  await expect(dialog).toContainText('Einige Änderungen sind noch nicht gespeichert. Möchten Sie abbrechen?');
  await dialog.getByRole('button', {name: 'Änderungen verwerfen', exact: true}).click();
  await expect(page).toHaveURL(/\/guardian\/management-ui\/roles/);
});

test('EditView; update - update object and grid reloads afterwards', async ({page}) => {
  await page.goto('/guardian/management-ui/roles');

  await page.getByRole('button', {name: 'Suchen', exact: true}).click();
  await expect(page.locator('.uStandbyFullScreen')).toBeVisible();
  await expect(page.locator('.uStandbyFullScreen')).not.toBeAttached();

  const rows = page.locator('tbody').nth(0).getByRole('row');

  const row = rows
    .filter({has: page.getByText('role-1', {exact: true})})
    .filter({has: page.getByText('app-1', {exact: true})})
    .filter({has: page.getByText('namespace-1', {exact: true})});

  await expect(row).toBeAttached();
  await expect(row.getByText('Role 1 for App 1, Namespace 1')).toBeAttached();

  await row.getByRole('button', {name: 'role-1', exact: true}).click();

  const newDisplayName = 'newdisplayname';
  await page.getByLabel('Anzeigename', {exact: true}).fill(newDisplayName);

  await page.locator('.listView__header__buttons').getByRole('button', {name: 'Speichern', exact: true}).filter({}).click();

  await expect(page).toHaveURL(/\/guardian\/management-ui\/roles/);

  await expect(page.locator('.uStandbyFullScreen').first()).toBeVisible();
  await expect(page.locator('.uStandbyFullScreen').first()).not.toBeAttached();

  await expect(row).toBeAttached();
  await expect(row.getByText(newDisplayName)).toBeAttached();
});


// For some reason the vue RouterLink does not have aria-current="page" set when navigating to the page directly.
// It is set when getting there vie the ListView.
// Not sure if user error in router setup or vue but.
test.skip('EditView; update - page tabs are correct', async ({page}) => {
  await page.goto('/guardian/management-ui/roles/edit/app-1:namespace-1:role-1');
  await expect(page.locator('.uStandbyFullScreen').first()).toBeVisible();
  await expect(page.locator('.uStandbyFullScreen').first()).not.toBeAttached();
  const buttons = await page.locator('.routeButtons');
  await expect(buttons.getByText('Rolle')).toHaveAttribute('aria-current', 'page');
  await expect(buttons.getByText('Capabilites')).not.toHaveAttribute('aria-current', 'page');
});
