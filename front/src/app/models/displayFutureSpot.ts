import { timer } from 'rxjs';

import { QuerySetProduct } from './querySetProduct';
import { QuerySetSubProduct } from './querySetSubProduct';
import { QuerySetStreamPrice } from './querySetStreamPrice';
import { StreamPrice } from './streamPrice';
import { Position } from './position';

export interface IDisplayFutureSpot {
  // dictionary with id = 'subProductId'
  id: number;
  productId: number;
  productType: string;
  displayName: string;
  size: number;
  bid: number;
  offer: number;
  ts: number;
}

export class DisplayFutureSpot implements IDisplayFutureSpot {
  public id: number;
  public productId: number;
  public productType: string;
  public displayName: string;
  public size = 0;
  public avgPrice = 0;
  public contractSize: number;
  public bid: number;
  public offer: number;

  public MTM = 0;

  public ts: number;
  public move = 0;
  public bidHovered = false;
  public offerHovered = false;

  constructor(
    QSsubProduct: QuerySetSubProduct,
    QSproduct: QuerySetProduct,
    QSstreamPrice: QuerySetStreamPrice
  ) {
    this.id = QSstreamPrice.pk;
    this.productId = QSproduct.pk;
    this.productType = QSproduct.fields.productType;

    if (this.productType === 'S') {
      this.displayName = QSproduct.fields.name;
    } else if (this.productType === 'F') {
      this.displayName =
        QSproduct.fields.name + ' ' + QSproduct.fields.expiryDisplay;
    }

    this.bid = QSstreamPrice.fields.bid;
    this.offer = QSstreamPrice.fields.offer;
    this.ts = QSstreamPrice.fields.ts;
    this.contractSize = QSproduct.fields.contractSize;
  }

  update(data: StreamPrice): void {
    if (data.bid > this.bid) {
      this.move = 1;
    } else if (data.bid < this.bid) {
      this.move = -1;
    } else {
      this.move = 0;
    }

    this.bid = data.bid;
    this.offer = data.offer;
    this.ts = data.ts;

    if (this.size !== 0) {
      this.calculateMTM();
    }

    const myTimer = timer(500);
    myTimer.subscribe(done => (this.move = 0));
  }

  updatePosition(data: Position): void {
    this.size = data.size;
    if (data.buy === false) {
      this.size = -this.size;
    }
    this.avgPrice = Math.round(data.avgPrice * 100) / 100;

    this.calculateMTM();
  }

  calculateMTM(): void {
    if (this.size === 0) {
      this.MTM = 0;
    } else if (this.size > 0) {
      this.MTM = this.size * (this.bid - this.avgPrice) * this.contractSize;
    } else if (this.size < 0) {
      this.MTM = this.size * (this.offer - this.avgPrice) * this.contractSize;
    }
  }
}
