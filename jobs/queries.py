from typing import List

class QueryBuilder:
    # Countries/regions known for visa sponsorship opportunities
    DEFAULT_TARGET_COUNTRIES = [
        "united states", "usa", "canada", "germany", "netherlands", "ireland", 
        "australia", "new zealand", "uk", "united kingdom", "sweden", "denmark",
        "switzerland", "austria", "singapore"
    ]

    def build(self, skills: List[str], job_title: str = "", target_country: str = "", include_remote: bool = True) -> List[str]:
        base_queries = ["visa sponsorship", "work visa", "sponsor visa", "relocation support"]
        
        generated_queries = set()

        # Generate queries for each combination
        for b_q in base_queries:
            # Case 1: Only base query + job title
            if job_title:
                generated_queries.add(f"{job_title} {b_q}")
            else:
                generated_queries.add(b_q)

            # Case 2: Base query + skill + job title
            for skill in skills:
                if job_title:
                    generated_queries.add(f"{job_title} {b_q} {skill}")
                else:
                    generated_queries.add(f"{b_q} {skill}")

        final_queries = []
        for q in generated_queries:
            # Add target country
            if target_country:
                final_queries.append(f"{q} {target_country}")
            else:
                # If no specific target country, add queries for default countries
                for country in self.DEFAULT_TARGET_COUNTRIES:
                    final_queries.append(f"{q} {country}")
            
            # Add remote option
            if include_remote:
                final_queries.append(f"{q} remote")
                if target_country:
                    final_queries.append(f"{q} {target_country} remote")
                else:
                    for country in self.DEFAULT_TARGET_COUNTRIES:
                        final_queries.append(f"{q} {country} remote")

        # Deduplicate and limit
        dedup = []
        seen = set()
        for q in final_queries:
            k = q.lower().strip()
            if k not in seen:
                seen.add(k)
                dedup.append(q)
        return dedup[:50] # Increased limit to 50 to accommodate more combinations
