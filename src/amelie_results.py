import re

def parse_ranks_from_report(report_path):
    """
    Parse the report file and extract the rank of the causative gene for each patient.
    
    Args:
        report_path: Path to the report file
    
    Returns:
        Dictionary with patient names as keys and a tuple of (causative_gene, rank) as values.
        If the causative gene is not found in the rankings, rank will be None.
    """
    results = {}
    current_patient = None
    causative_gene = None
    current_section = None
    
    with open(report_path, 'r') as file:
        content = file.read()
        
    # Split the content by patient sections
    patient_sections = re.split(r'## Patient \d+ - ', content)
    
    # Skip the first element if it's empty
    if not patient_sections[0].strip():
        patient_sections = patient_sections[1:]
    
    for section in patient_sections:
        if not section.strip():
            continue
            
        # Extract patient name
        patient_name = section.split('\n')[0].strip()
        
        # Extract causative gene
        causative_gene_match = re.search(r'### Causative Gene: ([^\n]+)', section)
        if causative_gene_match:
            causative_gene = causative_gene_match.group(1).strip()
        else:
            continue  # Skip if no causative gene found
            
        # Find Clinical Interpretation section
        interpretation_section = section.split('### Clinical Interpretation')[-1] if '### Clinical Interpretation' in section else ""
        
        # Search for ranks in the interpretation section
        rank = None
        
        # Look for typical rank patterns in the interpretation text
        rank_patterns = [
            # Pattern for "Rank: X\nGene: CAUSATIVE_GENE"
            rf"Rank:\s*(\d+)[^\n]*\n[^\n]*Gene:\s*{re.escape(causative_gene)}",
            
            # Pattern for "Rank: X\nGene: **CAUSATIVE_GENE**"
            rf"Rank:\s*(\d+)\s*\nGene:\s*\*\*{re.escape(causative_gene)}\*\*",

            # Pattern for "**Rank: X**\nGene: **CAUSATIVE_GENE**"
            rf"\*\*Rank:\s*(\d+)\*\*\s*\nGene:\s*\*\*{re.escape(causative_gene)}\*\*",

            # Pattern for "**Rank: X**\nGene: **CAUSATIVE_GENE**"
            rf"\*\*Rank:\s*(\d+)\*\*\s*\nGene:\s*\*\*{re.escape(causative_gene)}\s*\(([^)]+)\)\*\*",

            # Pattern for "Gene: CAUSATIVE_GENE\nRank: X" 
            rf"Gene:\s*{re.escape(causative_gene)}[^\n]*\n[^\n]*Rank:\s*(\d+)",
            
            # Pattern for "#X: CAUSATIVE_GENE"
            rf"#(\d+)[^\n]*:\s*{re.escape(causative_gene)}",
            
            # Pattern for numbered lists like "1. CAUSATIVE_GENE"
            rf"(\d+)\.\s*\*\*{re.escape(causative_gene)}\*\*",
            
            # Pattern for "Rank (\d+): CAUSATIVE_GENE"
            rf"Rank\s*(\d+):\s*{re.escape(causative_gene)}",
            
            # Pattern for "CAUSATIVE_GENE is ranked #(\d+)"
            rf"{re.escape(causative_gene)}[^\n]*ranked\s*#?(\d+)"
        ]
        
        for pattern in rank_patterns:
            match = re.search(pattern, interpretation_section, re.IGNORECASE)
            if match:
                rank = int(match.group(1))
                break
    
        if rank is None:
            print(f"Warning: Rank for {causative_gene} not found in patient {patient_name}.")

        results[patient_name] = (causative_gene, rank)
    
    return results

def analyze_ranks(ranks_dict):
    """
    Analyze the ranks and provide summary statistics.
    
    Args:
        ranks_dict: Dictionary with patient names and (causative_gene, rank) tuples
    
    Returns:
        Dictionary with statistics
    """
    total_patients = len(ranks_dict)
    found_ranks = [rank for _, rank in ranks_dict.values() if rank is not None]
    missing_ranks = total_patients - len(found_ranks)
    
    stats = {
        "total_patients": total_patients,
        "patients_with_ranks": len(found_ranks),
        "patients_missing_ranks": missing_ranks,
        "average_rank": sum(found_ranks) / len(found_ranks) if found_ranks else None,
        "median_rank": sorted(found_ranks)[len(found_ranks)//2] if found_ranks else None,
        "rank_distribution": {}
    }
    
    # Count occurrences of each rank
    for rank in found_ranks:
        stats["rank_distribution"][rank] = stats["rank_distribution"].get(rank, 0) + 1
    
    return stats

if __name__ == "__main__":
    report_path = "data/report_gemini_2.5_pro.txt"
    ranks = parse_ranks_from_report(report_path)
    
    # Print results
    print("Patient Causative Gene Rankings:")
    print("-" * 40)
    not_found = []
    i = 0
    for patient, (gene, rank) in ranks.items():
        rank_str = str(rank) if rank is not None else "Not found in rankings"
        if rank is None:
            not_found.append(str(i))
        i += 1
        print(f"{patient}\t{gene}\t{rank_str}")
    
    print(", ".join(not_found))
    
    # Print statistics
    stats = analyze_ranks(ranks)
    print("\nSummary Statistics:")
    print("-" * 40)
    print(f"Total patients: {stats['total_patients']}")
    print(f"Patients with ranks found: {stats['patients_with_ranks']} ({stats['patients_with_ranks']/stats['total_patients']*100:.1f}%)")
    print(f"Patients with missing ranks: {stats['patients_missing_ranks']}")
    if stats['average_rank']:
        print(f"Average rank: {stats['average_rank']:.2f}")
        print(f"Median rank: {stats['median_rank']}")
    
    if stats['rank_distribution']:
        print("\nRank distribution:")
        for rank, count in sorted(stats['rank_distribution'].items()):
            print(f"  Rank {rank}: {count} patients ({count/stats['patients_with_ranks']*100:.1f}%)")