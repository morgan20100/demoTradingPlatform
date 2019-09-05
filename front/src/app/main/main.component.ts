import { Component, OnInit } from '@angular/core';
import { CookieService } from 'ngx-cookie-service';
import { Router } from '@angular/router';

import { ApiService } from '../api.service';

import { JSDictionary } from '../models/dictionary';

import { TradeService } from 'src/app/trade.service';

import { StreamPrice } from 'src/app/models/streamPrice';
import { QuerySetProduct } from 'src/app/models/querySetProduct';
import { QuerySetSubProduct } from 'src/app/models/querySetSubProduct';
import { DisplayFutureSpot } from 'src/app/models/displayFutureSpot';
import { DisplayOption } from '../models/displayOption';

export interface Tile {
  color: string;
  cols: number;
  rows: number;
  text: string;
}

@Component({
  selector: 'app-main',
  templateUrl: './main.component.html',
  styleUrls: ['./main.component.css']
})
export class MainComponent implements OnInit {
  constructor(
    private cookieService: CookieService,
    private router: Router,
    private apiService: ApiService,
    private tradeService: TradeService
  ) {}

  ngOnInit() {
    const mrToken = this.cookieService.get('mr-token');
    if (!mrToken) {
      this.router.navigate(['/auth']);
    }
  }

  logout() {
    this.cookieService.delete('mr-token');
    this.router.navigate(['/auth']);
  }

  switchToCrypto() {
    this.router.navigate(['/main/opportunity']);
  }
}
