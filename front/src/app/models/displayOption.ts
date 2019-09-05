import { StreamPrice } from './streamPrice';
import { QuerySetSubProduct } from './querySetSubProduct';
import { QuerySetProduct } from './querySetProduct';
import { Position } from './position';
import { timer } from 'rxjs';
import { GreeksData } from './greeksData';

export interface IDisplayOption {
  // dictionary with id and key = 'productId - strike'
  id: string;
  productId: number;
  callStreamPriceId: number;
  putStreamPriceId: number;
  callSubProductId: number;
  putSubProductId: number;

  contractSize: number;

  displayName: string; // OESX SEP19 3200 C

  callPosition: number;
  callAvgPrice: number;
  callBid: number;
  callThPrice: number;
  callOffer: number;

  strike: number;

  putBid: number;
  putThPrice: number;
  putOffer: number;
  putPosition: number;
  putAvgPrice: number;

  expiryType: string;

  ts: number;

  iv: number;
  deltaCall: number;
  deltaPut: number;
  deltaTotal: number;
  gamma: number;
  gammaTotal: number;
  vega: number;
  vegaTotal: number;
  thetaCall: number;
  thetaPut: number;
  thetaTotal: number;
  rhoCall: number;
  rhoPut: number;
  rhoTotal: number;

  hedgeSubProductId: number;

  MTM: number;

  update(data: StreamPrice): void;
  updatePosition(data: Position): void;
  updateGreeks(data: GreeksData): void;
  calculateMTM(): void;
  calculateGreeks(): void;
}

export class DisplayOption implements IDisplayOption {
  public id: string;
  public productId: number;
  public callStreamPriceId: number;
  public putStreamPriceId: number;
  public callSubProductId: number;
  public putSubProductId: number;

  public contractSize: number;

  public displayName: string;

  public callPosition = 0;
  public callAvgPrice = 0.0;
  public callBid: number;
  public callThPrice: number;
  public callOffer: number;

  public strike: number;

  public putPosition = 0;
  public putAvgPrice = 0.0;
  public putBid: number;
  public putThPrice: number;
  public putOffer: number;

  public expiryType: string;

  public ts: number;
  public move = 0;
  public callBidHovered = false;
  public callOofferHovered = false;
  public putBidHovered = false;
  public putOfferHovered = false;

  public iv = 0;
  public deltaCall = 0;
  public deltaPut = 0;
  public deltaTotal = 0;
  public gamma = 0;
  public gammaTotal = 0;
  public vega = 0;
  public vegaTotal = 0;
  public thetaCall = 0;
  public thetaPut = 0;
  public thetaTotal = 0;
  public rhoCall = 0;
  public rhoPut = 0;
  public rhoTotal = 0;

  public hedgeSubProductId = 0;

  public MTM = 0.0;

  constructor(QSsubProduct: QuerySetSubProduct, QSproduct: QuerySetProduct) {
    this.id = String(QSproduct.pk + '-' + QSsubProduct.fields.strike);

    this.productId = QSsubProduct.fields.product;

    this.strike = QSsubProduct.fields.strike;

    this.contractSize = QSproduct.fields.contractSize;

    this.displayName =
      QSproduct.fields.name +
      ' ' +
      QSproduct.fields.expiryDisplay +
      ' ' +
      this.strike;

    if (QSsubProduct.fields.callPut === 'C') {
      this.callSubProductId = QSsubProduct.pk;
    } else {
      this.putSubProductId = QSsubProduct.pk;
    }

    this.expiryType = QSsubProduct.fields.expiryType;

    this.hedgeSubProductId = QSproduct.fields.hedgeSubProductId;
  }

  initSecondOption(QSsubProduct: QuerySetSubProduct): void {
    if (QSsubProduct.fields.callPut === 'C') {
      this.callSubProductId = QSsubProduct.pk;
    } else {
      this.putSubProductId = QSsubProduct.pk;
    }
  }

  update(data: StreamPrice): void {
    if (data.subProduct_id === this.callSubProductId) {
      if (data.bid > this.callBid) {
        this.move = 1;
      } else if (data.bid < this.callBid) {
        this.move = -1;
      } else {
        this.move = 0;
      }

      this.callBid = data.bid;
      this.callOffer = data.offer;
    } else {
      if (data.bid > this.putBid) {
        this.move = 1;
      } else if (data.bid < this.putBid) {
        this.move = -1;
      } else {
        this.move = 0;
      }
      this.putBid = data.bid;
      this.putOffer = data.offer;
    }

    this.ts = data.ts;

    if (this.callPosition !== 0 || this.putPosition !== 0) {
      this.calculateMTM();
    }

    const myTimer = timer(1500);
    myTimer.subscribe(done => (this.move = 0));
  }

  updatePosition(data: Position): void {
    // if this is the call
    if (this.callSubProductId === data.subProduct) {
      this.callPosition = data.size;
      this.callAvgPrice = data.avgPrice;
      if (data.buy === false) {
        this.callPosition = -this.callPosition;
      }
      // if this is the put
    } else {
      this.putPosition = data.size;
      this.putAvgPrice = data.avgPrice;
      if (data.buy === false) {
        this.putPosition = -this.putPosition;
      }
    }

    this.calculateMTM();
    this.calculateGreeks();
  }

  calculateMTM(): void {
    this.MTM =
      this.callPosition *
        this.contractSize *
        (-this.callAvgPrice + (this.callBid + this.callOffer) / 2) +
      this.putPosition *
        this.contractSize *
        (-this.putAvgPrice + (this.putBid + this.putOffer) / 2);
  }

  updateGreeks(data: GreeksData): void {
    this.iv = data.iv;
    this.gamma = data.gamma;
    this.vega = data.vega;

    if (data.subProductId === this.callSubProductId) {
      this.deltaCall = data.delta;
      this.thetaCall = data.theta;
      this.rhoCall = data.rho;
    } else {
      this.deltaPut = data.delta;
      this.thetaPut = data.theta;
      this.rhoPut = data.rho;
    }

    this.calculateGreeks();
  }

  calculateGreeks(): void {
    this.deltaTotal =
      (this.deltaCall * this.callPosition + this.deltaPut * this.putPosition) *
      this.contractSize;
    this.gammaTotal =
      this.gamma * (this.callPosition + this.putPosition) * this.contractSize;
    this.vegaTotal =
      this.vega * (this.callPosition + this.putPosition) * this.contractSize;
    this.thetaTotal =
      (this.thetaCall * this.callPosition + this.thetaPut * this.putPosition) *
      this.contractSize;
    this.rhoTotal =
      (this.rhoCall * this.callPosition + this.rhoPut * this.putPosition) *
      this.contractSize;
  }
}
