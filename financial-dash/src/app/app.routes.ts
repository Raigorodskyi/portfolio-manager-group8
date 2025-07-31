import { Routes } from '@angular/router';
import { OverviewComponent } from './overview/overview.component';

export const routes: Routes = [
  { path: '', redirectTo: 'dashboard', pathMatch: 'full' },
  { path: 'dashboard', component: OverviewComponent },
];
