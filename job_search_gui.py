

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import job_search  # Import the original job search logic
import pandas as pd
from datetime import datetime
import os
import json
import requests
import sys
import webbrowser
import docx

def extract_text_from_docx(docx_path):
    """Extracts text from a DOCX file."""
    try:
        doc = docx.Document(docx_path)
        return "\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        print(f"Error reading DOCX file: {e}")
        return None

class JobSearchGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AI-Powered Job Search")
        self.geometry("800x600")

        # --- Style ---
        style = ttk.Style(self)
        style.theme_use("clam")

        # --- Main Frame ---
        main_frame = ttk.Frame(self, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # --- Notebook (Wizard) ---
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)

        # --- Create Frames for each step ---
        self.config_frame = ttk.Frame(self.notebook, padding="10")
        self.skills_frame = ttk.Frame(self.notebook, padding="10")
        self.prefs_frame = ttk.Frame(self.notebook, padding="10")
        self.results_frame = ttk.Frame(self.notebook, padding="10")
        self.cv_preview_frame = ttk.Frame(self.notebook, padding="10")

        self.notebook.add(self.config_frame, text="Configuration")
        self.notebook.add(self.cv_preview_frame, text="CV Preview")
        self.notebook.add(self.skills_frame, text="Skills")
        self.notebook.add(self.prefs_frame, text="Preferences")
        self.notebook.add(self.results_frame, text="Results")

        # --- Populate each frame ---
        self.create_config_widgets()
        self.create_cv_preview_widgets()
        self.create_skills_widgets()
        self.create_prefs_widgets()
        self.create_results_widgets()

        # --- Navigation Buttons ---
        nav_frame = ttk.Frame(main_frame, padding="10")
        nav_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))
        self.back_button = ttk.Button(nav_frame, text="Back", command=self.prev_step, state="disabled")
        self.back_button.pack(side="left")
        self.next_button = ttk.Button(nav_frame, text="Next", command=self.next_step)
        self.next_button.pack(side="right")

        self.all_jobs = []
        self.load_config()
        self.check_for_updates()

    def create_config_widgets(self):
        input_frame = ttk.LabelFrame(self.config_frame, text="Configuration", padding="10")
        input_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E))
        input_frame.columnconfigure(1, weight=1)

        # API Key
        ttk.Label(input_frame, text="SerpAPI Key:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.api_key_entry = ttk.Entry(input_frame, width=60)
        self.api_key_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2)
        
        serp_api_link = ttk.Label(input_frame, text="Get your SerpAPI key here", foreground="blue", cursor="hand2")
        serp_api_link.grid(row=0, column=2, sticky=tk.W, padx=5)
        serp_api_link.bind("<Button-1>", lambda e: webbrowser.open_new("https://serpapi.com/"))

        # CV Path
        ttk.Label(input_frame, text="CV Path:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.cv_path_entry = ttk.Entry(input_frame, width=60)
        self.cv_path_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2)
        self.browse_button = ttk.Button(input_frame, text="Browse", command=self.browse_cv)
        self.browse_button.grid(row=1, column=2, sticky=tk.W, padx=5)

        # Output Folder
        ttk.Label(input_frame, text="Output Folder:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.output_folder_entry = ttk.Entry(input_frame, width=60)
        self.output_folder_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=2)
        self.browse_output_button = ttk.Button(input_frame, text="Browse", command=self.browse_output_folder)
        self.browse_output_button.grid(row=2, column=2, sticky=tk.W, padx=5)

        # Output Format
        ttk.Label(input_frame, text="Output Format:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.output_format_combobox = ttk.Combobox(input_frame, values=["Excel", "CSV"])
        self.output_format_combobox.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=2)
        self.output_format_combobox.set("Excel")

    def create_cv_preview_widgets(self):
        cv_preview_label = ttk.Label(self.cv_preview_frame, text="CV Preview:")
        cv_preview_label.grid(row=0, column=0, sticky=tk.W, pady=2)

        self.cv_preview_text = tk.Text(self.cv_preview_frame, height=25, width=90)
        self.cv_preview_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    def create_skills_widgets(self):
        skills_label = ttk.Label(self.skills_frame, text="Extracted Skills (edit if necessary):")
        skills_label.grid(row=0, column=0, sticky=tk.W, pady=2)

        self.skills_text = tk.Text(self.skills_frame, height=20, width=90)
        self.skills_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        extract_button = ttk.Button(self.skills_frame, text="Extract Skills", command=self.extract_skills)
        extract_button.grid(row=2, column=0, pady=10)

    def create_prefs_widgets(self):
        prefs_frame = ttk.LabelFrame(self.prefs_frame, text="Preferences", padding="10")
        prefs_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E))
        prefs_frame.columnconfigure(1, weight=1)

        # Job Title
        ttk.Label(prefs_frame, text="Your Job Title:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.job_title_entry = ttk.Entry(prefs_frame, width=60)
        self.job_title_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2)

        # Location
        ttk.Label(prefs_frame, text="Location:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.location_combobox = ttk.Combobox(prefs_frame, values=job_search.COUNTRIES)
        self.location_combobox.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2)

        # Skills Section
        ttk.Label(prefs_frame, text="Skills Section Name:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.skills_section_entry = ttk.Entry(prefs_frame, width=60)
        self.skills_section_entry.insert(0, "Skills")
        self.skills_section_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=2)

        # Priorities
        priorities_frame = ttk.LabelFrame(self.prefs_frame, text="Priorities", padding="10")
        priorities_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=10, pady=10)

        self.visa_priority_var = tk.BooleanVar(value=True)
        self.remote_priority_var = tk.BooleanVar()

        ttk.Checkbutton(priorities_frame, text="Visa Sponsorship", variable=self.visa_priority_var).grid(row=0, column=0, sticky=tk.W)
        ttk.Checkbutton(priorities_frame, text="Remote Work", variable=self.remote_priority_var).grid(row=0, column=1, sticky=tk.W)

    def create_results_widgets(self):
        results_frame = ttk.LabelFrame(self.results_frame, text="Log and Results", padding="10")
        results_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        self.results_frame.rowconfigure(0, weight=1)
        self.results_frame.columnconfigure(0, weight=1)

        self.results_text = tk.Text(results_frame, height=20, width=90)
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.save_button = ttk.Button(self.results_frame, text="Save Results", command=self.save_results, state="disabled")
        self.save_button.grid(row=1, column=0, pady=10)

    def next_step(self):
        current_tab_index = self.notebook.index(self.notebook.select())
        
        if current_tab_index == 0: # Configuration
            self.save_config()
            self.notebook.select(current_tab_index + 1)
        elif current_tab_index == 1: # CV Preview
            self.notebook.select(current_tab_index + 1)
        elif current_tab_index == 2: # Skills
            self.notebook.select(current_tab_index + 1)
        elif current_tab_index == 3: # Preferences
            self.run_search()
            self.notebook.select(current_tab_index + 1)

        self.update_buttons()

    def prev_step(self):
        current_tab = self.notebook.index(self.notebook.select())
        if current_tab > 0:
            self.notebook.select(current_tab - 1)
        self.update_buttons()
        
    def update_buttons(self):
        current_tab = self.notebook.index(self.notebook.select())
        if current_tab == 0:
            self.back_button.config(state="disabled")
        else:
            self.back_button.config(state="normal")

        if current_tab == self.notebook.index("end") - 1:
            self.next_button.config(text="Finish", command=self.close_app)
        elif current_tab == 3:
            self.next_button.config(text="Search")
        else:
            self.next_button.config(text="Next")

    def close_app(self):
        self.destroy()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                self.api_key_entry.insert(0, config.get("api_key", ""))
                self.cv_path_entry.insert(0, config.get("cv_path", ""))
                self.job_title_entry.insert(0, config.get("job_title", ""))
                self.location_combobox.set(config.get("location", ""))
                self.output_folder_entry.insert(0, config.get("output_folder", ""))
                self.output_format_combobox.set(config.get("output_format", "Excel"))

    def save_config(self):
        config = {
            "api_key": self.api_key_entry.get().strip(),
            "cv_path": self.cv_path_entry.get().strip(),
            "job_title": self.job_title_entry.get().strip(),
            "location": self.location_combobox.get().strip(),
            "output_folder": self.output_folder_entry.get().strip(),
            "output_format": self.output_format_combobox.get().strip(),
        }
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f)

    def browse_cv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CV Files", "*.pdf *.doc *.docx")])
        if file_path:
            self.cv_path_entry.delete(0, tk.END)
            self.cv_path_entry.insert(0, file_path)
            self.preview_cv()

    def browse_output_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.output_folder_entry.delete(0, tk.END)
            self.output_folder_entry.insert(0, folder_path)

    def preview_cv(self):
        cv_path = self.cv_path_entry.get().strip()
        if not cv_path or not os.path.exists(cv_path):
            messagebox.showerror("Error", "Please provide a valid CV path.")
            return

        if cv_path.endswith(".pdf"):
            cv_text = job_search.extract_text_from_pdf(cv_path)
        elif cv_path.endswith(".docx"):
            cv_text = extract_text_from_docx(cv_path)
        else:
            messagebox.showerror("Error", "Unsupported file format. Please select a PDF or DOCX file.")
            return

        if not cv_text:
            self.cv_preview_text.delete(1.0, tk.END)
            self.cv_preview_text.insert(tk.END, "Failed to extract text from CV.")
            return

        self.cv_preview_text.delete(1.0, tk.END)
        self.cv_preview_text.insert(tk.END, cv_text)

    def extract_skills(self):
        cv_path = self.cv_path_entry.get().strip()
        if not cv_path or not os.path.exists(cv_path):
            messagebox.showerror("Error", "Please provide a valid CV path.")
            return

        skills_section_name = self.skills_section_entry.get().strip()
        
        if cv_path.endswith(".pdf"):
            cv_text = job_search.extract_text_from_pdf(cv_path)
        elif cv_path.endswith(".docx"):
            cv_text = extract_text_from_docx(cv_path)
        else:
            messagebox.showerror("Error", "Unsupported file format. Please select a PDF or DOCX file.")
            return

        if not cv_text:
            messagebox.showerror("Error", "Failed to extract text from CV.")
            return

        skills = job_search.extract_skills_from_specified_section(cv_text, skills_section_name)
        if not skills:
            messagebox.showinfo("No Skills Found", "No skills were found in the specified section of your CV.")
            return
            
        self.skills_text.delete(1.0, tk.END)
        self.skills_text.insert(tk.END, "\n".join(skills))

    def run_search(self):
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, "Starting job search...\n")
        self.update_idletasks()

        prioritized_skills = self.skills_text.get(1.0, tk.END).strip().split("\n")

        api_key = self.api_key_entry.get().strip()
        user_job_title = self.job_title_entry.get().strip()
        location = self.location_combobox.get().strip()

        try:
            preferences = {
                "visa_priority": self.visa_priority_var.get(),
                "remote_only": self.remote_priority_var.get(),
                "target_countries": [location] if location else [],
                "skill_focus": prioritized_skills
            }

            search_queries = job_search.search_jobs_with_visa_focus(prioritized_skills, preferences)
            if user_job_title:
                search_queries.insert(0, user_job_title)

            seen_jobs = set()

            for query in search_queries:
                self.results_text.insert(tk.END, f"Searching for: {query}\n")
                self.update_idletasks()
                jobs_raw = job_search.search_jobs_on_serpapi(query, api_key, location_filter=location)

                for job in jobs_raw:
                    job_id = f"{job.get('title', '')}-{job.get('company_name', '')}-{job.get('location', '')}"
                    if job_id in seen_jobs:
                        continue
                    seen_jobs.add(job_id)

                    score, score_reasons = job_search.calculate_job_score(job, prioritized_skills, preferences)
                    if score > 0:
                        formatted_job = job_search.format_job_data(job, query, score, score_reasons)
                        self.all_jobs.append(formatted_job)

            if not self.all_jobs:
                self.results_text.insert(tk.END, "No matching jobs found.\n")
                return

            # Display results
            self.results_text.insert(tk.END, "\n--- Top Job Matches ---\n")
            for job in sorted(self.all_jobs, key=lambda x: x['Relevance Score'], reverse=True)[:5]:
                self.results_text.insert(tk.END, f"Title: {job['Job Title']}\n")
                self.results_text.insert(tk.END, f"Company: {job['Company']}\n")
                self.results_text.insert(tk.END, f"Location: {job['Location']}\n")
                self.results_text.insert(tk.END, f"Score: {job['Relevance Score']} ({job['Score Reasons']})\n\n")

            self.save_button.config(state="normal")
            messagebox.showinfo("Success", f"Job search complete! Found {len(self.all_jobs)} relevant jobs.")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
            self.results_text.insert(tk.END, f"An error occurred: {e}\n")

    def save_results(self):
        if not self.all_jobs:
            messagebox.showwarning("No Results", "There are no results to save.")
            return

        output_folder = self.output_folder_entry.get().strip()
        if not output_folder:
            output_folder = job_search.create_results_folder()
            
        output_format = self.output_format_combobox.get().strip()
        
        if output_format == "Excel":
            output_filename = f"job_search_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        else:
            output_filename = f"job_search_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
        output_path = os.path.join(output_folder, output_filename)

        try:
            df = pd.DataFrame(self.all_jobs)
            df = df.sort_values(['Relevance Score', 'Posting Date'], ascending=[False, False])
            
            if output_format == "Excel":
                df.to_excel(output_path, index=False, engine='openpyxl')
            else:
                df.to_csv(output_path, index=False)

            messagebox.showinfo("Save Successful", f"Results saved to {output_path}")
        except Exception as e:
            messagebox.showerror("Save Error", f"An error occurred while saving: {e}")

    def check_for_updates(self):
        try:
            response = requests.get(VERSION_URL)
            if response.status_code == 200:
                latest_version_info = response.json()
                latest_version = latest_version_info.get("version")
                download_url = latest_version_info.get("url")

                if latest_version and download_url and latest_version > VERSION:
                    if messagebox.askyesno("Update Available", f"A new version ({latest_version}) is available. Do you want to update?"):
                        # Download the new executable
                        response = requests.get(download_url)
                        with open("job_search_gui_new.exe", "wb") as f:
                            f.write(response.content)

                        # Replace the current executable with the new one
                        os.rename("job_search_gui_new.exe", sys.executable)

                        # Restart the application
                        os.execl(sys.executable, sys.executable, *sys.argv)
        except Exception as e:
            print(f"Failed to check for updates: {e}")


if __name__ == "__main__":
    app = JobSearchGUI()
    app.mainloop()
