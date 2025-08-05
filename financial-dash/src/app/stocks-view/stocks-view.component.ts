import { Component, Inject, Input, OnInit, PLATFORM_ID } from '@angular/core';
import { Stock } from '../stock';
import { CommonModule, CurrencyPipe, isPlatformBrowser } from '@angular/common';
import { PortfolioService } from '../services/portfolio.service';

@Component({
  selector: 'app-stocks-view',
  imports: [CommonModule, CurrencyPipe],
  templateUrl: './stocks-view.component.html',
  styleUrl: './stocks-view.component.css'
})
export class StocksViewComponent implements OnInit {
stockValues: { [ticker: string]: Stock } = {};
stockList: { ticker: string; data: Stock }[] = [];
isBrowser: boolean = false;
stocksValuation: number = 0;
globalValue: number = 0;

constructor(@Inject(PLATFORM_ID) private platformId: Object, private portfolioService: PortfolioService) {
  this.isBrowser = isPlatformBrowser(platformId);
}
  
  ngOnInit(): void {
    if(isPlatformBrowser(this.platformId)) {
      this.globalValue = Number(localStorage.getItem('globalValue'));
    }// First, fetch stock values
    this.portfolioService.getStocks().subscribe((stockData) => {
      this.stockValues = stockData;
      this.stockList = Object.entries(stockData).map(([ticker, stock]) => ({
        ticker,
        data: stock
      }));
  
      // Calculate stocks total dynamically
      this.stocksValuation = this.stockList.reduce(
        (sum, stock) => sum + stock.data.current_price * stock.data.shares,
        0
      );

    });
  }
  getGainLoss(stock: Stock): number {
    return (stock.current_price - stock.purchase_price) * stock.shares;
  }  
  }

