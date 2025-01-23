import uuid

from sqlalchemy import UUID, Column, Numeric

from backend.database import Base


class Wallet(Base):
    """Model for wallet"""

    __tablename__ = 'wallets'
    uuid = Column(UUID, primary_key=True, default=uuid.uuid4, nullable=False)
    balance = Column(Numeric(15, 2), default=0, nullable=False)

    def __str__(self):
        return f'{self.__class__.__name__}(uuid={self.uuid})'

    def __repr__(self):
        return str(self)
