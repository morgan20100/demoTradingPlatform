export interface Position {
  id: number;
  buy: boolean;
  avgPrice: number;
  lastTradeTs: Date;
  size: number;
  subProduct: number;
}
