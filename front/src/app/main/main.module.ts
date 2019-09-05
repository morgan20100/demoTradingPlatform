import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Routes, RouterModule } from '@angular/router';

import { ApiService } from '../api.service';
import { AngularFontAwesomeModule } from 'angular-font-awesome';

import { ReactiveFormsModule, FormsModule } from '@angular/forms';
import { MainComponent } from './main.component';

import { DemoMaterialModule } from './../material-module';
import { MDBBootstrapModule } from 'angular-bootstrap-md';
import { TopBarComponent } from './top-bar/top-bar.component';
import { DisplayFutureSpotComponent } from './display-future-spot/display-future-spot.component';
import { DisplayOptionComponent } from './display-option/display-option.component';
import { NewFutureSpotOrderComponent } from './new-futureSpot-order/new-futureSpot-order.component';
import { NewOptionOrderComponent } from './new-option-order/new-option-order.component';
import { PnlComponent } from './pnl/pnl.component';
import { TradeComponent } from './trade/trade.component';
import { PositionComponent } from './position/position.component';
import { RiskComponent } from './risk/risk.component';
import { CallbackPipe } from './callback.pipe';
import { OpenedOrdersComponent } from './opened-orders/opened-orders.component';
import { OpportunityComponent } from './opportunity/opportunity.component';

const routes: Routes = [
  { path: 'tradingPlatform', component: MainComponent },
  { path: 'crypto', component: OpportunityComponent }
];

@NgModule({
  declarations: [
    MainComponent,
    TopBarComponent,
    DisplayFutureSpotComponent,
    DisplayOptionComponent,
    NewFutureSpotOrderComponent,
    NewOptionOrderComponent,
    PnlComponent,
    TradeComponent,
    PositionComponent,
    RiskComponent,
    CallbackPipe,
    OpenedOrdersComponent,
    OpportunityComponent
  ],
  imports: [
    CommonModule,
    ReactiveFormsModule,
    RouterModule.forChild(routes),
    AngularFontAwesomeModule,
    DemoMaterialModule,
    FormsModule,
    MDBBootstrapModule.forRoot()
  ],

  exports: [RouterModule],
  providers: [ApiService],
  entryComponents: [NewFutureSpotOrderComponent, NewOptionOrderComponent]
})
export class MainModule {}
