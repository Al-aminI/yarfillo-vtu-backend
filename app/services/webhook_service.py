"""Synchronous webhook processing."""
from decimal import Decimal
from flask import current_app
from app.extensions import db
from app.models import WebhookLog, Wallet, Transaction
from app.services.wallet_service import WalletService
from app.utils.security import verify_webhook_hash
from app.utils.helpers import generate_ref
from app.errors.exceptions import ValidationException


def process_payscribe_webhook(webhook_log: WebhookLog) -> None:
    """Process Payscribe webhook synchronously."""
    try:
        payload = webhook_log.payload
        event_type = webhook_log.event_type

        if event_type == "accounts.payment.status" or "payment" in event_type.lower():
            _handle_virtual_account_payment(payload, webhook_log)
        elif "transaction" in event_type.lower() or "status" in event_type.lower():
            _handle_transaction_status(payload, webhook_log)
        else:
            current_app.logger.warning(f"Unhandled webhook event type: {event_type}")
            webhook_log.mark_failed(f"Unhandled event type: {event_type}")
            db.session.commit()
    except Exception as e:
        current_app.logger.error(f"Error processing webhook: {str(e)}")
        webhook_log.mark_failed(str(e))
        db.session.commit()


def _handle_virtual_account_payment(payload: dict, webhook_log: WebhookLog) -> None:
    """Handle virtual account payment webhook."""
    try:
        transaction_data = payload.get("transaction", {})
        customer_data = payload.get("customer", {})

        account_number = customer_data.get("number") or payload.get("account_number") or payload.get("virtual_account")
        amount = payload.get("amount")
        trans_id = payload.get("trans_id") or payload.get("transaction_id")
        sender_account = transaction_data.get("sender_account") or payload.get("sender_account") or payload.get("sender")
        bank_code = transaction_data.get("bank_code") or payload.get("bank_code") or payload.get("bank")
        transaction_hash = payload.get("transaction_hash") or payload.get("hash")
        status = payload.get("status", "").lower() or transaction_data.get("status", "").lower()

        if not account_number or not amount:
            raise ValidationException("Missing required payment fields")

        wallet = Wallet.query.filter_by(payscribe_account_number=account_number).first()
        if not wallet:
            current_app.logger.warning(f"Wallet not found for account: {account_number}")
            webhook_log.mark_failed("Wallet not found")
            db.session.commit()
            return

        secret_key = current_app.config.get("PAYSCRIBE_SECRET_KEY", "")
        if transaction_hash and secret_key:
            if not verify_webhook_hash(
                secret_key=secret_key,
                sender_account=sender_account or "",
                virtual_account=account_number,
                bank_code=bank_code or "",
                amount=str(amount),
                trans_id=trans_id or "",
                received_hash=transaction_hash,
            ):
                current_app.logger.warning(f"Invalid transaction hash for account: {account_number}")
                webhook_log.mark_failed("Invalid transaction hash")
                db.session.commit()
                return

        existing_transaction = Transaction.query.filter_by(
            payscribe_transaction_id=trans_id,
            type="credit",
        ).first()
        if existing_transaction:
            current_app.logger.info(f"Transaction already processed: {trans_id}")
            webhook_log.mark_processed()
            db.session.commit()
            return

        if status == "success" or status == "completed" or payload.get("status_code") == 200:
            wallet_service = WalletService()
            reference = generate_ref("CR")
            wallet_service.credit_wallet(
                user_id=wallet.user_id,
                amount=Decimal(str(amount)),
                reference=reference,
                description=f"Wallet funding via virtual account {account_number}",
                payscribe_trans_id=trans_id,
            )
            current_app.logger.info(f"Wallet credited: {wallet.user_id}, Amount: {amount}")
            webhook_log.mark_processed()
            db.session.commit()
        else:
            current_app.logger.warning(f"Payment not successful. Status: {status}")
            webhook_log.mark_failed(f"Payment status: {status}")
            db.session.commit()
    except Exception as e:
        current_app.logger.error(f"Error handling virtual account payment: {str(e)}")
        webhook_log.mark_failed(str(e))
        db.session.commit()


def _handle_transaction_status(payload: dict, webhook_log: WebhookLog) -> None:
    """Handle transaction status update webhook (airtime/data)."""
    try:
        trans_id = payload.get("trans_id") or payload.get("transaction_id")
        ref = payload.get("ref") or payload.get("reference")
        status = payload.get("status", "").lower()

        if not trans_id and not ref:
            raise ValidationException("Missing transaction identifier")

        transaction = None
        if trans_id:
            transaction = Transaction.query.filter_by(payscribe_transaction_id=trans_id).first()
        if not transaction and ref:
            transaction = Transaction.query.filter_by(reference=ref).first()

        if not transaction:
            current_app.logger.warning(f"Transaction not found: {trans_id or ref}")
            webhook_log.mark_failed("Transaction not found")
            db.session.commit()
            return

        if status == "success" or status == "completed":
            transaction.update_status("success")
        elif status == "failed" or status == "error":
            transaction.update_status("failed")
            if transaction.type in ["airtime", "data"]:
                wallet = Wallet.query.filter_by(user_id=transaction.user_id).first()
                if wallet:
                    wallet.credit(transaction.amount)
        elif status == "pending" or status == "processing":
            transaction.update_status("processing")

        db.session.commit()
        webhook_log.mark_processed()
        db.session.commit()
    except Exception as e:
        current_app.logger.error(f"Error handling transaction status: {str(e)}")
        webhook_log.mark_failed(str(e))
        db.session.commit()
