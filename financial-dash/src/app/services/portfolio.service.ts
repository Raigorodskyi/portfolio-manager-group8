import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { map, Observable } from 'rxjs';
import { Bond, BuyBondResponse, MarketBond, SellBondResponse } from '../bond';
import { Stock } from '../stock';

@Injectable({
  providedIn: 'root',
})
export class PortfolioService {
  private cashValueUrl = 'http://127.0.0.1:5000/api/total_value';
  private stocksUrl = 'http://127.0.0.1:5000/api/stock_values';
  private bondsUrl = 'http://127.0.0.1:5000/api/bonds';
  private getStockUrl = 'http://127.0.0.1:5000/api/stock_action';
  private getBondUrl = 'http://127.0.0.1:5000/api/bond_action';
  private bankAccountsUrl = 'http://127.0.0.1:5000/api/bank_accounts';
  private transactionsUrl = 'http://127.0.0.1:5000/api/transactions';

  constructor(private http: HttpClient) {}

  getCashValue(): Observable<{ total_value: number; user_id: number }> {
    return this.http.get<{ total_value: number; user_id: number }>(
      this.cashValueUrl
    );
  }

  getBonds(): Observable<Bond[]> {
    return this.http.get<Bond[]>(this.bondsUrl);
  }

  getStocks(): Observable<{ [ticker: string]: Stock }> {
    return this.http.get<{ [ticker: string]: Stock }>(this.stocksUrl);
  }

  getStockByTicker(ticker: string): Observable<{ stock: Stock }> {
    const payload = {
      action: 'view',
      stock_ticker: ticker,
    };
    const headers = new HttpHeaders({
      'Content-Type': 'application/json',
    });

    return this.http.post<{ stock: Stock }>(this.getStockUrl, payload, {
      headers,
    });
  }

  buyStock(
    ticker: string,
    shares: number,
    bank_id: string
  ): Observable<{ stock: Stock }> {
    const payload = {
      action: 'buy',
      stock_ticker: ticker,
      number_of_shares: shares,
      bank_ID: bank_id,
    };
    const headers = new HttpHeaders({
      'Content-Type': 'application/json',
    });

    return this.http.post<{ stock: Stock }>(this.getStockUrl, payload, {
      headers,
    });
  }

  sellStock(
    ticker: string,
    shares: number,
    bank_id: string,
    purchase_price_per_stock: number
  ): Observable<{ stock: Stock }> {
    const payload = {
      action: 'sell',
      stock_ticker: ticker,
      number_of_shares: shares,
      bank_ID: bank_id,
      purchase_price_per_stock: purchase_price_per_stock,
    };
    const headers = new HttpHeaders({
      'Content-Type': 'application/json',
    });

    return this.http.post<{ stock: Stock }>(this.getStockUrl, payload, {
      headers,
    });
  }

  getBondByTicker(
    ticker: string
  ): Observable<{ [ticker: string]: MarketBond }> {
    const payload = {
      action: 'view',
      bond_ticker: ticker,
    };
    const headers = new HttpHeaders({
      'Content-Type': 'application/json',
    });

    return this.http.post<{ [ticker: string]: MarketBond }>(
      this.getBondUrl,
      payload,
      { headers }
    );
  }

  buyBond(
    ticker: string,
    shares: number,
    bank_id: number
  ): Observable<BuyBondResponse> {
    const payload = {
      action: 'buy',
      bond_ticker: ticker,
      number_of_bonds: shares,
      bank_ID: bank_id,
    };
  
    const headers = new HttpHeaders({
      'Content-Type': 'application/json',
    });
    console.log(payload);
  
    return this.http.post<BuyBondResponse>(this.getBondUrl, payload, { headers });
  }

  sellBond(
    ticker: string,
    shares: number,
    bank_id: number,
    purchase_price_per_bond: number
  ): Observable<SellBondResponse> {
    const payload = {
      action: 'sell',
      bond_ticker: ticker,
      number_of_bonds: shares,
      bank_ID: bank_id,
      purchase_price_per_bond: purchase_price_per_bond,
    };

    console.log(payload);
    const headers = new HttpHeaders({
      'Content-Type': 'application/json',
    });

    return this.http.post<SellBondResponse>(this.getBondUrl, payload, {
      headers,
    });
  }

  getBankAccounts(): Observable<any> {
    return this.http.get<any>(this.bankAccountsUrl);
  }

  getTransactions(bank_id: number): Observable<any> {
    return this.http.post<any>(this.transactionsUrl, { bank_id });
  }
}
