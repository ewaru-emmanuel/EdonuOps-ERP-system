import sqlite3
from datetime import datetime

def analyze_entry_sources():
    """Analyze journal entries to identify manual vs code-generated entries"""
    
    conn = sqlite3.connect('edonuops.db')
    cursor = conn.cursor()
    
    print('=' * 80)
    print('DETAILED JOURNAL ENTRY SOURCE ANALYSIS')
    print('=' * 80)
    print(f'Analysis Date: {datetime.now()}')
    print()
    
    # Get all journal entries with detailed info
    cursor.execute('''
        SELECT je.id, je.reference, je.description, je.total_debit, je.total_credit, 
               je.status, je.doc_date, je.created_at, je.user_id,
               COUNT(jl.id) as line_count,
               COALESCE(SUM(jl.debit_amount), 0) as line_debits,
               COALESCE(SUM(jl.credit_amount), 0) as line_credits
        FROM journal_entries je
        LEFT JOIN journal_lines jl ON je.id = jl.journal_entry_id
        GROUP BY je.id, je.reference, je.description, je.total_debit, je.total_credit, 
                 je.status, je.doc_date, je.created_at, je.user_id
        ORDER BY je.id
    ''')
    entries = cursor.fetchall()
    
    print('1. ENTRY-BY-ENTRY ANALYSIS:')
    print('-' * 80)
    
    code_generated = 0
    manual_entries = 0
    problematic_entries = 0
    
    for entry in entries:
        entry_id, ref, desc, entry_debit, entry_credit, status, doc_date, created_at, user_id, line_count, line_debit, line_credit = entry
        
        # Determine if entry is code-generated or manual
        is_code_generated = False
        entry_source = "UNKNOWN"
        
        # Check reference patterns
        if ref.startswith('TXN-') or ref.startswith('JE-') or ref.startswith('TEST-'):
            is_code_generated = True
            entry_source = "CODE-GENERATED"
        elif ref.startswith('BACKDATED-') or ref.startswith('FUTURE-') or ref.startswith('MC-'):
            is_code_generated = True
            entry_source = "CODE-GENERATED (TEST)"
        else:
            entry_source = "MANUAL/UNKNOWN"
        
        # Check for total mismatch
        entry_balanced = abs(entry_debit - entry_credit) < 0.01
        line_balanced = abs(line_debit - line_credit) < 0.01
        totals_match = abs(entry_debit - line_debit) < 0.01 and abs(entry_credit - line_credit) < 0.01
        
        has_issues = not entry_balanced or not line_balanced or not totals_match
        
        if has_issues:
            problematic_entries += 1
        
        if is_code_generated:
            code_generated += 1
        else:
            manual_entries += 1
        
        # Print detailed info for problematic entries
        if has_issues:
            print(f'❌ PROBLEMATIC ENTRY {entry_id}:')
            print(f'   Reference: {ref}')
            print(f'   Description: {desc}')
            print(f'   Source: {entry_source}')
            print(f'   Status: {status}')
            print(f'   Date: {doc_date}')
            print(f'   User ID: {user_id}')
            print(f'   Created: {created_at}')
            print(f'   Entry Totals: Debit ${entry_debit:.2f}, Credit ${entry_credit:.2f}')
            print(f'   Line Totals: Debit ${line_debit:.2f}, Credit ${line_credit:.2f}')
            print(f'   Line Count: {line_count}')
            print(f'   Entry Balanced: {"✅" if entry_balanced else "❌"}')
            print(f'   Line Balanced: {"✅" if line_balanced else "❌"}')
            print(f'   Totals Match: {"✅" if totals_match else "❌"}')
            
            # Get journal lines for this entry
            cursor.execute('''
                SELECT jl.account_id, a.code, a.name, jl.description, 
                       jl.debit_amount, jl.credit_amount
                FROM journal_lines jl
                LEFT JOIN accounts a ON jl.account_id = a.id
                WHERE jl.journal_entry_id = ?
                ORDER BY jl.id
            ''', (entry_id,))
            lines = cursor.fetchall()
            
            print(f'   Journal Lines:')
            for line in lines:
                acc_id, acc_code, acc_name, line_desc, debit, credit = line
                line_type = 'DEBIT' if debit > 0 else 'CREDIT'
                amount = debit if debit > 0 else credit
                print(f'     → Account {acc_code} ({acc_name}): {line_desc} - {line_type} ${amount:.2f}')
            print()
    
    print('2. SUMMARY STATISTICS:')
    print('-' * 80)
    print(f'Total Entries: {len(entries)}')
    print(f'Code-Generated Entries: {code_generated}')
    print(f'Manual/Unknown Entries: {manual_entries}')
    print(f'Problematic Entries: {problematic_entries}')
    print()
    
    # Analyze by source
    print('3. ANALYSIS BY SOURCE:')
    print('-' * 80)
    
    cursor.execute('''
        SELECT 
            CASE 
                WHEN reference LIKE 'TXN-%' OR reference LIKE 'JE-%' OR reference LIKE 'TEST-%' 
                     OR reference LIKE 'BACKDATED-%' OR reference LIKE 'FUTURE-%' OR reference LIKE 'MC-%'
                THEN 'CODE-GENERATED'
                ELSE 'MANUAL/UNKNOWN'
            END as source_type,
            COUNT(*) as count,
            SUM(CASE WHEN ABS(total_debit - total_credit) < 0.01 THEN 1 ELSE 0 END) as balanced_entries,
            SUM(CASE WHEN ABS(total_debit - total_credit) >= 0.01 THEN 1 ELSE 0 END) as unbalanced_entries
        FROM journal_entries
        GROUP BY source_type
    ''')
    source_analysis = cursor.fetchall()
    
    for source_type, count, balanced, unbalanced in source_analysis:
        balance_rate = (balanced / count * 100) if count > 0 else 0
        print(f'{source_type}:')
        print(f'  Total: {count}')
        print(f'  Balanced: {balanced} ({(balanced/count*100):.1f}%)')
        print(f'  Unbalanced: {unbalanced} ({(unbalanced/count*100):.1f}%)')
        print()
    
    # Check for entries with zero totals but non-zero lines
    print('4. ENTRIES WITH ZERO TOTALS BUT NON-ZERO LINES:')
    print('-' * 80)
    
    cursor.execute('''
        SELECT je.id, je.reference, je.description, je.total_debit, je.total_credit,
               COALESCE(SUM(jl.debit_amount), 0) as line_debits,
               COALESCE(SUM(jl.credit_amount), 0) as line_credits
        FROM journal_entries je
        LEFT JOIN journal_lines jl ON je.id = jl.journal_entry_id
        WHERE je.total_debit = 0 AND je.total_credit = 0
        GROUP BY je.id, je.reference, je.description, je.total_debit, je.total_credit
        HAVING line_debits > 0 OR line_credits > 0
        ORDER BY je.id
    ''')
    zero_total_entries = cursor.fetchall()
    
    if zero_total_entries:
        print(f'Found {len(zero_total_entries)} entries with zero totals but non-zero lines:')
        for entry in zero_total_entries:
            entry_id, ref, desc, entry_debit, entry_credit, line_debit, line_credit = entry
            print(f'  Entry {entry_id}: {ref} - {desc}')
            print(f'    Entry Totals: Debit ${entry_debit:.2f}, Credit ${entry_credit:.2f}')
            print(f'    Line Totals: Debit ${line_debit:.2f}, Credit ${line_credit:.2f}')
    else:
        print('✅ No entries found with zero totals but non-zero lines')
    
    print()
    
    # Check for entries with non-zero totals but zero lines
    print('5. ENTRIES WITH NON-ZERO TOTALS BUT ZERO LINES:')
    print('-' * 80)
    
    cursor.execute('''
        SELECT je.id, je.reference, je.description, je.total_debit, je.total_credit,
               COALESCE(SUM(jl.debit_amount), 0) as line_debits,
               COALESCE(SUM(jl.credit_amount), 0) as line_credits
        FROM journal_entries je
        LEFT JOIN journal_lines jl ON je.id = jl.journal_entry_id
        WHERE (je.total_debit > 0 OR je.total_credit > 0)
        GROUP BY je.id, je.reference, je.description, je.total_debit, je.total_credit
        HAVING line_debits = 0 AND line_credits = 0
        ORDER BY je.id
    ''')
    non_zero_total_entries = cursor.fetchall()
    
    if non_zero_total_entries:
        print(f'Found {len(non_zero_total_entries)} entries with non-zero totals but zero lines:')
        for entry in non_zero_total_entries:
            entry_id, ref, desc, entry_debit, entry_credit, line_debit, line_credit = entry
            print(f'  Entry {entry_id}: {ref} - {desc}')
            print(f'    Entry Totals: Debit ${entry_debit:.2f}, Credit ${entry_credit:.2f}')
            print(f'    Line Totals: Debit ${line_debit:.2f}, Credit ${line_credit:.2f}')
    else:
        print('✅ No entries found with non-zero totals but zero lines')
    
    conn.close()

if __name__ == '__main__':
    analyze_entry_sources()
