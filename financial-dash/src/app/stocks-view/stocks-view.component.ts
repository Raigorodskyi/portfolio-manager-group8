import { Component, Inject, Input, OnInit, PLATFORM_ID } from '@angular/core';
import { MarketStock, Stock } from '../stock';
import { CommonModule, CurrencyPipe, isPlatformBrowser } from '@angular/common';
import { PortfolioService } from '../services/portfolio.service';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { BankAccount } from '../bank-account';

@Component({
  selector: 'app-stocks-view',
  imports: [CommonModule, CurrencyPipe, FormsModule, RouterModule],
  templateUrl: './stocks-view.component.html',
  styleUrl: './stocks-view.component.css'
})

export class StocksViewComponent implements OnInit {
marketStockValues: { [ticker: string]: Stock } = {};
marketStockList: { ticker: string; data: Stock }[] = [];
currtentStockPrice: number = 0;
stockValues: { [ticker: string]: Stock } = {};
stockList: { ticker: string; data: Stock }[] = [];
isBrowser: boolean = false;
stocksValuation: number = 0;
globalValue: number = 0;
searchQuery: string = '';
showModal = false;
modalType: 'buy' | 'sell' = 'buy';
selectedStock: any = null;
modalQuantity: number = 1;
bankAccounts: BankAccount[] = [];
errorMessage: string = '';
selectedBankAccount: BankAccount | null = null;
response = '';
confirmationMessage: string | null = null;

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
  console.log(this.stockList);
      // Calculate stocks total dynamically
      this.stocksValuation = this.stockList.reduce(
        (sum, stock) => sum + stock.data.current_price * stock.data.shares,
        0
      );
    });
    this.getBankAccounts();
  }

  getBankAccounts() {
    this.portfolioService.getBankAccounts().subscribe((response) => {
      this.bankAccounts = response.bank_accounts;
      this.selectedBankAccount = this.bankAccounts[0];
      console.log(this.bankAccounts);
    });
  }

  getMarketStock() {
    const query = this.searchQuery.toUpperCase();
    this.portfolioService.getStockByTicker(query).subscribe({
      next: (stockData) => {
        this.marketStockValues = stockData;
        console.log(this.marketStockValues);
        this.errorMessage = '';
    },
    error: (err) => {
      console.error('Error fetching stock:', err);
      this.errorMessage = 'Could not fetch stock. Please check the ticker or try again later.';
    }

    });
  }

  getGainLoss(stock: Stock): number {
    return (stock.current_price - stock.purchase_price) * stock.shares;
  }  

  getTotalStockChange(): number {
    return this.stockList.reduce((sum, stock) => {
      const gain = (stock.data.current_price - stock.data.purchase_price) * stock.data.shares;
      return sum + gain;
    }, 0);
  }

  openModal(type: 'buy' | 'sell', stock: any) {
    this.getBankAccounts();
    this.response = '';
    this.modalType = type;
    this.selectedStock = stock;
    this.modalQuantity = 1;
    this.showModal = true;
    console.log(this.selectedStock);
  }
  
  closeModal() {
    this.showModal = false;
  }

  refreshStocks() {
    this.portfolioService.getStocks().subscribe((stockData) => {
      this.stockValues = stockData;
      this.stockList = Object.entries(stockData).map(([ticker, stock]) => ({
        ticker,
        data: stock
      }));
      this.stocksValuation = this.stockList.reduce(
        (sum, stock) => sum + stock.data.current_price * stock.data.shares,
        0
      );
    });
  }
  
  confirmTransaction() {
    if (!this.selectedStock || !this.modalQuantity) return;
  
    let total = 0;
    if (this.modalType === 'buy') {
      total = this.selectedStock.current_price * this.modalQuantity;
    } else {
      total = this.selectedStock.data.current_price * this.modalQuantity;
    }
  
    if (this.modalType === 'buy') {
      console.log(`Buying ${this.modalQuantity} of ${this.selectedStock.stock_ticker} for ${total}`);
      this.portfolioService.buyStock(
        this.selectedStock.stock_ticker,
        this.modalQuantity,
        this.selectedBankAccount?.bank_id || 1
      ).subscribe({
        next: (data) => {
          this.response = data.message ?? 'Stock purchase successful!';
          this.refreshStocks();
          this.clearResponseAfterDelay();
        },
        error: (err) => {
          this.response = 'Stock purchase failed.';
          console.error(err);
          this.clearResponseAfterDelay();
        }
      });
    } else {
      console.log(`Selling ${this.modalQuantity} of ${this.selectedStock.data.stock_ticker} for ${total}`);
      this.portfolioService.sellStock(
        this.selectedStock.data.stock_ticker,
        this.modalQuantity,
        this.selectedBankAccount?.bank_id || 1
      ).subscribe({
        next: (data) => {
          this.response = data.message ?? 'Stock sale successful!';
          this.refreshStocks();
          this.clearResponseAfterDelay();
        },
        error: (err) => {
          this.response = 'Stock sale failed.';
          console.error(err);
          this.clearResponseAfterDelay();
        }
      });
    }
  
    setTimeout(() => this.closeModal(), 2000);
  }
  
  private clearResponseAfterDelay() {
    setTimeout(() => {
      this.response = '';
    }, 4000); // Clear the message after 4 seconds
  }  
  
  }

