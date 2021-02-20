import os, csv
import maya
import pandas as pd


class Glucose_Data_Helper:
    def truncate_glucose_data(self, name):
        print("truncate_glucose_data")

        input_file = f"glucose_data/{name}_data.csv"
        output_file = f"glucose_data/truncated_{name}_data.csv"

        df_header = [
            "Device",
            "Serial Number",
            "Device Timestamp",
            "Record Type",
            "Historic Glucose mg/dL",
            "Scan Glucose mg/dL",
        ]

        df = pd.read_csv(
            input_file,
            delimiter=",",
            error_bad_lines=False,
            names=df_header,
        )

        df = df.drop([0, 1, 2])
        df = df.drop(["Serial Number"], axis=1)
        df = df.drop(df[df["Historic Glucose mg/dL"] == ""].index)
        df.insert(0, "Name", name)

        return df

    def split_device_time(self, dataframe):
        print("split_device_time")

        formatted_dates = []
        formatted_times = []

        device_timestamp = dataframe["Device Timestamp"]

        # loop through list
        for date_time_entry in device_timestamp:
            date_time_entry = date_time_entry.split(" ")
            date_entry = date_time_entry[0]
            date_entry = maya.parse(date_entry).datetime().date()
            formatted_dates.append(date_entry)

            time_entry = date_time_entry[1:3]
            time_entry = time_entry[0] + time_entry[1]
            time_entry = maya.parse(time_entry).datetime().time()
            formatted_times.append(time_entry)

        return [formatted_dates, formatted_times]

    def write_formatted_date_and_time(
        self, dataframe, formatted_dates, formatted_times
    ):
        print("write_formatted_date_and_time")

        dataframe["Date"] = formatted_dates
        dataframe["Time"] = formatted_times

        df = dataframe.drop(["Device Timestamp"], axis=1)

        return df

    def sort_data_by_timestamp(self, dataframe):
        print("sort_data_by_timestamp")

        df = dataframe.sort_values(
            by=["Date", "Time"],
        )

        return df

    def drop_record_type_at_six(self, dataframe):
        df = dataframe.drop(dataframe[dataframe["Record Type"] == "6"].index)

        return df

    def replace_nan(self, dataframe):
        dataframe.fillna("", inplace=True)

        return dataframe

    def add_and_drop_columns(self, dataframe):
        df = dataframe.drop(["Record Type"], axis=1)
        df["Glucose_Reading"] = df["Historic Glucose mg/dL"].astype(str) + df[
            "Scan Glucose mg/dL"
        ].astype(str)
        df = df.drop(["Historic Glucose mg/dL"], axis=1)
        df = df.drop(["Scan Glucose mg/dL"], axis=1)

        return df

    def make_data_horizontal(self, name, dataframe):
        print("make_data_horizontal")

        horizontal_data = []
        horizontal_data_entry_time = []
        horizontal_data_entry_data = []
        seperator = ["-", "-", "-"]

        date_cache = ""

        for index, row in dataframe.iterrows():
            # FIRST TIME WITH NEW MONTH
            if date_cache != row["Date"] and (date_cache == ""):
                date_cache = row["Date"]

                horizontal_data_entry_time.append(name)
                horizontal_data_entry_data.append(row["Date"])

                horizontal_data_entry_data.append(row["Glucose_Reading"])

            # OTHER TIMES WITH NEW MONTH
            elif date_cache != row["Date"] and (date_cache != ""):
                date_cache = row["Date"]

                # TAKE CARE OF OLD DATA
                horizontal_data.append(horizontal_data_entry_time)
                horizontal_data.append(horizontal_data_entry_data)
                horizontal_data.append(seperator)

                # RESET DATA LISTS
                horizontal_data_entry_time = []
                horizontal_data_entry_data = []

                # ADD NEW DATA
                horizontal_data_entry_time.append(name)
                horizontal_data_entry_data.append(row["Date"])

                horizontal_data_entry_data.append(row["Glucose_Reading"])

            else:
                horizontal_data_entry_time.append(row["Time"])
                horizontal_data_entry_data.append(row["Glucose_Reading"])

        # APPEND FINAL DATA
        horizontal_data.append(horizontal_data_entry_time)
        horizontal_data.append(horizontal_data_entry_data)

        return horizontal_data

    def write_to_csv_file(self, dataframe, name):
        dataframe = pd.DataFrame(dataframe)
        dataframe.to_csv(f"filtered_glucose_data/filtered_{name}_data.csv", index=False)

    def main(self, name):
        glucose_data_helper = Glucose_Data_Helper()

        df = glucose_data_helper.truncate_glucose_data(name=name)

        formatted_dates, formatted_times = glucose_data_helper.split_device_time(
            dataframe=df
        )

        df = glucose_data_helper.write_formatted_date_and_time(
            dataframe=df,
            formatted_dates=formatted_dates,
            formatted_times=formatted_times,
        )

        df = glucose_data_helper.sort_data_by_timestamp(dataframe=df)
        df = glucose_data_helper.drop_record_type_at_six(dataframe=df)
        df = glucose_data_helper.replace_nan(dataframe=df)
        df = glucose_data_helper.add_and_drop_columns(dataframe=df)
        df = glucose_data_helper.make_data_horizontal(name=name, dataframe=df)
        glucose_data_helper.write_to_csv_file(dataframe=df, name=name)