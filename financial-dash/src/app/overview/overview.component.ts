import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-overview',
  imports: [CommonModule],
  templateUrl: './overview.component.html',
  styleUrl: './overview.component.css'
})
export class OverviewComponent {
  stocks = [
    { name: 'Apple', ticker: 'AAPL', price: 200, gain: '+2%',  },
    { name: 'Tesla', ticker: 'TSLA', price: 700, gain: '-1.5%' }
    
  ];
}
