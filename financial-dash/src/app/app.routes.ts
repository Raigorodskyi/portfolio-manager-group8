import { Routes } from '@angular/router';
import { OverviewComponent } from './overview/overview.component';
import { BondsViewComponent } from './bonds-view/bonds-view.component';
import { StocksViewComponent } from './stocks-view/stocks-view.component';

export const routes: Routes = [
  { path: '', redirectTo: 'dashboard', pathMatch: 'full' },
  { path: 'dashboard', component: OverviewComponent },
  { path: 'stocks', component: StocksViewComponent },
  { path: 'bonds', component: BondsViewComponent }
];
