from tabula import read_pdf
import pandas as pd


def main():
    pdf = "Report"
    out = "Report"
    print("Parsing data from", pdf + ".pdf...")
    names = get_names(pdf)
    data = get_data(pdf)
    data = merge_names(names, data)
    result = merge_frames(data)
    try:
        result.to_excel(out + ".xlsx")
    except PermissionError:
        print("Please close " + out + ".xlsx and run again")
    finally:
        print("Data written to", out + ".xlsx")


def get_names(pdf_name) -> list:
    """Teammate Name Extraction"""
    name_area = (164.835, 122.265, 192.555, 427.185)
    names_dfs = read_pdf(pdf_name + ".pdf", pages="all", lattice=False, area=name_area)
    names = []
    for dataframe in names_dfs:
        names.append(dataframe.columns[0])
    del names_dfs
    return names


def get_data(pdf_name) -> list:
    """Page Data Extraction"""
    chart_area = (196.515, 8.415, 572.715, 785.565)
    chart_cols = ["Begin Time", "End Time", "Labor Type Code", "Activity Name", "Job Function", "Area",
                  "WMS Tran ID", "Red Cd", "Earned Minutes", "Adjusted Minutes", "Actual Time", "Job %",
                  "PF&D Time", "Off / Ref / Team / Std Event", "Cases", "Pallets", "-", "Locn", "Specialty"]
    d = read_pdf(pdf_name + ".pdf", pages="all", lattice=False, area=chart_area)
    sanitized = []
    for table in d:
        i = 0
        while len(table.columns) < len(chart_cols):
            table = table.join(pd.DataFrame({"Placeholder " + str(i): [0] * len(table.index)}))
            i += 1
        table.columns = chart_cols
        table = table.drop("-", axis=1).drop([0, 1, 2], axis=0).reset_index(drop=True)
        for row in range(len(table.index)):
            try:
                cases, pallets = (int(num) for num in str(table.at[row, "Pallets"]).split("  "))
                table.at[row, "Cases"] = cases
                table.at[row, "Pallets"] = pallets
            except ValueError:
                if str(table.at[row, "Activity Name"]) == "nan":
                    table.at[row, "Activity Name"] = str(table.at[row, "Pallets"])[:-1]
                table.at[row, "Pallets"] = ""
        sanitized.append(table)
    return sanitized


def merge_names(names, data) -> list:
    """Joining Teammate to Corresponding Data"""
    merged_frames = []
    for name, table in zip(names, data):
        n = pd.DataFrame({"Teammate": [name] * len(table.index)})
        merged_frames.append(table.join(n))

    return merged_frames


def merge_frames(data) -> pd.DataFrame:
    merged = pd.concat(data, ignore_index=True)
    return merged


if __name__ == "__main__":
    main()
