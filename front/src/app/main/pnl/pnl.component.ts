import {
  Component,
  OnInit,
  Input,
  Output,
  EventEmitter,
  NgModule
} from '@angular/core';

import { JSDictionary } from '../../models/dictionary';

import { TradeService } from 'src/app/trade.service';

import { Pnl } from 'src/app/models/pnl';

@Component({
  selector: 'app-pnl-component',
  templateUrl: './pnl.component.html',
  styleUrls: ['./pnl.component.css']
})
export class PnlComponent implements OnInit {
  constructor(private tradeService: TradeService) {}

  ngOnInit() {}

  pnl() {
    this.tradeService
      .getPnl()
      .subscribe(
        (result: Pnl[]) => console.log(result),
        error => console.log(error)
      );
  }
}
