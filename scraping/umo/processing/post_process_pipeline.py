import pandas as pd
from typing import List, Optional
from difflib import SequenceMatcher


def post_process_faculty_csv(fac_input_file: str, join_input_file: str, pub_input_file: str, fac_output_file: str) -> Optional[List]:
    """
    Post-process faculty CSV data by removing duplicates and entries without first names. Removes
    the corresponding entries from the publications and join CSVs as well.

    Args:
        fac_input_file: Path to the input faculty CSV file.
        join_input_file: Path to the input fac-pub join table CSV file.
        pub_input_file: Path to the input publication CSV file.
        fac_output_file: CSV path to save the filtered faculty data.
    """
    # Read the CSV file
    df_original_fac = pd.read_csv(fac_input_file)
    df_original_join = pd.read_csv(join_input_file)
    df_original_pub = pd.read_csv(pub_input_file)

    original_count = len(df_original_fac)
    print(f"Original rows: {original_count}")

    # Identify rows with missing or empty first_name (NaN, empty, or whitespace)
    name_missing_mask = df_original_fac["first_name"].isna() | (df_original_fac["first_name"].astype(str).str.strip() == "")
    name_missing_df = df_original_fac[name_missing_mask].copy()
    filtered_name_missing_df = df_original_fac[~name_missing_mask].copy()

    print(
        f"After removing missing first names: {len(filtered_name_missing_df)} (removed {original_count - len(filtered_name_missing_df)})"
    )

    # Identify possible junk names
    def _is_junk_name(row, threshold: float = 0.6) -> bool:
        first_name = str(row.get("first_name", ""))
        parts = first_name.split()
        if len(parts) < 5:
            return False
        if len(first_name) <= 40:
            return False

        email = row.get("email", "")
        if pd.isna(email) or str(email).strip() == "":
            return False

        candidate = f"{parts[0].lower()}.{parts[-1].lower()}"
        username = str(email).split("@")[0].lower()
        sim = SequenceMatcher(None, candidate, username).ratio()
        return sim < threshold

    junk_name_mask = filtered_name_missing_df.apply(_is_junk_name, axis=1)
    junk_name_df = filtered_name_missing_df[junk_name_mask].copy()
    filtered_junk_name_df = filtered_name_missing_df[~junk_name_mask].copy()

    print(
        f"After removing junk names: {len(filtered_junk_name_df)} (removed {len(filtered_name_missing_df) - len(filtered_junk_name_df)})"
    )

    # Identify duplicates (same first name, last name, and email)
    dup_mask = filtered_junk_name_df.duplicated(subset=["first_name", "last_name", "email"], keep="first")
    dup_df = filtered_junk_name_df[dup_mask].copy()
    final_df = filtered_junk_name_df[~dup_mask].copy()
    print(
        f"After removing duplicates: {len(final_df)} (removed {len(filtered_junk_name_df) - len(final_df)})"
    )

    # Write the final filtered faculty data
    final_df.to_csv(fac_output_file, index=False)

    if not name_missing_df.empty or not dup_df.empty or not junk_name_df.empty:
        removed_combined = pd.concat([name_missing_df, dup_df, junk_name_df], ignore_index=True)

        removed_faculty_ids = removed_combined["faculty_id"].tolist()
        print("Removing corresponding rows from join table and publication table.")

        # Find join rows to remove and which publication_ids they reference
        removed_join_rows = df_original_join[df_original_join["faculty_id"].isin(removed_faculty_ids)].copy()
        affected_publication_ids = removed_join_rows["publication_id"].dropna().astype(str).unique().tolist()

        # Remove join rows for the filtered faculty
        updated_join_df = df_original_join[~df_original_join["faculty_id"].isin(removed_faculty_ids)].copy()

        # Determine orphaned publication_ids (no remaining author links)
        if len(affected_publication_ids) == 0:
            orphan_pub_ids = []
        else:
            still_linked = updated_join_df[updated_join_df["publication_id"].astype(str).isin(affected_publication_ids)]["publication_id"].astype(str).unique().tolist()
            orphan_pub_ids = [pid for pid in affected_publication_ids if pid not in still_linked]

        # Remove orphaned publications from the publications dataframe
        if "publication_id" in df_original_pub.columns and len(orphan_pub_ids) > 0:
            updated_pub_df = df_original_pub[~df_original_pub["publication_id"].astype(str).isin(orphan_pub_ids)].copy()
        else:
            updated_pub_df = df_original_pub.copy()

        # Write updated join and publication CSVs (don't overwrite originals; add _updated suffix)
        join_output_file = join_input_file.replace("raw.csv", "filtered.csv")
        pub_output_file = pub_input_file.replace("raw.csv", "filtered.csv")
        updated_join_df.to_csv(join_output_file, index=False)
        updated_pub_df.to_csv(pub_output_file, index=False)

        print(f"Wrote updated join table to {join_output_file}")
        print(f"Wrote updated publications table to {pub_output_file}")

        return

    else:
        print("\nNo rows were filtered out.")
        print("\nNothing to remove from join/publication tables.")
        return


