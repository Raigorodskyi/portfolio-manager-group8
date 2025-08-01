# portfolio-manager-group8

This is a repository for CS foundations Portfolio Manager Project.
Group members: Mahrukh, Igor and Akhil

!!!!

To be able to run the UI
*make sure to be in financial-dash folder*
then, please run:
- npm install
- npm run start

Flask API endpoints:
- GET /api/stock_values: Gives back a json where the key is stock tickers and the values are as shown below
    stock_name: the full name of the company
    purchase_price: the original purchase price per share
    shares: the number of shares owned
    current_price: the most recent market price from Yahoo Finance
  
- /user/total_value : Gives you the total value in user_portfolio.total_value   
