# モデル設計書

## 🏗️ モデル設計方針

### SQLAlchemyモデル設計原則
- 明確なドメイン境界の定義
- DRY原則の遵守
- 型安全性の確保
- リレーションシップの適切な定義

### Pydanticスキーマ設計原則
- 入出力の明確な分離
- バリデーション規則の統一
- 再利用可能なベーススキーマ
- 自動ドキュメント生成対応

## 📊 ベースモデル設計

### SQLAlchemy Base Model
```python
from sqlalchemy import Column, Integer, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property

Base = declarative_base()

class TimestampMixin:
    """共通タイムスタンプMixin"""
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

class BaseModel(Base, TimestampMixin):
    """共通ベースモデル"""
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    
    @hybrid_property
    def is_new(self):
        """新規レコードかどうか"""
        return self.id is None
```

### Pydantic Base Schema
```python
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class BaseSchema(BaseModel):
    """共通ベーススキーマ"""
    model_config = ConfigDict(from_attributes=True)

class TimestampSchema(BaseSchema):
    """タイムスタンプスキーマ"""
    created_at: datetime
    updated_at: datetime

class IDSchema(BaseSchema):
    """ID付きスキーマ"""
    id: int = Field(..., gt=0)
```

## 🏭 ドメインモデル実装

### 1. 出荷管理ドメイン

#### SQLAlchemyモデル
```python
from sqlalchemy import Column, Integer, String, Date, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
import enum

class ShipmentStatus(str, enum.Enum):
    """出荷ステータス"""
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class ShipmentChecksheet(BaseModel):
    """出荷チェックシートモデル"""
    __tablename__ = "shipment_checksheets"
    
    shipment_no = Column(String(50), unique=True, nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    shipment_date = Column(Date, nullable=False, index=True)
    inspector_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    status = Column(Enum(ShipmentStatus), default=ShipmentStatus.DRAFT, nullable=False)
    
    # リレーションシップ
    customer = relationship("Customer", back_populates="checksheets")
    product = relationship("Product", back_populates="checksheets")
    inspector = relationship("Employee", back_populates="inspected_checksheets")
    items = relationship("ChecksheetItem", back_populates="checksheet", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ShipmentChecksheet(shipment_no={self.shipment_no})>"

class CheckResult(str, enum.Enum):
    """チェック結果"""
    OK = "OK"
    NG = "NG"
    NA = "NA"

class ChecksheetItem(BaseModel):
    """チェックシート項目モデル"""
    __tablename__ = "checksheet_items"
    
    checksheet_id = Column(Integer, ForeignKey("shipment_checksheets.id"), nullable=False)
    check_point = Column(String(200), nullable=False)
    result = Column(Enum(CheckResult), nullable=False)
    note = Column(Text)
    checked_at = Column(DateTime(timezone=True))
    
    # リレーションシップ
    checksheet = relationship("ShipmentChecksheet", back_populates="items")
```

#### Pydanticスキーマ
```python
from typing import List, Optional
from datetime import date, datetime
from pydantic import Field, field_validator

# リクエストスキーマ
class ChecksheetItemCreate(BaseSchema):
    """チェック項目作成スキーマ"""
    check_point: str = Field(..., min_length=1, max_length=200)
    result: CheckResult
    note: Optional[str] = None

class ShipmentChecksheetCreate(BaseSchema):
    """出荷チェックシート作成スキーマ"""
    shipment_no: str = Field(..., min_length=1, max_length=50)
    customer_id: int = Field(..., gt=0)
    product_id: int = Field(..., gt=0)
    shipment_date: date
    items: List[ChecksheetItemCreate] = Field(..., min_items=1)
    
    @field_validator('shipment_date')
    def validate_shipment_date(cls, v):
        if v < date.today():
            raise ValueError('出荷日は今日以降の日付を指定してください')
        return v

# レスポンススキーマ
class CustomerInfo(BaseSchema):
    """顧客情報スキーマ"""
    id: int
    customer_name: str
    customer_code: str

class ProductInfo(BaseSchema):
    """製品情報スキーマ"""
    id: int
    product_name: str
    product_code: str

class ChecksheetItemResponse(TimestampSchema):
    """チェック項目レスポンススキーマ"""
    id: int
    check_point: str
    result: CheckResult
    note: Optional[str]
    checked_at: Optional[datetime]

class ShipmentChecksheetResponse(TimestampSchema):
    """出荷チェックシートレスポンススキーマ"""
    id: int
    shipment_no: str
    customer: CustomerInfo
    product: ProductInfo
    shipment_date: date
    status: ShipmentStatus
    items: List[ChecksheetItemResponse]
```

### 2. 生産管理ドメイン

#### SQLAlchemyモデル
```python
class ProductionResult(BaseModel):
    """生産実績モデル"""
    __tablename__ = "production_results"
    
    work_order_no = Column(String(50), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    line_id = Column(Integer, ForeignKey("production_lines.id"), nullable=False)
    worker_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False, index=True)
    end_time = Column(DateTime(timezone=True))
    planned_quantity = Column(Integer, nullable=False)
    actual_quantity = Column(Integer, default=0, nullable=False)
    defect_quantity = Column(Integer, default=0, nullable=False)
    status = Column(String(20), nullable=False)
    
    # リレーションシップ
    product = relationship("Product", back_populates="production_results")
    line = relationship("ProductionLine", back_populates="results")
    worker = relationship("Employee", back_populates="production_results")
    defects = relationship("DefectRecord", back_populates="production_result", cascade="all, delete-orphan")
    
    @hybrid_property
    def efficiency(self):
        """生産効率"""
        if self.planned_quantity == 0:
            return 0
        return (self.actual_quantity / self.planned_quantity) * 100
    
    @hybrid_property
    def defect_rate(self):
        """不良率"""
        total = self.actual_quantity + self.defect_quantity
        if total == 0:
            return 0
        return (self.defect_quantity / total) * 100

class DefectRecord(BaseModel):
    """不良記録モデル"""
    __tablename__ = "defect_records"
    
    result_id = Column(Integer, ForeignKey("production_results.id"), nullable=False)
    defect_type_id = Column(Integer, ForeignKey("defect_types.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    cause = Column(Text)
    action_taken = Column(Text)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # リレーションシップ
    production_result = relationship("ProductionResult", back_populates="defects")
    defect_type = relationship("DefectType")
```

### 3. 在庫管理ドメイン

#### SQLAlchemyモデル
```python
from decimal import Decimal

class InventoryItem(BaseModel):
    """在庫品目モデル"""
    __tablename__ = "inventory_items"
    
    item_code = Column(String(50), unique=True, nullable=False, index=True)
    item_name = Column(String(200), nullable=False)
    category_id = Column(Integer, ForeignKey("item_categories.id"), nullable=False)
    unit = Column(String(20), nullable=False)
    min_stock_level = Column(Numeric(10, 2))
    max_stock_level = Column(Numeric(10, 2))
    current_stock = Column(Numeric(10, 2), default=0, nullable=False)
    location_id = Column(Integer, ForeignKey("storage_locations.id"))
    qr_code = Column(String(100), unique=True, index=True)
    is_active = Column(Boolean, default=True)
    
    # リレーションシップ
    category = relationship("ItemCategory", back_populates="items")
    location = relationship("StorageLocation", back_populates="items")
    transactions = relationship("InventoryTransaction", back_populates="item")
    
    @hybrid_property
    def stock_status(self):
        """在庫ステータス"""
        if self.current_stock <= 0:
            return "out_of_stock"
        elif self.min_stock_level and self.current_stock < self.min_stock_level:
            return "low_stock"
        elif self.max_stock_level and self.current_stock > self.max_stock_level:
            return "over_stock"
        return "normal"

class TransactionType(str, enum.Enum):
    """取引タイプ"""
    IN = "IN"
    OUT = "OUT"
    ADJUST = "ADJUST"

class InventoryTransaction(BaseModel):
    """在庫取引モデル"""
    __tablename__ = "inventory_transactions"
    
    item_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=False)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    quantity = Column(Numeric(10, 2), nullable=False)
    reference_no = Column(String(50))
    reference_type = Column(String(50))
    performed_by = Column(Integer, ForeignKey("employees.id"), nullable=False)
    note = Column(Text)
    transaction_date = Column(DateTime(timezone=True), server_default=func.now())
    
    # リレーションシップ
    item = relationship("InventoryItem", back_populates="transactions")
    performer = relationship("Employee")
```

## 🔧 共通モデル

### マスタデータモデル
```python
class Employee(BaseModel):
    """従業員モデル"""
    __tablename__ = "employees"
    
    employee_code = Column(String(20), unique=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    email = Column(String(100))
    is_active = Column(Boolean, default=True)
    
    # リレーションシップ
    department = relationship("Department", back_populates="employees")
    role = relationship("Role", back_populates="employees")

class Product(BaseModel):
    """製品モデル"""
    __tablename__ = "products"
    
    product_code = Column(String(50), unique=True, nullable=False)
    product_name = Column(String(200), nullable=False)
    product_type = Column(String(50))
    specification = Column(Text)
    unit = Column(String(20), nullable=False)
    is_active = Column(Boolean, default=True)

class Customer(BaseModel):
    """顧客モデル"""
    __tablename__ = "customers"
    
    customer_code = Column(String(50), unique=True, nullable=False)
    customer_name = Column(String(200), nullable=False)
    address = Column(Text)
    contact_person = Column(String(100))
    phone = Column(String(20))
    email = Column(String(100))
    is_active = Column(Boolean, default=True)
```

## 🔄 モデル変換ユーティリティ

```python
from typing import TypeVar, Type, List
from sqlalchemy.orm import Session
from pydantic import BaseModel as PydanticModel

T = TypeVar('T', bound=Base)
S = TypeVar('S', bound=PydanticModel)

class ModelConverter:
    """モデル変換ユーティリティ"""
    
    @staticmethod
    def to_schema(db_model: T, schema_class: Type[S]) -> S:
        """SQLAlchemyモデルをPydanticスキーマに変換"""
        return schema_class.model_validate(db_model)
    
    @staticmethod
    def to_schema_list(db_models: List[T], schema_class: Type[S]) -> List[S]:
        """SQLAlchemyモデルリストをPydanticスキーマリストに変換"""
        return [schema_class.model_validate(model) for model in db_models]
    
    @staticmethod
    def update_model(db_model: T, update_data: dict) -> T:
        """モデルの更新"""
        for field, value in update_data.items():
            if hasattr(db_model, field):
                setattr(db_model, field, value)
        return db_model
```