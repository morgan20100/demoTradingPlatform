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

@Component({
  selector: 'app-display-future-spot',
  templateUrl: './display-future-spot.component.html',
  styleUrls: ['./display-future-spot.component.css']
})
export class DisplayFutureSpotComponent implements OnInit {
  @Input() productType: string;

  public displayFutureSpots = new MatTableDataSource<DisplayFutureSpot>([]);
  public subscription: Subscription;

  public displayedColumns: string[] = [
    'market',
    'position',
    'bid',
    'offer',
    'ts'
  ];

  constructor(private tradeService: TradeService, private dialog: MatDialog) {
    this.subscription = this.tradeService
      .getDisplayFutureSpotsSubject()
      .subscribe(item => {
        if (item.productType === this.productType) {
          this.displayFutureSpots.data.push(item);
          this.displayFutureSpots._updateChangeSubscription();
        }
      });
  }

  ngOnInit() {}

  tradeFutureSpot(event: MouseEvent, element: DisplayFutureSpot, buy: number) {
    const dialogRef = this.dialog.open(NewFutureSpotOrderComponent, {
      position: {
        top: event.pageY - 65 + 'px',
        left: event.pageX - 240 + 'px'
      },
      data: { element, buy, callPut: '' },
      panelClass: 'custom-new-order-css'
    });
    dialogRef.afterClosed().subscribe(result => {
      // console.log('The dialog was closed', result);
      // feedback trade to do
    });
  }
}
