import pandas as pd


def post_process_faculty_csv(input_file: str, output_file: str) -> None:
    """
    Post-process faculty CSV data by removing duplicates and entries without first names.

    Args:
        input_file: Path to the input CSV file
        output_file: Path to the output CSV file
    """
    # Read the CSV file
    df = pd.read_csv(input_file)

    original_count = len(df)
    print(f"Original rows: {original_count}")

    # Remove people who don't have first name
    # Filter out rows where first_name is NaN, empty string, or whitespace only
    df = df[df["first_name"].notna() & (df["first_name"].str.strip() != "")]
    after_name_filter = len(df)
    print(
        f"After removing missing first names: {after_name_filter} (removed {original_count - after_name_filter} rows)"
    )

    # Remove duplicates (same first name, last name, and email should be considered a dupe row)
    # Keep the first occurrence of each duplicate
    df = df.drop_duplicates(subset=["first_name", "last_name", "email"], keep="first")
    final_count = len(df)
    print(
        f"After removing duplicates: {final_count} (removed {after_name_filter - final_count} duplicate rows)"
    )

    # Output a new CSV file with the filtered data
    df.to_csv(output_file, index=False)

    print(f"\nFiltered data written to {output_file}")
