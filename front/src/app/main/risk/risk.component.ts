import {
  Component,
  OnInit,
  Input,
  Output,
  EventEmitter,
  NgModule
} from '@angular/core';
import { MatDialog, MatDialogRef, MatTableDataSource } from '@angular/material';

import { JSDictionary } from '../../models/dictionary';

import { TradeService } from 'src/app/trade.service';

import { DisplayFutureSpot } from 'src/app/models/displayFutureSpot';
import { NewFutureSpotOrderComponent } from '../new-futureSpot-order/new-futureSpot-order.component';
import { Subscription } from 'rxjs';
import { moveItemInArray } from '@angular/cdk/drag-drop';
import { RouteConfigLoadEnd } from '@angular/router';
import { DisplayOption } from 'src/app/models/displayOption';
import { QuerySetProduct } from 'src/app/models/querySetProduct';
import { Pnl } from 'src/app/models/pnl';

@Component({
  selector: 'app-risk-component',
  templateUrl: './risk.component.html',
  styleUrls: ['./risk.component.css']
})
export class RiskComponent implements OnInit {
  public displayOptions = new Array<DisplayOption>();
  public subscriptionOption: Subscription;

  public displayFutureSpots = new Array<DisplayFutureSpot>();
  public subscriptionFutureSpot: Subscription;

  public querySetProducts = Array<QuerySetProduct>();
  public subscriptionQuerySetProduct: Subscription;

  public pnls = Array<Pnl>();
  public subscriptionPnl: Subscription;

  public deltas = new JSDictionary<string, number>();
  public gammas = new JSDictionary<string, number>();
  public vegas = new JSDictionary<string, number>();
  public thetas = new JSDictionary<string, number>();
  public rhos = new JSDictionary<string, number>();
  public mtms = new JSDictionary<string, number>();

  filterOptions(product: QuerySetProduct) {
    return product.fields.productType === 'O';
  }

  filterFutures(product: QuerySetProduct) {
    return product.fields.productType === 'F';
  }

  constructor(private tradeService: TradeService) {
    this.subscriptionOption = this.tradeService
      .getDisplayOptionsSubject()
      .subscribe(item => {
        this.displayOptions.push(item);
      });

    this.subscriptionFutureSpot = this.tradeService
      .getDisplayFutureSpotsSubject()
      .subscribe(item => {
        this.displayFutureSpots.push(item);
      });

    this.subscriptionQuerySetProduct = this.tradeService
      .getQuerySetProductSubject()
      .subscribe(item => {
        this.querySetProducts.push(item);
      });

    this.subscriptionPnl = this.tradeService.getPnlSubject().subscribe(item => {
      this.pnls.push(item);
    });
  }

  ngOnInit() {}

  getSumDeltas(): number {
    let sumDeltas = 0.0;
    this.deltas.getValues().forEach(element => {
      sumDeltas += element;
    });
    return sumDeltas;
  }

  getSumGammas(): number {
    let sumGammas = 0.0;
    this.gammas.getValues().forEach(element => {
      sumGammas += element;
    });
    return sumGammas;
  }

  getSumVegas(): number {
    let sumVegas = 0.0;
    this.vegas.getValues().forEach(element => {
      sumVegas += element;
    });
    return sumVegas;
  }

  getSumThetas(): number {
    let sumTheta = 0.0;
    this.thetas.getValues().forEach(element => {
      sumTheta += element;
    });
    return sumTheta;
  }

  getSumRhos(): number {
    let sumRhos = 0.0;
    this.rhos.getValues().forEach(element => {
      sumRhos += element;
    });
    return sumRhos;
  }
  getSumMTMs(): number {
    // MTM options
    let mtmOptions = 0.0;
    this.mtms.getValues().forEach(element => {
      mtmOptions += element;
    });

    // Day pnls future / options
    const pnls = this.pnls
      .filter(pnl => pnl.type !== 'S')
      .reduce((acc, obj) => {
        return acc + obj.value;
      }, 0);

    const alltotal = this.pnls.reduce((acc, obj) => {
      return acc + obj.value;
    }, 0);

    // MTM futures
    const mtmFutures = this.displayFutureSpots
      .filter(future => future.productType === 'F')
      .reduce((acc, future) => {
        return acc + future.MTM;
      }, 0);

    return mtmOptions + pnls + mtmFutures;
  }

  getFutureDeltas(product: QuerySetProduct): number {
    let delta = 0.0;
    let futurePrice = 0.0;

    for (const item of this.displayFutureSpots) {
      if (item.productId === product.pk) {
        futurePrice = (item.bid + item.offer) / 2;
        delta += item.size * futurePrice * item.contractSize;
        break;
      }
    }

    this.deltas.put(
      product.fields.name + ' ' + product.fields.expiryDisplay,
      delta
    );

    return delta;
  }

  getOptionDeltasAndSumUpGreeks(product: QuerySetProduct): number {
    let delta = 0.0;
    let gamma = 0.0;
    let vega = 0.0;
    let theta = 0.0;
    let rho = 0.0;
    let mtm = 0.0;

    let spotPrice = 0.0;

    for (const item of this.displayFutureSpots) {
      if (item.id === product.fields.hedgeSubProductId) {
        spotPrice = (item.bid + item.offer) / 2;
        break;
      }
    }
    delta =
      this.displayOptions
        .filter(option => option.productId === product.pk)
        .reduce((acc, obj) => {
          return acc + obj.deltaTotal;
        }, 0) * spotPrice;
    gamma =
      (this.displayOptions
        .filter(option => option.productId === product.pk)
        .reduce((acc, obj) => {
          return acc + obj.gammaTotal;
        }, 0) *
        spotPrice *
        spotPrice) /
      100;

    vega = this.displayOptions
      .filter(option => option.productId === product.pk)
      .reduce((acc, obj) => {
        return acc + obj.vegaTotal;
      }, 0);

    theta = this.displayOptions
      .filter(option => option.productId === product.pk)
      .reduce((acc, obj) => {
        return acc + obj.thetaTotal;
      }, 0);

    rho = this.displayOptions
      .filter(option => option.productId === product.pk)
      .reduce((acc, obj) => {
        return acc + obj.rhoTotal;
      }, 0);

    mtm = this.displayOptions
      .filter(option => option.productId === product.pk)
      .reduce((acc, obj) => {
        return acc + obj.MTM;
      }, 0);

    this.deltas.put(String(product.pk), delta);
    this.gammas.put(String(product.pk), gamma);
    this.vegas.put(String(product.pk), vega);
    this.thetas.put(String(product.pk), theta);
    this.rhos.put(String(product.pk), rho);
    this.mtms.put(String(product.pk), mtm);

    return delta;
  }

  getOptionGammas(product: QuerySetProduct): number {
    return this.gammas.get(String(product.pk));
  }

  getOptionVegas(product: QuerySetProduct): number {
    return this.vegas.get(String(product.pk));
  }

  getOptionThetas(product: QuerySetProduct): number {
    return this.thetas.get(String(product.pk));
  }

  getOptionRhos(product: QuerySetProduct): number {
    return this.rhos.get(String(product.pk));
  }
}
