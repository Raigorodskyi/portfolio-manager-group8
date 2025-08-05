# Portfolio Manager — Group 8

This is the repository for the **CS Foundations Portfolio Manager Project**.

**Group members:**
- Mahrukh
- Igor
- Akhil

---

## 🚀 Running the UI
To start the Angular frontend:

1. **Navigate** to the `financial-dash` folder:
   ```bash
   cd financial-dash

2. **Install dependencies**:
   ```bash
   npm install

3. **Run** the development server:
   ```bash
   npm run start
    # or
   ng serve

## 🌐 Flask API Endpoints

### **GET Requests**
| Endpoint | Description |
|----------|-------------|
| `/api/stock_values` | Returns information about all of the stocks the user owns. |
| `/api/total_value` | Returns the total value in `user_portfolio.total_value` (the cash the user has deposited in our app). |
| `/api/bank_accounts` | Returns the bank account name and type for the user. |
| `/api/bonds` | Returns information about all of the bonds the user owns. |

---

### **POST Requests**

#### **Stocks**
**Endpoint:** `/api/stock_action`  
- **Action:** `buy` / `sell` / `view`  
- **Parameters:**
  - **`view`** → requires `stock_ticker`
  - **`buy`** → requires `stock_ticker`, `number_of_shares`, `bank_ID`
  - **`sell`** → requires everything from **buy** + `purchase_price_per_stock`

#### **Bonds**
**Endpoint:** `/api/bond_action`  
- Same as `stock_action` but for bonds:
  - **`view`** → requires `bond_ticker`
  - **`buy`** → requires `bond_ticker`, `number_of_bonds`, `bank_ID`
  - **`sell`** → requires everything from **buy** + `purchase_price_per_bond`
