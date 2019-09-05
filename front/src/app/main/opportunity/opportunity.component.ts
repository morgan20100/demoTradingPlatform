import {
  Component,
  OnInit,
  Input,
  Output,
  EventEmitter,
  NgModule
} from '@angular/core';
import { Subject, Subscription } from 'rxjs';
import { MatTableDataSource } from '@angular/material';

import { TradeService } from 'src/app/trade.service';

import { Opportunity } from 'src/app/models/opportunity';
import { Router } from '@angular/router';

@Component({
  selector: 'app-opportunity-component',
  templateUrl: './opportunity.component.html',
  styleUrls: ['./opportunity.component.css']
})
export class OpportunityComponent implements OnInit {
  public opportunities = new MatTableDataSource<Opportunity>([]);
  public subscription: Subscription;
  public displayedColumns: string[] = [
    'symbol',
    'scalp',
    'buy',
    'buyExchange',
    'sell',
    'sellExchange'
  ];

  constructor(private tradeService: TradeService, private router: Router) {
    this.subscription = this.tradeService
      .getOpportunitiesSubject()
      .subscribe(opportunity => {
        if (opportunity) {
          this.opportunities.data.push(opportunity);
          this.opportunities._updateChangeSubscription();
        } else {
          this.opportunities = new MatTableDataSource<Opportunity>([]);
        }
      });
  }

  ngOnInit() {
    this.tradeService.connectToCryptoWS();
  }

  switchPlatform() {
    this.router.navigate(['/tradingPlatform']);
  }
}
