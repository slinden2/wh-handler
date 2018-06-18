class SQLQuery:

    enable_foreign_keys = """
        PRAGMA foreign_keys = 1;
    """

    # With the constraint, the get_record statement is not anymore needed. I will still use it in the _db_writer()
    # function, because that's the way I did it first.
    create_gen_data_table = """
        CREATE TABLE IF NOT EXISTS gen_data
        (
            export_id INTEGER PRIMARY KEY AUTOINCREMENT,
            export_time FLOAT,
            from_date FLOAT,
            to_date FLOAT,
            CONSTRAINT uniq_time UNIQUE (export_time)
        );
    """

    create_badge_data_table = """
        CREATE TABLE IF NOT EXISTS badge_data
        (
            id INTEGER PRIMARY KEY,
            badge_id TEXT,
            name TEXT,
            day FLOAT,
            first_entry TEXT,
            first_exit TEXT,
            second_entry TEXT,
            second_exit TEXT,
            month_id,
            FOREIGN KEY(month_id) REFERENCES gen_data(export_id)
        );
    """

    get_record = """
        SELECT
        export_time
        FROM gen_data
        WHERE
        export_time = ?;
    """

    get_export_id = """
        SELECT
        export_id
        FROM gen_data
        WHERE export_id = (
            SELECT MAX(export_id) FROM gen_data
        );
    """

    insert_gen_data = """
        INSERT INTO gen_data
        (
            export_time,
            from_date,
            to_date
        ) VALUES (?, ?, ?);
    """

    insert_badge_data = """
        INSERT INTO badge_data (
            badge_id,
            name,
            day,
            first_entry,
            first_exit,
            second_entry,
            second_exit,
            month_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """

    query_all = """
        SELECT * FROM gen_data INNER JOIN badge_data ON badge_data.month_id = gen_data.export_id;
    """

    query_employee = """
        SELECT * FROM badge_data WHERE name = ? ORDER BY day;
    """