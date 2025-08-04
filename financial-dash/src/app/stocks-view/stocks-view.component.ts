import { Component, Input } from '@angular/core';
import { Stock } from '../stock';
import { CommonModule, CurrencyPipe } from '@angular/common';

@Component({
  selector: 'app-stocks-view',
  imports: [CommonModule, CurrencyPipe],
  templateUrl: './stocks-view.component.html',
  styleUrl: './stocks-view.component.css'
})
export class StocksViewComponent {
@Input() stockList: any[] = [];

getGainLoss(stock: Stock): number {
  return (stock.current_price - stock.purchase_price) * stock.shares;
}
}
