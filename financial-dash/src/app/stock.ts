export interface Stock {
  stock_ticker: string;
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

export interface StockSellMessage {
  message: string;
  original_transaction_id: number;
  quantity_sold: number;
  sale_price_per_share: number;
  sale_transaction_id: number;
  sale_value: number;
  stock_ticker: string;
}

export class MarketStock {
  constructor(
    public stock_ticker: string,
    public stock_name: string,
    public current_price: number
  ) {}
}