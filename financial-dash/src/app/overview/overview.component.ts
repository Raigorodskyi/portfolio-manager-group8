import { Component, Inject, OnInit, PLATFORM_ID, ViewChild } from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { BaseChartDirective, NgChartsModule } from 'ng2-charts';
import { ChartData, ChartType } from 'chart.js';
import { PortfolioService } from '../services/portfolio.service';
import { Bond } from '../bond';
import { Stock } from '../stock';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-overview',
  imports: [CommonModule, NgChartsModule, RouterModule],
  templateUrl: './overview.component.html',
  styleUrl: './overview.component.css'
})
export class OverviewComponent implements OnInit {
  @ViewChild(BaseChartDirective) chart: BaseChartDirective | undefined;


  isBrowser: boolean = false;
  globalValue = 0;
  cash = 0;
  bonds: Bond[] = [];
  stockValues: { [ticker: string]: Stock } = {};
  stockList: { ticker: string; data: Stock }[] = [];

  constructor(@Inject(PLATFORM_ID) private platformId: Object, private portfolioService: PortfolioService) {
    this.isBrowser = isPlatformBrowser(platformId);
  }
  
  pieChartType: ChartType = 'pie';
  pieChartData: ChartData<'pie', number[], string> = {
    datasets: [
      {
        data: this.stockList.map(stock => stock.data.current_price),
        backgroundColor: ['#007aff', '#34c759', '#ff3b30']
      }
    ],
    labels: this.stockList.map(stock => stock.ticker)
  };

  // Calculate total value of bonds and stocks
getTotalValue(items: { price: number; quantity: number }[]): number {
  return items.reduce((sum, item) => sum + item.price * item.quantity, 0);
}

getGainLoss(stock: Stock): number {
  return (stock.current_price - stock.purchase_price) * stock.shares;
}

ngOnInit(): void {
  // First, fetch stock values
  this.portfolioService.getStocks().subscribe((stockData) => {
    this.stockValues = stockData;
    this.stockList = Object.entries(stockData).map(([ticker, stock]) => ({
      ticker,
      data: stock
    }));

    // Calculate stocks total dynamically
    const stocksTotal = this.stockList.reduce(
      (sum, stock) => sum + stock.data.current_price * stock.data.shares,
      0
    );

    // Then fetch bonds
    this.portfolioService.getBonds().subscribe((bondsData) => {
      this.bonds = bondsData;

      const bondsTotal = this.bonds.reduce((sum, bond) =>
        sum + bond['Current Market Price'] * bond['Number of Bonds'], 0);

      // Then fetch cash
      this.portfolioService.getCashValue().subscribe((cashData) => {
        this.cash = cashData.total_value;

        // Global portfolio value
        this.globalValue = this.cash + bondsTotal + stocksTotal;
        if(isPlatformBrowser(this.platformId)) {
          localStorage.setItem('globalValue', this.globalValue.toString());
        }

        // Update pie chart
        this.pieChartData = {
          labels: ['Cash', 'Bonds', 'Stocks'],
          datasets: [
            {
              data: [this.cash, bondsTotal, stocksTotal],
              backgroundColor: ['#fcd34d', '#60a5fa', '#8b5cf6']
            }
          ]
        };

        this.chart?.update();
      });
    });
  });
}


}
