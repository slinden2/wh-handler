import copy
import sqlite3
import os
import datetime
import pytz
from sql_query import SQLQuery


def _data_cleaner(input_file):
    """Reads a file and reformats it into lists.

    This function takes a text file as input and reformats it into lists
    that can be later be uploaded into database or converted into .csv file.

    """

    with open(input_file, 'r') as file:
        print("-" * 40)
        print("Reading file {}".format(input_file))
        ls = file.readlines()
        # Lets take the date that is easily available at the beginning of the file with string slicing.
        export_date = ls[3][:10]
        export_time = ls[3][11:16]
        from_date = ls[6][12:22]
        to_date = ls[7][12:22]
        gen_data = (export_date, export_time, from_date, to_date)

        ls2 = []

        # Then I iterate over the file and start formatting the data into lists.
        # Every day must have its own entry.
        for line in ls:
            ls2.append((line.strip()))
        ls2 = list(filter(None, ls2))
        id_rows = ['Nr', 'No']
        date_rows = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12',
                     '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26',
                     '27', '28', '29', '30', '31']
        ls = []
        ls4 = []
        badge_n = ""
        name = ""

        for line in ls2:
            i = 0
            if '/' in line:
                pass
            elif line[:2] in id_rows:
                if line[:2] == 'Nr':
                    badge_n = line[12:]
                else:
                    name = line[12:]
            elif line[:2] in date_rows:
                ls3 = line.split()
                if ls3[0][0] == '0':
                    ls3[0] = ls3[0][1]
                for ele in ls3:
                    ls4.append(ele)
                    i += 1
                # Insert at the beginning of each list the id and name so that the item can be
                # recognized afterwards.
                ls4.insert(0, name)
                ls4.insert(0, badge_n)
                ls.append(ls4)
                ls4 = []

        ls2 = copy.deepcopy(ls)
        # In case an employee has messed up his clock ins and outs, this for loop combines
        # double entries for certain dates.
        for i in range(len(ls2)):
            if ':' in ls2[i][2]:
                for item in ls2[i][2:]:
                    ls[i - 1].append(item)

        # This loop deletes double rows that were combined before.
        rows_to_del = 0
        for item in ls:
            if ':' in item[2]:
                rows_to_del += 1

        for i in range(len(ls) - rows_to_del):
            try:
                if ':' in ls[i][2]:
                    del ls[i]
            except IndexError:
                print("IndexError: Loop number: {}".format(i))

        # This loop searches for double clock ins and deletes all double entries
        # that are withing 600 s from other one.
        ls_comp = copy.deepcopy(ls)
        i = 0
        for item in ls_comp:
            j = 0
            if len(item) > 3:
                item2 = item[:]
                item.append('00:00')
                item2.insert(3, '00:00')
                for ele, ele2 in zip(item[3:], item2[3:]):
                    t = time_operator(ele, ele2, '-')
                    s = int(t[:2]) * 60 * 60 + int(t[3:5]) * 60
                    if s < 600:
                        print("Name: {:<20} | Date: {} | Record deleted: {}".format(ls[i][1], ls[i][2].zfill(2),
                                                                                    ls[i][j + 3]))
                        del ls[i][j + 3]
                        j -= 1
                    j += 1
            i += 1

        # Adding empty strings to the lists so that clock in/out times move to the correct indices.
        for item in ls:
            if 3 < len(item) < 7:
                if len(item) == 5 and item[4][:2] != '12' and item[4][:2] != '13':
                    item.insert(4, "")
                    item.insert(4, "")
                elif len(item) == 6:
                    if item[4][:2] == '12' and item[5][:2] != '13':
                        item.insert(5, "")
                    elif item[4][:2] == '13':
                        item.insert(4, "")

        # Filling the lists with empty strings so that every list has the same length.
        for item in ls:
            item.insert(0, gen_data[3])
            item.insert(0, gen_data[2])
            item.insert(0, gen_data[1])
            item.insert(0, gen_data[0])
            while len(item) < 11:
                item.append("")

        # Error check
        for item in ls:
            if len(item[6]) > 2:
                raise ValueError('Date error')
            if len(item) != 11:
                print(len(item))
                raise ValueError('Erroneous record length')

    return gen_data, ls


def time_operator(t1, t2, operator):
    """Sums and subtracts hours and minutes.

    The format of the hours and minutes must be 'HH:MM'"""

    # if len(str(t1)) or len(str(t2)) != 5:
    #     raise ValueError("The correct input format is 'HH:MM'. For example: '12:35'")
    #
    # if operator != '+' or operator != '-':
    #     raise ValueError("The operator must be either '+' or '-'.")

    t1_h = int(t1[:2])
    t1_m = int(t1[3:5])
    t2_h = int(t2[:2])
    t2_m = int(t2[3:5])
    t1_s = t1_h * 60 * 60 + t1_m * 60
    t2_s = t2_h * 60 * 60 + t2_m * 60
    t3_h = 0
    t3_m = 0

    if operator == '+':
        t3_s = t1_s + t2_s
        t3_h = t3_s // (60 * 60)
        t3_m = (t3_s % (60 * 60)) // 60

    elif operator == '-':

        t3_s = abs(t1_s - t2_s)
        t3_h = t3_s // (60 * 60)
        t3_m = (t3_s % (60 * 60)) // 60

    return "{}:{}".format(str(t3_h).zfill(2), str(t3_m).zfill(2))


def _file_writer(input_data: tuple):
    """Converts a tuple of lists into .csv."""

    data = input_data[1]
    day = data[0][3][:2]
    month = data[0][3][3:5]
    year = data[0][3][6:]
    file = "{}{}{}.txt".format(year, month, day)
    save_path = "C:\\Users\\Utente-006\\Documents\\Gestione\\Cronos\TXT\\"
    # Check if the file already exists
    if file not in os.listdir(save_path):
        with open(save_path + file, 'w') as f:
            print("Export data;Export time;From date;To date", file=f)
            for x in data[0][:4]:
                print(x, end=";", file=f)
            print(file=f)
            print("ID;Name;Date;Entry;Leave;Entry;Leave", file=f)
            for item in data:
                for ele in item[4:]:
                    print(ele, end=";", file=f)
                print(file=f)
            print("Successfully created {} created and saved in {}".format(file, save_path))
    else:
        print("A file for this period already exists.".format(save_path))


def open_db_conn():
    db_name = 'wh_db.sqlite'
    db = sqlite3.connect(db_name)
    c = db.cursor()
    return db, c


def commit_and_close(db, c):
    db.commit()
    c.close()
    db.close()


def _db_writer(input_data: tuple):
    """Uploads a tuple of lists into sqlite database

    Also converts string time formats to unix timestamp from Europe/Rome timezone to UTC.

    """

    gen_data, badge_data = input_data[0], input_data[1]
    db, c = open_db_conn()
    c.execute(SQLQuery.enable_foreign_keys)
    c.execute(SQLQuery.create_gen_data_table)
    c.execute(SQLQuery.create_badge_data_table)
    no_hr = '12:00'  # Set hour to data without hour to midday.
    export_time_timestamp = str_to_timestamp(gen_data[0], gen_data[1])
    from_date_timestamp = str_to_timestamp(gen_data[2], no_hr)
    to_date_timestamp = str_to_timestamp(gen_data[3], no_hr)
    data = (export_time_timestamp, from_date_timestamp, to_date_timestamp)
    record_exists = c.execute(SQLQuery.get_record, (data[0], )).fetchone()
    if record_exists is None:
        c.execute(SQLQuery.insert_gen_data, data)
        exp_id = c.execute(SQLQuery.get_export_id)
        month_id = exp_id.fetchone()
        year, month = gen_data[2][6:], gen_data[2][3:5]
        for line in badge_data:
            day = line[6]
            date = "{}/{}/{}".format(day, month, year)
            day_timestamp = str_to_timestamp(date, no_hr)
            line.insert(6, day_timestamp)
            del line[7]
            line.append(month_id[0])
            c.execute(SQLQuery.insert_badge_data, line[4:])
    else:
        print("A record for given export date already exists.")

    commit_and_close(db, c)


def select_all():
    db, c = open_db_conn()
    query_result = c.execute(SQLQuery.query_all).fetchall()
    return query_result


def select_employee(employee):
    db, c = open_db_conn()
    query_result = c.execute(SQLQuery.query_employee, (employee, )).fetchall()
    return query_result


def str_to_timestamp(date, time):
    """Converts string to unix timestamp

    :param date: str (DD/MM/YYYY)
    :param time: str (HH:MM)
    :return: float (unix timestamp (unix))
    """
    datehour = "{} {}".format(date, time)
    local = pytz.timezone('Europe/Rome')
    dt_from_str = datetime.datetime.strptime(datehour, '%d/%m/%Y %H:%M')
    local_dt = local.localize(dt_from_str, is_dst=None)
    utc_dt = local_dt.astimezone(pytz.utc)
    return utc_dt.timestamp()


def main():

    root = 'C:\\Users\\Utente-006\\Documents\\Gestione\\Cronos\\Test\\'
    source = os.walk(root)
    filename = 'FESPO099.TXT'

    for path, _, files in source:
        if filename in files:
            data = _data_cleaner("{}\\{}".format(path, filename))
            _file_writer(data)
            _db_writer(data)


if __name__ == "__main__":
    main()


