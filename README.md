# Crypto Bank Backend Ruslan Axmedov 230183

A FastAPI-based backend for a cryptocurrency bank, enabling user authentication, wallet management, USDT transactions, and conversion from Uzbekistani Som (UZS) to Tether (USDT). This project serves as a foundation for a secure and scalable crypto banking system.

## Table of Contents
- [Features](#features)
- [Technologies Used](#technologies-used)
- [API Endpoints](#api-endpoints)
- [Setup and Installation](#setup-and-installation)
- [Running the Application](#running-the-application)
- [Example Usage](#example-usage)
- [Future Plans](#future-plans)
- [Contributing](#contributing)
- [License](#license)

## Features
- **User Authentication**: Register and log in users with JWT-based authentication.
- **Wallet Management**: Each user gets a USDT wallet upon registration.
- **Transactions**: Support for deposits, withdrawals, and transfers in USDT.
- **Currency Conversion**: Convert UZS to USDT using a mock exchange rate (1 USDT = 12,700 UZS).
- **Transaction History**: Retrieve a user's transaction records.
- **Security**: Password hashing with bcrypt and JWT for secure API access.
- **Database**: SQLite for development (scalable to PostgreSQL/MySQL).

## Technologies Used
- **Python 3.7+**: Core programming language.
- **FastAPI**: High-performance web framework for building APIs.
- **SQLAlchemy**: ORM for database management.
- **SQLite**: Lightweight database for development.
- **Pydantic**: Data validation and serialization.
- **python-jose**: JWT handling for authentication.
- **passlib**: Password hashing with bcrypt.
- **Uvicorn**: ASGI server for running the FastAPI app.

## API Endpoints
The API is documented interactively via Swagger UI at `http://127.0.0.1:8000/docs` when the server is running.

| Endpoint | Method | Description | Authentication Required |
|----------|--------|-------------|------------------------|
| `/users/` | POST | Register a new user and create a USDT wallet | No |
| `/token` | POST | Log in and obtain a JWT token | No |
| `/wallets/` | GET | Retrieve user's wallets | Yes |
| `/transactions/` | POST | Create a transaction (deposit, withdrawal, transfer) | Yes |
| `/transactions/` | GET | Get transaction history | Yes |
| `/convert/uzs_to_usdt/` | POST | Convert UZS to USDT and deposit to wallet | Yes |

### Example Request/Response
**Register a User**:
```bash
curl -X POST "http://127.0.0.1:8000/users/" -H "Content-Type: application/json" -d '{"username": "testuser", "password": "testpass"}'
```
Response:
```json
{
  "id": 1,
  "username": "testuser"
}
```

**Convert UZS to USDT**:
```bash
curl -X POST "http://127.0.0.1:8000/convert/uzs_to_usdt/" -H "Authorization: Bearer <token>" -H "Content-Type: application/json" -d '{"amount_uzs": 127000}'
```
Response:
```json
{
  "uzs_amount": 127000,
  "usdt_amount": 10.0
}
```

## Setup and Installation
### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)
- Git (optional, for cloning the repository)

### Steps
1. **Clone the Repository** (or download the code):
   ```bash
   git clone <repository-url>
   cd crypto-bank-backend
   ```

2. **Create a Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install fastapi uvicorn sqlalchemy pydantic python-jose[cryptography] passlib[bcrypt]
   ```

4. **Verify Installation**:
   ```bash
   pip list
   ```
   Ensure all required packages are listed.

## Running the Application
1. **Navigate to the Project Directory**:
   ```bash
   cd path/to/crypto-bank-backend
   ```

2. **Run the FastAPI Server**:
   ```bash
   uvicorn bank_backend:app --reload
   ```

3. **Access the API**:
   - Open a browser or API client (e.g., Postman) and visit:
     - `http://127.0.0.1:8000/docs` for Swagger UI.
     - `http://127.0.0.1:8000/redoc` for ReDoc documentation.

4. **Stop the Server**:
   Press `Ctrl+C` in the terminal.

## Example Usage
1. **Register a User**:
   Use the `/users/` endpoint to create a user:
   ```bash
   curl -X POST "http://127.0.0.1:8000/users/" -H "Content-Type: application/json" -d '{"username": "testuser", "password": "testpass"}'
   ```

2. **Log In**:
   Obtain a JWT token:
   ```bash
   curl -X POST "http://127.0.0.1:8000/token" -d "username=testuser&password=testpass"
   ```
   Copy the `access_token` from the response.

3. **Convert UZS to USDT**:
   Convert 127,000 UZS to USDT:
   ```bash
   curl -X POST "http://127.0.0.1:8000/convert/uzs_to_usdt/" -H "Authorization: Bearer <token>" -H "Content-Type: application/json" -d '{"amount_uzs": 127000}'
   ```

4. **Check Wallet Balance**:
   ```bash
   curl -X GET "http://127.0.0.1:8000/wallets/" -H "Authorization: Bearer <token>"
   ```

## Future Plans
- **Frontend Development**:
  - Build a user-friendly frontend using **React** with **Tailwind CSS** for styling.
  - Features: User dashboard, wallet overview, transaction history, and conversion calculator.
  - Integration with the backend via Axios or Fetch for API calls.
- **Blockchain Integration**:
  - Connect to Ethereum or TRON for real USDT transactions using `web3.py`.
  - Implement wallet address generation and transaction signing.
- **Real-Time Exchange Rates**:
  - Integrate with APIs like CoinGecko or CoinMarketCap for accurate UZS to USDT rates.
- **Enhanced Security**:
  - Add two-factor authentication (2FA).
  - Implement rate limiting and IP whitelisting.
  - Enforce HTTPS and secure CORS policies.
- **Compliance**:
  - Integrate KYC/AML checks using third-party services.
  - Ensure compliance with Uzbekistan’s financial regulations.
- **Database Scalability**:
  - Migrate to PostgreSQL for production.
  - Add database indexing and caching (e.g., Redis).
- **Additional Cryptocurrencies**:
  - Support for BTC, ETH, and other stablecoins.
- **Mobile App**:
  - Develop iOS and Android apps using React Native.

## Contributing
Contributions are welcome! To contribute:
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/your-feature`).
3. Commit your changes (`git commit -m "Add your feature"`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Open a pull request.

Please ensure your code follows PEP 8 and includes tests.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.