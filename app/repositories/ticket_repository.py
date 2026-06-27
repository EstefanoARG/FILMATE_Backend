from sqlalchemy.orm import Session
from app.models.boleta_ticket import BoletaTicket


def get_ticket_by_transaction_id(db: Session, transaction_id: int):
    return db.query(BoletaTicket).filter(BoletaTicket.id_transaccion == transaction_id).first()
