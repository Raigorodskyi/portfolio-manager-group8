export interface Bond {
  'Bond Name': string;
  'Bond Ticker': string;
  'Bond Yield (%)': string;
  'Current Market Price (from YFinance)': number;
  'Number of Bonds': number;
  'Purchase Price per Bond': number;
}

export interface MarketBond {
  bond_ticker: string;
  bond_name: string;
  bond_yield: number;
  current_price: number;
  number_of_bonds: number;
  purchase_price_per_bond: number;
}