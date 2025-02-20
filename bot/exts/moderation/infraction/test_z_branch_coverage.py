import pytest

@pytest.mark.asyncio
async def test_branch_coverage():
    """
    After all other tests have run, parse branch_count.log and print coverage.
    """
    summarize_mark_branch_coverage("branch_count.log", total_branches=20)


def summarize_mark_branch_coverage(filename="branch_count.log", total_branches=20):
    """
    Reads `filename` line by line, finds lines of the form:
        'branch <number> executed'
    Collects those numbers into a set and prints them out.

    :param filename: The log file to parse (defaults to 'branch_count.log').
    :param total_branches: If you know the total possible branch IDs, use this
                           to calculate a coverage percentage. Otherwise set
                           to None to skip coverage calculation.
    """
    try:
        with open(filename, "r") as f:
            lines = f.read().splitlines()
    except FileNotFoundError:
        print(f"No {filename} file found; no branches were recorded.")
        return

    executed_branches = set()
    for line in lines:
        # e.g. "branch 3 executed"
        parts = line.strip().split()
        if len(parts) >= 3 and parts[0] == "branch" and parts[2] == "executed":
            try:
                branch_id = int(parts[1])
                executed_branches.add(branch_id)
            except ValueError:
                pass  # ignore lines that don't parse cleanly

    if not executed_branches:
        print("No branches were executed (or none were recorded).")
    else:
        print(f"Executed branches: {sorted(executed_branches)}")

        if total_branches:
            coverage = (len(executed_branches) / total_branches) * 100
            print(f"Branch coverage: {len(executed_branches)}/{total_branches} = {coverage:.2f}%")