import { Component, Inject, OnInit, PLATFORM_ID } from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { NgChartsModule } from 'ng2-charts';
import { ChartData, ChartType } from 'chart.js';

@Component({
  selector: 'app-overview',
  imports: [CommonModule, NgChartsModule],
  templateUrl: './overview.component.html',
  styleUrl: './overview.component.css'
})
export class OverviewComponent implements OnInit {

  isBrowser: boolean = false;
  globalValue = 0;

  constructor(@Inject(PLATFORM_ID) private platformId: Object) {
    this.isBrowser = isPlatformBrowser(platformId);
  }

  cash = 4500; 

  bonds = [
    { name: 'Bond1', ticker: 'AAAA', price: 200, gain: '+2%', quantity: 4 },
    { name: 'Bond2', ticker: 'BBBB', price: 700, gain: '-1.5%', quantity: 3 }
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

  ngOnInit() {
    const bondsTotal = this.getTotalValue(this.bonds);
    const stocksTotal = this.getTotalValue(this.stocks);
    this.globalValue = stocksTotal + bondsTotal + this.cash;
  
    this.pieChartData = {
      labels: ['Cash', 'Bonds', 'Stocks'],
      datasets: [
        {
          data: [this.cash, bondsTotal, stocksTotal],
          backgroundColor: ['#fcd34d', '#60a5fa', '#8b5cf6']
        }
      ]
    };
  }
}
