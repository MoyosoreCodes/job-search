
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import job_search  # Import the original job search logic
import pandas as pd
from datetime import datetime
import os
import json
import requests
import sys

CONFIG_FILE = "config.json"
VERSION = "1.0.0"
VERSION_URL = "https://gist.githubusercontent.com/Moyo-x/7144732583323615545bde54ed69638a/raw/version.json"

CONFIG_FILE = "config.json"

class JobSearchGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AI-Powered Job Search")
        self.geometry("800x600")

        # --- Main Frame ---
        main_frame = ttk.Frame(self, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # --- Input Frame ---
        input_frame = ttk.LabelFrame(main_frame, text="Configuration", padding="10")
        input_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E))
        input_frame.columnconfigure(1, weight=1)

        # API Key
        ttk.Label(input_frame, text="SerpAPI Key:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.api_key_entry = ttk.Entry(input_frame, width=60)
        self.api_key_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2)

        # CV Path
        ttk.Label(input_frame, text="CV Path:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.cv_path_entry = ttk.Entry(input_frame, width=60)
        self.cv_path_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2)
        self.browse_button = ttk.Button(input_frame, text="Browse", command=self.browse_cv)
        self.browse_button.grid(row=1, column=2, sticky=tk.W, padx=5)

        # Skills Section
        ttk.Label(input_frame, text="Skills Section Name:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.skills_section_entry = ttk.Entry(input_frame, width=60)
        self.skills_section_entry.insert(0, "Skills")
        self.skills_section_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=2)

        # Job Title
        ttk.Label(input_frame, text="Your Job Title:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.job_title_entry = ttk.Entry(input_frame, width=60)
        self.job_title_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=2)

        # Location
        ttk.Label(input_frame, text="Location:").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.location_combobox = ttk.Combobox(input_frame, values=job_search.COUNTRIES)
        self.location_combobox.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=2)

        # --- Priorities Frame ---
        priorities_frame = ttk.LabelFrame(main_frame, text="Priorities", padding="10")
        priorities_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=10, pady=10)

        self.visa_priority_var = tk.BooleanVar(value=True)
        self.remote_priority_var = tk.BooleanVar()

        ttk.Checkbutton(priorities_frame, text="Visa Sponsorship", variable=self.visa_priority_var).grid(row=0, column=0, sticky=tk.W)
        ttk.Checkbutton(priorities_frame, text="Remote Work", variable=self.remote_priority_var).grid(row=0, column=1, sticky=tk.W)

        # --- Control Frame ---
        control_frame = ttk.Frame(main_frame, padding="10")
        control_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E))
        control_frame.columnconfigure(0, weight=1)

        self.search_button = ttk.Button(control_frame, text="Search Jobs", command=self.run_search)
        self.search_button.grid(row=0, column=0, padx=5)

        self.save_button = ttk.Button(control_frame, text="Save Results", command=self.save_results, state="disabled")
        self.save_button.grid(row=0, column=1, padx=5)

        self.preview_cv_button = ttk.Button(control_frame, text="Preview CV", command=self.preview_cv, state="disabled")
        self.preview_cv_button.grid(row=0, column=2, padx=5)

        self.preview_skills_button = ttk.Button(control_frame, text="Preview Skills", command=self.preview_skills, state="disabled")
        self.preview_skills_button.grid(row=0, column=3, padx=5)

        # --- Results/Log Frame ---
        results_frame = ttk.LabelFrame(main_frame, text="Log and Results", padding="10")
        results_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)

        self.results_text = tk.Text(results_frame, height=20, width=90)
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # --- Status Bar ---
        self.status_bar = ttk.Label(self, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.grid(row=1, column=0, sticky=(tk.W, tk.E))

        self.all_jobs = []
        self.load_config()
        self.check_for_updates()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                self.api_key_entry.insert(0, config.get("api_key", ""))
                self.cv_path_entry.insert(0, config.get("cv_path", ""))
                self.job_title_entry.insert(0, config.get("job_title", ""))
                self.location_combobox.set(config.get("location", ""))
                if self.cv_path_entry.get():
                    self.preview_cv_button.config(state="normal")
                    self.preview_skills_button.config(state="normal")

    def save_config(self):
        config = {
            "api_key": self.api_key_entry.get().strip(),
            "cv_path": self.cv_path_entry.get().strip(),
            "job_title": self.job_title_entry.get().strip(),
            "location": self.location_combobox.get().strip(),
        }
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f)

    def open_skills_window(self, skills):
        skills_window = tk.Toplevel(self)
        skills_window.title("Select Skills to Prioritize")

        skills_vars = {}
        for i, skill in enumerate(skills):
            var = tk.BooleanVar(value=True)
            ttk.Checkbutton(skills_window, text=skill, variable=var).grid(row=i, column=0, sticky=tk.W)
            skills_vars[skill] = var

        def on_confirm():
            prioritized_skills = [skill for skill, var in skills_vars.items() if var.get()]
            self.run_search_with_skills(prioritized_skills)
            skills_window.destroy()

        confirm_button = ttk.Button(skills_window, text="Confirm", command=on_confirm)
        confirm_button.grid(row=len(skills), column=0, pady=10)


    def browse_cv(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if file_path:
            self.cv_path_entry.delete(0, tk.END)
            self.cv_path_entry.insert(0, file_path)
            self.preview_cv_button.config(state="normal")
            self.preview_skills_button.config(state="normal")

    def preview_skills(self):
        cv_path = self.cv_path_entry.get().strip()
        if not cv_path or not os.path.exists(cv_path):
            messagebox.showerror("Error", "Please provide a valid CV path.")
            return

        skills_section_name = self.skills_section_entry.get().strip()
        cv_text = job_search.extract_text_from_pdf(cv_path)
        if not cv_text:
            messagebox.showerror("Error", "Failed to extract text from CV.")
            return

        skills = job_search.extract_skills_from_specified_section(cv_text, skills_section_name)
        if not skills:
            messagebox.showinfo("No Skills Found", "No skills were found in the specified section of your CV.")
            return

        preview_window = tk.Toplevel(self)
        preview_window.title("Skills Preview")
        preview_window.geometry("400x300")

        text_widget = tk.Text(preview_window, wrap=tk.WORD)
        text_widget.pack(expand=True, fill=tk.BOTH)
        text_widget.insert(tk.END, "\n".join(skills))
        text_widget.config(state="disabled")

    def preview_cv(self):
        cv_path = self.cv_path_entry.get().strip()
        if not cv_path or not os.path.exists(cv_path):
            messagebox.showerror("Error", "Please provide a valid CV path.")
            return

        skills_section_name = self.skills_section_entry.get().strip()

        preview_window = tk.Toplevel(self)
        preview_window.title("CV Preview")
        preview_window.geometry("800x600")

        text_widget = tk.Text(preview_window, wrap=tk.WORD)
        text_widget.pack(expand=True, fill=tk.BOTH)

        cv_text = job_search.extract_text_from_pdf(cv_path)
        if not cv_text:
            text_widget.insert(tk.END, "Failed to extract text from CV.")
            return

        text_widget.insert(tk.END, cv_text)

        name = job_search.extract_name(cv_text)
        job_title = job_search.extract_job_title(cv_text)
        experience = job_search.extract_experience(cv_text)
        skills_from_cv = job_search.extract_skills_from_specified_section(cv_text, skills_section_name)

        text_widget.tag_configure("name", background="lightblue")
        text_widget.tag_configure("job_title", background="lightgreen")
        text_widget.tag_configure("experience", background="lightyellow")
        text_widget.tag_configure("highlight", background="yellow")

        def highlight_text(text, tag):
            if not text:
                return
            start_index = "1.0"
            while True:
                start_index = text_widget.search(text, start_index, stopindex=tk.END, nocase=True)
                if not start_index:
                    break
                end_index = f"{start_index}+{len(text)}c"
                text_widget.tag_add(tag, start_index, end_index)
                start_index = end_index

        highlight_text(name, "name")
        highlight_text(job_title, "job_title")
        highlight_text(experience, "experience")

        for skill in skills_from_cv:
            highlight_text(skill, "highlight")

    def run_search(self):
        self.save_config()
        self.status_bar.config(text="Extracting skills from CV...")
        self.search_button.config(state="disabled")

        cv_path = self.cv_path_entry.get().strip()
        if not cv_path or not os.path.exists(cv_path):
            messagebox.showerror("Error", "Please provide a valid CV path.")
            self.status_bar.config(text="Ready")
            self.search_button.config(state="normal")
            return

        cv_text = job_search.extract_text_from_pdf(cv_path)
        if not cv_text:
            messagebox.showerror("Error", "Failed to extract text from CV.")
            self.status_bar.config(text="Ready")
            self.search_button.config(state="normal")
            return

        skills_section_name = self.skills_section_entry.get().strip()
        skills_from_cv = job_search.extract_skills_from_specified_section(cv_text, skills_section_name)

        if not skills_from_cv:
            messagebox.showinfo("No Skills Found", "No skills were found in the specified section of your CV.")
            self.status_bar.config(text="Ready")
            self.search_button.config(state="normal")
            return

        self.open_skills_window(skills_from_cv)

    def run_search_with_skills(self, prioritized_skills):
        self.status_bar.config(text="Starting job search...")
        self.save_button.config(state="disabled")
        self.all_jobs = []

        api_key = self.api_key_entry.get().strip()
        user_job_title = self.job_title_entry.get().strip()
        location = self.location_combobox.get().strip()

        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, "Starting job search...\n")
        self.update_idletasks()

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
                self.status_bar.config(text=f"Searching for: {query}")
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
                self.status_bar.config(text="No matching jobs found.")
                self.search_button.config(state="normal")
                return

            # Display results
            self.results_text.insert(tk.END, "\n--- Top Job Matches ---\n")
            for job in sorted(self.all_jobs, key=lambda x: x['Relevance Score'], reverse=True)[:5]:
                self.results_text.insert(tk.END, f"Title: {job['Job Title']}\n")
                self.results_text.insert(tk.END, f"Company: {job['Company']}\n")
                self.results_text.insert(tk.END, f"Location: {job['Location']}\n")
                self.results_text.insert(tk.END, f"Score: {job['Relevance Score']} ({job['Score Reasons']})\n\n")

            self.status_bar.config(text=f"Job search complete! Found {len(self.all_jobs)} relevant jobs.")
            self.save_button.config(state="normal")
            messagebox.showinfo("Success", f"Job search complete! Found {len(self.all_jobs)} relevant jobs.")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
            self.results_text.insert(tk.END, f"An error occurred: {e}\n")
            self.status_bar.config(text="Error occurred.")
        finally:
            self.search_button.config(state="normal")

    def save_results(self):
        if not self.all_jobs:
            messagebox.showwarning("No Results", "There are no results to save.")
            return

        results_folder = job_search.create_results_folder()
        output_filename = f"job_search_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        output_path = os.path.join(results_folder, output_filename)

        try:
            df = pd.DataFrame(self.all_jobs)
            df = df.sort_values(['Relevance Score', 'Posting Date'], ascending=[False, False])
            df.to_excel(output_path, index=False, engine='openpyxl')
            messagebox.showinfo("Save Successful", f"Results saved to {output_path}")
            self.status_bar.config(text=f"Results saved to {output_path}")
        except Exception as e:
            messagebox.showerror("Save Error", f"An error occurred while saving: {e}")
            self.status_bar.config(text="Error saving results.")

    def check_for_updates(self):
        try:
            response = requests.get(VERSION_URL)
            if response.status_code == 200:
                latest_version_info = response.json()
                latest_version = latest_version_info.get("version")
                download_url = latest_version_info.get("url")

                if latest_version and download_url and latest_version > VERSION:
                    if messagebox.askyesno("Update Available", f"A new version ({latest_version}) is available. Do you want to update?"):
                        self.status_bar.config(text=f"Downloading update...")
                        self.update_idletasks()

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
