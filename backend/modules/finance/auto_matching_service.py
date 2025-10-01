"""
Auto-matching service for bank reconciliation
Uses intelligent algorithms to match transactions
"""

from datetime import datetime, timedelta
from sqlalchemy import and_, or_
from app import db
from .payment_models import PaymentTransaction, PartialPayment
from .advanced_models import AccountsReceivable, AccountsPayable


class AutoMatchingService:
    """Service for automatically matching bank transactions with invoices"""
    
    @staticmethod
    def find_potential_matches(bank_transaction, tolerance_days=3, amount_tolerance=0.01):
        """
        Find potential matches for a bank transaction
        
        Args:
            bank_transaction: Bank transaction to match
            tolerance_days: Days tolerance for date matching
            amount_tolerance: Amount tolerance percentage (0.01 = 1%)
        
        Returns:
            List of potential matches with confidence scores
        """
        matches = []
        
        # Extract transaction details
        amount = bank_transaction.get('amount', 0)
        transaction_date = datetime.strptime(bank_transaction.get('date', ''), '%Y-%m-%d').date()
        reference = bank_transaction.get('reference', '').lower()
        description = bank_transaction.get('description', '').lower()
        
        # Calculate date range
        start_date = transaction_date - timedelta(days=tolerance_days)
        end_date = transaction_date + timedelta(days=tolerance_days)
        
        # Calculate amount range
        min_amount = amount * (1 - amount_tolerance)
        max_amount = amount * (1 + amount_tolerance)
        
        # Search in Accounts Receivable (for incoming payments)
        if amount > 0:  # Incoming payment
            ar_invoices = AccountsReceivable.query.filter(
                and_(
                    AccountsReceivable.total_amount.between(min_amount, max_amount),
                    AccountsReceivable.due_date.between(start_date, end_date),
                    AccountsReceivable.status.in_(['pending', 'partial'])
                )
            ).all()
            
            for invoice in ar_invoices:
                confidence = AutoMatchingService._calculate_confidence(
                    bank_transaction, invoice, 'AR'
                )
                if confidence > 0.5:  # Minimum confidence threshold
                    matches.append({
                        'type': 'AR',
                        'invoice': invoice,
                        'confidence': confidence,
                        'match_reasons': AutoMatchingService._get_match_reasons(
                            bank_transaction, invoice, 'AR'
                        )
                    })
        
        # Search in Accounts Payable (for outgoing payments)
        elif amount < 0:  # Outgoing payment
            ap_invoices = AccountsPayable.query.filter(
                and_(
                    AccountsPayable.total_amount.between(abs(max_amount), abs(min_amount)),
                    AccountsPayable.due_date.between(start_date, end_date),
                    AccountsPayable.status.in_(['pending', 'partial'])
                )
            ).all()
            
            for invoice in ap_invoices:
                confidence = AutoMatchingService._calculate_confidence(
                    bank_transaction, invoice, 'AP'
                )
                if confidence > 0.5:
                    matches.append({
                        'type': 'AP',
                        'invoice': invoice,
                        'confidence': confidence,
                        'match_reasons': AutoMatchingService._get_match_reasons(
                            bank_transaction, invoice, 'AP'
                        )
                    })
        
        # Sort by confidence score (highest first)
        matches.sort(key=lambda x: x['confidence'], reverse=True)
        
        return matches[:5]  # Return top 5 matches
    
    @staticmethod
    def _calculate_confidence(bank_transaction, invoice, invoice_type):
        """Calculate confidence score for a potential match"""
        confidence = 0.0
        
        # Amount matching (40% weight)
        bank_amount = abs(bank_transaction.get('amount', 0))
        invoice_amount = invoice.total_amount
        amount_diff = abs(bank_amount - invoice_amount) / invoice_amount
        
        if amount_diff == 0:
            confidence += 0.4
        elif amount_diff <= 0.01:  # 1% tolerance
            confidence += 0.35
        elif amount_diff <= 0.05:  # 5% tolerance
            confidence += 0.25
        elif amount_diff <= 0.1:   # 10% tolerance
            confidence += 0.15
        
        # Date proximity (30% weight)
        bank_date = datetime.strptime(bank_transaction.get('date', ''), '%Y-%m-%d').date()
        due_date = invoice.due_date
        date_diff = abs((bank_date - due_date).days)
        
        if date_diff == 0:
            confidence += 0.3
        elif date_diff <= 1:
            confidence += 0.25
        elif date_diff <= 3:
            confidence += 0.2
        elif date_diff <= 7:
            confidence += 0.15
        elif date_diff <= 14:
            confidence += 0.1
        
        # Reference/description matching (20% weight)
        reference = bank_transaction.get('reference', '').lower()
        description = bank_transaction.get('description', '').lower()
        invoice_number = invoice.invoice_number.lower() if invoice.invoice_number else ''
        
        # Check for invoice number in reference or description
        if invoice_number and (invoice_number in reference or invoice_number in description):
            confidence += 0.2
        elif invoice_number and (
            any(part in reference for part in invoice_number.split('-')) or
            any(part in description for part in invoice_number.split('-'))
        ):
            confidence += 0.15
        
        # Customer/vendor name matching (10% weight)
        customer_name = getattr(invoice, 'customer_name', '').lower()
        vendor_name = getattr(invoice, 'vendor_name', '').lower()
        entity_name = customer_name or vendor_name
        
        if entity_name and (entity_name in description or any(
            word in description for word in entity_name.split() if len(word) > 3
        )):
            confidence += 0.1
        
        return min(confidence, 1.0)  # Cap at 100%
    
    @staticmethod
    def _get_match_reasons(bank_transaction, invoice, invoice_type):
        """Get human-readable reasons for the match"""
        reasons = []
        
        # Amount matching
        bank_amount = abs(bank_transaction.get('amount', 0))
        invoice_amount = invoice.total_amount
        amount_diff = abs(bank_amount - invoice_amount) / invoice_amount
        
        if amount_diff == 0:
            reasons.append("Exact amount match")
        elif amount_diff <= 0.05:
            reasons.append(f"Close amount match ({amount_diff*100:.1f}% difference)")
        
        # Date proximity
        bank_date = datetime.strptime(bank_transaction.get('date', ''), '%Y-%m-%d').date()
        due_date = invoice.due_date
        date_diff = abs((bank_date - due_date).days)
        
        if date_diff == 0:
            reasons.append("Same date as due date")
        elif date_diff <= 3:
            reasons.append(f"Close to due date ({date_diff} days)")
        
        # Reference matching
        reference = bank_transaction.get('reference', '').lower()
        description = bank_transaction.get('description', '').lower()
        invoice_number = invoice.invoice_number.lower() if invoice.invoice_number else ''
        
        if invoice_number and (invoice_number in reference or invoice_number in description):
            reasons.append("Invoice number found in transaction")
        
        # Entity name matching
        customer_name = getattr(invoice, 'customer_name', '')
        vendor_name = getattr(invoice, 'vendor_name', '')
        entity_name = customer_name or vendor_name
        
        if entity_name and entity_name.lower() in description:
            reasons.append(f"Entity name '{entity_name}' found in description")
        
        return reasons
    
    @staticmethod
    def auto_match_transaction(bank_transaction_id, invoice_id, invoice_type, confidence_threshold=0.8):
        """
        Automatically match a bank transaction with an invoice
        Only matches with high confidence
        """
        try:
            # Get the bank transaction (this would come from your bank feed)
            # For now, we'll simulate this
            
            # Create a payment transaction record
            payment_transaction = PaymentTransaction(
                transaction_number=f"AUTO-{bank_transaction_id}",
                payment_date=datetime.now().date(),
                amount=0,  # This would come from bank transaction
                payment_method_id=1,  # This would be determined from bank transaction
                status='matched',
                notes=f"Auto-matched with {confidence_threshold*100:.0f}% confidence"
            )
            
            db.session.add(payment_transaction)
            
            # Update invoice status if fully paid
            if invoice_type == 'AR':
                invoice = AccountsReceivable.query.get(invoice_id)
                if invoice and invoice.outstanding_amount <= payment_transaction.amount:
                    invoice.status = 'paid'
                    invoice.payment_date = payment_transaction.payment_date
            elif invoice_type == 'AP':
                invoice = AccountsPayable.query.get(invoice_id)
                if invoice and invoice.outstanding_amount <= payment_transaction.amount:
                    invoice.status = 'paid'
                    invoice.payment_date = payment_transaction.payment_date
            
            db.session.commit()
            
            return {
                'success': True,
                'payment_transaction_id': payment_transaction.id,
                'message': 'Transaction matched successfully'
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def get_unmatched_transactions(days_back=30):
        """Get unmatched bank transactions for the specified period"""
        # This would integrate with your bank feed API
        # For now, return simulated data
        
        from datetime import date
        
        simulated_transactions = [
            {
                'id': 'TXN001',
                'date': (date.today() - timedelta(days=1)).isoformat(),
                'amount': 1500.00,
                'reference': 'INV-2024-001',
                'description': 'Payment from ABC Corp',
                'bank_account': 'Main Checking'
            },
            {
                'id': 'TXN002',
                'date': (date.today() - timedelta(days=2)).isoformat(),
                'amount': -850.00,
                'reference': 'CHK-12345',
                'description': 'Payment to XYZ Supplies',
                'bank_account': 'Main Checking'
            },
            {
                'id': 'TXN003',
                'date': (date.today() - timedelta(days=3)).isoformat(),
                'amount': 2200.00,
                'reference': 'WIRE-789',
                'description': 'Wire transfer from DEF Ltd',
                'bank_account': 'Main Checking'
            }
        ]
        
        return simulated_transactions
    
    @staticmethod
    def run_auto_matching(confidence_threshold=0.8):
        """Run auto-matching for all unmatched transactions"""
        results = {
            'matched': 0,
            'potential_matches': 0,
            'no_matches': 0,
            'details': []
        }
        
        unmatched_transactions = AutoMatchingService.get_unmatched_transactions()
        
        for transaction in unmatched_transactions:
            matches = AutoMatchingService.find_potential_matches(transaction)
            
            if matches:
                best_match = matches[0]
                if best_match['confidence'] >= confidence_threshold:
                    # Auto-match with high confidence
                    match_result = AutoMatchingService.auto_match_transaction(
                        transaction['id'],
                        best_match['invoice'].id,
                        best_match['type'],
                        best_match['confidence']
                    )
                    
                    if match_result['success']:
                        results['matched'] += 1
                        results['details'].append({
                            'transaction_id': transaction['id'],
                            'action': 'matched',
                            'confidence': best_match['confidence'],
                            'invoice': f"{best_match['type']}-{best_match['invoice'].id}"
                        })
                    else:
                        results['details'].append({
                            'transaction_id': transaction['id'],
                            'action': 'failed',
                            'error': match_result['error']
                        })
                else:
                    # Potential match but below threshold
                    results['potential_matches'] += 1
                    results['details'].append({
                        'transaction_id': transaction['id'],
                        'action': 'potential',
                        'confidence': best_match['confidence'],
                        'matches': len(matches)
                    })
            else:
                # No matches found
                results['no_matches'] += 1
                results['details'].append({
                    'transaction_id': transaction['id'],
                    'action': 'no_matches'
                })
        
        return results

