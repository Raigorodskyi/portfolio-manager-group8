export interface Stock {
  current_price: number;
  purchase_price: number;
  shares: number;
  stock_name: string;
  transaction_ID: number;
}

export interface StockBuyMessage {
  message: string;
  quantity_sold: number;
  sale_value: number;
  stock_ticker: string;
  transaction_id: number;
}

export class MarketStock {
  constructor(
    public stock_ticker: string,
    public stock_name: string,
    public current_price: number
  ) {}
}