import {
  Component,
  OnInit,
  Input,
  Output,
  EventEmitter,
  NgModule
} from '@angular/core';

import { TradeService } from 'src/app/trade.service';

import { Trade } from 'src/app/models/trade';

import { MatTableDataSource } from '@angular/material';
import { Subject, Subscription } from 'rxjs';

@Component({
  selector: 'app-trade-component',
  templateUrl: './trade.component.html',
  styleUrls: ['./trade.component.css']
})
export class TradeComponent implements OnInit {
  public trades = new MatTableDataSource<Trade>([]);
  public subscription: Subscription;
  public displayedColumns: string[] = [
    'buySell',
    'size',
    'name',
    'price',
    'ts'
  ];

  constructor(private tradeService: TradeService) {
    this.subscription = this.tradeService
      .getTradesSubject()
      .subscribe(trade => {
        if (trade) {
          this.trades.data.unshift(trade);
          this.trades._updateChangeSubscription();
        }
      });
  }

  ngOnInit() {}
}
