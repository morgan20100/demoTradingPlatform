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

@Component({
  selector: 'app-opened-orders-component',
  templateUrl: './opened-orders.component.html',
  styleUrls: ['./opened-orders.component.css']
})
export class OpenedOrdersComponent implements OnInit {
  public displaySpots = new MatTableDataSource<DisplayFutureSpot>([]);
  public subscription: Subscription;

  public displayedColumns: string[] = [
    'market',
    'position',
    'openingPrice',
    'lastPrice',
    'pnl'
  ];
  public displayTotal: string[] = ['total', 'value'];

  constructor(private tradeService: TradeService, private dialog: MatDialog) {
    this.subscription = this.tradeService
      .getDisplayFutureSpotsSubject()
      .subscribe(item => {
        if (item.productType === 'S') {
          this.displaySpots.data.push(item);
          this.displaySpots._updateChangeSubscription();
        }
      });
  }

  ngOnInit() {}

  totalPnl() {
    let pnl = 0.0;
    for (const item of this.displaySpots.data.values()) {
      pnl += item.MTM;
    }
    return pnl;
  }
}
