import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { map, Observable } from 'rxjs';
import { Bond } from '../bond';
import { Stock } from '../stock';

@Injectable({
  providedIn: 'root'
})
export class PortfolioService {
  private cashValueUrl = 'http://127.0.0.1:5000/api/total_value';
  private stocksUrl = 'http://127.0.0.1:5000/api/stock_values';
  private bondsUrl = 'http://127.0.0.1:5000/api/bonds';
  private getStockUrl = 'http://127.0.0.1:5000/api/stock_value_from_ticker/';

  constructor(private http: HttpClient) {}

  getCashValue(): Observable<{ total_value: number; user_id: number }> {
    return this.http.get<{ total_value: number; user_id: number }>(this.cashValueUrl);
  }

  getBonds(): Observable<Bond[]> {
    return this.http.get<Bond[]>(this.bondsUrl);
  }
  

  getStocks(): Observable<{ [ticker: string]: Stock }> {
    return this.http.get<{ [ticker: string]: Stock }>(this.stocksUrl);
  }

  getStockByTicker(ticker: string): Observable<{ [ticker: string]: Stock }> {
    console.log(this.getStockUrl + ticker);
    return this.http.get<{ [ticker: string]: Stock }>(this.getStockUrl + ticker);
  }
}