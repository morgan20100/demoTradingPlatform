export interface QuerySetProduct {
  model: string;
  pk: number;
  fields: {
    id: number;
    name: string;
    productType: string;
    expiryDisplay: string;
    expiryTime: Date;
    contractSize: number;
    hedgeSubProductId: number;
  };
}
