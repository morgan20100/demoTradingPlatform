export interface QuerySetSubProduct {
  model: string;
  pk: number;
  fields: {
    name: string;
    callPut: string;
    product: number;
    strike: number;
    expiryType: string;
  };
}
