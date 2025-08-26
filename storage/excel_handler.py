import pandas as pd
import os
from datetime import datetime

class ExcelHandler:
    def save_results(self, jobs_data, results_folder):
        df = pd.DataFrame(jobs_data)
        output_filename = f"job_search_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        output_path = os.path.join(results_folder, output_filename)
        try:
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Job Search Results', index=False)
                self._add_status_dropdown(writer, 'Job Search Results', len(df))
            return output_path
        except Exception as e:
            print(f"Excel save error: {e}")
            fallback_path = os.path.join(results_folder, output_filename)
            df.to_excel(fallback_path, index=False)
            return fallback_path

    def _add_status_dropdown(self, writer, sheet_name, num_rows):
        try:
            from openpyxl.worksheet.datavalidation import DataValidation
            worksheet = writer.sheets[sheet_name]
            status_options = ["Not Applied", "Applied", "Interview Scheduled", "Rejected", "Offer Received"]
            dv = DataValidation(type="list", formula1=f'"{",".join(status_options)}"', showDropDown=True)
            dv.add(f'L2:L{num_rows + 1}')
            worksheet.add_data_validation(dv)
        except Exception as e:
            print(f"Dropdown validation error: {e}")
