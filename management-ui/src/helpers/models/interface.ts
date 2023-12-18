import type {UGridRow, UGridColumnDefinition, SubElementProps} from '@univention/univention-veb';

export type ObjectType = 'role' | 'context' | 'namespace' | 'capability';

export interface LabeledValue<T> {
  value: T;
  label: string;
}

export type GlobalAction = 'add';
export interface ListViewConfigs {
  role: ListViewConfig;
  context: ListViewConfig;
  namespace: ListViewConfig;
  capability: ListViewConfig;
}
export interface ListViewConfig {
  allowedGlobalActions: GlobalAction[];
  searchForm: Field[];
  searchFormValues: FormValues;
  columns: UGridColumnDefinition[];
}

export interface AddViewConfig {
  pages: Page[];
}

export type Access = 'none' | 'read' | 'write';
export type ContextAction = 'edit' | 'delete';

export interface Attribute {
  value?: unknown;
  access: Access;
}
export interface ListResponseModel {
  id: string;
  allowedActions: ContextAction[];
  attributes: Record<string, Attribute>;
}

export interface FieldExtendingInput {
  type: 'UExtendingInput';
  props: {
    name: string;
    label: string;
    description?: string;
    hint?: string;
    // required?: boolean;
    access?: 'write' | 'read' | 'none';
    rootElement: Field;
    extensions: Record<string, Field[]>;
  };
}
export interface FieldInputText {
  type: 'UInputText';
  props: {
    name: string;
    label: string;
    // modelValue: string;
    description?: string;
    hint?: string;
    required?: boolean;
    access?: 'write' | 'read' | 'none';
    validators?: ((value: string) => string)[];
  };
}
export interface FieldInputDate {
  type: 'UInputDate';
  props: {
    name: string;
    label: string;
    // modelValue: string;
    description?: string;
    hint?: string;
    required?: boolean;
    access?: 'write' | 'read' | 'none';
  };
}
export interface FieldInputPassword {
  type: 'UInputPassword';
  props: {
    name: string;
    label: string;
    // modelValue: string;
    description?: string;
    hint?: string;
    required?: boolean;
    access?: 'write' | 'read' | 'none';
  };
}
export interface FieldInputCheckbox {
  type: 'UInputCheckbox';
  props: {
    name: string;
    label: string;
    // modelValue: string;
    description?: string;
    hint?: string;
    required?: boolean;
    access?: 'write' | 'read' | 'none';
  };
}
export interface FieldSelect {
  type: 'USelect';
  props: {
    name: string;
    label: string;
    // modelValue: string;
    description?: string;
    hint?: string;
    required?: boolean;
    access?: 'write' | 'read' | 'none';
    options: {label: string; value: string}[];
  };
}
export interface FieldComboBox {
  type: 'UComboBox';
  props: {
    name: string;
    label: string;
    // modelValue: string;
    description?: string;
    hint?: string;
    required?: boolean;
    access?: 'write' | 'read' | 'none';
    standby?: any; // boolean | Ref<boolean>;
    options: {label: string; value: string}[];
  };
}
export interface FieldMultiSelect {
  type: 'UMultiSelect';
  props: {
    name: string;
    label: string;
    // modelValue: string;
    description?: string;
    hint?: string;
    required?: boolean;
    access?: 'write' | 'read' | 'none';
    columns: UGridColumnDefinition[];
    rows: UGridRow[];
  };
}
export interface FieldMultiInput {
  type: 'UMultiInput';
  props: {
    name: string;
    label: string;
    required: boolean;
    access?: 'write' | 'read' | 'none';
    subElements: Field[];
    description?: string;
    hint?: string;
    standby?: any; // boolean | Ref<boolean>;
  };
}
export interface FieldMultiObjectSelect {
  type: 'UMultiObjectSelect';
  props: {
    name: string;
    label: string;
    // modelValue: string;
    description?: string;
    hint?: string;
    required?: boolean;
    access?: 'write' | 'read' | 'none';

    initialRows: UGridRow[];
    columns: UGridColumnDefinition[];

    searchStandby: boolean;
    searchRows: UGridRow[];
    searchElements: SubElementProps[];
    searchColumns: UGridColumnDefinition[];
    searchCallback?: (values: Record<string, unknown>) => void;
  };
}
export interface FieldInputClassified {
  type: 'UInputClassified';
  props: {
    name: string;
    label: string;
    description?: string;
    hint?: string;
    access?: 'none';
  };
}
export type Field =
  | FieldComboBox
  | FieldExtendingInput
  | FieldInputCheckbox
  | FieldInputClassified
  | FieldInputDate
  | FieldInputPassword
  | FieldInputText
  | FieldMultiInput
  | FieldMultiObjectSelect
  | FieldMultiSelect
  | FieldSelect;

export interface Fieldset {
  label: string;
  name: string;
  rows: (Field | Field[])[];
}

export interface Page {
  label: string;
  name: string;
  fieldsets: Fieldset[];
}

export type FormValues = Record<string, unknown>;
export type DetailAction = 'save';
export interface DetailResponseModel {
  url: string;
  allowedActions: DetailAction[];
  pages: Page[];
  values: FormValues;
}
