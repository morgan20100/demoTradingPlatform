export interface QuerySetStreamPrice {
  model: string;
  pk: number; // subproduct_id
  fields: {
    bid: number;
    offer: number;
    ts: number;
  };
}
