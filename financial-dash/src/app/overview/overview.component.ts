import { Component, Inject, OnInit, PLATFORM_ID, ViewChild } from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { BaseChartDirective, NgChartsModule } from 'ng2-charts';
import { ChartData, ChartType } from 'chart.js';
import { PortfolioService } from '../services/portfolio.service';

@Component({
  selector: 'app-overview',
  imports: [CommonModule, NgChartsModule],
  templateUrl: './overview.component.html',
  styleUrl: './overview.component.css'
})
export class OverviewComponent implements OnInit {
  @ViewChild(BaseChartDirective) chart: BaseChartDirective | undefined;


  isBrowser: boolean = false;
  globalValue = 0;
  cash = 0;

  constructor(@Inject(PLATFORM_ID) private platformId: Object, private portfolioService: PortfolioService) {
    this.isBrowser = isPlatformBrowser(platformId);
  }


  bonds = [
    { name: 'Bond1', price: 200, rate: '+2%', quantity: 4, matDate: '2025-09-09' },
    { name: 'Bond2', price: 700, rate: '-1.5%', quantity: 3, matDate: '2025-09-09' }
  ]

  stocks = [
    { name: 'Apple', ticker: 'AAPL', price: 200, gain: '+2%', quantity: 2, priceAtPurchase: 40 },
    { name: 'Tesla', ticker: 'TSLA', price: 700, gain: '-1.5%', quantity: 5, priceAtPurchase: 100 }
    
  ];
  pieChartType: ChartType = 'pie';
  pieChartData: ChartData<'pie', number[], string> = {
    datasets: [
      {
        data: this.stocks.map(stock => stock.price),
        backgroundColor: ['#007aff', '#34c759', '#ff3b30']
      }
    ],
    labels: this.stocks.map(stock => stock.name)
  };

  // Calculate total value of bonds and stocks
getTotalValue(items: { price: number; quantity: number }[]): number {
  return items.reduce((sum, item) => sum + item.price * item.quantity, 0);
}

ngOnInit(): void {
  const bondsTotal = this.getTotalValue(this.bonds);
  const stocksTotal = this.getTotalValue(this.stocks);

  this.portfolioService.getTotalValue().subscribe((data) => {
    this.cash = data.total_value;
    console.log(this.cash);

    this.globalValue = data.total_value + bondsTotal + stocksTotal;

    this.pieChartData = {
      labels: ['Cash', 'Bonds', 'Stocks'],
      datasets: [
        {
          data: [data.total_value, bondsTotal, stocksTotal],
          backgroundColor: ['#fcd34d', '#60a5fa', '#8b5cf6']
        }
      ]
    };

    console.log(this.cash, bondsTotal, stocksTotal)
    this.chart?.update();
  });
}
}
