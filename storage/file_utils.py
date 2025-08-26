import os
from datetime import datetime

def create_results_folder():
    current_date = datetime.now()
    folder_name = current_date.strftime('%B_%d_%Y')
    results_folder = os.path.join('job_search_results', folder_name)
    os.makedirs(results_folder, exist_ok=True)
    return results_folder
