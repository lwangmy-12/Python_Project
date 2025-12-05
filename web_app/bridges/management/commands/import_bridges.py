import sqlite3
import os
from django.core.management.base import BaseCommand
from bridges.models import Bridge
from django.conf import settings

class Command(BaseCommand):
    help = 'Import bridges from SQLite database'

    def handle(self, *args, **options):
       
        #check 
        db_path = '/data/pa_bridges_clean.db'
        if not os.path.exists(db_path):
            db_path = os.path.join(settings.BASE_DIR.parent, 'data', 'pa_bridges_clean.db')
        
        if not os.path.exists(db_path):
            self.stdout.write(self.style.ERROR(f'Database not found at {db_path}'))

            self.stdout.write(f'Current dir: {os.getcwd()}')
            if os.path.exists('/data'):
                self.stdout.write(f'/data contents: {os.listdir("/data")}')
            return

        self.stdout.write(f'Connecting to {db_path}...')
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM pa_bridges_clean")
        rows = cursor.fetchall()

        self.stdout.write(f'Found {len(rows)} rows. Importing...')

        bridges_to_create = []
        count = 0
        

        Bridge.objects.all().delete()

        for row in rows:
            bridge = Bridge(
                state_code=str(row['STATE_CODE_001']),
                county_code=str(row['COUNTY_CODE_003']),
                structure_number=str(row['STRUCTURE_NUMBER_008']),
                location=row['LOCATION_009'],
                features_desc=row['FEATURES_DESC_006A'],
                facility_carried=row['FACILITY_CARRIED_007'],
                latitude=row['LAT_016'],
                longitude=row['LONG_017'],
                year_built=row['YEAR_BUILT_027'],
                structure_kind=row['STRUCTURE_KIND_043A'],
                structure_type=row['STRUCTURE_TYPE_043B'],
                deck_structure_type=row['DECK_STRUCTURE_TYPE_107'],
                main_unit_spans=row['MAIN_UNIT_SPANS_045'],
                max_span_len_mt=row['MAX_SPAN_LEN_MT_048'],
                structure_len_mt=row['STRUCTURE_LEN_MT_049'],
                adt=row['ADT_029'],
                year_adt=row['YEAR_ADT_030'],
                deck_cond=row['DECK_COND_058'],
                superstructure_cond=row['SUPERSTRUCTURE_COND_059'],
                substructure_cond=row['SUBSTRUCTURE_COND_060'],
                operating_rating=row['OPERATING_RATING_064'],
                inventory_rating=row['INVENTORY_RATING_066'],
                structural_eval=row['STRUCTURAL_EVAL_067'],
                data_year=row['DATA_YEAR']
            )
            bridges_to_create.append(bridge)
            count += 1

            if len(bridges_to_create) >= 1000:
                Bridge.objects.bulk_create(bridges_to_create)
                bridges_to_create = []
                self.stdout.write(f'Imported {count} bridges...')

        if bridges_to_create:
            Bridge.objects.bulk_create(bridges_to_create)
        
        conn.close()
        self.stdout.write(self.style.SUCCESS(f'Successfully imported {count} bridges'))
