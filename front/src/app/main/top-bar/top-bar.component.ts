import { Component, OnInit, Input, Output, EventEmitter } from '@angular/core';
import { CookieService } from 'ngx-cookie-service';
import { Router } from '@angular/router';
import { TradeService } from 'src/app/trade.service';
// import { Movie } from '../../models/movie';

@Component({
  selector: 'app-top-bar',
  templateUrl: './top-bar.component.html',
  styleUrls: ['./top-bar.component.css']
})
export class TopBarComponent implements OnInit {
  constructor(
    private tradeService: TradeService,
    private cookieService: CookieService,
    private router: Router
  ) {}

  ngOnInit() {
    this.tradeService.connectToTradingPlatformWS();
  }

  logout() {
    this.cookieService.delete('mr-token');
    this.router.navigate(['/auth']);
  }

  switchPlatform() {
    this.router.navigate(['/crypto']);
  }
}
