from modules.market import analyse_market
from modules.scanner import scan_watchlist
from modules.report import print_report


def main():

    market = analyse_market()

    results = scan_watchlist(market)

    print_report(
        market,
        results,
    )


if __name__ == "__main__":
    main()