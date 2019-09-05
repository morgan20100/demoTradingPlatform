import { QuerySetSubProduct } from './querySetSubProduct';
import { QuerySetProduct } from './querySetProduct';

export interface ITrade {
  id: number;
  buy: boolean;
  position: number;
  price: number;
  size: number;
  subProduct: number;
  ts: Date;
}

export class Trade implements ITrade {
  public id: number;
  public buy: boolean;
  public position: number;
  public price: number;
  public size: number;
  public subProduct: number;
  public ts: Date;

  public displayBuySell: string;
  public displayName: string;

  constructor(
    QSproduct: QuerySetProduct,
    QSsubProduct: QuerySetSubProduct,
    id: number,
    buy: boolean,
    position: number,
    price: number,
    size: number,
    subProduct: number,
    ts: Date
  ) {
    this.id = id;
    this.buy = buy;
    this.position = position;
    this.price = price;
    this.size = size;
    this.subProduct = subProduct;
    this.ts = ts;

    this.displayBuySell = this.buy ? 'Buy' : 'Sell';

    this.displayName =
      QSproduct.fields.name + ' ' + QSproduct.fields.expiryDisplay + ' ';

    if (QSproduct.fields.productType === 'O') {
      this.displayName += ' ' + QSsubProduct.fields.strike;
      if (QSsubProduct.fields.callPut === 'C') {
        this.displayName += ' Call';
      } else {
        this.displayName += ' Put';
      }
    }
  }
}
