import {
  Component,
  OnInit,
  Input,
  Output,
  EventEmitter,
  OnDestroy
} from '@angular/core';
import { MatDialog, MatTableDataSource } from '@angular/material';
import { JSDictionary } from 'src/app/models/dictionary';

import { TradeService } from 'src/app/trade.service';

import { DisplayOption } from 'src/app/models/displayOption';
import { NewOptionOrderComponent } from '../new-option-order/new-option-order.component';
import { Subscription } from 'rxjs';
import { QuerySetProduct } from 'src/app/models/querySetProduct';

@Component({
  selector: 'app-display-option',
  templateUrl: './display-option.component.html',
  styleUrls: ['./display-option.component.css']
})
export class DisplayOptionComponent implements OnInit, OnDestroy {
  public displayOptions = new MatTableDataSource<DisplayOption>([]);
  public subscriptionDisplayOptions: Subscription;

  public querySetProducts = Array<QuerySetProduct>();
  public subscriptionQuerySetProducts: Subscription;

  public displayedColumns: string[] = [
    'market',
    'iv',
    'callPosition',
    'callBid',
    'callOffer',
    'deltaCall',
    'strike',
    'deltaPut',
    'putBid',
    'putOffer',
    'putPosition',
    'ts'
  ];

  public selectedProduct: QuerySetProduct;
  public optionsToDisplay: string;

  constructor(private tradeService: TradeService, private dialog: MatDialog) {
    this.subscriptionDisplayOptions = this.tradeService
      .getDisplayOptionsSubject()
      .subscribe(item => {
        if (item) {
          this.displayOptions.data.push(item);
          console.log('getting options');
          this.displayOptions._updateChangeSubscription();
        }
      });

    this.subscriptionQuerySetProducts = this.tradeService
      .getQuerySetProductSubject()
      .subscribe(item => {
        this.querySetProducts.push(item);
      });
  }

  applyFilter(filterValue: number) {
    this.displayOptions.filter = String(filterValue);
  }

  ngOnInit(): void {
    this.displayOptions.filterPredicate = (
      data: DisplayOption,
      filter: string
    ) => {
      return data.productId === Number(filter);
    };
  }

  ngOnDestroy(): void {
    while (this.displayOptions.data.length > 0) {
      console.log('popping');
      this.displayOptions.data.pop();
    }
  }

  filterOnOptions(product: QuerySetProduct) {
    return product.fields.productType === 'O';
  }

  getSelectedProduct() {
    this.applyFilter(this.selectedProduct.pk);
  }

  tradeOption(
    event: MouseEvent,
    element: DisplayOption,
    buy: number,
    callPut: string
  ) {
    const dialogRef = this.dialog.open(NewOptionOrderComponent, {
      position: {
        top: event.pageY - 65 + 'px',
        left: event.pageX - 240 + 'px'
      },
      data: { element, buy, callPut },
      panelClass: 'custom-new-order-css'
    });
    dialogRef.afterClosed().subscribe(result => {
      // feedback trade is gone through
      // console.log('The dialog was closed', result);
    });
  }
}
