import { Component, Inject, OnInit, PLATFORM_ID } from '@angular/core';
import { Bond } from '../bond';
import { PortfolioService } from '../services/portfolio.service';
import { CommonModule, CurrencyPipe, isPlatformBrowser } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-bonds-view',
  imports: [CommonModule, CurrencyPipe, FormsModule],
  templateUrl: './bonds-view.component.html',
  styleUrl: './bonds-view.component.css'
})
export class BondsViewComponent implements OnInit {
bonds: Bond[] = [];
isBrowser: boolean = false;
bondValuation: number = 0;
globalValue: number = 0;
searchQuery: string = '';

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
}

getBondDiff(bond: Bond): number {
  return (bond['Current Market Price (from YFinance)'] - bond['Purchase Price per Bond']) 
              * bond['Number of Bonds'];
}

get filteredBonds() {
  const query = this.searchQuery.toLowerCase();
  return this.bonds.filter(bond =>
    bond['Bond Name'].toLowerCase().includes(query) ||
    bond['Bond Ticker'].toLowerCase().includes(query)
  );
}

}
