from src.analytics.logger import get_stats
from rich.console import Console
from rich.table import Table

def main():
    stats = get_stats()
    
    console = Console()
    
    table = Table(title="AAJAS Analytics Report")
    table.add_column("Metric", style="cyan")
    table.add_column("Count", style="magenta")
    
    for key, val in stats.items():
        table.add_row(key.replace("_", " ").title(), str(val))
        
    console.print(table)

if __name__ == "__main__":
    main()
