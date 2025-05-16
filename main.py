from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import List
import uuid

# FastAPI app
app = FastAPI(title="Crypto Bank Backend")

# Database setup (SQLite)
DATABASE_URL = "sqlite:///./crypto_bank.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Security settings
SECRET_KEY = "your-secret-key-1234567890"  # Change in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Database Models
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    wallets = relationship("Wallet", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")

class Wallet(Base):
    __tablename__ = "wallets"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    currency = Column(String, default="USDT")  # Only USDT for now
    balance = Column(Float, default=0.0)
    user = relationship("User", back_populates="wallets")

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Float)
    currency = Column(String)
    transaction_type = Column(String)  # "deposit", "withdrawal", "transfer"
    recipient_wallet_id = Column(Integer, ForeignKey("wallets.id"), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="transactions")
    recipient_wallet = relationship("Wallet")

# Create database tables
Base.metadata.create_all(bind=engine)

# Pydantic Models
class UserCreate(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str

class Token(BaseModel):
    access_token: str
    token_type: str

class WalletOut(BaseModel):
    id: int
    currency: str
    balance: float

class TransactionCreate(BaseModel):
    amount: float
    currency: str
    transaction_type: str
    recipient_wallet_id: int = None

class TransactionOut(BaseModel):
    id: int
    amount: float
    currency: str
    transaction_type: str
    recipient_wallet_id: int = None
    timestamp: datetime

class ConversionRequest(BaseModel):
    amount_uzs: float

# Dependency for DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Security functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

# Mock exchange rate (1 USDT = 12,700 UZS)
def convert_uzs_to_usdt(amount_uzs: float) -> float:
    exchange_rate = 12700  # Mock rate
    return amount_uzs / exchange_rate

# API Endpoints
@app.post("/users/", response_model=UserOut)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    # Create a USDT wallet for the user
    wallet = Wallet(user_id=db_user.id, currency="USDT", balance=0.0)
    db.add(wallet)
    db.commit()
    return db_user

@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/wallets/", response_model=List[WalletOut])
async def get_wallets(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Wallet).filter(Wallet.user_id == current_user.id).all()

@app.post("/transactions/", response_model=TransactionOut)
async def create_transaction(
        transaction: TransactionCreate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    wallet = db.query(Wallet).filter(Wallet.user_id == current_user.id, Wallet.currency == transaction.currency).first()
    if not wallet:
        raise HTTPException(status_code=400, detail="Wallet not found")

    if transaction.transaction_type == "deposit":
        wallet.balance += transaction.amount
    elif transaction.transaction_type == "withdrawal":
        if wallet.balance < transaction.amount:
            raise HTTPException(status_code=400, detail="Insufficient balance")
        wallet.balance -= transaction.amount
    elif transaction.transaction_type == "transfer":
        if wallet.balance < transaction.amount:
            raise HTTPException(status_code=400, detail="Insufficient balance")
        recipient_wallet = db.query(Wallet).filter(Wallet.id == transaction.recipient_wallet_id).first()
        if not recipient_wallet:
            raise HTTPException(status_code=400, detail="Recipient wallet not found")
        wallet.balance -= transaction.amount
        recipient_wallet.balance += transaction.amount
    else:
        raise HTTPException(status_code=400, detail="Invalid transaction type")

    db_transaction = Transaction(
        user_id=current_user.id,
        amount=transaction.amount,
        currency=transaction.currency,
        transaction_type=transaction.transaction_type,
        recipient_wallet_id=transaction.recipient_wallet_id
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    db.commit()  # Commit wallet balance changes
    return db_transaction

@app.get("/transactions/", response_model=List[TransactionOut])
async def get_transactions(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Transaction).filter(Transaction.user_id == current_user.id).all()

@app.post("/convert/uzs_to_usdt/")
async def convert_currency(
        conversion: ConversionRequest,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    usdt_amount = convert_uzs_to_usdt(conversion.amount_uzs)
    wallet = db.query(Wallet).filter(Wallet.user_id == current_user.id, Wallet.currency == "USDT").first()
    if not wallet:
        raise HTTPException(status_code=400, detail="USDT wallet not found")
    wallet.balance += usdt_amount
    db_transaction = Transaction(
        user_id=current_user.id,
        amount=usdt_amount,
        currency="USDT",
        transaction_type="deposit",
        recipient_wallet_id=None
    )
    db.add(db_transaction)
    db.commit()
    return {"uzs_amount": conversion.amount_uzs, "usdt_amount": usdt_amount}
