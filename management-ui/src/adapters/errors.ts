export class InvalidAdapterError extends Error {
  constructor(msg: string) {
    super(msg);
    Object.setPrototypeOf(this, InvalidAdapterError.prototype);
  }
}
