import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { Inject, Component, OnInit } from '@angular/core';
import { DisplayFutureSpot } from 'src/app/models/displayFutureSpot';
import { FormGroup, FormControl } from '@angular/forms';
import { TradeService } from 'src/app/trade.service';
import { Trade } from 'src/app/models/trade';
import { TradeFeedback } from 'src/app/models/tradeFeedback';

export interface NewOrderData {
  element: DisplayFutureSpot;
  buy: number;
}

@Component({
  templateUrl: './new-futureSpot-order.component.html',
  styleUrls: ['./new-futureSpot-order.component.css']
})
export class NewFutureSpotOrderComponent implements OnInit {
  constructor(
    public dialogRef: MatDialogRef<NewFutureSpotOrderComponent>,
    @Inject(MAT_DIALOG_DATA) public data: NewOrderData,
    private tradeService: TradeService
  ) {}

  public form: FormGroup = new FormGroup({
    size: new FormControl('')
  });

  orderType: string;
  defaultSize = 10;

  ngOnInit(): void {
    if (this.data.buy === 1) {
      this.orderType = 'Buy';
    } else {
      this.orderType = 'Sell';
    }
    this.form.get('size').setValue(10);
  }

  sendOrder(): void {
    const size = this.form.get('size').value;

    let price: number;
    const subproductId = this.data.element.id;

    if (this.data.buy === 1) {
      price = this.data.element.offer;
    } else {
      price = this.data.element.bid;
    }

    this.tradeService
      .newOrder(subproductId, this.data.buy, size, price)
      .subscribe(
        (result: TradeFeedback) =>
          this.tradeService.tradeFeedback(
            result.trade,
            result.position,
            result.pnl
          ),
        error => console.log(error)
      );

    this.dialogRef.close();
  }

  onNoClick(): void {
    this.dialogRef.close();
  }
}
