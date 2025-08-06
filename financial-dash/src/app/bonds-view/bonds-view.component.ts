import { Component, Inject, OnInit, PLATFORM_ID } from '@angular/core';
import { Bond, MarketBond } from '../bond';
import { PortfolioService } from '../services/portfolio.service';
import { CommonModule, CurrencyPipe, isPlatformBrowser } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { BankAccount } from '../bank-account';

@Component({
  selector: 'app-bonds-view',
  imports: [CommonModule, CurrencyPipe, FormsModule],
  templateUrl: './bonds-view.component.html',
  styleUrl: './bonds-view.component.css'
})
export class BondsViewComponent implements OnInit {
bonds: Bond[] = [];
marketBondValues: { [ticker: string]: MarketBond } = {};
marketBondList: { ticker: string; data: MarketBond }[] = [];
isBrowser: boolean = false;
bondValuation: number = 0;
globalValue: number = 0;
searchQuery: string = '';
showModal = false;
modalType: 'buy' | 'sell' = 'buy';
selectedBond: any = null;
modalQuantity: number = 1;
bankAccounts: BankAccount[] = [];
selectedBankAccount: BankAccount | null = null;
response: string = "";
purchasePrice: number = 0;


constructor(@Inject(PLATFORM_ID) private platformId: Object, private portfolioService: PortfolioService) {
  this.isBrowser = isPlatformBrowser(platformId);
}


ngOnInit(): void {
  if(isPlatformBrowser(this.platformId)) {
    this.globalValue = Number(localStorage.getItem('globalValue'));
  }
    this.portfolioService.getBonds().subscribe((bondsData) => {
      this.bonds = bondsData;

      this.bondValuation = this.bonds.reduce((sum, bond) =>
        sum + bond['Current Market Price (from YFinance)']* bond['Number of Bonds'], 0);
    });
    this.portfolioService.getBankAccounts().subscribe((response) => {
      this.bankAccounts = response.bank_accounts;
      this.selectedBankAccount = this.bankAccounts[0];
      console.log(this.bankAccounts);
    });
}

getBondDiff(bond: Bond): number {
  return (bond['Current Market Price (from YFinance)'] - bond['Purchase Price per Bond']) 
              * bond['Number of Bonds'];
}

getMarketBond() {
  const query = this.searchQuery.toUpperCase();

  this.portfolioService.getBondByTicker(query).subscribe((bond) => {
    this.marketBondValues = bond;
  console.log(this.marketBondValues);
});

}

openModal(type: 'buy' | 'sell', bond: any) {
  this.modalType = type;
  this.selectedBond = bond;
  this.modalQuantity = 1;
  this.showModal = true;
  console.log(bond.data['Purchase Price per Bond'])
}

closeModal() {
  this.showModal = false;
}

confirmTransaction() {
  if (!this.selectedBond || !this.modalQuantity) return;

  const total = this.selectedBond.current_price * this.modalQuantity;

  if (this.modalType === 'buy') {
    console.log(`Buying ${this.modalQuantity} of ${this.selectedBond.ticker} for ${total} from account ${this.selectedBankAccount?.bank_id}`);

    this.portfolioService.buyBond(this.selectedBond.ticker, this.modalQuantity, this.selectedBankAccount == null ? 1 : 
      this.selectedBankAccount.bank_id).subscribe(data => {
        this.response = data.message ?? '';
      });
  } else {
    console.log(`Selling ${this.modalQuantity} of ${this.selectedBond.ticker} for ${total} to account ${this.selectedBankAccount?.bank_id} purch price ${this.selectedBond.data['Purchase Price per Bond']}`);
    this.portfolioService.sellBond(this.selectedBond.ticker, this.modalQuantity, this.selectedBankAccount == null ? 1 : 
      this.selectedBankAccount.bank_id, this.selectedBond.data['Purchase Price per Bond']).subscribe(data => {
        this.response = data.message ?? '';
      });
  }

  setTimeout(() => this.closeModal(), 2000);
}


}