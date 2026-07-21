from modules.journal import save_planned_opportunities
from modules.learning import generate_learning_report
from modules.market import analyse_market
from modules.report import print_report
from modules.scanner import scan_watchlist


def _print_journal_result(result: dict) -> None:
    print()
    print("TRADE JOURNAL")
    print("-" * 88)
    print(f"Journal file       : {result['path']}")
    print(f"Eligible plans     : {result['eligible']}")
    print(f"New rows added     : {result['added']}")
    print(f"Duplicates skipped : {result['duplicates_skipped']}")
    print(f"Total journal rows : {result['total_rows']}")
    print()
    print("Journal entries are planned opportunities only;")
    print("they do not represent executed trades.")


def _print_learning_result(result: dict) -> None:
    analysis = result["analysis"]
    print()
    print("LEARNING ENGINE")
    print("-" * 88)
    print(f"Learning report    : {result['path']}")
    print(f"Entries reviewed   : {analysis['total_entries']}")

    if analysis["status"] == "NO_DATA":
        print("Status             : Waiting for journal history")
        return

    print(f"Average score      : {analysis['average_score']:.1f}/100")
    print(f"Average R:R        : {analysis['average_reward_risk']:.2f}R")
    print(f"Risk pass rate     : {analysis['risk_pass_rate']:.1f}%")
    print(f"Most frequent      : {analysis['most_frequent_symbol']}")
    print()
    print("Learning insights describe planned setups, not realised returns.")


def main() -> None:
    market = analyse_market()
    results = scan_watchlist(market)

    print_report(market, results)

    journal_result = save_planned_opportunities(results)
    _print_journal_result(journal_result)

    learning_result = generate_learning_report()
    _print_learning_result(learning_result)


if __name__ == "__main__":
    main()
