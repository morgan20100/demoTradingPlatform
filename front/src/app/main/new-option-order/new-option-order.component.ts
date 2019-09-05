import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { Inject, Component, OnInit } from '@angular/core';
import { FormGroup, FormControl } from '@angular/forms';

import { TradeService } from 'src/app/trade.service';

import { DisplayOption } from 'src/app/models/displayOption';
import { TradeFeedback } from 'src/app/models/tradeFeedback';

export interface NewOrderData {
  element: DisplayOption;
  buy: number;
  callPut: string;
}

@Component({
  templateUrl: './new-option-order.component.html',
  styleUrls: ['./new-option-order.component.css']
})
export class NewOptionOrderComponent implements OnInit {
  constructor(
    public dialogRef: MatDialogRef<NewOptionOrderComponent>,
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
    let subproductId: number;

    if (this.data.callPut === 'Call') {
      if (this.data.buy === 1) {
        price = this.data.element.callOffer;
      } else {
        price = this.data.element.callBid;
      }
      subproductId = this.data.element.callSubProductId;
    } else {
      if (this.data.buy === 1) {
        price = this.data.element.putOffer;
      } else {
        price = this.data.element.putBid;
      }
      subproductId = this.data.element.putSubProductId;
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
