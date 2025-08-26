from typing import List

class QueryBuilder:
    def build(self, skills: List[str], target_country: str = "", include_remote: bool = True) -> List[str]:
        base = ["visa sponsorship", "work visa", "sponsor visa", "relocation support"]
        core = skills[:8] if skills else []
        queries = []
        for b in base:
            if core:
                queries.append(f"{b} " + " ".join(core))
            else:
                queries.append(b)
        if target_country:
            queries = [q + f" {target_country}" for q in queries]
        if include_remote:
            queries.extend([q + " remote" for q in queries])
        dedup = []
        seen = set()
        for q in queries:
            k = q.lower().strip()
            if k not in seen:
                seen.add(k)
                dedup.append(q)
        return dedup[:20]
