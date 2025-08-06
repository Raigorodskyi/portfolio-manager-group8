import { Component, Inject, OnInit, PLATFORM_ID } from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { PortfolioService } from '../services/portfolio.service';

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './profile.component.html',
  styleUrls: ['./profile.component.css'],
})
export class ProfileComponent implements OnInit {
  bankAccounts: any[] = [];
  transactions: any[] = [];
  selectedBankId: number | null = null;
  isBrowser: boolean = false;

  constructor(
    @Inject(PLATFORM_ID) private platformId: Object,
    private portfolioService: PortfolioService
  ) {
    this.isBrowser = isPlatformBrowser(platformId);
  }

  ngOnInit(): void {
    if (this.isBrowser) {
      this.getBankAccounts();
    }
  }

  getBankAccounts() {
    this.portfolioService.getBankAccounts().subscribe({
      next: (res) => {
        this.bankAccounts = res.bank_accounts;
      },
      error: (err) => {
        console.error('Failed to fetch bank accounts', err);
      },
    });
  }

  selectBankAccount(bank_id: number) {
    this.selectedBankId = bank_id;
    this.portfolioService.getTransactions(bank_id).subscribe({
      next: (res) => {
        this.transactions = res;
      },
      error: (err) => {
        console.error('Failed to fetch transactions', err);
      },
    });
  }
}
