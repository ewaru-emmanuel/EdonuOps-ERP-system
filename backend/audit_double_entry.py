#!/usr/bin/env python3
"""
Double-Entry Accounting System Audit
====================================
Comprehensive audit of the double-entry accounting system
"""

import sqlite3
import json
from datetime import datetime

def audit_double_entry_system():
    """Audit the double-entry accounting system"""
    
    # Connect to database
    conn = sqlite3.connect('edonuops.db')
    cursor = conn.cursor()
    
    print('=' * 60)
    print('DOUBLE-ENTRY ACCOUNTING SYSTEM AUDIT')
    print('=' * 60)
    print(f'Audit Date: {datetime.now()}')
    print()
    
    # 1. Check user accounts
    print('1. USER ACCOUNTS:')
    cursor.execute("SELECT id, email, username FROM users WHERE email LIKE '%edonuerp%'")
    users = cursor.fetchall()
    
    if not users:
        print("   No users found with edonuerp email")
        return
    
    for user in users:
        print(f'   User ID: {user[0]}, Email: {user[1]}, Username: {user[2]}')
    print()
    
    # 2. Check journal entries for this user
    user_id = users[0][0]
    print(f'2. JOURNAL ENTRIES FOR USER {user_id}:')
    cursor.execute('''
        SELECT id, reference, description, total_debit, total_credit, status, doc_date
        FROM journal_entries 
        WHERE user_id = ? 
        ORDER BY doc_date DESC, id DESC
        LIMIT 10
    ''', (user_id,))
    entries = cursor.fetchall()
    
    if not entries:
        print("   No journal entries found for this user")
        return
    
    balanced_entries = 0
    unbalanced_entries = 0
    
    for entry in entries:
        entry_id, ref, desc, total_debit, total_credit, status, doc_date = entry
        is_balanced = abs(total_debit - total_credit) < 0.01
        balance_check = '✅ BALANCED' if is_balanced else '❌ UNBALANCED'
        
        if is_balanced:
            balanced_entries += 1
        else:
            unbalanced_entries += 1
        
        print(f'   Entry {entry_id}: {ref} - {desc}')
        print(f'     Debits: ${total_debit:.2f}, Credits: ${total_credit:.2f} - {balance_check}')
        print(f'     Status: {status}, Date: {doc_date}')
        
        # Check journal lines for this entry
        cursor.execute('''
            SELECT account_id, description, debit_amount, credit_amount
            FROM journal_lines 
            WHERE journal_entry_id = ?
            ORDER BY id
        ''', (entry_id,))
        lines = cursor.fetchall()
        
        total_line_debits = 0
        total_line_credits = 0
        
        for line in lines:
            acc_id, line_desc, debit, credit = line
            total_line_debits += debit
            total_line_credits += credit
            
            line_type = 'DEBIT' if debit > 0 else 'CREDIT'
            amount = debit if debit > 0 else credit
            print(f'       → Account {acc_id}: {line_desc} - {line_type} ${amount:.2f}')
        
        # Verify line totals match entry totals
        line_balance_check = '✅ MATCH' if abs(total_line_debits - total_debit) < 0.01 and abs(total_line_credits - total_credit) < 0.01 else '❌ MISMATCH'
        print(f'       Line Totals: Debits ${total_line_debits:.2f}, Credits ${total_line_credits:.2f} - {line_balance_check}')
        print()
    
    # 3. Summary statistics
    print('3. SUMMARY STATISTICS:')
    print(f'   Total Entries Checked: {len(entries)}')
    print(f'   Balanced Entries: {balanced_entries} ✅')
    print(f'   Unbalanced Entries: {unbalanced_entries} ❌')
    print(f'   Balance Compliance: {(balanced_entries/len(entries)*100):.1f}%')
    print()
    
    # 4. Check for any entries with both debit and credit on same line
    print('4. CHECKING FOR INVALID JOURNAL LINES:')
    cursor.execute('''
        SELECT journal_entry_id, account_id, description, debit_amount, credit_amount
        FROM journal_lines 
        WHERE journal_entry_id IN (
            SELECT id FROM journal_entries WHERE user_id = ?
        )
        AND debit_amount > 0 AND credit_amount > 0
    ''', (user_id,))
    invalid_lines = cursor.fetchall()
    
    if invalid_lines:
        print(f'   ❌ Found {len(invalid_lines)} invalid lines with both debit and credit amounts:')
        for line in invalid_lines:
            entry_id, acc_id, desc, debit, credit = line
            print(f'     Entry {entry_id}, Account {acc_id}: {desc} - Debit ${debit:.2f}, Credit ${credit:.2f}')
    else:
        print('   ✅ No invalid journal lines found (no lines with both debit and credit)')
    print()
    
    # 5. Check account balances
    print('5. ACCOUNT BALANCES:')
    cursor.execute('''
        SELECT a.id, a.code, a.name, a.type,
               COALESCE(SUM(jl.debit_amount), 0) as total_debits,
               COALESCE(SUM(jl.credit_amount), 0) as total_credits,
               COALESCE(SUM(jl.debit_amount), 0) - COALESCE(SUM(jl.credit_amount), 0) as balance
        FROM accounts a
        LEFT JOIN journal_lines jl ON a.id = jl.account_id
        LEFT JOIN journal_entries je ON jl.journal_entry_id = je.id
        WHERE je.user_id = ? OR je.user_id IS NULL
        GROUP BY a.id, a.code, a.name, a.type
        HAVING total_debits > 0 OR total_credits > 0
        ORDER BY a.code
    ''', (user_id,))
    account_balances = cursor.fetchall()
    
    for acc in account_balances:
        acc_id, code, name, acc_type, debits, credits, balance = acc
        print(f'   Account {code} ({name}): Debits ${debits:.2f}, Credits ${credits:.2f}, Balance ${balance:.2f}')
    
    conn.close()
    
    print()
    print('=' * 60)
    print('AUDIT COMPLETE')
    print('=' * 60)

if __name__ == '__main__':
    audit_double_entry_system()
