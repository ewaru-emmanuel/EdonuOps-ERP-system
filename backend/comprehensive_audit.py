import sqlite3
from datetime import datetime

def comprehensive_double_entry_audit():
    """Comprehensive audit of double-entry accounting system"""
    
    conn = sqlite3.connect('edonuops.db')
    cursor = conn.cursor()
    
    print('=' * 80)
    print('COMPREHENSIVE DOUBLE-ENTRY ACCOUNTING AUDIT')
    print('=' * 80)
    print(f'Audit Date: {datetime.now()}')
    print()
    
    # 1. Check all journal entries for balance compliance
    print('1. JOURNAL ENTRY BALANCE COMPLIANCE:')
    cursor.execute('''
        SELECT id, reference, description, total_debit, total_credit, status, doc_date, user_id
        FROM journal_entries 
        ORDER BY doc_date DESC, id DESC
    ''')
    entries = cursor.fetchall()
    
    balanced_entries = 0
    unbalanced_entries = 0
    total_entries = len(entries)
    
    for entry in entries:
        entry_id, ref, desc, total_debit, total_credit, status, doc_date, user_id = entry
        is_balanced = abs(total_debit - total_credit) < 0.01
        balance_check = '✅ BALANCED' if is_balanced else '❌ UNBALANCED'
        
        if is_balanced:
            balanced_entries += 1
        else:
            unbalanced_entries += 1
            print(f'   ❌ Entry {entry_id}: {ref} - {desc}')
            print(f'      Debits: ${total_debit:.2f}, Credits: ${total_credit:.2f} - {balance_check}')
            print(f'      User ID: {user_id}, Status: {status}, Date: {doc_date}')
    
    print(f'   Total Entries: {total_entries}')
    print(f'   Balanced Entries: {balanced_entries} ✅')
    print(f'   Unbalanced Entries: {unbalanced_entries} ❌')
    print(f'   Balance Compliance: {(balanced_entries/total_entries*100):.1f}%' if total_entries > 0 else '   Balance Compliance: N/A')
    print()
    
    # 2. Check journal lines for proper double-entry structure
    print('2. JOURNAL LINE STRUCTURE COMPLIANCE:')
    cursor.execute('''
        SELECT journal_entry_id, account_id, description, debit_amount, credit_amount
        FROM journal_lines 
        ORDER BY journal_entry_id, id
    ''')
    lines = cursor.fetchall()
    
    invalid_lines = 0
    valid_lines = 0
    
    for line in lines:
        entry_id, acc_id, desc, debit, credit = line
        has_both = debit > 0 and credit > 0
        has_neither = debit == 0 and credit == 0
        has_one = (debit > 0 and credit == 0) or (debit == 0 and credit > 0)
        
        if has_both or has_neither:
            invalid_lines += 1
            issue = 'BOTH DEBIT AND CREDIT' if has_both else 'NEITHER DEBIT NOR CREDIT'
            print(f'   ❌ Entry {entry_id}, Account {acc_id}: {desc} - {issue}')
            print(f'      Debit: ${debit:.2f}, Credit: ${credit:.2f}')
        else:
            valid_lines += 1
    
    print(f'   Total Lines: {len(lines)}')
    print(f'   Valid Lines: {valid_lines} ✅')
    print(f'   Invalid Lines: {invalid_lines} ❌')
    print(f'   Line Compliance: {(valid_lines/len(lines)*100):.1f}%' if len(lines) > 0 else '   Line Compliance: N/A')
    print()
    
    # 3. Verify entry totals match line totals
    print('3. ENTRY TOTALS vs LINE TOTALS VERIFICATION:')
    cursor.execute('''
        SELECT je.id, je.reference, je.total_debit, je.total_credit,
               COALESCE(SUM(jl.debit_amount), 0) as line_debits,
               COALESCE(SUM(jl.credit_amount), 0) as line_credits
        FROM journal_entries je
        LEFT JOIN journal_lines jl ON je.id = jl.journal_entry_id
        GROUP BY je.id, je.reference, je.total_debit, je.total_credit
        ORDER BY je.id
    ''')
    entry_line_totals = cursor.fetchall()
    
    matching_totals = 0
    mismatched_totals = 0
    
    for entry in entry_line_totals:
        entry_id, ref, entry_debit, entry_credit, line_debit, line_credit = entry
        debit_match = abs(entry_debit - line_debit) < 0.01
        credit_match = abs(entry_credit - line_credit) < 0.01
        
        if debit_match and credit_match:
            matching_totals += 1
        else:
            mismatched_totals += 1
            print(f'   ❌ Entry {entry_id}: {ref}')
            print(f'      Entry Totals - Debit: ${entry_debit:.2f}, Credit: ${entry_credit:.2f}')
            print(f'      Line Totals - Debit: ${line_debit:.2f}, Credit: ${line_credit:.2f}')
    
    print(f'   Total Entries: {len(entry_line_totals)}')
    print(f'   Matching Totals: {matching_totals} ✅')
    print(f'   Mismatched Totals: {mismatched_totals} ❌')
    print(f'   Total Compliance: {(matching_totals/len(entry_line_totals)*100):.1f}%' if len(entry_line_totals) > 0 else '   Total Compliance: N/A')
    print()
    
    # 4. Check for orphaned journal lines
    print('4. ORPHANED JOURNAL LINES CHECK:')
    cursor.execute('''
        SELECT COUNT(*) FROM journal_lines jl
        LEFT JOIN journal_entries je ON jl.journal_entry_id = je.id
        WHERE je.id IS NULL
    ''')
    orphaned_count = cursor.fetchone()[0]
    
    if orphaned_count > 0:
        print(f'   ❌ Found {orphaned_count} orphaned journal lines')
    else:
        print('   ✅ No orphaned journal lines found')
    print()
    
    # 5. Sample detailed analysis of recent entries
    print('5. DETAILED ANALYSIS OF RECENT ENTRIES:')
    cursor.execute('''
        SELECT je.id, je.reference, je.description, je.total_debit, je.total_credit, je.status, je.doc_date
        FROM journal_entries je
        ORDER BY je.doc_date DESC, je.id DESC
        LIMIT 5
    ''')
    recent_entries = cursor.fetchall()
    
    for entry in recent_entries:
        entry_id, ref, desc, total_debit, total_credit, status, doc_date = entry
        print(f'   Entry {entry_id}: {ref} - {desc}')
        print(f'     Status: {status}, Date: {doc_date}')
        print(f'     Entry Totals: Debit ${total_debit:.2f}, Credit ${total_credit:.2f}')
        
        # Get journal lines for this entry
        cursor.execute('''
            SELECT jl.account_id, a.code, a.name, jl.description, jl.debit_amount, jl.credit_amount
            FROM journal_lines jl
            LEFT JOIN accounts a ON jl.account_id = a.id
            WHERE jl.journal_entry_id = ?
            ORDER BY jl.id
        ''', (entry_id,))
        lines = cursor.fetchall()
        
        line_debit_total = 0
        line_credit_total = 0
        
        for line in lines:
            acc_id, acc_code, acc_name, line_desc, debit, credit = line
            line_debit_total += debit
            line_credit_total += credit
            
            line_type = 'DEBIT' if debit > 0 else 'CREDIT'
            amount = debit if debit > 0 else credit
            print(f'       → Account {acc_code} ({acc_name}): {line_desc} - {line_type} ${amount:.2f}')
        
        print(f'     Line Totals: Debit ${line_debit_total:.2f}, Credit ${line_credit_total:.2f}')
        
        # Verify balance
        entry_balanced = abs(total_debit - total_credit) < 0.01
        line_balanced = abs(line_debit_total - line_credit_total) < 0.01
        totals_match = abs(total_debit - line_debit_total) < 0.01 and abs(total_credit - line_credit_total) < 0.01
        
        print(f'     Entry Balance: {"✅ BALANCED" if entry_balanced else "❌ UNBALANCED"}')
        print(f'     Line Balance: {"✅ BALANCED" if line_balanced else "❌ UNBALANCED"}')
        print(f'     Totals Match: {"✅ MATCH" if totals_match else "❌ MISMATCH"}')
        print()
    
    # 6. Overall system health assessment
    print('6. OVERALL SYSTEM HEALTH ASSESSMENT:')
    overall_score = 0
    max_score = 0
    
    # Balance compliance
    max_score += 1
    if total_entries > 0 and (balanced_entries/total_entries) >= 0.95:
        overall_score += 1
        print('   ✅ Balance Compliance: EXCELLENT (≥95%)')
    elif total_entries > 0 and (balanced_entries/total_entries) >= 0.90:
        print('   ⚠️  Balance Compliance: GOOD (≥90%)')
    else:
        print('   ❌ Balance Compliance: NEEDS IMPROVEMENT (<90%)')
    
    # Line structure compliance
    max_score += 1
    if len(lines) > 0 and (valid_lines/len(lines)) >= 0.95:
        overall_score += 1
        print('   ✅ Line Structure: EXCELLENT (≥95%)')
    elif len(lines) > 0 and (valid_lines/len(lines)) >= 0.90:
        print('   ⚠️  Line Structure: GOOD (≥90%)')
    else:
        print('   ❌ Line Structure: NEEDS IMPROVEMENT (<90%)')
    
    # Total matching compliance
    max_score += 1
    if len(entry_line_totals) > 0 and (matching_totals/len(entry_line_totals)) >= 0.95:
        overall_score += 1
        print('   ✅ Total Matching: EXCELLENT (≥95%)')
    elif len(entry_line_totals) > 0 and (matching_totals/len(entry_line_totals)) >= 0.90:
        print('   ⚠️  Total Matching: GOOD (≥90%)')
    else:
        print('   ❌ Total Matching: NEEDS IMPROVEMENT (<90%)')
    
    # Orphaned lines check
    max_score += 1
    if orphaned_count == 0:
        overall_score += 1
        print('   ✅ Data Integrity: EXCELLENT (No orphaned lines)')
    else:
        print('   ❌ Data Integrity: NEEDS IMPROVEMENT (Orphaned lines found)')
    
    print()
    print(f'OVERALL DOUBLE-ENTRY COMPLIANCE SCORE: {overall_score}/{max_score} ({(overall_score/max_score*100):.1f}%)')
    
    if overall_score == max_score:
        print('🎉 EXCELLENT: System fully complies with double-entry accounting principles!')
    elif overall_score >= max_score * 0.75:
        print('✅ GOOD: System mostly complies with double-entry accounting principles.')
    else:
        print('❌ NEEDS IMPROVEMENT: System has significant double-entry compliance issues.')
    
    conn.close()

if __name__ == '__main__':
    comprehensive_double_entry_audit()
