import sys
import os
from collections import defaultdict

# Add project root to sys.path
sys.path.append(os.getcwd())

from backend.app.database import SessionLocal
from backend.app.models.user import QuoteSnapshot
from backend.app.symbol_meta import get_sector_for_symbol
from sqlalchemy import func, distinct

def comprehensive_sector_check():
    print("=" * 80)
    print("COMPREHENSIVE SECTOR VERIFICATION")
    print("=" * 80)
    
    db = SessionLocal()
    try:
        # 1. Get overall statistics
        total_records = db.query(QuoteSnapshot).count()
        total_symbols = db.query(func.count(distinct(QuoteSnapshot.symbol))).scalar()
        records_with_sector = db.query(QuoteSnapshot).filter(QuoteSnapshot.sector != None).filter(QuoteSnapshot.sector != '').count()
        records_without_sector = db.query(QuoteSnapshot).filter((QuoteSnapshot.sector == None) | (QuoteSnapshot.sector == '')).count()
        
        print(f"\nOVERALL STATISTICS:")
        print(f"   Total Records: {total_records}")
        print(f"   Unique Symbols: {total_symbols}")
        print(f"   Records WITH sector: {records_with_sector} ({records_with_sector/total_records*100:.1f}%)")
        print(f"   Records WITHOUT sector: {records_without_sector} ({records_without_sector/total_records*100:.1f}%)")
        
        # 2. Get unique symbols and check which can be resolved
        print(f"\nCHECKING SYMBOL RESOLUTION:")
        print("-" * 80)
        
        all_symbols = db.query(distinct(QuoteSnapshot.symbol)).all()
        all_symbols = [s[0] for s in all_symbols]
        
        resolvable = 0
        unresolvable = 0
        resolution_report = []
        
        for symbol in all_symbols:
            sector = get_sector_for_symbol(symbol)
            if sector:
                resolvable += 1
                resolution_report.append((symbol, sector, "[OK] RESOLVABLE"))
            else:
                unresolvable += 1
                resolution_report.append((symbol, None, "[MISSING] NOT FOUND"))
        
        print(f"   Resolvable Symbols: {resolvable}/{len(all_symbols)} ({resolvable/len(all_symbols)*100:.1f}%)")
        print(f"   Unresolvable Symbols: {unresolvable}/{len(all_symbols)} ({unresolvable/len(all_symbols)*100:.1f}%)")
        
        # 3. Show detailed breakdown
        print(f"\nDETAILED SYMBOL BREAKDOWN:")
        print("-" * 80)
        print(f"{'Symbol':<20} {'Sector':<40} {'Status':<20}")
        print("-" * 80)
        
        for symbol, sector, status in sorted(resolution_report):
            sector_display = sector if sector else "N/A"
            print(f"{symbol:<20} {sector_display:<40} {status:<20}")
        
        # 4. Check for symbols with NULL sectors in DB but are resolvable
        print(f"\nSYMBOLS WITH NULL SECTORS (RESOLVABLE):")
        print("-" * 80)
        
        null_sector_symbols = db.query(distinct(QuoteSnapshot.symbol)).filter(
            (QuoteSnapshot.sector == None) | (QuoteSnapshot.sector == '')
        ).all()
        null_sector_symbols = [s[0] for s in null_sector_symbols]
        
        fixable_count = 0
        for symbol in null_sector_symbols:
            sector = get_sector_for_symbol(symbol)
            if sector:
                count = db.query(QuoteSnapshot).filter(
                    QuoteSnapshot.symbol == symbol,
                    (QuoteSnapshot.sector == None) | (QuoteSnapshot.sector == '')
                ).count()
                print(f"   {symbol:<20} -> {sector:<40} ({count} records)")
                fixable_count += 1
        
        if fixable_count == 0:
            print("   [OK] No fixable NULL sectors found!")
        else:
            print(f"\n   Total fixable symbols: {fixable_count}")
        
        # 5. Summary
        print(f"\n" + "=" * 80)
        print("SUMMARY:")
        print("=" * 80)
        if records_without_sector == 0:
            print("[SUCCESS] All records have sectors populated!")
        elif fixable_count > 0:
            print(f"[WARNING] {fixable_count} symbols have NULL sectors but CAN be resolved.")
            print(f"   These are likely old records from before the fix.")
            print(f"   New ingestion will populate sectors correctly.")
        else:
            print(f"[INFO] Some symbols don't have sector data in nse_working_stocks.json")
            print(f"   This is expected for symbols not in the metadata file.")
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    comprehensive_sector_check()
