import { Injectable, Output, EventEmitter } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { CookieService } from 'ngx-cookie-service';
import { WebSocketSubject } from 'rxjs/websocket';
import { JSDictionary } from 'src/app/models/dictionary';
import { Observable, Subject, BehaviorSubject } from 'rxjs';

import { WSMessage } from 'src/app/models/wsMessage';
import { StreamPrice } from 'src/app/models/streamPrice';
import { QuerySetStreamPrice } from 'src/app/models/querySetStreamPrice';
import { QuerySetProduct } from 'src/app/models/querySetProduct';
import { QuerySetSubProduct } from 'src/app/models/querySetSubProduct';
import { DisplayFutureSpot } from 'src/app/models/displayFutureSpot';
import { DisplayOption } from 'src/app/models/displayOption';
import { Pnl } from './models/pnl';
import { Trade } from './models/trade';
import { Position } from './models/position';
import { HtmlTagDefinition } from '@angular/compiler';
import { TradeFeedback } from './models/tradeFeedback';
import { GreeksData } from './models/greeksData';
import { Opportunity } from './models/opportunity';

// import { StreamPriceComponent } from './main/stream-price/stream-price.component';

@Injectable({
  providedIn: 'root'
})
export class TradeService {
  private baseUrl = 'http://127.0.0.1:8000/';
  private baseWSUrl = 'ws://127.0.0.1:8000/';
  private baseTradeUrl = `${this.baseUrl}api/trade/`;
  private basePnlUrl = `${this.baseUrl}api/pnl/`;
  private basePositionUrl = `${this.baseUrl}api/position/`;

  private token = this.cookieService.get('mr-token');
  private headers = new HttpHeaders({
    'Content-Type': 'application/json'
  });

  private platformSocket$: WebSocketSubject<WSMessage>;
  private cryptoSocket$: WebSocketSubject<WSMessage>;

  // private streamPrices = new JSDictionary<string, StreamPrice>();

  private products = new JSDictionary<string, QuerySetProduct>();
  private subProducts = new JSDictionary<string, QuerySetSubProduct>();

  private displayFutureSpots = new JSDictionary<string, DisplayFutureSpot>();
  private displayOptions = new JSDictionary<string, DisplayOption>();

  // private trades = new Array<Trade>();
  private subjectTrades = new Subject<Trade>();
  private subjectDisplayFutureSpots = new Subject<DisplayFutureSpot>();
  private subjectDisplayOptions = new Subject<DisplayOption>();
  private subjectQuerySetProduct = new Subject<QuerySetProduct>();
  private subjectPnls = new Subject<Pnl>();

  // Crypto //
  private subjectOpportunities = new Subject<Opportunity>();

  constructor(
    private httpClient: HttpClient,
    private cookieService: CookieService
  ) {}

  getAuthHeaders() {
    const token = this.cookieService.get('mr-token');
    return new HttpHeaders({
      'Content-Type': 'application/json',
      Authorization: `Token ${token}`
    });
  }

  // WS connection
  connectToTradingPlatformWS(): void {
    this.disconnectFromCryptoWS();

    this.platformSocket$ = new WebSocketSubject(
      this.baseWSUrl + 'ws/api/tradingData/'
    );

    this.platformSocket$.subscribe(
      message => this.handlePlatformWSMessage(message),
      err => console.error(err),
      () => console.warn('Completed!')
    );
  }

  disconnectFromTradingPlatformWS(): void {
    if (this.platformSocket$ != null) {
      this.platformSocket$.unsubscribe();
    }
  }

  connectToCryptoWS(): void {
    this.disconnectFromTradingPlatformWS();

    this.cryptoSocket$ = new WebSocketSubject(
      this.baseWSUrl + 'ws/api/crypto/'
    );

    this.cryptoSocket$.subscribe(
      message => this.handleCrytpoWSMessage(message),
      err => console.error(err),
      () => console.warn('Completed!')
    );
  }

  disconnectFromCryptoWS(): void {
    if (this.cryptoSocket$ != null) {
      this.cryptoSocket$.unsubscribe();
    }
  }

  // Handle incoming WS messages for the crypto dashboard
  handleCrytpoWSMessage(message: WSMessage): void {
    switch (message.data.type) {
      // Crypto //
      case 'opportunities': {
        this.subjectOpportunities.next();
        const arrOpportunities = JSON.parse(message.data.content) as Array<
          Opportunity
        >;
        // this.subjectOpportunities = new Subject<Opportunity>();
        for (const item of arrOpportunities) {
          this.subjectOpportunities.next(item);
        }
        break;
      }
    }
  }
  // Handle incoming WS messages for the trading platform
  handlePlatformWSMessage(message: WSMessage): void {
    console.log(message.data.type);
    switch (message.data.type) {
      // live price update of futureSpot or option
      case 'streamPrice': {
        const arrStreamPrice = message.data.content as Array<StreamPrice>;
        for (const item of arrStreamPrice) {
          // this.streamPrices.put(String(item.subProduct_id), item);
          if (
            this.displayFutureSpots.get(String(item.subProduct_id)) !== null
          ) {
            this.displayFutureSpots
              .get(String(item.subProduct_id))
              .update(item);
          } else {
            const tempSubProduct = this.subProducts.get(
              String(item.subProduct_id)
            );

            const key = String(
              tempSubProduct.fields.product + '-' + tempSubProduct.fields.strike
            );

            this.displayOptions.get(key).update(item);
          }
        }
        break;
      }

      // at startup, retrieve the latest queryset database version of stream prices
      case 'querySetStreamPrice': {
        const arrStreamPrice = JSON.parse(message.data.content) as Array<
          QuerySetStreamPrice
        >;

        for (const item of arrStreamPrice) {
          const streamPrice: StreamPrice = {
            bid: item.fields.bid,
            offer: item.fields.offer,
            ts: item.fields.ts,
            subProduct_id: item.pk
          };

          // build dictionary of streamPrices (key = subProduct_id)
          // this.streamPrices.put(String(item.pk), streamPrice);

          const subProduct = this.subProducts.get(String(item.pk));

          const product = this.products.get(
            String(this.subProducts.get(String(item.pk)).fields.product)
          );
          // for futureSpot (key = subProduct_id)
          if (product.fields.productType !== 'O') {
            const displayFutureSpot: DisplayFutureSpot = new DisplayFutureSpot(
              subProduct,
              product,
              item
            );
            this.displayFutureSpots.put(String(item.pk), displayFutureSpot);
            this.subjectDisplayFutureSpots.next(displayFutureSpot);

            // for options
          } else {
            const price: StreamPrice = {
              bid: item.fields.bid,
              offer: item.fields.offer,
              subProduct_id: item.pk,
              ts: item.fields.ts
            };
            const tempSubProduct = this.subProducts.get(String(item.pk));
            const key = String(
              tempSubProduct.fields.product + '-' + tempSubProduct.fields.strike
            );
            this.displayOptions.get(key).update(price);
          }
        }

        // we have already loaded the products, subproducts and streamprice
        // we can call the API to get the trader's data
        // positions, trades, pnl, (orders, etc)

        // retrieve trades by ts DESC limit 100 (could do from x to y / 100 by page in the future)
        this.getTrades().subscribe(
          (result: any) => this.processGetTrades(result.trades),
          error => console.log(error)
        );

        this.getPositions().subscribe(
          (result: any) => this.processGetPositions(result.positions),
          error => console.log(error)
        );

        break;
      }

      // retrieve querySet of products
      case 'querySetProduct': {
        const arrProducts = JSON.parse(message.data.content) as Array<
          QuerySetProduct
        >;
        // build dictionary of products (key = product_id)
        for (const item of arrProducts) {
          this.products.put(String(item.pk), item);
          this.subjectQuerySetProduct.next(item);
        }
        break;
      }

      // retrieve querySet of SubProducts
      case 'querySetSubProduct': {
        // needs to be cleared when switching from crypto to tradingPlatform
        this.displayOptions = new JSDictionary<string, DisplayOption>();

        const arrSubProducts = JSON.parse(message.data.content) as Array<
          QuerySetSubProduct
        >;

        for (const item of arrSubProducts) {
          // build dictionary of subProducts (key = subProduct_id)
          this.subProducts.put(String(item.pk), item);

          // build dictionary of displayOptions (key = Product_id-strike)
          if (item.fields.callPut !== '') {
            const key = String(item.fields.product + '-' + item.fields.strike);

            const subProduct = this.displayOptions.get(key);

            // if none of the call or put already set up
            if (subProduct === null) {
              const product = this.products.get(String(item.fields.product));
              const displayOption: DisplayOption = new DisplayOption(
                item,
                product
              );

              this.displayOptions.put(key, displayOption);

              // if the call or the put is already set up
            } else {
              this.displayOptions.get(key).initSecondOption(item);
              this.subjectDisplayOptions.next(this.displayOptions.get(key));
            }
          }
        }
        break;
      }

      // live greeks update
      case 'greeksData': {
        const arrGreeksData = JSON.parse(message.data.content) as Array<
          GreeksData
        >;

        for (const item of arrGreeksData) {
          const tempSubProduct = this.subProducts.get(
            String(item.subProductId)
          );

          const key = String(
            tempSubProduct.fields.product + '-' + tempSubProduct.fields.strike
          );

          this.displayOptions.get(key).updateGreeks(item);
        }

        break;
      }

      default: {
        break;
      }
    }
  }

  // For observables: products, subproducts and streamPrices, futureSpot and options
  public getProducts(): any {
    const productsObservable = new Observable(observer => {
      observer.next(this.products);
    });
    return productsObservable;
  }

  public getQuerySetProductSubject(): Observable<QuerySetProduct> {
    return this.subjectQuerySetProduct.asObservable();
  }

  public getSubProducts(): any {
    const subProductsObservable = new Observable(observer => {
      observer.next(this.subProducts);
    });
    return subProductsObservable;
  }

  public getDisplayFutureSpotsSubject(): Observable<DisplayFutureSpot> {
    return this.subjectDisplayFutureSpots.asObservable();
  }

  public getDisplayOptionsSubject(): Observable<DisplayOption> {
    return this.subjectDisplayOptions.asObservable();
  }

  public getPnlSubject(): Observable<Pnl> {
    return this.subjectPnls.asObservable();
  }

  // ORDER //

  // send to back end new trade
  public newOrder(
    subProductId: number,
    buy: number,
    size: number,
    price: number
  ) {
    const body = JSON.stringify({ subProductId, buy, size, price });

    if (size !== 0) {
      return this.httpClient.post<TradeFeedback>(
        `${this.baseTradeUrl}newOrder/`,
        body,
        {
          headers: this.getAuthHeaders()
        }
      );
    }
  }

  // retrieve pnl from backend
  public getPnl() {
    return this.httpClient.get<Pnl[]>(`${this.basePnlUrl}dailyPnl/`, {
      headers: this.getAuthHeaders()
    });
  }

  // TRADES ->

  // retrieve trades from backend
  public getTrades() {
    return this.httpClient.get<Array<Trade>>(`${this.baseTradeUrl}trades/`, {
      headers: this.getAuthHeaders()
    });
  }

  // create trade objects and store them
  public processGetTrades(trades: Array<Trade>) {
    for (const trade of trades) {
      const subProduct = this.subProducts.get(String(trade.subProduct));
      const product = this.products.get(String(subProduct.fields.product));

      const tradeObj = new Trade(
        product,
        subProduct,
        trade.id,
        trade.buy,
        trade.position,
        trade.price,
        trade.size,
        trade.subProduct,
        trade.ts
      );

      this.subjectTrades.next(tradeObj);
    }
  }

  // to subscribe to our observable
  public getTradesSubject(): Observable<Trade> {
    return this.subjectTrades.asObservable();
  }

  // update trades and positions
  public tradeFeedback(trade: Trade, position: Position, pnl: Pnl[]): void {
    const subProduct = this.subProducts.get(String(trade.subProduct));
    const product = this.products.get(String(subProduct.fields.product));

    const tradeObj = new Trade(
      product,
      subProduct,
      trade.id,
      trade.buy,
      trade.position,
      trade.price,
      trade.size,
      trade.subProduct,
      trade.ts
    );

    this.subjectTrades.next(tradeObj);

    if (product.fields.productType === 'O') {
      this.displayOptions
        .get(String(product.pk + '-' + subProduct.fields.strike))
        .updatePosition(position);
    } else {
      this.displayFutureSpots
        .get(String(subProduct.pk))
        .updatePosition(position);
    }

    if (pnl) {
      for (const item of pnl) {
        console.log('item pml', item);
        this.subjectPnls.next(item);
      }
    }
  }
  // <- TRADES //

  // POSITIONS -> //
  // retrieve positons from backend
  public getPositions() {
    return this.httpClient.get<Position[]>(
      `${this.basePositionUrl}positions/`,
      {
        headers: this.getAuthHeaders()
      }
    );
  }

  // process positions and update display futureSpot / option
  public processGetPositions(positions: Array<Position>) {
    for (const position of positions) {
      const subProduct = this.subProducts.get(String(position.subProduct));
      const product = this.products.get(String(subProduct.fields.product));

      if (product.fields.productType === 'O') {
        const displayOption = this.displayOptions.get(
          String(product.pk + '-' + subProduct.fields.strike)
        );
        displayOption.updatePosition(position);
      } else {
        const thing = this.displayFutureSpots.get(String(subProduct.pk));
        thing.updatePosition(position);
      }
    }
  }
  // <- POSITIONS //

  // CRYPTO -> //

  // to subscribe to our observable
  public getOpportunitiesSubject(): Observable<Opportunity> {
    return this.subjectOpportunities.asObservable();
  }

  // <- CRYPTO //
}
